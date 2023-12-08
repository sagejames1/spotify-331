from flask import Flask, request, url_for, session, redirect, render_template

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import time
import os
import requests

#DEFINING CONSTS
CLIENT_ID = "7335fe8c6a29494394c314526901fc59"
CLIENT_SECRET = "cc7ed1f76e35410392b62fd6a01d4e73"
TOKEN_INFO = "token_info"
SECRET_KEY = "asdf"
SHORT_TERM = "short_term"
MEDIUM_TERM = "medium_term"
LONG_TERM = "long_term"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external=True),
        scope = "user-top-read user-library-read"
    )

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info: 
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60 
    if (is_expired): 
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info 

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route("/")
def index():
    name = 'username'
    return render_template('index.html', title='Welcome', username=name)

@app.route("/login")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
    

@app.route("/redirectPage")
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code') 
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("getTracks", _external=True))

@app.route("/getTracks")
def getTracks():
    user_token = get_token()

    sp = spotipy.Spotify(
        auth = user_token['access_token']
    )

    current_user_name = sp.current_user()['display_name'] 

    short_term_track = sp.current_user_top_tracks(
        limit=1,
        offset=0,
        time_range=SHORT_TERM
    )

    medium_term_track = sp.current_user_top_tracks(
        limit=1,
        offset=0,
        time_range=MEDIUM_TERM
    )
    long_term_track = sp.current_user_top_tracks(
        limit=1,
        offset=0,
        time_range=LONG_TERM,
    )

    short_term_artist = sp.current_user_top_artists(
        limit=6,
        offset=0,
        time_range=SHORT_TERM
    )

    medium_term_artist = sp.current_user_top_artists(
        limit=6,
        offset=0,
        time_range=MEDIUM_TERM
    )

    long_term_artist = sp.current_user_top_artists(
        limit=6,
        offset=0,
        time_range=LONG_TERM
    )

    if os.path.exists(".cache"): 
        os.remove(".cache")
    
    return render_template('tracks.html', user_name = current_user_name, short_term_track=short_term_track, medium_term_track=medium_term_track, long_term_track=long_term_track, short_term_artist=short_term_artist, medium_term_artist=medium_term_artist, long_term_artist=long_term_artist)
