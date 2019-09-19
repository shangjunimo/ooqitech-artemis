# -*- coding: utf-8 -*-
"""
项目中一些常用的函数
"""

import json
import logging
from functools import wraps

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse, QueryDict

from .timestr import format_time

logger = logging.getLogger('deploy.app')


def mount_json(*required_args):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 1:
                request = args[0]
            else:
                request = args[1]
            lack = []
            try:
                if request.method == 'GET':
                    data = request.GET
                elif request.content_type == 'application/json':
                    data = json.loads(request.body) or {}
                elif request.method == 'POST':
                    data = request.POST
                else:
                    data = QueryDict(request.body)
            except ValueError:
                return JsonResponse({'error': 'JSON 格式错误'}, status=400)
            for arg in required_args:
                if arg not in data:
                    lack.append(arg)
            if lack:
                return JsonResponse({'message': '缺失必需参数: {}'.format(', '.join(lack))}, status=400)
            request.json_data = data
            return func(*args, **kwargs)

        return wrapper

    return decorator


def app_name_to_id(app_name):
    """获取应用名对应的 ID"""
    from projects.models import Project
    try:
        return Project.objects.get(app_name=app_name).id
    except Exception as e:
        logger.error('获取应用 ID 失败：{}'.format(e))
        return 0


def app_id_to_name(app_id):
    """根据应用 ID 获取对应应用名"""
    from projects.models import Project
    try:
        return Project.objects.get(id=app_id).app_name
    except Exception as e:
        logger.error('获取应用名失败：{}'.format(e))
        return ''


def latest_version_id(app_name='', app_id=None):
    """获取应用最新版本号（构建号）"""

    if not app_id:
        app_id = app_name_to_id(app_name)
    if not 'app_name':
        return ''
    from repertory.models import prd_running_app_version, app_version
    pr = prd_running_app_version.objects.filter(app_id=app_id).order_by('-create_time').first()
    if pr:
        pv = app_version.objects.filter(id=pr.version_id).first()
        if not pv:
            return ''
        else:
            return pv.promoted_number
    else:
        return ''


def render_results(results, **kwargs):
    """对结果的时间进行格式化
    Args:
        results: 数据库模型查询结果集
        kwargs: 键为要转换的属性，值为一个函数或字典，将该属性值转换
    """

    for item in results:
        for t in ('plan_time', 'start_time', 'create_time', 'update_time', 'end_time'):
            if t in item:
                item[t] = format_time(item[t])
        for k, v in kwargs.items():
            if k in item:
                v = getattr(v, '__getitem__', None) or v
                try:
                    if callable(v):
                        item[k] = v(item[k])
                except Exception as e:
                    logger.error(e)

    return results


def paginate(query_set, limit, curr):
    """分页并对结果进行封装
    Args:
        query_set: django.db.models.query.QuerySet
        limit: 条数限制，为 0 时不限制
        curr: 当前页
    """

    if limit and int(limit):
        paginator = Paginator(query_set, limit)
        try:
            results = paginator.page(curr)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
    else:
        results = query_set

    return results


def load_json(*required_args):
    """将请求数据解析成 JSON 格式，并对需要的参数进行检查, 使用在视图函数中"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = args[1]
            lack = []
            try:
                if request.method == 'GET':
                    data = request.GET
                elif request.content_type == 'application/json':
                    data = json.loads(request.body) or {}
                elif request.method == 'POST':
                    data = request.POST
                else:
                    data = QueryDict(request.body)
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': 500, 'msg': 'JSON 解析失败'})
            for arg in required_args:
                if arg not in data:
                    lack.append(arg)
            if lack:
                return JsonResponse({'code': 400, 'msg': '缺失参数: {}'.format(', '.join(lack))})
            return func(*args, data=data, **kwargs)

        return wrapper

    return decorator


def group(func):
    """获取用户所在组, 使用在视图函数中"""

    @wraps(func)
    def wrapper(*args, **kwargs):

        # 用户筛选（admin/ 用户组）
        request = args[1]
        user_id = request.session.get('user_id')
        try:
            from authority.models import UserInfo
            user_obj = UserInfo.objects.get(id=user_id)
            if user_obj.groups.all():
                group_name = user_obj.groups.all().values('name')[0].get('name')
            else:
                group_name = ''
        except Exception as e:
            logging.error(e)
            return JsonResponse({'code': 500, 'msg': 'Failed to find user group'})

        return func(*args, group_name=group_name, **kwargs)

    return wrapper


class DotDict(dict):
    """
    a dictionary that supports dot notation
    as well as dictionary access notation
    usage: d = DotDict() or d = DotDict({'val1':'first'})
    set attributes: d.val2 = 'second' or d['val2'] = 'second'
    get attributes: d.val2 or d['val2']
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
