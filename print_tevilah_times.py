#!/usr/bin/env python3

from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation
from datetime import datetime, date, time, timedelta
from types import SimpleNamespace

settings = SimpleNamespace(TIME_ZONE = 'America/New_York')

#copied from views.py

def get_zman(d):
    location = GeoLocation("New York, NY", 40.85139828693182, -73.93642913006643, settings.TIME_ZONE, elevation=0)
    calendar = ZmanimCalendar(geo_location=location, date=d)
    zman = calendar.sunset_offset_by_degrees(97.3) # seems to be three medium stars
    #TODO change html to not require prep type for first come first served days? speed?
    return zman.replace(second=0, microsecond=0)

day = timedelta(days=1)
if __name__ == "__main__":
    today = date.today()
    for days in range(365):
        day = today + timedelta(days=days)
        print(get_zman(day))
        #print(str(day)+","+str(get_zman(day)))
