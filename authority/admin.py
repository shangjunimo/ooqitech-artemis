# -*- coding: utf-8 -*-
from django.contrib import admin


# Register your models here.
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'action', 'group')

