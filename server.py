from os.path import join, dirname
from os import environ
from dotenv import load_dotenv
import requests
import json
from flask import Flask, request, Response, current_app


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
app = Flask(__name__)

with open('profanity_list.txt') as f:
    profanity_list = [line.strip() for line in f.readlines()]

@app.route('/')
def send_site():
    return current_app.send_static_file('index.html')

@app.route('/api/track')
def get_track():
    params = {
        'q_track': request.args.get('track'),
        'q_artist': request.args.get('artist'),
        'format': 'json',
        'apikey': environ.get('MUSIXMATCH_KEY')
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
