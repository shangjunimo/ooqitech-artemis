# -*- coding: utf-8 -*-

import logging

import pika
from django.conf import settings

logger = logging.getLogger('deploy.app')


class MQ_CONSUMER(object):

    def __init__(self, queue, callback, port=5672):
        self._mq_credentials_user = settings.__getattr__('MQ_CREDENTIAL_USER')
        self._mq_credentials_password = settings.__getattr__('MQ_CREDENTIAL_PASSWORD')
        self._mq_host = settings.__getattr__('MQ_HOST')
        self._queue = queue
        self._callback = callback

        if port is not None:
            self._mq_port = port
        else:
            self._mq_port = 5672

        if self._callback is None:
            raise Exception('call back is required')

        try:
            self._credentials = pika.PlainCredentials(self._mq_credentials_user, self._mq_credentials_password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(self._mq_host, self._mq_port, '/', self._credentials))
            self._channel = self._connection.channel()
            logger.info('{} chanel初始化成功'.format(self._queue))
        except Exception as e:
            logger.error('{} chanel初始化失败，失败原因{}'.format(self._queue, e.message))
            raise Exception('{}{}chanel初始化失败，失败原因{}'.format(self._queue, e.message))

    def bind_consumer_queue(self):

        try:
            self._channel.queue_declare(queue=self._queue)
            self._channel.basic_consume(on_message_callback=self._callback, queue=self._queue, auto_ack=True)
            self._channel.start_consuming()
            logger.info('{}队列监听成功'.format(self._queue))
        except Exception as e:
            logger.info('{}队列监听失败，失败原因{}'.format(self._queue, e.message))
