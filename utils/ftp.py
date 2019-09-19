# -*- coding: utf-8 -*-

import ftplib
import logging
import os
from StringIO import StringIO

from django.conf import settings

logger = logging.getLogger('deploy.app')


class FtpUtils():

    def __init__(self):
        self.ftp_host = settings.__getattr__('FTP_HOST')
        self.ftp_port = settings.__getattr__('FTP_PORT')
        self.ftp_user = settings.__getattr__('FTP_USER')
        self.ftp_password = settings.__getattr__('FTP_PASSWORD')

        try:
            self._connect = ftplib.FTP(host=self.ftp_host, user=self.ftp_user, passwd=self.ftp_password)
        except Exception as e:
            raise Exception(e.message)

    def upload_file(self, ftp_path, local_path):

        assert os.path.isfile(local_path)

        try:
            with open(local_path, 'rb') as f:
                self._connect.storbinary('STOR ' + ftp_path, f)
                logger.info('{}上传到{}成功'.format(local_path, ftp_path))
                return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error('{}上传到{}失败，失败原因{}'.format(local_path, ftp_path, e.message))
            return False

    def download_file(self, ftp_path, local_path):
        try:
            with open(local_path, 'wb') as f:
                self._connect.retrbinary('RETR ' + ftp_path, f.write)
                logger.info('{}下载到{}成功'.format(ftp_path, local_path))
                return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error('{}下载到到{}失败，失败原因{}'.format(ftp_path, local_path, e.message))
            return False

    def mkdirs(self, dirs):
        try:
            self._connect.mkd(dirs)
            logger.error('创建{}成功'.format(dirs))
            return True
        except Exception as e:
            logger.error('创建{}失败，原因{}'.format(dirs, e.message))
            return False

    def __del__(self):

        if self._connect:
            self._connect.close()


def read_ftp_file(ftp_url, text=False):
    '''根据 FTP 地址读取文件内容'''
    ftp_url = ftp_url.replace('\\', '/')
    a, b = ftp_url.split('@', 1)
    url, file = b.split('/', 1)
    user, passwd = a.split('/')[-1].split(':')
    ftp = ftplib.FTP(url, user, passwd)
    r = StringIO()
    ftp.retrbinary('RETR /{}'.format(file), r.write)
    content = r.getvalue()
    if text:
        try:
            content = content.decode('gbk')
        except UnicodeDecodeError:
            try:
                content = content.decode('utf-8')
            except Exception as e:
                logger.error(e)
                content = content.decode('utf-8', 'ignore')
    return content
