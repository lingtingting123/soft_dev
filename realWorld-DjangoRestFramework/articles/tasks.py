from celery import shared_task
from django.utils import timezone
from .models import Article


@shared_task
def publish_scheduled_articles():
    now = timezone.now()
    # 查询所有 scheduledAt 小于等于当前时间且 scheduledAt 不为空的文章
    articles_to_publish = Article.objects.filter(scheduledAt__lte=now, scheduledAt__isnull=False)
    for article in articles_to_publish:
        article.scheduledAt = None  # 清空 scheduledAt 字段
        article.save()
        # 可以在这里添加其他发布逻辑，例如发送通知等