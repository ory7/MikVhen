from django.urls import path
from django.shortcuts import redirect

from . import views
from .admin import admin_site

urlpatterns = [
    path('', views.index, name='index'),
    path('times', views.times, name='times'),
    path('payment', views.payment, name='payment'),
    path('save', views.save, name='save'),

    path('staging/', views.index, name='index', kwargs={'prefix':'staging/'}),
    path('staging/times', views.times, name='times', kwargs={'prefix':'staging/'}),
    path('staging/payment', views.payment, name='payment', kwargs={'prefix':'staging/'}),
    path('staging/save', views.save, name='save', kwargs={'prefix':'staging/'}),

    path('waterpressure', lambda req: redirect('admin/attendant/')),
    path('funds', lambda req: redirect('https://www.zeffy.com/en-US/peer-to-peer/a7b20dfc-38c4-4b60-9e6f-0ded8c350426')),
    path('5786', lambda req: redirect('https://www.zeffy.com/en-US/donation-form/mikvah-of-washington-heights--5786')),
    path('dishes', lambda req: redirect('https://www.zeffy.com/en-US/donation-form/keilim-mikvah-maintenance-and-repair')),
    path('tevila', lambda req: redirect('https://square.link/u/42NOAqm4')),
    path('donation', lambda req: redirect('https://square.link/u/42NOAqm4')),
    path('rh', lambda req: redirect('https://checkout.square.site/merchant/MLHGSEB8R2M5J/checkout/QMTLZN64RYKP5C5MYC6CZMBR')),
    path('men', lambda req: redirect('https://checkout.square.site/merchant/MLHGSEB8R2M5J/checkout/M2RWVNHV22QNYEXW4ZAHMP7J')),
    path('students', lambda req: redirect('https://checkout.square.site/merchant/MLHGSEB8R2M5J/checkout/MERIKWNSYOSMUCFGBIJVHTSW')),
    path('pay', lambda req: redirect('https://www.kajinc.org/form/mikveh-donation.html')),
    path('admin/', admin_site.urls, name='mikvah_admin'),
]
