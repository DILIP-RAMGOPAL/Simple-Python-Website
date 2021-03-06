from django.shortcuts import render
from datetime import date
from geolite2 import geolite2
from json import dumps
import datetime
import pytz
import os
import geocoder
import reverse_geocoder as rg
from timezonefinder import TimezoneFinder


def homepage(request):
    now = datetime.datetime.now()
    x = geolite2.reader().get(request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR'))
    latlag = []
    try:
        my_tz_name = x['location']['time_zone']
        result_state = x['country']['names']['en']
        latlag.append(x['location']['latitude'])
        latlag.append(x['location']['longitude'])
        result = rg.search(latlag)
    except (TypeError, KeyError):
        g = geocoder.ip('me')
        tf = TimezoneFinder()
        result = rg.search(g.latlng)
        my_tz_name = tf.timezone_at(lng=float(result[0]['lon']), lat=float(result[0]['lat']))
        result_state = result[0]["name"]
    result_district = result[0]["admin1"]
    result_place = result[0]["admin2"]
    timezone = pytz.timezone(my_tz_name)
    today = date.today()
    date_day = today.strftime("%A")
    date_date = today.strftime("%d %B %Y %Z")
    now = now.astimezone(timezone)
    dataJSON = dumps(my_tz_name)
    ctxt = {"timezone": timezone, "data": dataJSON, "date": date_day, "date_date": date_date, "g": result_place, "result_district": result_district, "result_state": result_state}
    return render(request, "index.html", ctxt)


def convert_timezone(request):
    ctxt = {"timezone": pytz.all_timezones}
    if request.method == 'POST':
        time = request.POST.get("time")
        date = request.POST.get("date")
        if time:
            tz1 = request.POST.get("tz1")
            tz2 = request.POST.get("tz2")
            time = time + " " + date
            time = convert_datetime_timezone(time, tz1, tz2)
            ctxt["time"] = time
    return render(request, "timezone.html", ctxt)


def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)
    dt = datetime.datetime.strptime(dt, "%H:%M %Y-%m-%d")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%H:%M %d-%m-%Y")
    return dt


def cidr(request):
    ctxt = {}
    if request.method == 'POST':
        cidr = request.POST.get("cidr")
        if "/" not in cidr:
            return render(request, "cidr.html")
        (addrString, cidrString) = cidr.split('/')
        addr = addrString.split('.')
        if (len(addr) != 4) and (int(cidrString) < 33):
            return render(request, "cidr.html")
        if not (int(cidrString) < 33):
            return render(request, "cidr.html")
        for i in addr:
            if not (int(i) < 256):
                return render(request, "cidr.html")
        cidr = int(cidrString)
        mask = [0, 0, 0, 0]
        for i in range(cidr):
            mask[int(i/8)] = mask[int(i/8)] + (1 << (7 - i % 8))
        net = []
        for i in range(4):
            net.append(int(addr[i]) & mask[i])
        broad = list(net)
        brange = 32 - cidr
        for i in range(brange):
            broad[3 - int(i/8)] = broad[3 - int(i/8)] + (1 << (i % 8))
        hosts = {"first": list(net), "last": list(broad)}
        hosts["count"] = 1
        wildcard = []
        for i in range(4):
            wildcard.append(255 - mask[i])
        final_mask = ""
        final_wildcard = ""
        final_firstip = ""
        final_lastip = ""
        for i in str(mask):
            if i == ",":
                final_mask += "."
                continue
            final_mask += i
        for i in str(wildcard):
            if i == ",":
                final_wildcard += "."
                continue
            final_wildcard += i
        for i in str(hosts["first"]):
            if i == ",":
                final_firstip += "."
                continue
            final_firstip += i
        for i in str(hosts["last"]):
            if i == ",":
                final_lastip += "."
                continue
            final_lastip += i
        for i in range(4):
            hosts["count"] += (hosts["last"][i] - hosts["first"][i]) * 2**(8*(3-i))
        ctxt = {"address": addrString, "netmask": final_mask, "wildcard": final_wildcard, "host1": final_firstip, "host2": final_lastip, "count": hosts["count"]}
    return render(request, "cidr.html", ctxt)


def epoch(request):
    if request.method == 'POST':
        epoch = request.POST.get("epoch")
        try:
            x = geolite2.reader().get(request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR'))
            time = datetime.datetime.fromtimestamp(float(epoch))
            if x is None:
                g = geocoder.ip('me')
                tf = TimezoneFinder()
                result = rg.search(g.latlng)
                my_tz_name = tf.timezone_at(lng=float(result[0]['lon']), lat=float(result[0]['lat']))
                my_tz = pytz.timezone(my_tz_name)
            else:
                my_tz_name = x['location']['time_zone']
                my_tz = pytz.timezone(my_tz_name)
            time = time.astimezone(my_tz)
        except (ValueError, KeyError):
            return render(request, "epoch.html", {"msg": "value error"})
        time_utc = time.astimezone(pytz.utc).strftime("%H:%M:%S : %d-%m-%Y")
        ctxt = {"time": time.strftime("%H:%M:%S : %d-%m-%Y"), "time_utc": time_utc, "timezone": my_tz}
        return render(request, "epoch.html", ctxt)
    return render(request, "epoch.html")


def disclaimer(request):
    return render(request, "disclaimer.html")
