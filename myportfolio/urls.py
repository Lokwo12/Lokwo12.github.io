"""
URL configuration for myportfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from portfolio.sitemaps import StaticViewSitemap, PostSitemap, ProjectSitemap, BlogCategorySitemap, BlogTagSitemap

urlpatterns = [
    # Admin password reset (forgot password)
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(template_name='admin/password_reset_form.html'), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='admin/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='admin/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='admin/password_reset_complete.html'), name='password_reset_complete'),

    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
    path('blog/', include('blog.urls')),
    path('sitemap.xml', cache_page(60 * 60 * 24)(sitemap), {'sitemaps': {
        'static': StaticViewSitemap,
        'blog': PostSitemap,
        'projects': ProjectSitemap,
        'blog-categories': BlogCategorySitemap,
        'blog-tags': BlogTagSitemap,
    }}, name='sitemap'),
    path('robots.txt', cache_page(60 * 60 * 24)(TemplateView.as_view(template_name='robots.txt', content_type='text/plain'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
