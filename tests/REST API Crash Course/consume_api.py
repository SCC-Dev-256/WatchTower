import requests
import json
response = requests.get(
    'http://api.stackexchange.com/2.2/questions?order=desc&sort=activity&site=stackoverflow')

for data in response.json()['items']:
    print(data['title'])