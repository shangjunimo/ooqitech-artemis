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
            name='App_to_dubbo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.IntegerField()),
                ('dubbo_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_app_to_dubbo',
            },
        ),
        migrations.CreateModel(
            name='Dubbo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='name')),
                ('port', models.IntegerField(default=0)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_dubbo',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='appname')),
                ('chinese_name', models.CharField(max_length=100, verbose_name='\u4e2d\u6587\u540d\u79f0')),
                ('role_name', models.CharField(max_length=64, verbose_name='\u6240\u5c5e\u90e8\u95e8')),
                ('dev_group', models.CharField(max_length=50, verbose_name='\u5f00\u53d1\u90e8\u95e8')),
                ('test_group', models.CharField(max_length=50, verbose_name='\u6d4b\u8bd5\u90e8\u95e8')),
                ('project_type', models.IntegerField(choices=[(1, 'java'), (2, 'jar'), (3, 'h5')], default=1, verbose_name='\u9879\u76ee\u7c7b\u578b')),
                ('project_describe', models.CharField(max_length=200, verbose_name='\u9879\u76ee\u63cf\u8ff0')),
                ('status', models.IntegerField(choices=[(0, '\u4e0d\u53ef\u7528'), (1, '\u53ef\u7528')], default=1, verbose_name='\u9879\u76ee\u72b6\u6001')),
                ('health_status', models.IntegerField(choices=[(0, '\u6210\u529f'), (1, '\u5931\u8d25')], default=0)),
                ('is_root', models.IntegerField(choices=[(0, '\u975eROOT'), (1, 'ROOT')], default=0, verbose_name='war\u5305\u540d\u662f\u5426\u4e3aROOT')),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['create_time'],
                'db_table': 't_ops_project',
            },
        ),
        migrations.CreateModel(
            name='Role_To_Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(db_index=True, max_length=50, verbose_name='rolename')),
                ('app_name', models.CharField(max_length=50, verbose_name='appname')),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 't_ops_role_to_project',
            },
        ),
    ]
