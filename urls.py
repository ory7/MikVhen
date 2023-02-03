from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('times', views.times, name='times'),
    path('payment', views.payment, name='payment'),
    path('save', views.save, name='save'),
    path('attendant', views.attendant, name='attendant'),
]
