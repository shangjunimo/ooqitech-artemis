# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-16 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='app_version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.IntegerField()),
                ('promoted_number', models.IntegerField(default=0)),
                ('version_type', models.IntegerField(choices=[(0, '\u6700\u65b0\u7248\u672c'), (1, '\u5386\u53f2\u7248\u672c')], default=1)),
                ('is_published', models.IntegerField(choices=[(0, '\u672a\u88ab\u53d1\u5e03'), (1, '\u5df2\u7ecf\u53d1\u5e03')], default=0)),
                ('ftp_url', models.CharField(default=None, max_length=128, unique=True)),
                ('origin_path', models.CharField(default='', max_length=512)),
                ('app_date', models.DateTimeField()),
                ('md5sum', models.CharField(max_length=32)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_app_version',
            },
        ),
        migrations.CreateModel(
            name='batch_sync_version_detail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_id', models.CharField(max_length=256)),
                ('app_id', models.IntegerField()),
                ('promoted_number', models.IntegerField(default=0)),
                ('excute_status', models.IntegerField(choices=[(0, '\u540c\u6b65\u6210\u529f'), (1, '\u540c\u6b65\u5931\u8d25'), (2, '\u672a\u540c\u6b65')], default=1)),
                ('origin_path', models.CharField(default=None, max_length=512)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_batch_sync_version_detail',
            },
        ),
        migrations.CreateModel(
            name='extra_app_version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(max_length=128)),
                ('promoted_number', models.IntegerField(default=0)),
                ('version_type', models.IntegerField(choices=[(0, '\u6700\u65b0\u7248\u672c'), (1, '\u5386\u53f2\u7248\u672c')], default=1)),
                ('ftp_url', models.CharField(default=None, max_length=128, unique=True)),
                ('app_date', models.DateTimeField()),
                ('md5sum', models.CharField(max_length=32)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_extra_app_version',
            },
        ),
        migrations.CreateModel(
            name='lastest_sync_date',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latest_time', models.CharField(max_length=128)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_lastest_sync_date',
            },
        ),
        migrations.CreateModel(
            name='prd_running_app_version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.IntegerField()),
                ('version_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_prd_running_app_version',
            },
        ),
        migrations.CreateModel(
            name='sync_version_history',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('excute_uuid', models.CharField(max_length=128, unique=True)),
                ('excute_status', models.IntegerField(choices=[(1, '\u6267\u884c\u4e2d'), (2, '\u6210\u529f'), (3, '\u5931\u8d25')], default=1)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(auto_now=True)),
                ('job_count', models.IntegerField(default=0)),
                ('change_jobs', models.IntegerField(default=0)),
                ('last_job_name', models.CharField(max_length=512, null=True)),
                ('job_status', models.IntegerField(choices=[(0, '\u6210\u529f'), (1, '\u5931\u8d25')], default=0)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_sync_version_history',
            },
        ),
    ]
