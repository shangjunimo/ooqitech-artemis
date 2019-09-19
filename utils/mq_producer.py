# -*- coding: utf-8 -*-

import logging

import pika
from django.conf import settings

logger = logging.getLogger('deploy.app')


class MQ_PRODUCER(object):

    def __init__(self, queue, message, port=5672):
        self._mq_credentials_user = settings.__getattr__('MQ_CREDENTIAL_USER')
        self._mq_credentials_password = settings.__getattr__('MQ_CREDENTIAL_PASSWORD')
        self._mq_host = settings.__getattr__('MQ_HOST')
        self._queue = queue
        self._message = message

        if port is not None:
            self._mq_port = port
        else:
            self._mq_port = 5672

        try:
            self._credentials = pika.PlainCredentials(self._mq_credentials_user, self._mq_credentials_password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(self._mq_host, self._mq_port, '/', self._credentials))
            self._channel = self._connection.channel()
            logger.info('{}{}chanel初始化成功'.format(self._queue, self._message))
        except Exception as e:
            logger.info('{}{}chanel初始化失败，失败原因{}'.format(self._queue, self._message, e))
            raise Exception('{}{}chanel初始化失败，失败原因{}'.format(self._queue, self._message, e))

    def send_message(self):
        try:
            self._channel.basic_publish(exchange="", routing_key=self._queue, body=self._message)
            logger.info('{}{}消息发送成功'.format(self._queue, self._message))
            return True
        except Exception as e:
            logger.info('{}{}消息发送失败，原因{}'.format(self._queue, self._message, e.message))
            return False
