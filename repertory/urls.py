# -*- coding: utf-8 -*-
from django.conf.urls import url

from views import (AppVersionView, AvaibleDeployPromotoedNumberListView, AvaibleDeployVersionView,
                   AvaibleRollbackVersionView, BatchSyncDetailView, MirrorVersionDetailListView, MirrorVersionListView,
                   PullSingleAppPackageView, RsyncVersionView)

urlpatterns = [
    url(r'single$', PullSingleAppPackageView.as_view(), name='single'),
    url(r'multi$', MirrorVersionDetailListView.as_view(), name='multi'),
    url(r'^version/deploy/', AvaibleDeployVersionView.as_view(), name='versiondeploy'),
    url(r'^version/rollback/', AvaibleRollbackVersionView.as_view(), name='versionrollback'),
    url(r'^version/promotono/list/', AvaibleDeployPromotoedNumberListView.as_view(), name='versionpromotonolist'),
    url(r'^mirror/app/list/', MirrorVersionListView.as_view(), name='mirrorapp'),
    url(r'^mirror/list/', MirrorVersionListView.as_view(), name='mirrorapp'),
    url(r'^mirror/app/detail/', MirrorVersionDetailListView.as_view(), name='mirrorappdetail'),
    url(r'^mirror/app/resync/', RsyncVersionView.as_view(), name='mirrorappdersync'),
    url(r'^mirrorss/sync/batchlist', BatchSyncDetailView.as_view(), name='mirrorsynclist'),
    url(r'^appversion/', AppVersionView.as_view(), name='appversion'),
]
