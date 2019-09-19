# -*- coding: utf-8 -*-

from django.conf.urls import url

from views import *

urlpatterns = [
    url(r'^list/', ProjectInfoView.as_view(), name='project_list'),
    url(r'^search/', ProjectSearchView.as_view(), name='project_search'),
    url(r'^add/', ProjectAddView.as_view(), name='project_add'),
    url(r'^del/', ProjectDelView.as_view(), name='project_del'),
    url(r'^edit/', ProjectEditView.as_view(), name='project_edit'),
    url(r'^ip/', IpListView.as_view(), name='ip'),
    url(r'^appid/', AppIdApiView.as_view(), name='app_id'),  # 废弃
    url(r'^apps/', AppListApiView.as_view(), name='app_list'),  # 废弃
    url(r'^api/apps/', AppListApiView.as_view(), name='app_list'),
    url(r'^api/appid/', AppIdApiView.as_view(), name='app_id'),
    url(r'^api/public/projects/', ProjectInfoApiView.as_view(), name='api_project_info'),
]
