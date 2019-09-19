# -*- coding: utf-8 -*-
from django.conf.urls import url

from views import (DeptAddView, DeptDelView, DeptEditView, DeptManagerView, ForgetPasswdView, GroupEmailView, LoginView,
                   RoleAddView, RoleDelView, RoleEditView, RoleGroupAddView, RoleGroupDelView, RoleGroupView,
                   RoleManagerView, UserAddView, UserDelView, UserEditView, UserEmailApiView, UserManagerView,
                   UserMangerInfoView, UserMangerPasswd, logout)

urlpatterns = [
    url(r'login/', LoginView.as_view(), name='login'),
    url(r'^logout/', logout),
    url(r'^info/', UserMangerInfoView.as_view(), name='info'),
    url(r'^passwd/', UserMangerPasswd.as_view(), name='passwd'),
    url(r'^passwd_forget/', ForgetPasswdView.as_view(), name='forgetpasswd'),
    url(r'^add/', UserAddView.as_view(), name='add'),
    url(r'^del/', UserDelView.as_view(), name='del'),
    url(r'^edit/', UserEditView.as_view(), name='edit'),
    url(r'^role/', RoleManagerView.as_view(), name='role'),
    url(r'^manager/', UserManagerView.as_view(), name='manager'),
    url(r'^dept/', DeptManagerView.as_view(), name='dept'),
    url(r'^deptadd/', DeptAddView.as_view(), name='deptadd'),
    url(r'^deptedit/', DeptEditView.as_view(), name='deptedit'),
    url(r'^deptdele/', DeptDelView.as_view(), name='deptdele'),
    url(r'^roleadd/', RoleAddView.as_view(), name='roleadd'),
    url(r'^roleedit/', RoleEditView.as_view(), name='roleedit'),
    url(r'^roledel/', RoleDelView.as_view(), name='roledel'),
    url(r'^rolegroup/', RoleGroupView.as_view(), name='rolegroup'),
    url(r'^rolegroupadd/', RoleGroupAddView.as_view(), name='rolegroupadd'),
    url(r'^rolegroupdel/', RoleGroupDelView.as_view(), name='rolegroupdel'),
    url(r'^api/group/email/', GroupEmailView.as_view(), name='groupemail'),
    url(r'^api/user/email/', UserEmailApiView.as_view(), name='user_email'),
]
