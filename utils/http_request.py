# -*- coding: utf-8 -*-

import cookielib
import json
import logging
import urllib2
from urllib import urlencode

from requests.models import Response

logger = logging.getLogger('deploy.app')


class RequestWithMethod(urllib2.Request):
    def __init__(self, *args, **kwargs):
        self._method = kwargs.pop('method', None)
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method if self._method else super(RequestWithMethod, self).get_method()


class Response(object):
    '''请求响应封装'''

    def __init__(self, resp):
        self.headers = resp.headers.dict
        self.url = resp.url
        self.response = resp
        self.cookie = resp.info().get('Set-Cookie')
        self.data = resp.read()
        self._json = None

    @property
    def json(self):
        if self._json is None:
            self._json = json.loads(self.data)
        return self._json

    @property
    def content(self):
        return self.data


class MyRequest():

    def __init__(self):
        cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

    @classmethod
    def get(self, url, data=None, headers={}):
        if data:
            url += '?{}'.format(urlencode(data))
            data = None
        req = RequestWithMethod(url, data, headers=headers, method='GET')
        resp = urllib2.urlopen(req)
        return Response(resp)

    def dispatch(self, url, data=None, method='GET', headers={}, is_json=False):
        '''分发 POST、PUT、DELETE 请求

        Args:
            url: str
            data: dict
            method: str of ['POST', 'PUT', 'DELETE']
            headers: dict
            is_json: bool
        '''
        if data:
            if is_json:
                data = json.dumps(data)
                _headers = {'Content-type': 'application/json'}
                _headers.update(headers)
                headers = _headers
            else:
                data = urlencode(data)
        if method.upper() == 'GET':
            if data:
                url += '?{}'.format(data)
            data = None

        req = RequestWithMethod(url, data, headers=headers, method=method)
        resp = self.opener.open(req)
        return Response(resp)

    @classmethod
    def _dispatch(self, url, data, method, headers={}, is_json=False):
        '''分发 POST、PUT、DELETE 请求

        Args:
            url: str
            data: dict
            method: str of ['POST', 'PUT', 'DELETE']
            headers: dict
            is_json: bool
        '''
        if data:
            if is_json:
                data = json.dumps(data)
                _headers = {'Content-type': 'application/json'}
                _headers.update(headers)
                headers = _headers
            else:
                data = urlencode(data)

        req = RequestWithMethod(url, data, headers=headers, method=method)
        resp = urllib2.urlopen(req)
        return Response(resp)

    @classmethod
    def post(self, url, data=None, headers={}, is_json=False):
        return self._dispatch(url, data, 'POST', headers, is_json)

    @classmethod
    def put(self, url, data=None, headers={}, is_json=False):
        return self._dispatch(url, data, 'PUT', headers, is_json)

    @classmethod
    def delete(self, url, data=None, headers={}, is_json=False):
        return self._dispatch(url, data, 'DELETE', headers, is_json)


def requests_get(url):
    try:
        response = json.loads(urllib2.urlopen(url).read())
        return response
    except Exception as e:
        logger.error(e)
        return None


def requests_post(url, data):
    '''Post 请求
    Args:
        url: URL
        data: 字典格式参数
    Returns:
        字典格式返回值
    '''
    try:
        if type(data) == dict:
            data = json.dumps(data)
        req = urllib2.Request(url, data, headers={'Content-type': 'application/json'})
        res = urllib2.urlopen(req)
        return json.loads(res.read())
    except Exception as e:
        logger.error(e)
        return None
