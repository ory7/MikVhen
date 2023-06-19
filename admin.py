from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib import admin
from django.urls import path
from .models import Appointment
from .models import DayConfiguration
from . import views

from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("Datetime", "Created_at", "private_contact")

class MikvahAdmin(admin.AdminSite):
    site_title = "Mikvah Admin"
    site_header = "Mikvah Admin"
    site_url = "/mikvah/admin/attendant/"

    def get_urls(self):
        urls = super(MikvahAdmin, self).get_urls()
        my_urls = [path("attendant/", self.admin_view(views.attendant), name="attendant"),]
        #logger.info(my_urls + urls)
        return my_urls + urls

admin_site = MikvahAdmin(name='mikvah_admin')
admin_site.register(Appointment, AppointmentAdmin)
admin_site.register(DayConfiguration)
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
