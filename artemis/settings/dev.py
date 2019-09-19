# -*- coding: utf-8 -*-

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ops_ope',
        'HOST': '127.0.0.1',
        'USER': 'user',
        'PORT': 3306,
        'PASSWORD': "password",
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8",
        }
    }
}

# Email ENV
EMAIL_ENV = 'dev'
EMAIL_USE_SSL = False

# RabbitMQ
import djcelery

djcelery.setup_loader()
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_URL = 'amqp://user:password@127.0.0.1:5672/vhost'
CELERY_RESULT_BACKEND = 'amqp://user:password@127.0.0.1:5672/vhost'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_MAX_TASKS_PER_CHILD = 3
CELERY_CONSUMER_MQ_BROKER_URL = 'amqp://user:password@127.0.0.1:5672'

# FTP
FTP_HOST = '127.0.0.1'
FTP_PORT = 21
FTP_DEPLOY_PATH = 'deploy'
FTP_LOG_PATH = 'logs'
FTP_USER = 'deploy_pull'
FTP_PASSWORD = ''

# url
URL = 'http://127.0.0.1:8000'

# mq
MQ_CREDENTIAL_USER = 'guest'
MQ_CREDENTIAL_PASSWORD = 'guest'
MQ_HOST = '127.0.0.1'
EXCHANGES = {
    'default': {
        'name': 'task',
        'type': 'topic',
    }
}


SRE_ENV = False

SFTP_PUSH_WAR_ROLLBACK_REMOTE_DIR = '/usr/local/src/backup/apache-tomcat-{app_name}'
