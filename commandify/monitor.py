from time import sleep

import commandify.spotify as sp
from commandify.utils import current_time

REQUEST_INTERVAL = 0.5

def new_play(song_id):
    play = {
        'time_started': current_time(),
        'time_ended': -1,
        'song_id': song_id,
        'playing': True,
        'progress': -1
    }
    play['id'] = sp.db_provider.add_play(song_id, play['time_started'],
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
                    song_id = current_track['item']['id']
                    progress = current_track['progress_ms'] / 1000.
                    if play is None:
                        play = new_play(song_id)
                    else:
                        if song_id != play['song_id']: # song changed
                            sp.db_provider.update_play_time_ended(play['id'],
                                                                  time)
                            play = new_play(song_id)
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
            except KeyError as e:
                """
                sometimes spotify's api sends wrong data resulting in a KeyError
                """
                pass
            sleep(REQUEST_INTERVAL)
    except KeyboardInterrupt as e:
        print('quitting..')
        on_exit()
