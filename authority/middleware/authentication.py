# -*- coding: utf-8 -*-
import re

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class ValidPermission(MiddlewareMixin):

    def process_request(self, request):
        # 定义白名单
        current_path = request.path_info
        white_list = ['/user/login/', '/user/logout/', '/user/passwd_forget/', '/tasks/api/dbs/',
                      '/projects/appid/', '/projects/apps/', '/repertory/appversion/',
                      '/projects/api/apps/', '/projects/api/appid/', '/projects/api/public/*', '/tasks/api/public/*', ]
        # white_list = ['.*']
        for p in white_list:
            ret = re.match(p, current_path)
            if ret:
                return None
        if not request.session.get('permissions'):
            return HttpResponseRedirect('/user/login/')

        # 权限控制
        permissions = request.session.get('permissions', [])
        for item in permissions.values():
            urls = item.get("urls")
            for p in urls:
                p = '^{path}$'.format(path=p)
                ret = re.match(p, current_path)
                if ret:
                    request.actions = item.get("actions")
                    return None
        return HttpResponse('你没有访问权限！')
