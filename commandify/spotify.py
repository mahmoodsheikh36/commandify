import requests
import json
import http.server
import socketserver
import webbrowser
import urllib.parse
import os.path
import sys

from commandify.db import DBProvider
from commandify.utils import current_time

db_provider = DBProvider()

SPOTIFY_API_RESULTS_LIMIT = 50
ACCESS_TOKEN_EXPIRE_SECONDS = 2000 # its actually 3600 but lets be more careful

__location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

class AuthCodeHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        auth_code = self.path.split('code=')[1]
        db_provider.add_auth_code(auth_code)
        self.wfile.write(b'received auth code')
        self.send_response(200)

    def log_message(self, format, *args):
        pass

def listen_for_auth_code_request(redirect_uri):
    port = int(redirect_uri.split(':')[2])
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('0.0.0.0', port), AuthCodeHTTPRequestHandler) as httpd:
        httpd.handle_request()

def get_scopes():
    with open(os.path.join(__location__, 'scopes.json')) as scopes_file:
        return json.loads(scopes_file.read())

def get_auth_code(client_id, redirect_uri, scope):
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope
    }
    encoded_params = urllib.parse.urlencode(params)
    url = 'https://accounts.spotify.com/authorize?{}'.format(encoded_params)
    if webbrowser.open(url, new=2):
        print('opened the auth page in your web browser, please authenticate')
        listen_for_auth_code_request(redirect_uri)
        return db_provider.get_auth_code()
    else:
        print('couldnt find a default browser to open the auth page')
        sys.exit(1)

def get_refresh_token(client_id, client_secret, code, redirect_uri):
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    })
    parsed_response = json.loads(response.text)
    db_provider.add_access_token(parsed_response['access_token'])
    db_provider.add_refresh_token(parsed_response['refresh_token'])

def get_access_token(client_id, client_secret, refresh_token):
    response = requests.post('https://accounts.spotify.com/api/token', data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    })
    parsed_response = json.loads(response.text)
    db_provider.add_access_token(parsed_response['access_token'])
    return db_provider.get_access_token()

def access_token_has_expired(access_token):
    return current_time() > access_token['time'] +\
            ACCESS_TOKEN_EXPIRE_SECONDS * 1000

def list_library_tracks(access_token, offset=0):
    r = requests.get('https://api.spotify.com/v1/me/tracks',
                     headers = {
                         'Authorization': 'Bearer {}'.format(access_token)
                     }, params = {
                         'limit': SPOTIFY_API_RESULTS_LIMIT,
                         'offset': offset
                     })
    return json.loads(r.text)

def pause(access_token):
    requests.put('https://api.spotify.com/v1/me/player/pause',
                 headers = {
                     'Authorization': 'Bearer {}'.format(access_token)
                 })

def resume(access_token):
    requests.put('https://api.spotify.com/v1/me/player/play',
                 headers = {
                     'Authorization': 'Bearer {}'.format(access_token)
                 })

def get_current_track(access_token):
    r = requests.get('https://api.spotify.com/v1/me/player/currently-playing',
                     headers = {
                         'Authorization': 'Bearer {}'.format(access_token)
                     })
    if r.text == '':
        return None
    return json.loads(r.text)

def get_valid_access_token(client_id, client_secret, refresh_token):
    access_token = db_provider.get_access_token()
    if access_token_has_expired(access_token):
        get_access_token(client_id, client_secret, refresh_token['token'])
        return db_provider.get_access_token()
    return access_token
