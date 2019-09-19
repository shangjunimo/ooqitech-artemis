# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import json
import logging

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from authority.models import UserInfo
from .models import app_version, batch_sync_version_detail, prd_running_app_version, sync_version_history
from projects.models import Project
from .tasks import disable_task, pull_single_app_package_task, resync_single_app_version, sync_all_version_task_v2
from utils.project_utils import paginate
from utils.timestr import format_time, json_datatime_converter

logger = logging.getLogger('deploy.app')


# Create your views here.


class PullSingleAppPackageView(View):

    def post(self, request):
        try:
            requests_data = json.loads(request.body)
            package_path = requests_data.get('package_path')
            promoted_number = requests_data.get('promoted_number')
            logger.info('收到单应用推送成功，参数{}'.format(requests_data))
            pull_single_app_package_task.delay(package_path=package_path, promoted_number=promoted_number)
            return JsonResponse({'status': 0, 'msg': 'success'})
        except Exception as e:
            logger.error(e.message)
            import traceback
            traceback.print_exc()
            logger.info('收到单应用推送失败，参数{}，失败原因{}'.format(requests_data, e.message))
            return JsonResponse({'status': 1, 'msg': 'failed'})


class CrontabCreateView(View):

    def post(self, request):
        try:
            status = disable_task(name='测试发送邮件定时任务')
            logger.info(status)
            if status:
                return JsonResponse({'code': 0})
            else:
                return JsonResponse({'code': 1})
        except Exception as e:
            import traceback
            traceback.print_exc()


class CrontabDisableView(View):

    def post(self, request):
        try:
            status = disable_task(name='测试发送邮件定时任务')
            logger.info(status)
            if status:
                return JsonResponse({'code': 0})
            else:
                return JsonResponse({'code': 1})
        except Exception as e:
            import traceback
            traceback.print_exc()


class CrontabModifyView(View):

    def post(self, request):
        try:
            status = disable_task(name='测试发送邮件定时任务')
            logger.info(status)
            if status:
                return JsonResponse({'code': 0})
            else:
                return JsonResponse({'code': 1})
        except Exception as e:
            import traceback
            traceback.print_exc()


class AvaibleDeployVersionView(View):
    template_name = 'deploy/push_iframe.html'

    def get(self, request):
        print('ex..')
        return render(request, self.template_name)

    def post(self, request):
        res = {}
        requests_data = None
        print(request.POST)
        try:
            requests_data = request.POST

            logger.info(requests_data)

            if requests_data.get("app_id"):
                app_id = requests_data.get('app_id')
            else:
                app_name = requests_data.get('app_name')
                app_id = Project.objects.get(app_name=app_name).id

            prd_running_app_version_id = prd_running_app_version.objects.filter(app_id=app_id).values('version_id')

            if len(prd_running_app_version_id) == 1:
                l = app_version.objects.filter(is_published=0, app_id=app_id).exclude(
                    id=prd_running_app_version_id[0].get('version_id')).order_by('-app_date')[:10].values('id',
                                                                                                          'app_date',
                                                                                                          'md5sum',
                                                                                                          'promoted_number')
            else:
                l = app_version.objects.filter(is_published=0, app_id=app_id).order_by('-app_date')[:10].values('id',
                                                                                                                'app_date',
                                                                                                                'md5sum',
                                                                                                                'promoted_number')

            r = []
            for i in list(l):
                r.append(json.loads(json.dumps(i, default=json_datatime_converter)))

            res["total"] = len(r)
            res["data"] = {"item": list(r)}
            res['status'] = 0
            res['msg'] = 'success'
            logger.info('{}返回成功'.format(requests_data))
            return JsonResponse(res)
        except Exception as e:
            import traceback
            traceback.print_exc()
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'failed'
            logger.info('{}返回失败{}'.format(requests_data, e.message))
        return JsonResponse(res)


class AvaibleRollbackVersionView(View):
    template_name = 'deploy/rollback_iframe.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {}
        requests_data = None
        try:
            requests_data = request.POST

            if requests_data.get("app_id"):
                app_id = requests_data.get('app_id')
            else:
                app_name = requests_data.get('app_name')
                app_id = Project.objects.get(app_name=app_name).id

            prd_running_app_version_id = prd_running_app_version.objects.filter(app_id=app_id).values('version_id')

            if len(prd_running_app_version_id) == 1:
                l = app_version.objects.filter(is_published=1, app_id=app_id).exclude(
                    id=prd_running_app_version_id[0].get('version_id')).order_by('-app_date')[:5].values('id',
                                                                                                         'app_date',
                                                                                                         'md5sum',
                                                                                                         'promoted_number')
            else:
                l = app_version.objects.filter(is_published=1, app_id=app_id).order_by('-app_date')[:5].values('id',
                                                                                                               'app_date',
                                                                                                               'md5sum',
                                                                                                               'promoted_number')

            r = []
            for i in list(l):
                r.append(json.loads(json.dumps(i, default=json_datatime_converter)))

            res["total"] = len(r)
            res["data"] = {"item": list(r)}
            res['status'] = 0
            res['msg'] = 'success'
            logger.info('{}返回成功'.format(requests_data))
            return JsonResponse(res)
        except Exception as e:
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'failed'
            logger.info('{}返回失败{}'.format(requests_data, e.message))
        return JsonResponse(res)


class MultiTestView(View):

    def post(self, request):
        try:
            sync_all_version_task_v2()

            return JsonResponse({'status': 0})
        except Exception as e:

            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 1})


class MirrorVersionListView(View):
    template_name = 'repertory/repertory.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {}
        try:
            user_id = request.session.get('user_id')
            user_obj = UserInfo.objects.get(id=user_id)
            if user_obj.groups.all():
                group_name = user_obj.groups.all().values('name')[0].get('name')
            else:
                group_name = ''

            sql = '''SELECT p.id as id, p.app_name as app_name, b.end_time as last_sync_time, b.batch_id as last_sync_uuid,
                     b.promoted_number as last_sync_promoted_number, b.excute_status as last_sync_status
                     FROM (SELECT * from `t_ops_batch_sync_version_detail` ORDER BY end_time DESC) as b, ({}) as p
                     WHERE b.app_id=p.id {}
                     GROUP BY b.app_id;'''

            if group_name == 'admin':
                sub_sql = '''SELECT p.id, p.app_name from `t_ops_project` p'''
            else:
                sub_sql = '''SELECT p.id, p.app_name from `t_ops_project` p, `t_ops_role_to_project` rp
                             WHERE rp.role_name='{}' and rp.app_name=p.app_name'''

            # 搜索
            kw = request.POST.get('kw', '').strip()
            if kw:
                sql = sql.format(sub_sql, "and p.app_name like '%%{}%%'".format(kw))
            else:
                sql = sql.format(sub_sql, '')
            batches = list(batch_sync_version_detail.objects.raw(sql))
            total = len(batches)
            batches = paginate(batches, request.POST.get('limit', 10), request.POST.get('curr'))
            r = []
            for b in batches:
                r.append({
                    'id': b.id,
                    'app_name': b.app_name,
                    'last_sync_time': b.last_sync_time,
                    'last_sync_uuid': b.last_sync_uuid,
                    'last_sync_promoted_number': b.last_sync_promoted_number,
                    'last_sync_status': b.last_sync_status
                })

            res["total"] = total
            res["data"] = {"item": r}
            res['status'] = 0
            res['msg'] = 'success'
            return JsonResponse(res)
        except Exception as e:

            logger.error(e.message)
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'failed'
        return JsonResponse(res)


class MirrorVersionDetailListView(View):
    template_name = 'repertory/repo_detail_iframe.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {}
        requests_data = json.loads(request.body)
        print(requests_data)
        try:

            if requests_data.has_key("app_id"):
                app_id = requests_data.get('app_id')
            else:
                app_name = requests_data.get('app_name')
                app_id = Project.objects.get(app_name=app_name).id

            batch_sync_version_detail_instance = batch_sync_version_detail.objects

            batch_sync_version_detail_instance_parameter_list = batch_sync_version_detail_instance.filter(
                app_id=app_id).order_by('-start_time')[:10].values()
            r = []

            if len(batch_sync_version_detail_instance_parameter_list) > 0:
                for p in batch_sync_version_detail_instance_parameter_list:
                    d = {}
                    d['app_id'] = p.get('app_id')
                    d['app_name'] = Project.objects.get(id=d.get('app_id')).app_name
                    d['sync_uuid'] = p.get('batch_id')
                    d['sync_promoted_number'] = p.get('promoted_number')
                    d['sync_start_time'] = format_time(p.get('start_time'))
                    d['sync_end_time'] = format_time(p.get('end_time'))
                    d['sync_status'] = p.get('excute_status')
                    r.append(d)
            res["total"] = len(r)
            res["data"] = {"item": r}
            res['status'] = 0
            res['msg'] = 'success'
            return JsonResponse(res)
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(e.message)
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'failed'
        return JsonResponse(res)


class RsyncVersionView(View):

    def post(self, request):
        res = {}
        requests_data = json.loads(request.body)
        try:

            if requests_data.has_key("app_id"):
                app_id = requests_data.get('app_id')
                app_name = Project.objects.get(id=app_id).app_name
            else:
                app_name = requests_data.get('app_name')
                app_id = Project.objects.get(app_name=app_name).id

            promoted_number = requests_data.get('promoted_number')
            status = resync_single_app_version(app_id=app_id, promoted_number=promoted_number)
            if status:
                logger.info('{}重新同步单应用成功'.format(app_name))
                res['code'] = 0
                res['msg'] = 'success'
            else:
                res["code"] = 500
                res["msg"] = 'failed'
            return JsonResponse(res)
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(e.message)
            res["code"] = 500
            res["msg"] = 'failed'
            logger.info('{}重新同步单应用失败'.format(app_name))
        return JsonResponse(res)


class BatchSyncDetailView(View):
    template_name = 'repertory/repertory_monitor.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {}
        try:

            batch_sync_version_detail_instance = sync_version_history.objects.order_by('-end_time')[:30].values(
                'excute_uuid', 'start_time', 'end_time', 'change_jobs', 'job_count', 'last_job_name')
            r = []
            for p in batch_sync_version_detail_instance:
                d = {}
                d['excute_uuid'] = p.get('excute_uuid')
                d['start_time'] = format_time(p.get('start_time'))
                d['end_time'] = format_time(p.get('end_time'))
                d['change_jobs'] = p.get('change_jobs')
                d['job_count'] = p.get('job_count')
                d['last_job_name'] = format_time(p.get('last_job_name'))
                r.append(d)
            limit = request.POST.get('limit')
            paginator = Paginator(r, limit)
            page = request.POST.get('curr')
            try:
                s = paginator.page(page)
            except PageNotAnInteger:
                s = paginator.page(1)
            except EmptyPage:
                s = paginator.page(paginator.num_pages)
            res["total"] = len(r)
            res["data"] = {"item": s.object_list}
            res['status'] = 0
            res['msg'] = 'success'
            return JsonResponse(res)
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(e.message)
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'failed'
        return JsonResponse(res)


class AvaibleDeployPromotoedNumberListView(View):

    def post(self, request):
        res = {}
        requests_data = json.loads(request.body)
        promoted_number = list()
        try:
            app_name = requests_data.get("app_name")
            app_id = Project.objects.get(app_name=app_name).id

            if requests_data.get('task_type') == '1':
                prd_running_app_version_id = prd_running_app_version.objects.filter(app_id=app_id).values(
                    'version_id')

                if len(prd_running_app_version_id) == 1:
                    l = app_version.objects.filter(is_published=1, app_id=app_id).exclude(
                        id=prd_running_app_version_id[0].get('version_id')).order_by('-app_date')[:5].values(
                        'promoted_number')
                else:
                    l = app_version.objects.filter(is_published=1, app_id=app_id).order_by('-app_date')[
                        :5].values('promoted_number')
                for i in l:
                    promoted_number.append(str(i["promoted_number"]))

            else:
                promoted_number = [str(i["promoted_number"]) for i in list(
                    app_version.objects.filter(app_id=app_id, is_published=0, version_type=0).order_by(
                        '-promoted_number')[
                    :10].values('promoted_number'))]
            r = promoted_number

            res["data"] = r
            res['code'] = 0
            res['msg'] = 'success'
            logger.info('{}返回成功'.format(requests_data))
            return JsonResponse(res)
        except Exception as e:
            res["data"] = []
            res["code"] = 500
            res["msg"] = 'failed'
            logger.info('{}返回失败{}'.format(requests_data, e.message))
        return JsonResponse(res)


class AppVersionView(View):
    def get(self, request):
        versions = app_version.objects.all()
        versions = {v.promoted_number: v.version_type for v in versions}

        return JsonResponse({
            'versions': versions
        })
