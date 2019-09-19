FROM python:2.7.16-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
RUN mkdir -p /usr/local/src/artemis

WORKDIR /usr/local/src/artemis

COPY requirements.txt ./

RUN apk add build-base python-dev mysql-dev libffi-dev \
        bash \
        bash-doc \
        bash-completion

RUN sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h -i.bkp
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt

RUN rm -rf /var/cache/apk/*

COPY . .

CMD [ "python","manage.py","runserver","0.0.0.0:8000" ]