from os.path import join, dirname
from os import environ
from dotenv import load_dotenv
import requests
import json
import spotipy
import math
from flask import Flask, request, Response, render_template


def get_score(lyrics):
    def score_function(x):
        return 1 - math.exp(x * -74.07113)

    lyrics = lyrics.split()
    print("Butt" in profanity_list)
    profanity_words = [word for word in lyrics if word.lower() in profanity_list]
    profanity_count = len(profanity_words) / len(lyrics)
    unique_profanity = set(profanity_words)
    unique_profanity_score = len(unique_profanity) / 7
    return score_function(profanity_count) * max(0.5, unique_profanity_score), unique_profanity

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
app = Flask(__name__)

with open('profanity_list.txt') as f:
    profanity_list = [line.strip() for line in f.readlines()]


@app.route('/')
def send_site():
    authorize_url = 'https://accounts.spotify.com/authorize/?'
    params = {
        'client_id': environ.get('SPOTIPY_CLIENT_ID'),
        'response_type': 'code',
        'redirect_uri': 'http://localhost:5000/create'
    }
    return render_template('index.html', authorize_url=authorize_url + requests.compat.urlencode(params))


@app.route('/create')
def create_menu():
    data = {
        'grant_type': 'authorization_code',
        'code': request.args.get('code'),
        'client_id': environ.get('SPOTIPY_CLIENT_ID'),
        'client_secret': environ.get('SPOTIPY_CLIENT_SECRET'),
        'redirect_uri': 'http://localhost:5000/create'
    }
    r = requests.post('https://accounts.spotify.com/api/token', data=data)
    sp = spotipy.Spotify(auth=r.json()['access_token'])

    length = 0
    playlists = []
    while length == 0 or length > len(playlists):
        playlist_data = sp.current_user_playlists(limit=50, offset=len(playlists))
        length = playlist_data['total']

        playlists += [{
            'name': playlist['name'],
            'id': playlist['id'],
            'image': playlist['images'][0]['url']
        } for playlist in playlist_data['items']]

    return Response(
        json.dumps(playlists),
        status=r.status_code,
        content_type='json'
    )


@app.route('/api/track')
def get_track():
    params = {
        'q_track': request.args.get('track'),
        'q_artist': request.args.get('artist'),
        'format': 'json',
        'apikey': environ.get('MUSIXMATCH_KEY')
    }

    print(environ.get('MUSIXMATCH_KEY'))
    r = requests.get('https://api.musixmatch.com/ws/1.1/matcher.lyrics.get', params=params)
    data = r.json()
    lyrics_text = data['message']['body']['lyrics']['lyrics_body']
    score, unique_profanity = get_score(lyrics_text)
    return Response(
        json.dumps({
            'lyrics': lyrics_text,
            'score': score,
            'unique_profanity': list(unique_profanity)
        }),
        status=r.status_code,
        content_type='json'
    )

app.run(debug=True)
