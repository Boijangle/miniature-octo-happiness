import sys
import random
from pytz import timezone
import datetime
from datetime import datetime
import pytz
from libs import post_text
import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials

username = os.environ.get("USERNAME")
client_id = os.environ.get("SPOTIPY_CLIENT_ID")
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
playlist_id = os.environ.get("SPOTIPY_PLAYLIST_ID")
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def post_rand_song():
    results = sp.user_playlist(username, playlist_id, 'tracks,next')
    tracks = results['tracks']
    all_tracks = tracks['items']
    while tracks['next']:
        tracks = sp.next(tracks)
        all_tracks += tracks['items']

    random_track = random.choice(all_tracks)
    post_text("test", sys.arg[1])
    """post_text(u'\U0001F3B5\U0001F4C5: ' + random_track['track']['name'] + ' - ' + random_track['track']['artists'][0]['name']
    + ' ' + random_track['track']['external_urls']['spotify'], sys.argv[1])"""
