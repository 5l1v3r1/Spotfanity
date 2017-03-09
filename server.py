import requests
import json
from flask import Flask, request, Response


app = Flask(__name__)
api_key = '847d1383d7e8d5f9d0a685c9ee091a34'

with open('profanity_list.txt') as f:
    profanity_list = [line.strip() for line in f.readlines()]


@app.route('/')
def hello():
    params = {
        'q_track': request.args.get('track'),
        'q_artist': request.args.get('artist'),
        'format': 'json',
        'apikey': api_key
    }

    r = requests.get('https://api.musixmatch.com/ws/1.1/matcher.lyrics.get', params=params)
    data = r.json()
    lyrics_text = data['message']['body']['lyrics']['lyrics_body']
    lyrics = lyrics_text.split()
    profanity_count = [word for word in lyrics if word in profanity_list]
    return Response(
        json.dumps({
            'lyrics': lyrics_text,
            'profanity': profanity_count,
            'percentage': len(profanity_count) / len(lyrics) * 100
        }),
        status=r.status_code,
        content_type='json'
    )

app.run()
