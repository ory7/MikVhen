from django.db import models
from datetime import timedelta
from zoneinfo import ZoneInfo
from django.contrib import admin

class Appointment(models.Model):
    datetime = models.DateTimeField()
    contact = models.CharField(max_length=20)
    minutes_offset = models.IntegerField()
    textable = models.BooleanField()
    payment = models.CharField(max_length=8, null=True)
    notes = models.TextField(default="", blank=True)

    @admin.display(ordering='datetime')
    def display_datetime(self):
        return self.datetime.astimezone(ZoneInfo("America/New_York")).strftime("%a %Y-%m-%d %I:%M PM")

    @admin.display(ordering='contact') #at least allow grouping them together
    def display_contact(self):
        return self.contact[-4:]

class DayConfiguration(models.Model):
    date = models.DateField()
    opening = models.TimeField()
    first_come_first_served = models.BooleanField(default=False)
