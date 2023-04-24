from django.urls import path

from . import views
from .admin import admin_site

urlpatterns = [
    path('', views.index, name='index'),
    path('times', views.times, name='times'),
    path('payment', views.payment, name='payment'),
    path('save', views.save, name='save'),
    path('admin/', admin_site.urls, name='mikvah_admin'),
]
