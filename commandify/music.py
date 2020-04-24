class Track:
    def __init__(self, track_id, name, artists, album, plays, preview_url, track_number,
                 popularity, duration_ms):
        self.id = track_id
        self.name = name
        self.popularity = popularity
        self.preview_url = preview_url
        self.track_number = track_number
        self.popularity = popularity
        self.duration_ms = duration_ms
        self.artists = artists
        self.album = album
        self.plays = plays

    def ms_listened(self, from_time=None, to_time=None):
        total = 0
        """
        i should only iterate through plays after from_time and before to_time
        if performance is an issue, which it probably is.. but whatever
        """
        for play in self.plays:
            total += play.ms_listened(from_time, to_time)
        return total

    # returns a beautiful formatted time string
    def time_listened(self, from_time=None, to_time=None):
        ms_listened = self.ms_listened(from_time, to_time)
        seconds = (ms_listened // 1000) % 60
        minutes = (ms_listened // 60000) % 60
        hours = (ms_listened // 360000)
        if minutes > 0:
            if hours > 0:
                return '{} hrs, {} mins, {} secs'.format(hours, minutes, seconds)
            return '{} mins, {} secs'.format(minutes, seconds)
        return '{} secs'.format(seconds)

class Album:
    def __init__(self, album_id, name, tracks, artists, type, release_date,
                 release_date_precision, image_url):
        self.id = album_id
        self.name = name
        self.type = type
        self.release_date = release_date
        self.release_date_precision = release_date_precision
        self.image_url = image_url
        self.tracks = tracks
        self.artists = artists

class Artist:
    def __init__(self, artist_id, name, albums):
        self.id = artist_id
        self.name = name
        self.albums = albums

class Play: # gotta add seeks too, but im not using them atm
    def __init__(self, play_id, track, time_started, time_ended, resumes, pauses):
        self.id = play_id
        self.resumes = resumes
        self.pauses = pauses
        self.time_started = time_started
        self.time_ended = time_ended
        self.track = track

    def ms_listened(self, from_time=None, to_time=None):
        if abs(len(self.pauses) - len(self.resumes)) > 1:
            return 0
        if from_time is None:
            from_time = self.time_started
        elif from_time > self.time_ended:
            return 0
        if to_time is None:
            to_time = self.time_ended
        elif to_time < self.time_started:
            return 0
        if from_time < self.time_started:
            from_time = self.time_started
        if to_time > self.time_ended:
            to_time = self.time_ended
        milliseconds = to_time - from_time
        for i in range(len(self.resumes)):
            pause = self.pauses[i]
            resume = self.resumes[i]
            time_paused = pause.time
            time_resumed = resume.time
            if time_paused > to_time:
                continue
            if time_resumed < from_time:
                continue
            if time_paused < from_time:
                time_paused = from_time
            if time_resumed > to_time:
                time_resumed = to_time
            milliseconds -= time_resumed - time_paused
        if len(self.pauses) > len(self.resumes):
            time_paused = self.pauses[-1].time
            if time_paused < to_time:
                if time_paused < from_time:
                    time_paused = from_time
                milliseconds -= to_time - time_paused
        return milliseconds

class Resume:
    def __init__(self, resume_id, time):
        self.id = resume_id
        self.time = time

class Pause:
    def __init__(self, pause_id, time):
        self.id = pause_id
        self.time = time

# Seek class should be added too, similar to Pause and Resume
