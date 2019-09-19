# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.


class Project(models.Model):
    status = (
        (0, '不可用'),
        (1, '可用')
    )
    proj_type = (
        (1, 'java'),
        (2, 'jar'),
        (3, 'h5')
    )

    root_status = (
        (0, '非ROOT'),
        (1, 'ROOT'),
    )
    health_status = (
        (0, '成功'),
        (1, '失败'),
    )
    app_name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='appname')
    chinese_name = models.CharField(max_length=100, verbose_name='中文名称')
    role_name = models.CharField(max_length=64, verbose_name='所属部门')
    dev_group = models.CharField(max_length=50, verbose_name='开发部门')
    test_group = models.CharField(max_length=50, verbose_name='测试部门')
    project_type = models.IntegerField(default=1, choices=proj_type, verbose_name='项目类型')
    project_describe = models.CharField(max_length=200, verbose_name='项目描述')
    status = models.IntegerField(default=1, choices=status, verbose_name='项目状态')
    health_status = models.IntegerField(choices=health_status, default=0)
    is_root = models.IntegerField(default=0, choices=root_status, verbose_name='war包名是否为ROOT')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.app_name

    class Meta:
        db_table = 't_ops_project'
        ordering = ["create_time"]


class Role_To_Project(models.Model):
    role_name = models.CharField(max_length=50, blank=False, db_index=True, verbose_name='rolename')
    app_name = models.CharField(max_length=50, verbose_name='appname')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.app_name

    class Meta:
        db_table = 't_ops_role_to_project'


class Dubbo(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='name')
    port = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_dubbo'


class App_to_dubbo(models.Model):
    app_id = models.IntegerField()
    dubbo_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_ops_app_to_dubbo'
