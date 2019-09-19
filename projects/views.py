# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import render, render_to_response
from django.views import View

from authority.models import Role, UserInfo
from .models import Project, Role_To_Project
from utils.project_utils import load_json, paginate, render_results
from utils.timestr import format_time

# Create your views here.

logger = logging.getLogger('deploy.app')


class ProjectInfoApiView(View):
    @load_json()
    def get(self, request, data):
        projs = Project.objects.all().values().order_by('-create_time')
        if data.get('app_name'):
            app_name = data['app_name']
            projs = projs.filter(app_name__contains=app_name)
        apps = list(projs)

        total = len(apps)
        apps = list(paginate(apps, data.get('limit', 10), data.get('curr', 1)))
        apps = render_results(apps)
        return JsonResponse({
            'code': 0,
            'status': 0,
            'msg': 'Success',
            'total': total,
            'page': data.get('curr', 1),
            'data': {
                'item': apps
            }
        })


class ProjectInfoView(View):
    template_name = 'projects/project_list.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {
            "status": 0,
            "msg": '',
        }
        r = []
        project_dict, config_status = dict(), dict()

        try:
            user_id = request.session.get('user_id')

            user_obj = UserInfo.objects.get(id=user_id)
            if user_obj.groups.all():
                group_name = user_obj.groups.all().values('name')[0].get('name')
            else:
                group_name = ''

            if group_name == 'admin':
                _all = list(Project.objects.all().values())
            else:
                _all = list(Role_To_Project.objects.filter(role_name=group_name).all().values())
                project_filter = Project.objects.filter(role_name=group_name).all().values()
                for i in project_filter:
                    project_dict[i["app_name"]] = [i["chinese_name"], i["dev_group"], i["project_type"], i["status"]]
            for i in _all:

                i["create_time"] = format_time(i["create_time"])
                i["update_time"] = format_time(i["update_time"])

                if i.get("chinese_name") is None and project_dict.get(i["app_name"]) is not None:
                    i["chinese_name"] = project_dict.get(i["app_name"])[0]
                    i["dev_group"] = project_dict.get(i["app_name"])[1]
                    i["project_type"] = project_dict.get(i["app_name"])[2]
                    i["status"] = project_dict.get(i["app_name"])[3]

                i["user"] = user_obj.username
                r.append(i)
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
        except Exception as e:
            logger.error(e)
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'ERROR'
        return JsonResponse(res)


class ProjectSearchView(View):
    template_name = 'projects/edit_project_iframe.html'

    def get(self, request):
        all_role = Role.objects.all().values()
        roles = {}
        for p in all_role:
            if p["name"] == 'admin':
                continue
            if not roles.get(p["name"]):
                roles[p["name"]] = p["id"]
        filter_res = Project.objects.filter(id=request.GET.get('id')).values()[0]
        filter_res['role'] = roles
        filter_res['sre_env'] = "False"

        return render(request, self.template_name, filter_res)

    def post(self, request):
        res = {
            "status": 0,
            "msg": '',
        }
        r = []

        user_id = request.session.get('user_id')
        project_name = request.POST.get('project_name').strip()
        user_obj = UserInfo.objects.get(id=user_id)
        group_name = user_obj.groups.all().values('name')[0].get('name')
        user_app = []
        if group_name == 'admin':
            _all = list(Project.objects.all().values())

        else:
            _all = list(Role_To_Project.objects.filter(role_name=group_name).all().values())

        for i in _all:
            user_app.append(i["app_name"])

        try:
            filter_res = Project.objects.filter(app_name__contains=project_name).values()
            for i in filter_res:
                if i["app_name"] not in user_app:
                    continue
                i["create_time"] = format_time(i["create_time"])
                i["update_time"] = format_time(i["update_time"])
                i["user"] = user_obj.username
                r.append(i)
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

        except Exception as e:
            logging.error(e)
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'ERROR'
        return JsonResponse(res)


class ProjectAddView(View):
    template_name = 'projects/add_project_iframe.html'

    def get(self, request):

        all_role = Role.objects.all().values()
        roles = {}
        r = {}
        for p in all_role:
            if p["name"] == 'admin':
                continue
            if not roles.get(p["name"]):
                roles[p["name"]] = p["id"]
        r['role'] = roles
        r['sre_env'] = "False"
        return render(request, self.template_name, r)

    def post(self, request):

        res = {"code": 0, "msg": "success"}
        try:
            Project.objects.create(
                app_name=request.POST.get('app_name'),
                chinese_name=request.POST.get('c_name'),
                role_name=request.POST.get('role_name'),
                dev_group=request.POST.get('dev_group'),
                test_group=request.POST.get('test_group'),
                project_describe=request.POST.get('desc'),
                project_type=request.POST.get('ptype'),
                is_root=request.POST.get('wartype'),
                status=1
            )
            Role_To_Project.objects.create(
                role_name=request.POST.get('role_name'),
                app_name=request.POST.get('app_name'),
            )
            logger.info("添加{}项目成功.".format(request.POST.get('app_name')))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("添加{}项目失败, error: {}".format(request.POST.get('app_name'), str(e)))
        return JsonResponse(res)


class ProjectDelView(View):
    def post(self, request):
        res = {"code": 0, "msg": "删除成功"}
        try:
            app_name = Project.objects.get(id=request.POST.get('id')).app_name

            Project.objects.filter(app_name=app_name).delete()
            Role_To_Project.objects.filter(app_name=app_name).delete()
            logger.info("删除{}项目成功.".format(request.POST.get('id')))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("删除{}项目失败, error: {}".format(request.POST.get('id'), str(e)))
        return JsonResponse(res)


class ProjectEditView(View):
    def post(self, request):
        rstatus = {'code': 0, 'msg': 'success'}
        try:

            Project.objects.filter(app_name=request.POST.get('app_name')).update(
                app_name=request.POST.get('app_name'),
                chinese_name=request.POST.get('c_name'),
                role_name=request.POST.get('role_name'),
                dev_group=request.POST.get('dev_group'),
                test_group=request.POST.get('test_group'),
                project_describe=request.POST.get('desc'),
                is_root=request.POST.get('wartype'),
                status=request.POST.get('status'),
            )

            Role_To_Project.objects.filter(app_name=request.POST.get('app_name')).update(
                role_name=request.POST.get('role_name')
            )
            logger.info("编辑 {} 项目信息成功.".format(request.POST.get('app_name')))
        except Exception as e:
            logging.error("编辑 {} 项目信息失败, error: {}".format(request.POST.get('app_name'), str(e)))
            rstatus = {'code': 500, 'msg': str(e)}
        return JsonResponse(rstatus)


class IpListView(View):
    def post(self, request):
        iplist = []
        for i in range(1, 100):
            iplist.append('192.168.1.' + str(i))
        res = {'code': 0, 'msg': '', 'ips': iplist}
        return JsonResponse(res)


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class AppIdApiView(View):
    '''根据应用名获取对应的 id'''

    def get(self, request):
        app_name = request.GET.get('app_name')
        try:
            app_id = Project.objects.filter(app_name=app_name).all()[0].id
        except IndexError as ie:
            return JsonResponse({
                'error': 'App {} not found'.format(app_name)
            })

        return JsonResponse({
            'app_id': app_id
        })


class AppListApiView(View):
    '''根据组名获取对应的应用列表'''

    def get(self, request):
        '''根据组名获取该组的应用列表
        Returns:
            {
                'applist': [{'app_id': 'app name'},]
            }
        '''

        if not request.session.get('user_id'):
            group_name = 'admin'
        else:
            user_id = request.session.get('user_id')
            try:
                user_obj = UserInfo.objects.get(id=user_id)
                group_name = user_obj.groups.all().values('name')[0].get('name')
            except Exception as e:
                logging.error(e)
                return JsonResponse({
                    'code': 500,
                    'error': '请登录或传入 <group_name> 参数'
                })

        lang = request.GET.get('lang')
        if group_name == 'admin':
            apps = Project.objects.values().all()
        else:
            apps = Project.objects.filter(
                app_name__in=Role_To_Project.objects.filter(role_name=group_name).values('app_name')
            ).values().all()
        if lang == 'cn':
            # 获取中文名
            apps = {app.get('app_name'): app.get('chinese_name') for app in apps}
        else:
            apps = {app.get('id'): app.get('app_name') for app in apps}

        res = {
            'msg': 'Success',
            'code': 0,
            'apps': apps
        }

        return JsonResponse(res)


def handler404(request, exception, template_name="404.html"):
    response = render_to_response("404.html")
    response.status_code = 404
    return response
