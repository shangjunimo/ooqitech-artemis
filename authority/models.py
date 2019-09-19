# -*- coding: utf-8 -*-
import sys

reload(sys);
sys.setdefaultencoding("utf8")
from django.db import models

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, tel=None, groups=None, is_admin=None):
        """
        username 是唯一标识，没有会报错
        """

        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
            email=email,
            tel=tel,
            groups=groups,
        )
        user.is_active = True
        user.is_admin = False
        user.set_password(password)  # 检测密码合理性
        user.save(using=self._db)  # 保存密码
        return user

    def create_superuser(self, username, password, email=None, tel=None, groups=None):
        user = self.create_user(username=username,
                                password=password,
                                email=email,
                                tel=tel,
                                groups=groups,
                                )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user

    def set_passwd(self, username, password):
        user = self.get(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user


class UserInfo(AbstractBaseUser):
    username = models.CharField(max_length=32, unique=True, db_index=True, verbose_name='用户名')
    password = models.CharField(max_length=100, verbose_name=u'密码')
    email = models.EmailField(max_length=255, null=True, verbose_name=u'邮箱')
    tel = models.CharField(max_length=20, verbose_name=u'手机号')
    groups = models.ManyToManyField('Role', verbose_name=u'部门')
    create_date = models.DateField(auto_now=True, verbose_name=u'创建时间')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'  # 必须有一个唯一标识--USERNAME_FIELD

    REQUIRED_FIELDS = ['email']

    def __unicode__(self):  # __unicode__ on Python 2
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_all_user(self):
        return

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户'

    objects = UserManager()  # 创建用户


class Role(models.Model):
    name = models.CharField('标题', unique=True, max_length=64)
    detail = models.CharField(max_length=64)
    email = models.EmailField(max_length=255, null=True, verbose_name=u'邮箱')
    desc = models.CharField(max_length=64, null=True, blank=True)
    permission = models.ManyToManyField(to='Permission')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'


class Permission(models.Model):
    title = models.CharField('标题', unique=True, max_length=64)
    url = models.CharField('路由', max_length=128)
    action = models.CharField('动作', max_length=32, default="")
    group = models.ForeignKey(
        to='PermissionGroup',
        on_delete=models.CASCADE,
        default=1,
    )

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'


class PermissionGroup(models.Model):
    title = models.CharField('标题', unique=True, max_length=64)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = '权限组'
        verbose_name_plural = '权限组'


class Notification(models.Model):
    business_id = models.IntegerField(verbose_name='业务方id')
    dept_id = models.IntegerField(verbose_name='部门id')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 't_ops_notification'
