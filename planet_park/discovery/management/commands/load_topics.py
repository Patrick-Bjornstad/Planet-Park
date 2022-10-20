from django.core.management.base import BaseCommand
from discovery.models import Topic

import requests

class Command(BaseCommand):
    help = 'Loads topic IDs and names to DB'

    def handle(self, *args, **options):
        print('Loading topics...')

        headers = {'X-Api-Key': 'Bamp04M3ruvAdHfpBfwzcVf6rCsNncGgmzS5Rjq3'}
        response = requests.get('https://developer.nps.gov/api/v1/topics?limit=100', headers=headers)

        topics = response.json()['data']
        for topic_elem in topics:
            topic = Topic()
            topic.topic_id = topic_elem['id']
            topic.name = topic_elem['name']
            topic.save()
