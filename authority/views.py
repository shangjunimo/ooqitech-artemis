# -*- coding: utf-8 -*-
import datetime
import logging

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import auth
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views import View

from authority.middleware.permission import initial_permission
from models import *
from tasks import SendEmail
from utils.randome_string import get_random_string_from_random
from utils.timestr import format_time, get_time_now

# Create your views here.
logger = logging.getLogger('deploy.app')


class HttpBase():
    def __init__(self):
        self.msg = None
        self.__http_cod_msg = {
            405: {"code": 405, "msg": "method not allow"},
            200: {"code": 0, "msg": "success"},
            500: {"code": 500, "msg": self.msg},
        }

    def response(self, status):
        return JsonResponse(self.__http_cod_msg.get(status))

    def setmsg(self, msg):
        self.msg = msg


class LoginView(View, HttpBase):
    template_name = 'user/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        status = {"code": 0, "msg": "登录成功"}

        name = request.POST.get('username')
        pwd = request.POST.get('password')
        user = auth.authenticate(username=name, password=pwd)
        if user:
            auth.login(request, user)
            logger.info('{} user login success.'.format(name))
            # 注册权限和user_id
            initial_permission(user, request)
            return JsonResponse(status)
        logger.error('{} user login error, password: {}'.format(name, pwd))
        status = {"code": 500, "msg": "账号或密码错误"}
        return JsonResponse(status)


class ForgetPasswdView(View):
    template_name = 'user/forget.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        user = UserInfo.objects.filter(username=username)
        if not user:
            logger.error({"status": "faild", "code": 500, "msg": "用户名不存在"})
            return JsonResponse({"status": "faild", "code": 500, "msg": "用户名不存在"})

        if email != user.values('email')[0]['email']:
            logger.error({"status": "faild", "code": 500, "msg": "邮箱地址不正确"})
            return JsonResponse({"status": "faild", "code": 500, "msg": "邮箱地址不正确"})
        new_password = get_random_string_from_random(8)
        UserInfo.objects.set_passwd(username, new_password)
        subject = "应用管理系统-密码找回--{}".format(settings.__getattr__('EMAIL_ENV'))
        context = '''
            <html>
            <meta charset="utf-8">
            <body>
            <p style="margin-left: 20px">Welcome {}:</p>
                <span style="margin-left: 50px;display: block">你的邮箱： {},</span>
                <span style="margin-left: 50px;padding: 0">你的密码：{}</span>

                </br>
                </br>
                </br>
                <p style="margin-left: 500px">运维团队 {}</p>

        <p style="color: red">此邮件为系统自动发送，请勿回复！</p>
        <p>-----------------------------------------------</p>
            </body>
            </html>

                  '''.format(username, email, new_password, get_time_now())
        SendEmail.delay(email, subject, context)
        logger.info("{} 用户密码修改成功".format(username))
        return JsonResponse({"status": "success", "code": 0})


class UserMangerInfoView(View):
    template_name = 'user/userinfo.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone = request.POST.get('cellphone')
        email = request.POST.get('email')
        res = {'code': 200, 'msg': 'success'}

        try:
            UserInfo.objects.filter(username=request.user).update(
                tel=phone,
                email=email
            )
            logger.info("{} 用户信息修改成功，tel: {}, email: {}".format(request.user, phone, email))
        except Exception as e:
            res = {'code': 500, 'msg': str(e)}
            logger.error("{} 用户信息修改失败, error: {}".format(request.user, str(e)))
        return JsonResponse(res)


class UserMangerPasswd(View):
    template_name = 'user/passwd.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        old_pass = request.POST.get('old_passwd')
        newpass = request.POST.get('passwd')
        user = UserInfo.objects.filter(username=request.user)
        passwd = user[0].password
        if check_password(newpass, passwd):
            logger.error("{}用户修改密码失败，密码校验失败".format(request.user))
            return JsonResponse({'code': 500, 'msg': '密码错误'})

        hash_pass = make_password(newpass, None, 'pbkdf2_sha256')
        UserInfo.objects.filter(username=request.user).update(password=hash_pass)
        logger.error("{}用户修改密码成功")
        return JsonResponse({'code': 200, 'msg': 'success'})


class UserManagerView(View):
    template_name = 'user/userlist.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):

        res = {
            "status": 0,
            "msg": '',
        }
        user_list = []
        groups = dict()
        try:
            user = UserInfo.objects.all()

            print(user)
            for userobj in user:
                print(userobj.groups.all())
                group = userobj.groups.all().values('name')
                if group:
                    groups[userobj.id] = group[0]['name']

            user2 = UserInfo.objects.all().values()
            for i in user2:
                i["create_date"] = datetime.datetime.strftime(i["create_date"], '%Y-%m-%d')
                i["last_login"] = format_time(i["last_login"])
                i['group'] = groups.get(i["id"])
                user_list.append(i)
            limit = request.POST.get('limit')
            paginator = Paginator(user_list, limit)
            page = request.POST.get('curr')
            try:
                s = paginator.page(page)
            except PageNotAnInteger:
                s = paginator.page(1)
            except EmptyPage:
                s = paginator.page(paginator.num_pages)
            res["total"] = len(user_list)
            res["data"] = {"item": s.object_list}
        except Exception as e:
            logger.error(e)
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'ERROR'
        return JsonResponse(res)


class UserAddView(View):
    template_name = 'user/add_user_iframe.html'

    def get(self, request):

        all_role = Role.objects.all().values()
        print(all_role)
        roles = {}
        r = {}
        for p in all_role:
            if not roles.get(p["name"]):
                roles[p["name"]] = p["id"]
        print(roles)
        r["groups"] = roles
        return render(request, self.template_name, r)

    def post(self, request):

        res = {"code": 0, "msg": "添加成功"}
        print(request.POST.get('groupname'))
        if request.POST.get('groupname') == 'default':
            logger.error("添加用户失败，部门不能为空")
            res = {"code": 500, "msg": "部门不能为空"}
            return JsonResponse(res)

        is_admin = request.POST.get('is_admin')
        print(request.POST)
        group = Role.objects.get(name=request.POST.get('groupname'))

        print('group', group)
        try:
            if is_admin:
                user = UserInfo(
                    username=request.POST.get('username'),
                    password=make_password(request.POST.get('password'), None, 'pbkdf2_sha256'),
                    email=request.POST.get('email'),
                    tel=request.POST.get('phone'),
                    is_admin=is_admin,
                )
                user.save()
                user.groups.add(group)
                user.save()
            else:
                user = UserInfo(
                    username=request.POST.get('username'),
                    password=make_password(request.POST.get('password'), None, 'pbkdf2_sha256'),
                    email=request.POST.get('email'),
                    tel=request.POST.get('phone'),
                )
                user.save()
                user.groups.add(group)
                user.save()
            logger.info("添加 {} 用户成功.".format(request.POST.get('username')))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("添加 {} 用户失败, error: {}".format(request.POST.get('username'), str(e)))
        return JsonResponse(res)


class UserDelView(View):

    def post(self, request):
        res = {"code": 0, "msg": "删除成功"}
        id = request.POST.get('id')

        group = UserInfo.objects.get(id=id).groups.all()[0]
        print('group', group)
        user = UserInfo.objects.get(id=request.POST.get('id'))
        group_object = Role.objects.get(name=group)
        try:
            user.groups.remove(group_object)
            user.delete()
            logger.info("删除 {} 用户成功".format(user))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("删除 {} 用户失败， error: {}".format(user, str(e)))
        return JsonResponse(res)


class UserEditView(View):
    template_name = 'user/edit_user_iframe.html'

    def get(self, request):

        all_role = Role.objects.all().values()
        groups = {}
        r = {}
        for p in all_role:
            if not groups.get(p["name"]):
                groups[p["name"]] = p["id"]

        userinfo = UserInfo.objects.filter(id=request.GET.get('id'))
        user_group = userinfo[0].groups.all().values('name')

        filter_res = userinfo.values()[0]
        if user_group:
            filter_res['user_group'] = user_group[0]["name"]
        filter_res['all_group'] = groups

        return render(request, self.template_name, filter_res)

    def post(self, request):
        res = {"code": 0, "msg": "success"}
        print(request.POST)
        group = Role.objects.get(name=request.POST.get('groupname'))
        print('group', group)
        passwd = request.POST.get('password')
        if passwd:
            UserInfo.objects.filter(
                username=request.POST.get('username')).update(
                email=request.POST.get('email'),
                tel=request.POST.get('phone'),
                password=make_password(passwd, None, 'pbkdf2_sha256'),
            )
        else:
            UserInfo.objects.filter(
                username=request.POST.get('username')).update(
                email=request.POST.get('email'),
                tel=request.POST.get('phone'),
            )
        try:
            user = UserInfo.objects.get(username=request.POST.get('username'))
            user.groups.clear()
            user.groups.add(group)
            user.save()
            logger.info('{}用户资料修改成功'.format(request.POST.get('username')))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("{}用户资料修改失败".format(request.POST.get('username')))

        return JsonResponse(res)




class RoleManagerView(View):
    template_name = 'user/rolelist.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {
            "status": 0,
            "msg": '',
        }
        permission_list = []
        groups = dict()
        try:
            permission = Permission.objects.all()

            for perobj in permission:

                groups[perobj.id] = perobj.group.title

            per = Permission.objects.all().values()
            for i in per:
                i['permissiongroup'] = groups.get(i["id"])
                permission_list.append(i)
            limit = request.POST.get('limit')
            paginator = Paginator(permission_list, limit)
            page = request.POST.get('curr')
            try:
                s = paginator.page(page)
            except PageNotAnInteger:
                s = paginator.page(1)
            except EmptyPage:
                s = paginator.page(paginator.num_pages)
            res["total"] = len(permission_list)
            res["data"] = {"item": s.object_list}
        except Exception as e:
            logger.error(e)
            res["data"] = {"item": []}
            res['total'] = 0
            res["status"] = 500
            res["msg"] = 'ERROR'
        return JsonResponse(res)


class RoleAddView(View):
    template_name = 'user/add_role_iframe.html'

    def get(self, request):
        permission = PermissionGroup.objects.all()
        permission_group = {}
        r = {}
        for p in permission:
            pg_title = p.title
            if not permission_group.get(pg_title):
                permission_group[pg_title] = pg_title
        r["groups"] = permission_group
        return render(request, self.template_name, r)

    def post(self, request):
        res = {"code": 0, "msg": "添加成功"}
        print(request.POST)
        if request.POST.get('permissiongroupname') == 'default':
            logger.error("添加权限组失败，error: 权限组不能为空")
            res = {"code": 500, "msg": "权限组不能为空"}
            return JsonResponse(res)
        permissiongroup = PermissionGroup.objects.get(title=request.POST.get('permissiongroupname'))
        print('aaa')
        try:
            permission = Permission.objects.create(
                title=request.POST.get('rolegroupname'),
                url=request.POST.get('url'),
                action=request.POST.get('action'),
                group=permissiongroup
            )
            permission.save()
            logger.info("添加{}权限成功.".format(request.POST.get('rolegroupname')))
        except IntegrityError:
            res = {"code": 500, "msg": '权限名称已存在'}
            logging.error("添加{}权限失败，error: {}".format(request.POST.get('rolegroupname').encode('utf-8'), '权限名称已存在'))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logger.error("添加{}权限失败，error: {}".format(request.POST.get('rolegroupname'), str(e)))

        return JsonResponse(res)


class RoleEditView(View):
    template_name = 'user/edit_role_iframe.html'

    def get(self, request):
        permissiongroup = PermissionGroup.objects.all().values('title')

        permission_group_dic = {}
        for pg in permissiongroup:
            permission_group_dic[pg["title"]] = pg["title"]

        permission = Permission.objects.filter(id=request.GET.get('id')).values()[0]

        permission_group_name = PermissionGroup.objects.filter(id=permission["group_id"]).values('title')[0]
        filter_res = permission
        filter_res['permission_group'] = permission_group_name["title"]
        filter_res['all_permission'] = permission_group_dic
        return render(request, self.template_name, filter_res)

    def post(self, request):
        res = {"code": 0, "msg": "修改成功"}
        permission_group = PermissionGroup.objects.get(title=request.POST.get('permissiongroupname'))
        try:

            Permission.objects.filter(
                title=request.POST.get('title')).update(
                url=request.POST.get('url'),
                action=request.POST.get('action'),
                group=permission_group
            )
            logger.info("修改权限组成功")
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("修改组失败，error: {}".format(str(e)))

        return JsonResponse(res)


class RoleDelView(View):

    def post(self, request):
        res = {"code": 0, "msg": "删除成功"}
        id = request.POST.get('id')

        bind_role = Permission.objects.get(id=id).role_set.all()
        if len(bind_role) > 0:
            res = {"code": 200, "msg": "该权限已绑定到用户，请解绑后再试！"}
            logger.error("删除权限组失败，该权限已绑定到用户，请解绑后再试！")
            return JsonResponse(res)

        try:
            Permission.objects.filter(id=id).delete()
            logger.info("删除 {} 权限成功".format(id))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("删除 {} 权限失败, error: ".format(id, str(e)))
        return JsonResponse(res)


class DeptManagerView(View):
    template_name = 'user/deptlist.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {
            "status": 0,
            "msg": '',
        }
        r = []
        try:
            _all = Role.objects.all().values()
            for i in _all:
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


class DeptAddView(View):
    template_name = 'user/add_dept_iframe.html'

    def get(self, request):
        all_permission = Permission.objects.all().values()
        permissions = {}
        r = {}
        for p in all_permission:
            print(p)
            if not permissions.get(p["title"]):
                permissions[p["title"]] = p["id"]
        r["permession"] = permissions
        return render(request, self.template_name, r)

    def post(self, request):
        res = {"code": 0, "msg": "添加成功"}
        per_count = len(Permission.objects.all())
        permissions = list()
        for l in xrange(per_count):
            key = '{}[{}]'.format('permessions', l)
            if request.POST.get(key):
                permissions.append(request.POST.get(key))

        if len(permissions) == 0:
            logger.error("添加部门失败，权限不能为空")
            return JsonResponse({"code": 500, "msg": "权限不能为空"})
        try:
            role = Role(
                name=request.POST.get('name').encode('utf-8'),
                detail=request.POST.get('fullname').encode('utf-8'),
                email=request.POST.get('email').encode('utf-8'),
                desc=request.POST.get('desc').encode('utf-8')
            )
            role.save()
            for p in permissions:
                per = Permission.objects.get(title=p)
                role.permission.add(per)
                role.save()
            logger.info("添加{}部门成功.".format(request.POST.get('name')))
        except IntegrityError:
            res = {"code": 500, "msg": '部门已存在'}
            logging.error("添加{}部门失败，error: {}".format(request.POST.get('name').encode('utf-8'), '部门已存在'))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("添加{}部门失败，error: {}".format(request.POST.get('name').encode('utf-8'), str(e)))

        return JsonResponse(res)


class DeptEditView(View):
    template_name = 'user/edit_dept_iframe.html'

    def get(self, request):

        all_permission = Permission.objects.all().values()
        permissions = {}
        role_permission = []
        for p in all_permission:
            permissions[p["title"]] = p["id"]

        roleinfo = Role.objects.filter(id=request.GET.get('id'))
        r = roleinfo[0].permission.all().values('title')
        for i in r:
            role_permission.append(i["title"])

        filter_res = roleinfo.values()[0]
        filter_res['user_permission'] = role_permission
        filter_res['all_permission'] = permissions

        return render(request, self.template_name, filter_res)

    def post(self, request):
        res = {"code": 0, "msg": "编辑成功"}
        print('request post', request.POST)
        per_count = len(Permission.objects.all())
        permissions = list()
        for l in xrange(per_count):
            key = '{}[{}]'.format('permessions', l)
            if request.POST.get(key):
                permissions.append(request.POST.get(key))
        if len(permissions) == 0:
            logger.error("编辑部门信息失败，权限不能为空")
            return JsonResponse({"code": 500, "msg": "权限不能为空"})
        try:
            Role.objects.filter(
                id=request.POST.get('id')).update(
                name=request.POST.get('name'),
                detail=request.POST.get('fullname'),
                email=request.POST.get('email'),
                desc=request.POST.get('desc')
            )
            roleinfo = Role.objects.get(name=request.POST.get('name'))
            roleinfo.permission.clear()
            for p in permissions:
                per = Permission.objects.get(title=p)
                roleinfo.permission.add(per)
                roleinfo.save()
            logger.info("编辑{}部门信息成功.".format(request.POST.get('name')))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("编辑{}部门信息失败, error: {}".format(request.POST.get('name'), str(e)))

        return JsonResponse(res)


class DeptDelView(View):

    def post(self, request):
        res = {"code": 0, "msg": "删除成功"}
        id = request.POST.get('id')

        users = Role.objects.get(id=id).userinfo_set.all()
        if len(users) > 0:
            logger.error("删除部门失败，用户已绑定该部门，请解绑后再试！")
            res = {"code": 200, "msg": "用户已绑定该部门，请解绑后再试！"}
            return JsonResponse(res)

        all_permission = Role.objects.get(id=id).permission.all().values('title')

        role = Role.objects.get(id=id)
        try:
            for permission in all_permission:
                per = Permission.objects.get(title=permission["title"])
                role.permission.remove(per)

            role.delete()
            logger.info("删除 {} 部门成功.".format(role))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("删除 {} 部门失败, error: {}".format(role, str(e)))
        return JsonResponse(res)


class RoleGroupView(View):
    template_name = 'user/rolegrouplist.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {
            "status": 0,
            "msg": '',
        }
        r = []
        try:
            _all = PermissionGroup.objects.all().values()
            for i in _all:
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


class RoleGroupAddView(View):
    template_name = 'user/add_rolegroup_iframe.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        res = {"code": 0, "msg": "添加成功"}

        try:
            PermissionGroup.objects.create(
                title=request.POST.get('rolegroupname')
            )
            logger.info("添加 {} 权限组成功.".format(request.POST.get('rolegroupname')))
        except IntegrityError:
            res = {"code": 500, "msg": '权限组已存在'}
            logging.error("添加{}权限失败，error: {}".format(request.POST.get('rolegroupname').encode('utf-8'), '权限组已存在'))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("添加 {} 权限组失败, error: {}".format(request.POST.get('rolegroupname'), str(e)))

        return JsonResponse(res)


class RoleGroupDelView(View):
    def post(self, request):
        res = {"code": 0, "msg": "删除成功"}
        id = request.POST.get('id')

        permessiong = PermissionGroup.objects.get(id=id)
        if len(permessiong.permission_set.all()) > 0:
            logger.error("删除权限组失败，权限组已绑定权限，请解绑后再试！")
            res = {"code": 200, "msg": "权限组已绑定权限，请解绑后再试！"}
            return JsonResponse(res)

        title = ''
        try:
            title = PermissionGroup.objects.filter(id=id).values('title')[0]
            PermissionGroup.objects.get(id=id).delete()
            logger.info("删除 {} 权限组成功".format(title))
        except Exception as e:
            res = {"code": 500, "msg": str(e)}
            logging.error("删除 {} 权限组失败, error: {}".format(title, str(e)))
        return JsonResponse(res)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def reset_pwd(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    user = UserInfo.objects.filter(username=username)
    if not user:
        return JsonResponse({"status": "faild", "code": 500, "msg": "用户名不存在"})

    if email != user.values('email')[0]['email']:
        return JsonResponse({"status": "faild", "code": 500, "msg": "邮箱地址不正确"})
    new_password = get_random_string_from_random(8)
    UserInfo.objects.set_passwd(username, new_password)
    subject = "应用管理系统-密码找回--{}".format(settings.__getattr__('EMAIL_ENV'))
    context = '''
        <html>
        <meta charset="utf-8">
        <body>
        <p style="margin-left: 20px">Welcome {}:</p>
            <span style="margin-left: 50px;display: block">你的邮箱： {},</span>
            <span style="margin-left: 50px;padding: 0">你的密码：{}</span>
            
            </br>
            </br>
            </br>
            <p style="margin-left: 500px">运维团队 {}</p>
    
    <p style="color: red">此邮件为系统自动发送，请勿回复！</p>
    <p>-----------------------------------------------</p>
        </body>
        </html>
        
              '''.format(username, email, new_password, get_time_now())
    SendEmail(email, subject, context)
    return JsonResponse({"status": "success", "code": 0})


class GroupEmailView(View):

    def get(self, request):
        try:
            res = list(Role.objects.all().values('id', 'name'))
            return JsonResponse({'code': 200, 'data': res, 'msg': 'success'})
        except Exception as e:
            logger.error('获取部门邮箱失败：error: {}'.format(e))
        return JsonResponse({"code": 200})


class UserEmailApiView(View):
    def get(self, request):
        """获取用户 ID"""
        try:
            res = list(UserInfo.objects.all().values('id', 'username'))
            return JsonResponse({
                'code': 200,
                'data': res,
                'msg': 'Success'
            })
        except Exception as e:
            logger.error('获取用户 ID 失败：{}'.format(e))
            return JsonResponse({
                'code': 500,
                'msg': '获取失败'
            })
