from django.contrib import admin

from .models import Appointment
from .models import DayConfiguration

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("display_datetime", "display_contact")

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(DayConfiguration)
