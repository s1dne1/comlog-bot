import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comlog_web.settings')

app = Celery('comlog_web')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()