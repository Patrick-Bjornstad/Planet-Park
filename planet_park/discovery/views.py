from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
import requests
import json

from discovery.models import Park
from reviews.models import Review

headers = {'X-Api-Key': 'Bamp04M3ruvAdHfpBfwzcVf6rCsNncGgmzS5Rjq3'}
weather_api = 'f9112f0d1ffb4405c4f90445d59c91a6'

# Create your views here.
@login_required(login_url='/')
def discover(request):
    return render(request, 'discovery/discover.html')

@login_required(login_url='/')
def info_page(request, park_code):
    park_obj = Park.objects.filter(code=park_code)[0]

    # Extract park model info
    topics = park_obj.topics.all()
    activities = park_obj.activities.all()

    # Extract review model info
    reviews = Review.objects.filter(park=park_obj)
    if reviews:
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    else:
        avg_rating = 'N/A'

    # Live queried info
    alerts = requests.get(f'https://developer.nps.gov/api/v1/alerts?parkCode={park_code}&limit=5', headers=headers).json()['data']
    for alert in alerts:
        alert['lastIndexedDate'] = alert['lastIndexedDate'][0:10]
    lat = park_obj.latitude
    lon = park_obj.longitude
    weather = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=hourly,minutely,alerts&units=imperial&appid={weather_api}').json()
    things_to_do = requests.get(f'https://developer.nps.gov/api/v1/thingstodo?parkCode={park_code}&limit=10', headers=headers).json()['data']

    context = {
        'park': park_obj,
        'topics': topics,
        'activities': activities,
        'avg_rating': avg_rating,
        'alerts': alerts,
        'weather': weather,
        'things_to_do': things_to_do
    }
    return render(request, 'discovery/info.html', context)
