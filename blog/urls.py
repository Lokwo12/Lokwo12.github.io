from django.urls import path
from . import views
from .feeds import LatestPostsFeed
from django.views.decorators.cache import cache_page

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('category/<slug:category>/', views.post_list_by_category, name='post_list_by_category'),
    path('tag/<slug:tag>/', views.post_list_by_tag, name='post_list_by_tag'),
    path('rss.xml', cache_page(60 * 60 * 24)(LatestPostsFeed()), name='post_feed'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
