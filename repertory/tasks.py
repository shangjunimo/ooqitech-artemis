# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime
import json
import logging
import os
import platform
import time
import uuid

from celery import task
from django.conf import settings
from django.db import connection
from django.db import transaction
from django.utils import timezone
from djcelery import models as celery_models
from event_consumer.handlers import message_handler

from projects.models import Project
from utils.crypt import Md5
from utils.emails import SendEmail
from utils.ftp import FtpUtils
from utils.mq_producer import MQ_PRODUCER
from utils.randome_string import get_random_string_from_random
from utils.timestr import get_file_create_time, get_time_now
from .models import app_version, batch_sync_version_detail, extra_app_version, lastest_sync_date, sync_version_history

# Create your views here.
logger = logging.getLogger('deploy.app')


@task
def sync_all_version_task():
    artifacts_dir = settings.__getattr__('ARTIFACTS_DIR')
    mount_point = settings.__getattr__('MOUNT_POINT_PREFIX') + os.sep

    inotify_file = artifacts_dir + os.sep + 'inotify.txt'

    if not os.path.exists(inotify_file):
        inotify_file = artifacts_dir + os.sep + '.inotify.txt'

    latest_sync_date = lastest_sync_date.objects.values('latest_time').order_by('-id').first().get('latest_time')
    logger.info('查询到上次同步时间{}'.format(str(lastest_sync_date)))

    start_time = get_time_now()
    count = 0
    last_job_name = None

    try:
        with open(inotify_file) as f:
            lines = f.readlines()
            job_count = 0
            for line in lines:
                sync_date = line.split(' ')[0]
                if 'window'.lower() in platform.system().lower():
                    postion = 5
                else:
                    postion = 6
                try:
                    promoted_number = int(line.split(' ')[1].split('/')[postion])
                except Exception as e:
                    logger.error(e)
                    subject = '【警告】同步 .inotify.txt 失败'
                    content = '解析 .inotify.txt 失败，该行内容为<{}>'.format(line)
                    SendEmail.delay(receive_users='{}'.format(settings.RECEIVE_USERS), subject=subject, content=content)
                    continue

                package_path = line.split(' ')[1].replace(artifacts_dir, mount_point).strip()

                # 兼容全量同步
                if not os.path.exists(package_path):
                    logger.info('{}同步文件已经被jenkins删除，忽略此版本'.format(package_path))
                    continue

                logger.info('读取到{}'.format(package_path))

                last_job_name = line

                if int(line.split(' ')[0]) > int(latest_sync_date):
                    job_count = job_count + 1
                    logger.info('批量同步任务{}开始同步'.format(package_path))
                    pull_single_app_package_task(package_path=package_path, promoted_number=promoted_number)
                    count = count + 1
                    logger.info('批量任务第{}{}执行成功'.format(count, package_path))

            with transaction.atomic():
                sync_version_history.objects.create(excute_uuid=uuid.uuid1(), excute_status=0, start_time=start_time,
                                                    end_time=get_time_now(), job_status=0, change_jobs=count,
                                                    job_count=job_count, last_job_name=last_job_name)
                lastest_sync_date.objects.create(latest_time=str(sync_date))
                logger.info('同步任务成功结束，总同步任务{}，成功完成同步任务{}'.format(job_count, count))

    except Exception as e:
        import traceback
        traceback.print_exc()
        with transaction.atomic():
            sync_version_history.objects.create(excute_uuid=uuid.uuid1(), excute_status=1, start_time=start_time,
                                                end_time=get_time_now(), job_status=0, change_jobs=count,
                                                job_count=job_count, last_job_name=last_job_name)
            lastest_sync_date.objects.create(latest_time=str(sync_date))

        logger.error('同步任务失败，总同步任务{}，成功完成同步任务{}，失败原因{}'.format(job_count, count, e.message))


@task
def sync_all_version_task_v2():
    artifacts_dir = settings.__getattr__('ARTIFACTS_DIR').replace('\\', '/')
    mount_point = settings.__getattr__('MOUNT_POINT_PREFIX') + os.sep

    inotify_file = artifacts_dir + os.sep.replace('\\', '/') + 'inotify.txt'

    if not os.path.exists(inotify_file):
        inotify_file = artifacts_dir + os.sep.replace('\\', '/') + '.inotify.txt'

    latest_sync_date = lastest_sync_date.objects.values('latest_time').order_by('-id').first().get('latest_time')

    start_time = get_time_now()
    last_job_name = None

    uuid_string = uuid.uuid1()

    try:
        with open(inotify_file) as f:
            lines = f.readlines()
            job_count = 0
            for line in lines:
                sync_date = line.split(' ')[0]
                try:
                    promoted_number = int(line.split(' ')[1].strip().split('/')[-2])
                except Exception as e:
                    logger.error(e)
                    subject = '【警告】同步 .inotify.txt 失败'
                    content = '解析 .inotify.txt 失败，该行内容为<{}>'.format(line)
                    SendEmail.delay(receive_users='{}'.format(settings.RECEIVE_USERS), subject=subject, content=content)
                    continue
                package_path = line.split(' ')[1].replace(artifacts_dir, mount_point).strip()

                # 兼容全量同步
                if not os.path.exists(package_path):
                    logger.info('{}同步文件已经被jenkins删除，忽略此版本'.format(package_path))
                    continue
                logger.info('读取到{}'.format(package_path))

                # 读取最新更新日志入库
                if int(line.split(' ')[0]) > int(latest_sync_date):
                    app_name = package_path.split('/')[-1].replace('-pro', '').replace('.war', '').replace('.zip', '')
                    app_name_with_subfix = package_path.split('/')[-1].strip()
                    try:
                        if 'war' in app_name_with_subfix:
                            app_id = Project.objects.get(app_name=app_name).id
                        else:
                            pass
                    except Exception as e:
                        logger.error('{}批量任务{}入待同步数据库失败'.format(uuid_string, app_name))
                        SendEmail.delay(receive_users='{}'.format(settings.__getattr__('RECEIVE_USERS')),
                                        subject='【注意】{}--{}批量推送未知应用{}入库失败，构建号为{}，源文件路径为{}'.format(
                                            settings.__getattr__('EMAIL_ENV'), uuid_string, app_name, promoted_number,
                                            package_path),
                                        content='请核实，于{}未知应用{}入库失败，请核实该应用是否存在'.format(get_time_now(), app_name))
                        continue
                    with transaction.atomic():
                        batch_sync_version_detail.objects.create(batch_id=uuid_string, app_id=app_id,
                                                                 promoted_number=promoted_number, start_time=start_time,
                                                                 origin_path=package_path, excute_status=2)
                        lastest_sync_date.objects.create(latest_time=str(sync_date))
                        logger.info('待同步应用{}-{}入库成功'.format(promoted_number, app_name))

            # sync_version_list=batch_sync_version_detail.objects.filter(batch_id=uuid_string,excute_status=2).values('batch_id','origin_path','promoted_number','app_id')
            cursor = connection.cursor()
            # sql='SELECT `t_ops_batch_sync_version_detail`.`app_id`, `t_ops_batch_sync_version_detail`.`batch_id`, `t_ops_batch_sync_version_detail`.`origin_path`, MAX(`t_ops_batch_sync_version_detail`.`promoted_number`) AS `max_promoted_number` FROM `t_ops_batch_sync_version_detail` WHERE `t_ops_batch_sync_version_detail`.`batch_id` = "{}" GROUP BY `t_ops_batch_sync_version_detail`.`app_id`'.format(uuid_string)
            sql = 'SELECT app_id,batch_id,origin_path,promoted_number FROM (SELECT *  FROM `t_ops_batch_sync_version_detail` WHERE `batch_id` = "{}" ORDER BY app_id DESC,promoted_number DESC) t GROUP BY app_id;'.format(
                uuid_string)
            cursor.execute(sql)
            sync_version_list = cursor.fetchall()

            for svl in sync_version_list:
                # package_path = svl.get('origin_path')
                package_path = svl[2]
                # promoted_number = svl.get('promoted_number')
                promoted_number = svl[3]
                # app_id = svl.get('app_id')
                app_id = svl[0]
                try:
                    logger.info('批次{}批量同步任务{}-{}开始同步'.format(uuid_string, promoted_number, package_path))
                    pull_single_app_package_task(package_path=package_path, promoted_number=promoted_number)
                    logger.info('批次{}批量同步任务{}-{}同步成功'.format(uuid_string, promoted_number, package_path))
                    batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id,
                                                             promoted_number=promoted_number).update(
                        end_time=get_time_now(), excute_status=0)

                except Exception as e:
                    batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id,
                                                             promoted_number=promoted_number).update(
                        end_time=get_time_now(), excute_status=1)
                    logger.info(
                        '批次{}批量同步任务{}-{}同步失败，失败原因{}'.format(uuid_string, promoted_number, package_path, e.message))
                    continue

                last_job_name = '{}'.format(package_path)

            with transaction.atomic():
                batch_sync_version_detail_instance = batch_sync_version_detail.objects.filter(batch_id=uuid_string)
                job_count = batch_sync_version_detail_instance.count()
                change_jobs = batch_sync_version_detail_instance.filter(excute_status=0).count()
                sync_version_history.objects.create(excute_uuid=uuid_string, excute_status=0, start_time=start_time,
                                                    end_time=get_time_now(), job_status=0, change_jobs=change_jobs,
                                                    job_count=job_count, last_job_name=last_job_name)
                logger.info('同步任务成功结束，总同步任务{}，成功完成同步任务{}'.format(job_count, change_jobs))

    except Exception as e:
        import traceback
        traceback.print_exc()
        with transaction.atomic():
            batch_sync_version_detail_instance = batch_sync_version_detail.objects.filter(batch_id=uuid_string)
            job_count = batch_sync_version_detail_instance.count()
            change_jobs = batch_sync_version_detail_instance.filter(excute_status=0).count()
            sync_version_history.objects.create(excute_uuid=uuid_string, excute_status=1, start_time=start_time,
                                                end_time=get_time_now(), job_status=0, change_jobs=change_jobs,
                                                job_count=job_count, last_job_name=last_job_name)
        logger.error('同步任务失败，总同步任务{}，成功完成同步任务{}，失败原因{}'.format(job_count, change_jobs, e.message))


@task
def send_sync_all_version_message():
    artifacts_dir = settings.__getattr__('ARTIFACTS_DIR').replace('\\', '/')
    mount_point = settings.__getattr__('MOUNT_POINT_PREFIX') + os.sep

    inotify_file = artifacts_dir + os.sep.replace('\\', '/') + 'inotify.txt'

    if not os.path.exists(inotify_file):
        inotify_file = artifacts_dir + os.sep.replace('\\', '/') + '.inotify.txt'

    latest_sync_date = lastest_sync_date.objects.values('latest_time').order_by('-id').first().get('latest_time')

    start_time = get_time_now()
    last_job_name = None

    uuid_string = uuid.uuid1()
    app_name = None

    try:
        with open(inotify_file) as f:
            lines = f.readlines()
            for line in lines:
                sync_date = line.split(' ')[0]

                try:
                    promoted_number = int(line.split(' ')[1].strip().split('/')[-2])
                except Exception as e:
                    logger.error(e)
                    subject = '【警告】同步 .inotify.txt 失败'
                    content = '解析 .inotify.txt 失败，该行内容为<{}>'.format(line)
                    SendEmail.delay(receive_users='{}'.format(settings.RECEIVE_USERS), subject=subject, content=content)
                    continue
                package_path = line.split(' ')[1].replace(artifacts_dir, mount_point).strip()

                # 兼容全量同步
                if not os.path.exists(package_path):
                    continue

                # 读取最新更新日志入库
                if int(line.split(' ')[0]) > int(latest_sync_date):
                    logger.info('读取到{}'.format(package_path))
                    app_name = package_path.split('/')[-1].replace('-pro', '').replace('.war', '').replace('.zip', '')
                    app_name_with_subfix = package_path.split('/')[-1].strip()
                    try:
                        if 'war' in app_name_with_subfix:
                            app_id = Project.objects.get(app_name=app_name).id
                        else:
                            pass
                    except Exception as e:
                        logger.info('{}批量任务{}入待同步数据库失败'.format(uuid_string, app_name))
                        SendEmail.delay(receive_users='{}'.format(settings.__getattr__('RECEIVE_USERS')),
                                        subject='【注意】{}--{}批量推送未知应用{}入库失败，构建号为{}，源文件路径为{}'.format(
                                            settings.__getattr__('EMAIL_ENV'), uuid_string, app_name, promoted_number,
                                            package_path),
                                        content='请核实，于{}未知应用{}入库失败，请核实该应用是否存在'.format(get_time_now(), app_name))
                        continue
                    with transaction.atomic():
                        batch_sync_version_detail.objects.create(batch_id=uuid_string, app_id=app_id,
                                                                 promoted_number=promoted_number, start_time=start_time,
                                                                 origin_path=package_path, excute_status=2)
                        lastest_sync_date.objects.create(latest_time=str(sync_date))
                        logger.info('待同步应用{}-{}入库成功'.format(promoted_number, app_name))

        message = str(uuid_string)
        message = json.dumps({'uuid_string': message})
        producer = MQ_PRODUCER(queue='t_ops_sync_version_message', message=message)
        if producer.send_message():
            logger.info('待同步应用{}-{}消息{}发送成功'.format(promoted_number, app_name, message))
        else:
            logger.info('待同步应用{}-{}消息{}发送失败，请重新补发消息'.format(promoted_number, app_name, message))
    except Exception as e:
        import traceback
        traceback.print_exc()
        with transaction.atomic():
            batch_sync_version_detail_instance = batch_sync_version_detail.objects.filter(batch_id=uuid_string)
            job_count = batch_sync_version_detail_instance.count()
            change_jobs = batch_sync_version_detail_instance.filter(excute_status=0).count()
            sync_version_history.objects.create(excute_uuid=uuid_string, excute_status=1, start_time=start_time,
                                                end_time=get_time_now(), job_status=0, change_jobs=change_jobs,
                                                job_count=job_count, last_job_name=last_job_name)
        logger.error('同步任务失败，总同步任务{}，成功完成同步任务{}，失败原因{}'.format(job_count, change_jobs, e.message))


def sync_all_version_task_v3(uuid_string):
    # sync_version_list=batch_sync_version_detail.objects.filter(batch_id=uuid_string,excute_status=2).values('batch_id','origin_path','promoted_number','app_id')
    cursor = connection.cursor()
    # sql='SELECT `t_ops_batch_sync_version_detail`.`app_id`, `t_ops_batch_sync_version_detail`.`batch_id`, `t_ops_batch_sync_version_detail`.`origin_path`, MAX(`t_ops_batch_sync_version_detail`.`promoted_number`) AS `max_promoted_number` FROM `t_ops_batch_sync_version_detail` WHERE `t_ops_batch_sync_version_detail`.`batch_id` = "{}" GROUP BY `t_ops_batch_sync_version_detail`.`app_id`'.format(uuid_string)
    sql = 'SELECT app_id,batch_id,origin_path,promoted_number FROM (SELECT *  FROM `t_ops_batch_sync_version_detail` WHERE `batch_id` = "{}" ORDER BY app_id DESC,promoted_number DESC) t GROUP BY app_id;'.format(
        uuid_string)
    cursor.execute(sql)
    sync_version_list = cursor.fetchall()

    for svl in sync_version_list:
        start_time = get_time_now()
        # package_path = svl.get('origin_path')
        package_path = svl[2]
        # promoted_number = svl.get('promoted_number')
        promoted_number = svl[3]
        # app_id = svl.get('app_id')
        app_id = svl[0]
        try:
            logger.info('批次{}批量同步任务{}-{}开始同步'.format(uuid_string, promoted_number, package_path))
            pull_single_app_package_task(package_path=package_path, promoted_number=promoted_number)
            logger.info('批次{}批量同步任务{}-{}同步成功'.format(uuid_string, promoted_number, package_path))
            batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id,
                                                     promoted_number=promoted_number).update(end_time=get_time_now(),
                                                                                             excute_status=0)

        except Exception as e:
            batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id,
                                                     promoted_number=promoted_number).update(end_time=get_time_now(),
                                                                                             excute_status=1)
            logger.info('批次{}批量同步任务{}-{}同步失败，失败原因{}'.format(uuid_string, promoted_number, package_path, e.message))
            continue

        last_job_name = '{}'.format(package_path)

    with transaction.atomic():
        batch_sync_version_detail_instance = batch_sync_version_detail.objects.filter(batch_id=uuid_string)
        job_count = batch_sync_version_detail_instance.count()
        change_jobs = batch_sync_version_detail_instance.filter(excute_status=0).count()
        sync_version_history.objects.create(excute_uuid=uuid_string, excute_status=0, start_time=start_time,
                                            end_time=get_time_now(), job_status=0, change_jobs=change_jobs,
                                            job_count=job_count, last_job_name=last_job_name)
        logger.info('同步任务成功结束，总同步任务{}，成功完成同步任务{}'.format(job_count, change_jobs))


@task
def sync_all_version_task_v4(uuid_string, app_id, promoted_number):
    """录入构建号触发同步"""
    try:
        sync_version = batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id, excute_status=2,
                                                                promoted_number=promoted_number).first()
        if sync_version:
            package_path = sync_version.origin_path
            batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id,
                                                     promoted_number=promoted_number).update(start_time=get_time_now())
            logger.info('批次{}批量同步任务{}-{}开始同步'.format(uuid_string, promoted_number, package_path))
            pull_single_app_package_task(package_path=package_path, promoted_number=promoted_number)
            logger.info('批次{}批量同步任务{}-{}同步成功'.format(uuid_string, promoted_number, package_path))
            batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id,
                                                     promoted_number=promoted_number).update(end_time=get_time_now(),
                                                                                             excute_status=0)
        else:
            logger.info('批次{}同步任务{}-{}已同步过，不再同步'.format(uuid_string, app_id, promoted_number))

    except Exception as e:
        batch_sync_version_detail.objects.filter(batch_id=uuid_string, app_id=app_id,
                                                 promoted_number=promoted_number).update(end_time=get_time_now(),
                                                                                         excute_status=1)
        logger.info('批次{}批量同步任务{}-{}同步失败，失败原因{}'.format(uuid_string, promoted_number, package_path, e.message))

    with transaction.atomic():
        batch_sync_version_detail_instance = batch_sync_version_detail.objects.filter(batch_id=uuid_string)
        job_count = batch_sync_version_detail_instance.count()
        change_jobs = batch_sync_version_detail_instance.filter(excute_status=0).count()
        logger.info('同步任务成功结束，总同步任务{}，成功完成同步任务{}'.format(job_count, change_jobs))


@message_handler(routing_keys='t_ops_sync_version_message')
def process_sync_message(body):
    logger.info('收到mq消息{}'.format(body.encode('utf-8')))
    sync_all_version_task_v3(uuid_string=eval(body.encode('utf-8')).get('uuid_string'))


@task
def pull_single_app_package_task(package_path, promoted_number):
    assert os.path.isfile(package_path)
    try:
        app_name = package_path.split('/')[-1].replace('-pro', '').replace('.war', '').replace('.zip', '')
        app_name_with_subfix = package_path.split('/')[-1].strip()
        ftp_base_dir = settings.__getattr__('FTP_DEPLOY_PATH')
        random_dir = get_random_string_from_random(length=8, mix_type='LU')

        if 'war' in app_name_with_subfix:
            ftp_path = ftp_base_dir + os.sep + random_dir + os.sep + app_name + '.war'
        else:
            pass

        f = FtpUtils()
        f.mkdirs(ftp_base_dir + os.sep + random_dir)
        f.upload_file(ftp_path=ftp_path, local_path=package_path)

        md5sum = Md5.md5sum(package_path)
        version_type = 0
        app_date = get_file_create_time(file_path=package_path)
        ftp_url = 'ftp://{}:{}@{}{}{}'.format(settings.__getattr__('FTP_USER'), settings.__getattr__('FTP_PASSWORD'),
                                              settings.__getattr__('FTP_HOST'), os.sep, ftp_path)
        logger.info(ftp_url)
        is_published = 0
        promoted_number = promoted_number

        if Project.objects.filter(app_name=app_name).count() == 1:

            if 'war' in app_name_with_subfix:
                app_id = Project.objects.get(app_name=app_name).id
            else:
                pass
            app_version_object = app_version.objects.filter(app_id=app_id, is_published=0,
                                                            promoted_number=promoted_number)

            if app_version_object.count() == 0:
                app_version.objects.create(app_id=app_id, version_type=version_type, app_date=str(app_date),
                                           md5sum=md5sum,
                                           ftp_url=ftp_url, is_published=is_published, promoted_number=promoted_number,
                                           origin_path=package_path)
            else:
                app_version_object.update(md5sum=md5sum, ftp_url=ftp_url, app_date=app_date)

            logger.info('{}应用推送ftp成功'.format(app_name))
        else:
            extra_app_version.objects.create(app_name=app_name, version_type=version_type, app_date=str(app_date),
                                             md5sum=md5sum, ftp_url=ftp_url, promoted_number=promoted_number)
            SendEmail.delay(receive_users='{}'.format(settings.__getattr__('RECEIVE_USERS')),
                            subject='【注意】{}--推送未知应用{}入库'.format(settings.__getattr__('EMAIL_ENV'), app_name),
                            content='请核实，于{}未知应用{}入库成功，请核实该应用是否存在'.format(get_time_now(), app_name))
            logger.warn('{}应用推送ftp成功'.format(app_name))

    except Exception as e:
        logger.error('{}-{}推送ftp失败'.format(package_path, promoted_number))
        import traceback
        traceback.print_exc()


@task
def resync_single_app_version(promoted_number, app_name=None, app_id=None):
    if app_id is not None:
        app_id = app_id

    if app_name is not None:
        app_name = app_name
        app_id = Project.objects.get(app_name=app_name).id

    batch_sync_version_detail_instance = batch_sync_version_detail.objects.filter(app_id=app_id,
                                                                                  promoted_number=promoted_number)

    try:
        start_time = get_time_now()
        package_path = batch_sync_version_detail_instance.values('origin_path')[0].get('origin_path')
        logger.info('{}{}单应用同步开始'.format(package_path, promoted_number))
        pull_single_app_package_task(package_path=package_path, promoted_number=promoted_number)
        batch_sync_version_detail_instance.update(excute_status=0, start_time=start_time, end_time=get_time_now())
        logger.info('{}单应用同步成功'.format(package_path))
        return True
    except Exception as e:
        start_time = get_time_now()
        batch_sync_version_detail_instance.update(excute_status=1, start_time=start_time, end_time=get_time_now())
        logger.error('{}单应用同步失败，失败原因{}'.format(package_path, e.message))
        return False


@task
def celery_test_task():
    import time
    time.sleep(5)
    SendEmail.delay(receive_users='debao.fan@xiangme.cn', subject='celery_test_task subject',
                    content='celery_test_task cpntent')


@task
def create_task(name, task, task_args, crontab_time):
    '''
        name # 任务名字
        task # 执行的任务 "myapp.tasks.add"
        task_args # 任务参数 {"x":1, "Y":1}

        crontab_time # 定时任务时间 格式：
        {
            'month_of_year': 9 # 月份
            'day_of_month': 5 # 日期
            'hour': 01 # 小时
            'minute':05 # 分钟
        }
        '''

    # task任务， created是否定时创建
    task, created = celery_models.PeriodicTask.objects.get_or_create(name=name, task=task)

    # 获取 crontab
    crontab = celery_models.CrontabSchedule.objects.filter(**crontab_time).first()
    if crontab is None:
        # 如果没有就创建，有的话就继续复用之前的crontab
        crontab = celery_models.CrontabSchedule.objects.create(**crontab_time)

    task.crontab = crontab  # 设置crontab
    task.enabled = True  # 开启task
    task.kwargs = json.dumps(task_args)  # 传入task参数
    expiration = timezone.now() + datetime.timedelta(day=1)
    task.expires = expiration  # 设置任务过期时间为现在时间的一天以后
    task.save()
    return True


def disable_task(name):
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = False
        task.save()
        return True
    except celery_models.PeriodicTask.DoesNotExist:
        return False


def enable_task(name):
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = True
        task.save()
        return True
    except celery_models.PeriodicTask.DoesNotExist:
        return False


def restart_task(name):
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = False
        task.save()
        time.sleep(2)
        task.enabled = True
        task.save()
        return True
    except celery_models.PeriodicTask.DoesNotExist:
        return False
