from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# 设置 Django 项目的设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建 Celery 应用
app = Celery('config')

# 从 Django 设置中加载 Celery 配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现并加载所有已安装应用中的任务
app.autodiscover_tasks()

# 定义定时任务调度
app.conf.beat_schedule = {
    'publish-scheduled-articles-every-minute': {
        'task': 'articles.tasks.publish_scheduled_articles',
        'schedule': crontab(minute='*/1'),  # 每分钟检查一次
    },
}