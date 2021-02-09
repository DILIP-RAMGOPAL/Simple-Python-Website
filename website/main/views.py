from django.shortcuts import render
from datetime import date
from django.utils import timezone
import datetime
import pytz
import os
import geocoder
import reverse_geocoder as rg


def homepage(request):
    now = datetime.datetime.now()
    my_tz_name = '/'.join(os.path.realpath('/etc/localtime').split('/')[-2:])
    my_tz = pytz.timezone(my_tz_name)
    now = now.astimezone(my_tz)
    current_time = now.strftime("%I:%M")
    current_seconds = now.strftime(":%S %P")
    timezone = my_tz
    today = date.today()
    date_day = today.strftime("%A")
    date_date = today.strftime("%d %B %Y %Z")
    g = geocoder.ip('me')
    result = rg.search(g.latlng)
    result_place = result[0]["name"]
    result_district = result[0]["admin1"]
    result_state = result[0]["admin2"]
#    timezone.activate(pytz.timezone(my_tz))
    ctxt = {"time": current_time, "current_seconds": current_seconds, "timezone": timezone, "date": date_day, "date_date": date_date, "g": result_place, "result_district": result_district, "result_state": result_state}
    return render(request, "index.html", ctxt)


def timezone(request):
    ctxt = {"timezone": pytz.all_timezones}
    if request.method == 'POST':
        time = request.POST.get("time")
        if time:
            tz1 = request.POST.get("tz1")
            tz2 = request.POST.get("tz2")
            time2 = convert_datetime_timezone(time, tz1, tz2)
            ctxt["time"] = time2
    return render(request, "timezone.html", ctxt)


def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)
    dt = datetime.datetime.strptime(dt, "%H:%M")
    dt = dt.replace(year=2021)
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%H:%M")
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
        for i in range(4):
            hosts["count"] += (hosts["last"][i] - hosts["first"][i]) * 2**(8*(3-i))
        ctxt = {"address": addrString, "netmask": mask, "wildcard": wildcard, "host1": hosts["first"], "host2": hosts["last"], "count": hosts["count"]}
    return render(request, "cidr.html", ctxt)


def disclaimer(request):
    return render(request, "disclaimer.html")
