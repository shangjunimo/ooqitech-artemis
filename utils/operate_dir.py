# -*- coding: utf-8 -*-
import logging
import os
import shutil

logger = logging.getLogger('deploy.app')


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        return True
    return False


def copy_dir(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                os.unlink(d)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def clean_dir(dst):
    logger.info('清空{}目录'.format(dst))
    if os.path.exists(dst):
        shutil.rmtree(dst)
        os.mkdir(dst)
        return
    os.mkdir(dst)
    return
