from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('about/', views.about, name='about'),
    path('about.pdf', views.about_pdf, name='about_pdf'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/confirm/<uuid:token>/', views.subscribe_confirm, name='subscribe_confirm'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe, name='unsubscribe'),
    path('recommend/', views.recommend, name='recommend'),
    path('sitemap/', views.html_sitemap, name='html_sitemap'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('gallery/', views.gallery, name='gallery'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('portfolio.pdf', views.portfolio_pdf, name='portfolio_pdf'),
]
