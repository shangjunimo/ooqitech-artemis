# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-17 14:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authority', '0002_auto_20190917_1344'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='groups',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='groups',
            field=models.ManyToManyField(to='authority.Role', verbose_name='\u90e8\u95e8'),
        ),
    ]
