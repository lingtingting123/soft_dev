from django.urls import path, include 
from rest_framework.routers import DefaultRouter

from articles import views 
from .views import check_title
from .views import viewed_articles
from .views import clear_history

article_router = DefaultRouter(trailing_slash=False)
article_router.register('articles', views.ArticleView, basename='articles')
article_router.register('tags', views.TagView)

urlpatterns = [
    path('', include(article_router.urls)),
    path('api/articles/check-title', check_title, name='check_title'),
    path('api/articles/viewed', views.viewed_articles, name='viewed_articles'),
    path('clear-history', clear_history, name='clear_history'),
]
