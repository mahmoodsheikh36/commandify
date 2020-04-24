import sqlite3
from pathlib import Path
import os.path

from commandify.utils import current_time
from commandify.music import *

__location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

def get_cache_dir():
    cache_dir = str(Path.home()) + '/.cache/commandify/'
    Path(cache_dir).mkdir(exist_ok=True, parents=True)
    return cache_dir

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBProvider():
    def __init__(self, path=get_cache_dir() + 'data.sqlite'):
        self.path = path
        new_db = False
        if not os.path.isfile(self.path):
            new_db = True
        self.conn = self.get_new_conn()
        if new_db:
            with open(os.path.join(__location__, 'schema.sql')) as schema_file:
                self.conn.executescript(schema_file.read())

    def get_new_conn(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = dict_factory
        return conn

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def add_auth_code(self, code):
        c = self.cursor()
        c.execute('INSERT INTO auth_codes (time, code) VALUES (?, ?)',
                  (current_time(), code))
        self.commit()

    def get_auth_code(self):
        return self.cursor().execute('SELECT * FROM auth_codes ORDER BY\
                                      time DESC LIMIT 1').fetchone()

    def add_refresh_token(self, token):
        self.cursor().execute('INSERT INTO refresh_tokens (time, token)\
                               VALUES (?, ?)',
                              (current_time(), token))
        self.commit()

    def get_refresh_token(self):
        return self.cursor().execute('SELECT * FROM refresh_tokens ORDER BY\
                                      time DESC LIMIT 1').fetchone()

    def add_access_token(self, token):
        self.cursor().execute('INSERT INTO access_tokens (time, token)\
                               VALUES (?, ?)',
                              (current_time(), token))
        self.commit()

    def get_access_token(self):
        return self.cursor().execute('SELECT * FROM access_tokens ORDER BY time\
                                      DESC LIMIT 1').fetchone()

    def get_track(self, track_id):
        return self.cursor().execute('SELECT * FROM tracks WHERE id = ?',
                                     (track_id,)).fetchone()

    def add_play(self, track_id, time_started, time_ended):
        c = self.cursor()
        c.execute('INSERT INTO plays (time_started, time_ended, track_id)\
                   VALUES (?, ?, ?)',
                  (time_started, time_ended, track_id))
        self.commit()
        return c.lastrowid

    def update_play_time_ended(self, play_id, time_ended):
        self.cursor().execute('UPDATE plays SET time_ended = ? WHERE id = ?',
                              (time_ended, play_id))
        self.commit()

    def add_pause(self, play_id, time):
        c = self.cursor()
        c.execute('INSERT INTO pauses (play_id, time)\
                   VALUES (?, ?)',
                  (play_id, time))
        self.commit()
        return c.lastrowid

    def add_resume(self, play_id, time):
        c = self.cursor()
        c.execute('INSERT INTO resumes (play_id, time)\
                   VALUES (?, ?)',
                  (play_id, time))
        self.commit()
        return c.lastrowid

    def add_seek(self, play_id, time, position):
        c = self.cursor()
        c.execute('INSERT INTO seeks (play_id, time, position)\
                   VALUES (?, ?, ?)',
                  (play_id, time, position))
        self.commit()
        return c.lastrowid

    def track_exists(self, track_id):
        return self.get_track(track_id) is not None

    def artist_exists(self, artist_id):
        return self.get_artist(artist_id) is not None

    def album_exists(self, album_id):
        return self.get_album(album_id) is not None

    def get_artist(self, artist_id):
        return self.cursor().execute('SELECT * FROM artists WHERE id = ?',
                                     (artist_id,)).fetchone()

    def get_album(self, album_id):
        return self.cursor().execute('SELECT * FROM albums WHERE id = ?',
                                     (album_id,)).fetchone()

    def get_tracks(self):
        return self.cursor().execute('SELECT * FROM tracks').fetchall()

    def add_artist(self, artist_id, name):
        c = self.cursor()
        c.execute('INSERT INTO artists (id, name)\
                   VALUES (?, ?)',
                  (artist_id, name))
        self.commit()

    def add_album(self, album_id, name, type, release_date, release_date_precision,
                  image_url):
        c = self.cursor()
        c.execute("""
        INSERT INTO albums(id, name, type, release_date, release_date_precision, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (album_id, name, type, release_date, release_date_precision, image_url))
        self.commit()

    def add_track(self, track_id, name, duration_ms, popularity, preview_url,
                  track_number, explicit, album_id):
        c = self.cursor()
        c.execute("""
        INSERT INTO tracks (id, name, duration_ms, popularity, preview_url, track_number,
                           explicit, album_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (track_id, name, duration_ms, popularity, preview_url, track_number,
              explicit, album_id))
        self.commit()

    def add_track_artist(self, track_id, artist_id):
        c = self.cursor()
        c.execute('INSERT INTO track_artists (artist_id, track_id)\
                   VALUES (?, ?)',
                  (artist_id, track_id))
        self.commit()
        return c.lastrowid

    def add_album_artist(self, album_id, artist_id):
        c = self.cursor()
        c.execute('INSERT INTO album_artists (album_id, artist_id)\
                   VALUES (?, ?)',
                  (album_id, artist_id))
        self.commit()
        return c.lastrowid

    def add_track_from_spotify_obj(self, track):
        track_artist_ids = []
        for artist in track['artists']:
            if not self.artist_exists(artist['id']):
                self.add_artist(artist['id'], artist['name'])
            track_artist_ids.append(artist['id'])

        album_id = track['album']['id']
        album_artist_ids = []
        album = track['album']
        if not self.album_exists(album_id):
            self.add_album(album_id, album['name'], album['type'], album['release_date'],
                           album['release_date_precision'], album['images'][0]['url'])

        album_artist_ids = []
        for artist in track['album']['artists']:
            if not self.artist_exists(artist['id']):
                self.add_artist(artist['id'], artist['name'])
            album_artist_ids.append(artist['id'])

        self.add_track(track['id'], track['name'], track['duration_ms'],
                       track['popularity'], track['preview_url'], track['track_number'],
                       track['explicit'], album_id)

        for album_artist_id in album_artist_ids:
            self.add_album_artist(album_id, album_artist_id)

        for track_artist_id in track_artist_ids:
            self.add_track_artist(track['id'], track_artist_id)

    def get_track_artists_for_track(self, track_id):
        return self.cursor().execute('SELECT * FROM track_artists WHERE track_id = ?',
                                     (track_id,)).fetchall()

    def get_track(self, track_id):
        track = self.cursor().execute('SELECT * FROM tracks WHERE id = ?',
                                      (track_id,)).fetchone()
        if track is None:
            return None
        track['artist_ids'] = [track_artist['artist_id'] for track_artist in
                               self.get_track_artists_for_track(track['id'])]
        return track

    def get_artists(self):
        return self.cursor().execute('SELECT * FROM artists').fetchall()

    def get_albums(self):
        return self.cursor().execute('SELECT * FROM albums').fetchall()

    def get_tracks(self):
        return self.cursor().execute('SELECT * FROM tracks').fetchall()

    def get_track_artists(self):
        return self.cursor().execute('SELECT * FROM track_artists').fetchall()

    def get_album_artists(self):
        return self.cursor().execute('SELECT * FROM album_artists').fetchall()

    def get_tracks(self):
        tracks = self.cursor().execute("""
        SELECT tracks.*, albums.name as album_name, albums.id as album_id,
        albums.image_url as album_image_url
        FROM tracks INNER JOIN albums ON tracks.album_id = albums.id
        """).fetchall()
        track_artists = self.get_track_artists()
        artists = self.get_artists()
        for track in tracks:
            for track_artist in track_artists:
                if track_artist['track_id'] == track['id']:
                    for artist in artists:
                        if track_artist['artist_id'] == artist['id']:
                            if not 'artists' in track:
                                track['artists'] = [artist]
                            else:
                                track['artists'].append(artist)
                            break
        return tracks

    def get_plays(self):
        return self.cursor().execute('SELECT * FROM plays').fetchall()

    def get_pauses(self):
        return self.cursor().execute('SELECT * FROM pauses').fetchall()

    def get_resumes(self):
        return self.cursor().execute('SELECT * FROM resumes').fetchall()

    def get_music(self):
        db_tracks = self.get_tracks()
        db_albums = self.get_albums()
        db_artists = self.get_artists()
        db_album_artists = self.get_album_artists()
        db_track_artists = self.get_track_artists()
        db_resumes = self.get_resumes()
        db_pauses = self.get_pauses()
        db_plays = self.get_plays()

        # use dicts because their lookup is o(1) and we do alot of lookups here
        track_dict = {}
        album_dict = {}
        artist_dict = {}
        play_dict = {}

        for db_artist in db_artists:
            artist = Artist(db_artist['id'], db_artist['name'], [])
            artist_dict[artist.id] = artist

        for db_album in db_albums:
            album = Album(db_album['id'], db_album['name'], [], [], db_album['type'],
                          db_album['release_date'], db_album['release_date_precision'],
                          db_album['image_url'])
            album_dict[album.id] = album

        for db_track in db_tracks:
            track = Track(db_track['id'], db_track['name'], [],
                          album_dict[db_track['album_id']], [], db_track['preview_url'],
                          db_track['track_number'], db_track['popularity'],
                          db_track['duration_ms'])
            track_dict[track.id] = track
            album_dict[db_track['album_id']].tracks.append(track)

        for db_play in db_plays:
            play = Play(db_play['id'], track_dict[db_play['track_id']],
                        db_play['time_started'], db_play['time_ended'], [], [])
            play_dict[play.id] = play
            track_dict[db_play['track_id']].plays.append(play)

        for db_resume in db_resumes:
            resume = Resume(db_resume['id'], db_resume['time'])
            play_dict[db_resume['play_id']].resumes.append(resume)

        for db_pause in db_pauses:
            pause = Pause(db_pause['id'], db_pause['time'])
            play_dict[db_pause['play_id']].pauses.append(pause)

        for db_track_artist in db_track_artists:
            track_dict[db_track_artist['track_id']].artists.append(
                artist_dict[db_track_artist['artist_id']])

        for db_album_artist in db_album_artists:
            album_dict[db_album_artist['album_id']].artists.append(
                artist_dict[db_album_artist['artist_id']])
            artist_dict[db_album_artist['artist_id']].albums.append(
                album_dict[db_album_artist['album_id']])

        return list(album_dict.values()), list(track_dict.values()),\
               list(artist_dict.values()), list(play_dict.values())
