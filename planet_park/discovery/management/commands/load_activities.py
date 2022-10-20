from django.core.management.base import BaseCommand
from discovery.models import Activity

import requests

class Command(BaseCommand):
    help = 'Loads activity IDs and names to DB'

    def handle(self, *args, **options):
        print('Loading activities...')

        headers = {'X-Api-Key': 'Bamp04M3ruvAdHfpBfwzcVf6rCsNncGgmzS5Rjq3'}
        response = requests.get('https://developer.nps.gov/api/v1/activities?limit=100', headers=headers)

        activities = response.json()['data']
        for activity_elem in activities:
            activity = Activity()
            activity.activity_id = activity_elem['id']
            activity.name = activity_elem['name']
            activity.save()
