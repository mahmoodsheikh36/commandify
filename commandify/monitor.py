import traceback
from time import sleep
from requests.exceptions import RequestException

import commandify.spotify as sp
from commandify.utils import current_time

REQUEST_INTERVAL = 0.5

def new_play(track_id):
    play = {
        'time_started': current_time(),
        'time_ended': -1,
        'track_id': track_id,
        'playing': True,
        'progress': -1
    }
    play['id'] = sp.db_provider.add_play(track_id, play['time_started'],
                                         play['time_ended'])
    return play

def start(client_id, client_secret, refresh_token):

    def on_exit():
        pass

    try:
        play = None
        prev_request_time = current_time()
        while True:
            try:
                access_token = sp.get_valid_access_token(client_id, client_secret,
                                                         refresh_token)
                current_track = sp.get_current_track(access_token['token'])
                time = current_time()

                if current_track is not None:
                    playing = current_track['is_playing']
                    track_id = current_track['item']['id']
                    progress = current_track['progress_ms'] / 1000.

                    if not sp.db_provider.track_exists(track_id):
                        sp.db_provider.add_track_from_spotify_obj(current_track['item'])

                    if play is None:
                        play = new_play(track_id)
                    else:
                        if track_id != play['track_id']: # track changed
                            sp.db_provider.update_play_time_ended(play['id'],
                                                                  time)
                            play = new_play(track_id)
                        if not playing and play['playing']: # paused
                            sp.db_provider.add_pause(play['id'], time)
                            play['playing'] = False
                        elif playing and not play['playing']: # resumed
                            sp.db_provider.add_resume(play['id'], time)
                            play['playing'] = True
                        else: # if nothing just update time_ended to be safe..?
                            sp.db_provider.update_play_time_ended(play['id'],
                                                                  time)
                        if play['progress'] != -1: # if not new play
                            seconds_passed = (time - prev_request_time) / 1000
                            error = abs(seconds_passed - abs(progress - play['progress']))
                            if error > 5:
                                sp.db_provider.add_seek(play['id'], time, progress)
                        play['progress'] = progress
                else: # spotify was closed / nothing is playing
                    if play is not None:
                        sp.db_provider.update_play_time_ended(play['id'],
                                                              time)
                        play = None

                prev_request_time = time
            except (KeyError, TypeError, RequestException) as e:
                """
                sometimes spotify's api sends wrong data resulting in a KeyError
                or a TypeError
                we just end the current play in case an exception occurs
                """
                play = None
                traceback.print_tb(e.__traceback__)
                print(e)
            sleep(REQUEST_INTERVAL)
    except KeyboardInterrupt as e:
        print('quitting..')
        on_exit()
