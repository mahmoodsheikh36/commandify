from time import sleep

import commandify.spotify as sp

REQUEST_INTERVAL = 0.5

def on_exit():
    pass

def start(client_id, client_secret, refresh_token):
    try:
        while True:
            access_token = sp.get_valid_access_token(client_id, client_secret,
                                                     refresh_token)
            current_track = sp.get_current_track(access_token['token'])
            if current_track is not None:
                print(current_track)
            sleep(REQUEST_INTERVAL)
    except KeyboardInterrupt as e:
        print('quitting..')
        on_exit()
