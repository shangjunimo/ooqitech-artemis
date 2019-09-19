# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from celery import Celery
from event_consumer.handlers import AMQPRetryConsumerStep

from artemis.settings import CELERY_CONSUMER_MQ_BROKER_URL


class Config:
    enable_utc = False
    timezone = 'Asia/Shanghai'
    BROKER_URL = CELERY_CONSUMER_MQ_BROKER_URL
    CELERY_RESULT_BACKEND = CELERY_CONSUMER_MQ_BROKER_URL


consumer_app = Celery()
consumer_app.config_from_object(Config)
consumer_app.steps['consumer'].add(AMQPRetryConsumerStep)
