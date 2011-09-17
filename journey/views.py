from journey.models import Journey, People, Vehicle
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.core import serializers
from journey.forms import JourneyForm, NewJourneyForm


from datetime import datetime

import sys
import json


def journey_detail_from_url (request, journey_url):
    journey = Journey.objects.get(url = journey_url)
    if journey:
        journey_detail(request, journey.id)
    else:
        return render_to_response('journey/error.html',
                                  {'debug': "This journey doesn't exist"})


def journey_detail(request, journey_id):
    journey = Journey.objects.get(pk=journey_id)
    av = journey.available_seats()
    sys.stderr.write("views.py")
    peoples_json = "{}"
    peoples = People.objects.filter(journey = journey_id)
    if 0 < len(peoples):
        js = json_object(peoples[0])
        sys.stderr.write("#" * 50)
        sys.stderr.write("obj : %s" % js)
        peoples_json = "[" + ",".join(map(json_object, peoples)) + "]"

    vehicles_json = "{}"
    vehicles = Vehicle.objects.filter(journey = journey_id)
    if 0 < len(vehicles):
        js = json_object(vehicles[0])
        sys.stderr.write("#" * 50)
        sys.stderr.write("obj : %s" % js)
        vehicles_json = "[" + ",".join(map(json_object, vehicles)) + "]"

    return render_to_response('journey/detail.html',
                              {'journey': journey,
                               'seats':av,
                               'peoples':peoples_json,
                               'vehicles':vehicles_json})


def journey_edit(request, journey_id):
    journey = Journey.objects.get(pk=journey_id)
    vehicles = Vehicle.objects.filter(journey = journey_id)
    peoples = People.objects.filter(journey = journey_id)
    av = journey.available_seats()
    return render_to_response('journey/edit.html',
                              {'journey': journey,
                               'seats':av,
                               'peoples':peoples,
                               'vehicles':vehicles})


def journey_form_render(request, journey_id):
    c = {}
    c.update(csrf(request))
    journey = Journey.objects.filter(pk=journey_id)
    if journey and 1 <= len(journey):
        journey = journey[0]
    else:
        return render_to_response('journey/edit.html', c)
    peoples_q = People.objects.filter(journey = journey_id)
    vehicles = Vehicle.objects.filter(journey = journey_id)
    peoples = []
    for p_q in peoples_q:
        p = {}
        p["name"] = p_q.name
        p["count"] = p_q.count
        v = vehicles.filter(people = p_q)
        if 1 == len(v):
            p["vehicle_name"] = v[0].name
            p["vehicle_seats"] = v[0].seats
        peoples.append(p)

    available_seats = journey.available_seats()
    if 0 == available_seats:
        are_seats_available = 0
    if 0 > available_seats:
        are_seats_available = -1
        available_seats = available_seats * -1
    else:
        if 0 < available_seats:
            are_seats_available = 1

    c.update({'journey': journey,
              'are_seats':are_seats_available,
              'seats':available_seats,
              'peoples':peoples,
              'vehicles':vehicles})

    return render_to_response('journey/edit.html', c)


def journey_form(request, journey_id):
    c = {}
    c.update(csrf(request))
    journey = Journey.objects.filter(pk=journey_id)
    if journey and 1 <= len(journey):
        journey = journey[0]
    else:
        return journey_form_render(request, journey_id)
    if "POST" == request.method:
        form = JourneyForm(request.POST, journey = journey)
        if form.is_valid():
            sys.stderr.write("Valid\n")
            people_name = form.cleaned_data['people_name']
            people_count = form.cleaned_data['people_count']
            p = People(name = people_name, count = people_count, journey = journey)
            p.save()
            vehicle_name = form.cleaned_data['vehicle_name']
            vehicle_seats = form.cleaned_data['vehicle_seats']
            if vehicle_name or vehicle_seats:
                v = Vehicle(name = vehicle_name, seats = vehicle_seats,
                            people = p, journey = journey)
                v.save()
            return journey_form_render(request, journey_id)
        else:
            return journey_form_render(request, journey_id)
    else:
        return journey_form_render(request, journey_id)

def journey_view(request, journey_id):
    c = {}
    c.update(csrf(request))
    j = Journey.objects.filter(id = journey_id)
    if 0 < len(j):
        j = j[0]
    else:
        j = None
    c["journey"] = j
    return render_to_response('journey/view.html', c)

def journey_new(request):
    c = {}
    c.update(csrf(request))
    if "POST" == request.method:
        form = NewJourneyForm(request.POST)
        if form.is_valid():
            sys.stderr.write("Valid\n")
            journey_title = form.cleaned_data["title"]
            j = Journey(title = journey_title)
            j.save()
            return journey_view(request, j.id)
        else:
            sys.stderr.write("INVALID\n")


    return render_to_response('journey/new.html', c)

def index(request):
    journeys = Journey.objects.all()[:5]
    sys.stderr.write("views.py")
    journeys_and_seats = []
    for j in journeys:
        journeys_and_seats.append((j,j.available_seats()))
    return render_to_response('journey/index.html', {'journeys_and_seats': journeys_and_seats})

def json_object(obj = None):
    if obj is None:
        return ("{}")
    json_obj = {}
    attrs = obj._meta.fields
    for attr in obj._meta.fields:
        attr_value = obj.__getattribute__(attr.name)
        str_value = ""
#        sys.stderr.write("[%s] = %s (%s)\n" % (attr.name, attr_value, type(attr_value)))
        if "id" in dir(attr_value):
            str_value = attr_value.id
        elif datetime == type(attr_value):
            sys.stderr.write("[%s] = %s (%s)\n" % (attr.name, attr_value, dir(attr_value)))
            str_value = "%.2d:%.2d %.4d/%.2d/%.2d" % (attr_value.hour,
                                                      attr_value.minute,
                                                      attr_value.year,
                                                      attr_value.month,
                                                      attr_value.day)
        else:
            str_value = unicode(attr_value)
        json_obj[attr.name] = str_value

    return json.dumps(json_obj)

def people_new(request):
    try:
        if "POST" != request.method:
            return render_to_response('journey/error.html',
                                      {'debug': "Only POST method is allowed on this URL"})
        request_items = request.POST.items()
        if (1 != len(request_items)):
            return render_to_response('journey/error.html',
                                      {'message': "Incorrect number of params (1 expected)",
                                       'debug': "[%s]" % request.POST})
        sys.stderr.write("Data raw: %s\n" % request_items)
        sys.stderr.write("Data len: %s\n" % len(request_items))
        json_str = str(request_items[0][0])
        json_data = json.loads(json_str)
        name = json_data["name"]
        if "count" in json_data:
            count = json_data["count"]
        else:
            count = 1
        p = People(name = name, count = count)
        p.save()
        return HttpResponse(json_object(p))

    except Exception as e:
        sys.stderr.write("ERROR:\n")
        sys.stderr.write("%s" % type(e))
        sys.stderr.write("%s" % e.message)
        return render_to_response('journey/error.html',
                                  {'debug': "[%s]" % request.POST})

def vehicle_new(request):
    try:
        if "POST" != request.method:
            return render_to_response('journey/error.html',
                                      {'debug': "Only POST method is allowed on this URL"})
        request_items = request.POST.items()
        if (1 != len(request_items)):
            return render_to_response('journey/error.html',
                                      {'message': "Incorrect number of params (1 expected)",
                                       'debug': "[%s]" % request.POST})
        sys.stderr.write("Data raw: %s\n" % request_items)
        sys.stderr.write("Data len: %s\n" % len(request_items))
        json_str = str(request_items[0][0])
        json_data = json.loads(json_str)
        name = json_data["name"]
        p = People(name = name, count = count)
        p.save()
        return HttpResponse(json_object(p))

    except Exception as e:
        sys.stderr.write("ERROR:\n")
        sys.stderr.write("%s" % type(e))
        sys.stderr.write("%s" % e.message)
        return render_to_response('journey/error.html',
                                  {'debug': "[%s]" % request.POST})

def journey_json(request, journey_id):
    journey = Journey.objects.get(pk=journey_id)
    return HttpResponse(json_object(journey))

def people_json(request, people_id):
    people = People.objects.get(pk=people_id)
    return HttpResponse(json_object(people))

def vehicle_json(request, vehicle_id):
    vehicle = Vehicle.objects.get(pk=vehicle_id)
    return HttpResponse(json_object(vehicle))

def ootest(request):
    sys.stderr.write("In test\n")
    c = {}
    c.update(csrf(request))
    sys.stderr.write("%s\n" % c)
    return render_to_response('journey/debug.html',
                              c) #{'debug': "Only POST method is allowed on this URL"})
