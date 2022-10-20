from django.core.management.base import BaseCommand
from discovery.models import Park, Topic, Activity, State

import requests

class Command(BaseCommand):
    help = 'Loads all park information to DB'

    def handle(self, *args, **options):
        print('Loading parks...')

        headers = {'X-Api-Key': 'Bamp04M3ruvAdHfpBfwzcVf6rCsNncGgmzS5Rjq3'}
        response = requests.get('https://developer.nps.gov/api/v1/parks?limit=1000', headers=headers)

        parks_all = response.json()['data']
        parks = []
        for park_elem in parks_all:
            if park_elem['designation'] == 'National Park':
                parks.append(park_elem)
        
        for park_elem in parks:
            park = Park()

            # Basic fields
            park.park_id = park_elem['id']
            park.name = park_elem['fullName']
            park.code = park_elem['parkCode']
            park.latitude = float(park_elem['latitude'])
            park.longitude = float(park_elem['longitude'])
            park.url = park_elem['url']
            park.description = park_elem['description']

            # Extract address
            addresses = park_elem['addresses']
            for address in addresses:
                if address['type'] == 'Physical':
                    park.address = f'{address["line1"]}, {address["city"]} {address["stateCode"]} {address["postalCode"]}'
                    break
            
            # Extract contact info - phone
            phone_numbers = park_elem['contacts']['phoneNumbers']
            for phone in phone_numbers:
                if phone['type'] == 'Voice':
                    park.phone = phone['phoneNumber']
                    break
            
            # Extract contact info - email
            email = park_elem['contacts']['emailAddresses'][0]['emailAddress']
            park.email = email

            # Extract min and max entrance fees
            entrance_fee_elems = park_elem['entranceFees']
            entrance_fees = []
            for entrance_fee_elem in entrance_fee_elems:
                entrance_fees.append(float(entrance_fee_elem['cost']))
                park.min_price = min(entrance_fees)
                park.max_price = max(entrance_fees)

            # Save instance before many to many field handling
            park.save()
            
            # Handle many to many field - states
            states = park_elem['states'].split(',')
            for state_abb in states:
                state_obj = State.objects.get(pk=state_abb)
                park.states.add(state_obj)
            
            # Handle many to many field - topics
            topic_elems = park_elem['topics']
            topic_keys = []
            topic_names = []
            for topic_elem in topic_elems:
                topic_keys.append(topic_elem['id'])
                topic_names.append(topic_elem['name'])
            for (topic_key, topic_name) in zip(topic_keys, topic_names):
                try:
                    topic_obj = Topic.objects.get(pk=topic_key)
                except:
                    new_topic = Topic()
                    new_topic.topic_id = topic_key
                    new_topic.name = topic_name
                    new_topic.save()
                    topic_obj = new_topic
                park.topics.add(topic_obj)
            
            # Handle many to many field - activities
            activity_elems = park_elem['activities']
            activity_keys = []
            activity_names = []
            for activity_elem in activity_elems:
                activity_keys.append(activity_elem['id'])
                activity_names.append(activity_elem['name'])
            for (activity_key, activity_name) in zip(activity_keys, activity_names):
                try:
                    activity_obj = Activity.objects.get(pk=activity_key)
                except:
                    new_activity = Activity()
                    new_activity.activity_id = activity_key
                    new_activity.name = activity_name
                    new_activity.save()
                    activity_obj = new_activity
                park.activities.add(activity_obj)
