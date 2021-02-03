from django.shortcuts import render
import datetime
import pytz


# Create your views here.
def homepage(request):
    ctxt = {"timezone": pytz.all_timezones}
    if request.method == 'POST':
        time = request.POST.get("time")
        tz1 = request.POST.get("tz1")
        tz2 = request.POST.get("tz2")
        time2 = convert_datetime_timezone(time, tz1, tz2)
        ctxt["time"] = time2
        return render(request, "main.html", ctxt)
    return render(request, "main.html", ctxt)


def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)
    dt = datetime.datetime.strptime(dt, "%H:%M")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%H:%M")
    return dt
