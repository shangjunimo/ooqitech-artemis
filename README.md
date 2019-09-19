# Artemis

开源 artemis 系统，基于 Python2.7 和 Django1.11

## 主要功能

- 用户权限，完整的权限控制，部门管理等。
- 项目管理。支持项目的添加、修改与删除等。
- repo 管理。结合项目管理模块可对项目进行自动同步，项目版本控制等。

## 安装

首先需要安装 MySQL5.6、RabbitMQ，之后再用 `pip` 安装依赖：

```shell
pip install -r requirements
```

## 配置

配置在 `settings` 目录下，可根据环境选择不同的配置。

### RabbitMQ 相关配置

系统使用 RabbitMQ 作为消息队列，示例相关配置如下：

```python
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

MQ_CREDENTIAL_USER = 'guest'
MQ_CREDENTIAL_PASSWORD = 'guest'
MQ_HOST = '127.0.0.1'
EXCHANGES = {
    'default': {
        'name': 'task',
        'type': 'topic',
    }
}
```

## 运行

修改配置中的数据库配置，比如：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'you-database-name',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'host',
        'PORT': 3306,
    }
}
```

创建对应的数据库之后在终端下执行以下命令创建相应的表：

```shell
python manage.py makemigrations
python manage.py migrate
```

将 authority/middleware/authentication.py 中的 `# white_list = ['.*']` 取消注释，运行

```python manage.py runserver```

浏览器打开 http://127.0.0.1:8000/ 即可看到效果。

## 用户与权限控制

完成上一步之后，此时系统中还没有用户。

在【用户权限】-【权限组管理】中添加权限组，权限管理中添加相应的权限（如 `url: ".*", 动作: "*"`）并关联权限组。

之后再添加部门，并关联权限组。最后是添加用户，用户关联部门。现在可以用创建好的用户登录系统了。

将 authority/middleware/authentication.py 中的 `white_list = ['.*']` 再注释掉，重启系统，刷新页面，即可看到登录页面，用刚刚创建的用户登录即可。
