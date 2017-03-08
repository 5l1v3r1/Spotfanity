import requests
import json
from flask import Flask, request, Response

app = Flask(__name__)
api_key = '847d1383d7e8d5f9d0a685c9ee091a34'

@app.route("/")
def hello():
    params = {
        'q_track': request.args.get('track'),
        'q_artist': request.args.get('artist'),
        'format': 'json',
        'apikey': api_key
    }
    r = requests.get('https://api.musixmatch.com/ws/1.1/matcher.lyrics.get', params=params)
    data = json.loads(r.text)
    return Response(
        data['message']['body']['lyrics']['lyrics_body'],
        status=r.status_code,
        content_type='json'
    )

app.run()
