# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.

class app_version(models.Model):
    version_type = (

        (0, '最新版本'),
        (1, '历史版本')
    )

    is_published = (

        (0, '未被发布'),
        (1, '已经发布')
    )

    app_id = models.IntegerField()
    promoted_number = models.IntegerField(default=0)
    version_type = models.IntegerField(choices=version_type, default=1)
    is_published = models.IntegerField(choices=is_published, default=0)
    ftp_url = models.CharField(unique=True, max_length=128, default=None)
    origin_path = models.CharField(max_length=512, default='')
    app_date = models.DateTimeField()
    md5sum = models.CharField(max_length=32)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_app_version'


class prd_running_app_version(models.Model):
    version_type = (

        (0, '最新版本'),
        (1, '历史版本')
    )

    app_id = models.IntegerField()
    version_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_prd_running_app_version'


class sync_version_history(models.Model):
    excute_status = (

        (1, '执行中'),
        (2, '成功'),
        (3, '失败'),
    )

    job_status = (

        (0, '成功'),
        (1, '失败'),
    )

    excute_uuid = models.CharField(max_length=128, unique=True)
    excute_status = models.IntegerField(default=1, choices=excute_status)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(auto_now=True)
    job_count = models.IntegerField(default=0)
    change_jobs = models.IntegerField(default=0)
    last_job_name = models.CharField(null=True, max_length=512)
    job_status = models.IntegerField(default=0, choices=job_status)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_sync_version_history'


class extra_app_version(models.Model):
    version_type = (

        (0, '最新版本'),
        (1, '历史版本')
    )

    is_published = (

        (0, '未被发布'),
        (1, '已经发布')
    )

    app_name = models.CharField(max_length=128)
    promoted_number = models.IntegerField(default=0)
    version_type = models.IntegerField(choices=version_type, default=1)
    ftp_url = models.CharField(unique=True, max_length=128, default=None)
    app_date = models.DateTimeField()
    md5sum = models.CharField(max_length=32)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_extra_app_version'


class lastest_sync_date(models.Model):
    latest_time = models.CharField(max_length=128, null=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_lastest_sync_date'


class batch_sync_version_detail(models.Model):
    excute_status = (

        (0, '同步成功'),
        (1, '同步失败'),
        (2, '未同步')
    )

    batch_id = models.CharField(max_length=256)
    app_id = models.IntegerField()
    promoted_number = models.IntegerField(default=0)
    excute_status = models.IntegerField(default=1, choices=excute_status)
    origin_path = models.CharField(max_length=512, null=False, default=None)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_batch_sync_version_detail'
