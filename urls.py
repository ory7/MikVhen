from django.urls import path
from django.shortcuts import redirect

from . import views
from .admin import admin_site

urlpatterns = [
    path('', views.index, name='index'),
    path('times', views.times, name='times'),
    path('payment', views.payment, name='payment'),
    path('save', views.save, name='save'),
    path('waterpressure', lambda req: redirect('admin/attendant/')),
    path('pay', lambda req: redirect('https://www.kajinc.org/form/mikveh-donation.html')),
    path('admin/', admin_site.urls, name='mikvah_admin'),
]
