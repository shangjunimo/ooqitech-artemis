# -*- coding: utf-8 -*-
import logging
import os
import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import task

from artemis.settings import EMAIL_FROM_USER, EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_PORT

logger = logging.getLogger('deploy.app')


@task
def SendEmail(receive_users, subject, content=None, files=None):
    try:
        msg = MIMEMultipart('related')
        content = MIMEText(content, 'html', _charset='utf-8')
        msg.attach(content)
        if files:
            for i, attachment_file in enumerate(files):
                print(attachment_file)
                part = MIMEApplication(open(attachment_file, 'rb').read())
                part.add_header('Content-Disposition', 'attachment',
                                filename=os.path.splitext(os.path.split(attachment_file)[-1])[0])
                msg.attach(part)
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = EMAIL_FROM_USER
        msg['To'] = receive_users
        server = smtplib.SMTP()
        server.connect(EMAIL_HOST, EMAIL_PORT)
        try:
            server.login(EMAIL_FROM_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_FROM_USER, receive_users, msg.as_string())
            logger.info("sendmail " + EMAIL_FROM_USER + ' ' + receive_users + ' success')
        except Exception as e:
            logger.info(e.message)
            logger.info("sendmail authentication failed")
        finally:
            server.quit()
        return

    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
    return
