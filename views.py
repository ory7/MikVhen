from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation
from re import compile, findall
from .models import Appointment
from .models import DayConfiguration
from logging import exception
try:
    from twilio.rest import Client
except Exception:
    exception("Could not import twilio, will not be able to sms")

#configurable values

best_time = time(18, 0)
weekday_appointment_minutes = 10
friday_appointment_minutes = 5
earliest_open = time(17, 0)
earliest_close = time(21, 0)
#_open_minutes means how many minutes before the zman to open; negative means after the zman
#TODO make it more clear
friday_open_minutes = 5
weekday_open_minutes = -30
saturday_open_minutes = 65
saturday_latest_close = time(23, 59)
nonsaturday_latest_close = time(23, 0)
#_total_minutes means the minimum number of minutes to be open, as long as that doesn't pass _latest_close
nonfriday_total_minutes = 2*60+30
friday_total_minutes = 60
timeout_seconds = 5*60
prep_minutes = {"bath":30, "shower":10, "":5}
prep_minutes_at_close = {"bath":50, "shower":25, "":15}
#TODO table with key-value pairs in database, how to trigger reload?

Friday = "Friday"
Saturday = "Saturday"
day_spellings = ["Monday", "Tuesday", "Wednesday", "Thursday", Friday, Saturday, "Sunday"]

def get_zman(d):
    location = GeoLocation("New York, NY", 40.85139828693182, -73.93642913006643, settings.TIME_ZONE, elevation=0)
    calendar = ZmanimCalendar(geo_location=location, date=d)
    zman = calendar.sunset_offset_by_degrees(97.3) # seems to be three medium stars
    #TODO change html to not require prep type for first come first served days? speed?
    return zman.replace(second=0, microsecond=0)


def index(request):
    #TODO optional password
    #TODO display if already scheduled, secure cookie or only password?
    #TODO cancel button
    days = list(day_spellings)
    for x in range(today().weekday()):
        days.append(days.pop(0))
    return render(request, "pick_day.html", {
        "contact":request.COOKIES.get("contact", ""),
        "textconfirm":request.COOKIES.get("textconfirm", "yes"),
        "days":days,
        })

def times(request):
    day_param = request.GET.get("day", "")
    earlier_param = request.GET.get("earlier", "")
    prep_param = request.GET.get("prep", "") #TODO remember from cookie?
    contact_param = request.GET.get("contact", "")
    textconfirm_param = request.GET.get("textconfirm", "")
    later_param = request.GET.get("later", "")
    textable_param = request.GET.get("textable", False) #TODO separate table

    start = date_from_param(day_param)
    stop = start + timedelta(days=1)
    appointments = Appointment.objects.filter(datetime__gte=start, datetime__lte=stop)
    appointment_times = list(localize(a) for a in appointments)

    #TODO automatic holiday support

    zman = get_zman(start)
    day_configuration = DayConfiguration.objects.filter(date=start)
    if len(day_configuration) == 1:
        first_come_first_served = day_configuration[0].first_come_first_served
        open_time = combine(start, day_configuration[0].opening)
        close_time = combine(start, day_configuration[0].closing)
    else:
        first_come_first_served = day_param == Friday
        open_time = get_open_time(zman, day_param)
        close_time = get_close_time(zman, day_param, open_time)

    if first_come_first_served:
        appointment_minutes = friday_appointment_minutes
        prep_param = ""
    else:
        appointment_minutes = weekday_appointment_minutes

    best_time_today = combine(start, best_time)
    rounded_best_time = open_time
    while rounded_best_time < best_time_today:
        rounded_best_time += timedelta(minutes=appointment_minutes)
    if later_param:
        candidate = combine(start, time_from_param(later_param))
        earlier_available = True
    elif not earlier_param and open_time < rounded_best_time:
        candidate = rounded_best_time
        earlier_available = True
    else:
        earlier_available = False
        candidate = open_time

    debug={'earliest':open_time, 'latest':close_time, }
    times = []
    later_available = True
    for i in range(100): #just not infinite for safety
        if candidate+timedelta(minutes=prep_minutes_at_close[prep_param]) > close_time:
            later_available = False
            break
        if candidate+timedelta(minutes=prep_minutes[prep_param]) >= zman:
            if candidate not in appointment_times:
                times.append(candidate)
                if first_come_first_served:
                    break
                if len(times) == 3:
                    break
        candidate = candidate + timedelta(minutes=appointment_minutes)

    formatted_times = [nice_time(t) for t in times]

    response = render(request, "pick_time.html", {
        "timestamp":int(datetime.now().timestamp()),
        "times":formatted_times,
        "date":nice_date(start),
        "day":day_param,
        "contact":contact_param, #pass it through so that people can still use without cookies
        "prep":prep_param,
        "zman":nice_time(zman),
        "later_available":later_available,
        "earlier_available":earlier_available,
        "first_come_first_served":first_come_first_served,
        #"debug":debug
        })
    if contact_param:
        response.set_cookie("contact", contact_param, max_age=60*60*24*365)
        response.set_cookie("textconfirm", textconfirm_param, max_age=60*60*24*365)
    return response

def get_open_time(zman, day_param):
    if day_param == Friday:
        open_minutes = friday_open_minutes
    elif day_param == Saturday:
        open_minutes = saturday_open_minutes
    else:
        open_minutes = weekday_open_minutes
    open_time = zman + timedelta(minutes=open_minutes-zman.minute%5)
    open_time = max(open_time, combine(open_time, earliest_open))
    return open_time

def get_close_time(zman, day_param, open_time):
    if day_param == Friday:
        total_minutes = friday_total_minutes
        latest_close = nonsaturday_latest_close
    elif day_param == Saturday:
        total_minutes = nonfriday_total_minutes
        latest_close = saturday_latest_close
    else:
        total_minutes = nonfriday_total_minutes
        latest_close = nonsaturday_latest_close
    close_time = open_time + timedelta(minutes=total_minutes)
    close_time = max(close_time, combine(open_time, earliest_close))
    close_time = min(close_time, combine(open_time, latest_close))
    return close_time

def payment(request):
    day_param = request.GET.get("day")
    time_param = request.GET.get("time")
    contact_param = request.GET.get("contact", "unknown")
    prep_param = request.GET.get("prep", "")
    timestamp_param = request.GET.get("timestamp")

    #debug = {'woo':prep_param}

    return render(request, "pick_pay.html", {
        "day":day_param,
        "time":time_param,
        "contact":contact_param,
        "prep":prep_param,
        "timestamp":timestamp_param,
        #"debug":debug
        })

@csrf_exempt #b/c not worried about bogus appointments
def save(request):
    day_param = request.POST.get("day")
    time_param = request.POST.get("time")
    contact_param = ''.join(findall(r'\w', request.POST.get("contact", "unknown")))
    prep_param = request.POST.get("prep", "")
    payment_param = request.POST.get("payment")
    notes_param = request.POST.get("notes")
    timestamp_param = request.POST.get("timestamp")

    if datetime.now() - datetime.fromtimestamp(int(timestamp_param)) > timedelta(seconds=timeout_seconds):
        d = { 'f':datetime.fromtimestamp(int(timestamp_param)), 'n':datetime.now() }
        return render(request, "timeout.html", {
           # 'debug': d
            })

    entry = combine(date_from_param(day_param), time_from_param(time_param))

    #replace any other upcoming appointments
    Appointment.objects.filter(contact=contact_param, datetime__gte=today()).delete()

    appointment = Appointment(datetime=entry,
            contact=contact_param,
            payment=payment_param,
            notes=notes_param,
            minutes_offset = prep_minutes[prep_param],
            )
    appointment.save()
    alert = False
    now = datetime.now(tz=ZoneInfo(settings.TIME_ZONE))
    if request.COOKIES.get("textconfirm"):
        send_sms_confirm(entry.date(), time_param, contact_param)
    send_sms_log(entry.date(), time_param, contact_param, entry.date() == now.date() and now.hour > 12)
    return render(request, "scheduled.html", {
        "date":entry.date(),
        "day":day_param,
        "time":time_param,
        "payment":payment_param,
        #"debug":d,
        })

def send_sms_confirm(date: str, time: str, contact: str):
    if not hasattr(settings, 'TWILIO_SID'):
        return
    client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        client.messages.create(
            body=f"Confirmed! Your appointment is {time} PM {date}",
            from_=settings.TWILIO_SMS_SENDER,
            to=contact,
        )
    except Exception:
        exception("Could not sms a confirmation")

def send_sms_log(date: str, time: str, contact: str, alert: bool):
    try:
        client.messages.create(
            body=(alert and "ALERT! " or "")+f"{contact} scheduled for {date} {time} PM",
            from_=settings.TWILIO_SMS_SENDER,
            to=settings.TWILIO_SMS_LOG_RECIPIENT,
        )
    except Exception as e:
        exception("Could not sms a log entry")

def attendant(request):
    date_param = request.GET.get("date")
    next_date = str(today())
    if date_param == 'all':
        appointments = Appointment.objects.filter(datetime__gte=today()).order_by("datetime")
    else:
        one_date = date.fromisoformat(date_param) if date_param else today()
        next_date = one_date+timedelta(days=1)
        appointments = Appointment.objects.filter(datetime__gte=noon(one_date), datetime__lt=noon(next_date)).order_by("datetime")
    formatted_appointments = [{
        "day":nice_date(localize(a)),
        "arrival_time":nice_time(localize(a)),
        "tvila_time":nice_time(localize(a)+timedelta(minutes=a.minutes_offset)),
        "contact":a.contact,
        "payment":a.payment,
        "notes":a.notes,
        } for a in appointments]
    return render(request, "attendant.html", {"appointments":formatted_appointments,"next_date":str(next_date),})

#TODO export appointments to csv

def noon(d):
    return combine(d, time(12, 0))

def nice_date(d):
    return d.strftime("%A, %Y-%m-%d")

def nice_time(t):
    return t.time().strftime("%I:%M")

day_dict = dict(zip(day_spellings, range(7)))

def date_from_param(day_param):
    day = day_dict.get(day_param)
    #TODO error handling?
    days = day - today().weekday()
    if days < 0:
        days += 7
    return today() + timedelta(days)

time_re = compile(r"(\d+):(\d+)")

def time_from_param(time_param):
    (hour, minute) = time_re.match(time_param).groups()
    return time(12+int(hour), int(minute))

#TODO simplify localization now that we're using settings.TIME_ZONE?
def localize(dt):
    return dt.datetime.astimezone(ZoneInfo(settings.TIME_ZONE))

def combine(d, t):
    return datetime.combine(d, t, tzinfo=ZoneInfo(settings.TIME_ZONE))

def today():
    return datetime.now(tz=ZoneInfo(settings.TIME_ZONE)).date()
