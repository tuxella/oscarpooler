from journey.models import Journey, People, Vehicle
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.core import serializers
from journey.forms import JourneyForm, NewJourneyForm


from datetime import datetime

import sys
import json
import settings

def get_journey_from_token(token = ""):
    sys.stderr.write("Type 3: %s\n" % type(token))
    try:
        journey = Journey.objects.get(url_token = token[:Journey.URL_HASH_LEN])
    except:
        journey = None

    # If no admin token was given, we just return the journey
    if len(token) <= 16:
        return journey
    else:
        # Compare the admin_token given with the one stored in the database
        return {"journey":journey,
                "admin":token == journey.url_admin_token}

def journey_detail_from_url (request, journey_url):
    journey = Journey.objects.get(url = journey_url)
    if journey:
        journey_detail(request, journey.id)
    else:
        return render_to_response('journey/error.html',
                                  {'debug': "This journey doesn't exist"})


def render_error(request_dict):
    return render_to_response('journey/error.html', request_dict)

def journey_form_render(request, journey_url):
    c = {}
    c.update(csrf(request))
    sys.stderr.write("Type 2: %s\n" % type(journey_url))
    journey = get_journey_from_token(journey_url)
    if hasattr(journey, "id"):
        sys.stderr.write("\nNot admin\n")
    else:
        sys.stderr.write("\nAdmin\n")

    journey_id = journey.id
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
              'from': journey.from_addr,
              'are_seats':are_seats_available,
              'seats':available_seats,
              'peoples':peoples,
              'vehicles':vehicles})
    return render_to_response('journey/edit.html', c)

def journey_form(request, journey_url):
    c = {}
    c.update(csrf(request))
    sys.stderr.write("Type 1: %s\n" % type(journey_url))
    journey = get_journey_from_token(journey_url)
    if journey is None:
        return render_error({"debug":"This journey doesn't exist : %s" % journey_url})

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
            return journey_form_render(request, journey_url)
        else:
            return journey_form_render(request, journey_url)
    else:
        return journey_form_render(request, journey_url)

def current_site_url():
    url = getattr(settings, 'MY_DJANGO_URL_PATH', '')
    return url

def journey_view(request, journey_id):
    c = {}
    c.update(csrf(request))
    j = Journey.objects.filter(id = journey_id)
    if 0 < len(j):
        j = j[0]
    else:
        j = None
    c["journey"] = j
    c["base_url"] = current_site_url()
    return render_to_response('journey/view.html', c)

def journey_new(request):
    c = {}
    c.update(csrf(request))
    if "POST" == request.method:
        form = NewJourneyForm(request.POST)
        if form.is_valid():
            sys.stderr.write("Valid\n")
            journey_title = form.cleaned_data["title"]
            j = Journey(title = journey_title,
                        from_addr = form.cleaned_data["from_addr"],
                        to_addr = form.cleaned_data["to_addr"],
                        meeting_addr = form.cleaned_data["meeting_addr"],
                        date = form.cleaned_data["date"])
            j.save()
            return journey_view(request, j.id)
        else:
            sys.stderr.write("%s\n" % dir(form))
            if "title" in form.errors:
                c.update({"title":"error",
                          "title_old_value" : form.data["title"],
                          "from_addr_old_value" : form.data["from_addr"],
                          "to_addr_old_value" : form.data["to_addr"],
                          "meeting_addr_old_value" : form.data["meeting_addr"],
                          "date_old_value" : form.data["date"]})
                return render_to_response('journey/new.html', c)
    else:
        return render_to_response('journey/new.html', c)

def index(request):
    journeys = Journey.objects.all()[:100]
    sys.stderr.write("views.py")
    journeys_and_seats = []
    for j in journeys:
        journeys_and_seats.append((j,j.available_seats()))
    return render_to_response('journey/index.html', {'journeys_and_seats': journeys_and_seats})
