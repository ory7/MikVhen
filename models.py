from django.conf import settings
from django.contrib import admin
from django.db import models
from datetime import timedelta
from zoneinfo import ZoneInfo

class Appointment(models.Model):
    datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True) #TODO why isn't this visible in the single view admin?
    contact = models.CharField(max_length=20)
    minutes_offset = models.IntegerField()
    textable = models.BooleanField(default=False)
    payment = models.CharField(max_length=8, null=True)
    notes = models.TextField(default="", blank=True)

    @admin.display(ordering='datetime')
    def Datetime(self):
        return self.datetime.astimezone(ZoneInfo(settings.TIME_ZONE)).strftime('%a %d %b %Y, %I:%M%p')

    @admin.display(ordering='created_at')
    def Created_at(self):
        return self.created_at.astimezone(ZoneInfo(settings.TIME_ZONE)).strftime('%d %b %Y, %I:%M%p')

    @admin.display(ordering='contact') #at least allow grouping them together
    def private_contact(self):
        return self.contact[-4:]

class DayConfiguration(models.Model):
    date = models.DateField()
    opening = models.TimeField()
    first_come_first_served = models.BooleanField(default=False)
