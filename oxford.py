import requests
import json
import os

app_id = os.environ.get("OXFORD_ID")
app_key = os.environ.get("OXFORD_API_KEY")

def define_word(word):
    language = 'en'
    word_id = word

    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower()

    r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key}).json()
    print(app_id)
    print(app_key)

    result = word.capitalize() + ": " + r['results']['lexicalEntries']['senses']['definitions'][0]
    return result
