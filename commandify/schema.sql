PRAGMA foreign_keys = OFF;

CREATE TABLE auth_codes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  code TEXT NOT NULL
);

CREATE TABLE refresh_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  token TEXT NOT NULL
);

CREATE TABLE access_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  token TEXT NOT NULL
);

CREATE TABLE tracks (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  duration_ms INTEGER NOT NULL,
  popularity INTEGER NOT NULL,
  preview_url TEXT, -- spotify sometimes doesnt provide one
  track_number INTEGER NOT NULL,
  explicit INTEGER NOT NULL, -- 0=false, 1=true
  album_id TEXT NOT NULL,
  FOREIGN KEY (album_id) REFERENCES albums (id)
);

CREATE TABLE albums (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  release_date TEXT NOT NULL,
  release_date_precision TEXT NOT NULL,
  image_url TEXT NOT NULL
);

CREATE TABLE album_artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id TEXT NOT NULL,
  album_id TEXT NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (album_id) REFERENCES albums (id)
);

CREATE TABLE track_artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id TEXT NOT NULL,
  track_id TEXT NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (track_id) REFERENCES tracks (id)
);

CREATE TABLE artists (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE plays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time_started INTEGER NOT NULL,
  time_ended INTEGER NOT NULL,
  track_id TEXT NOT NULL,
  FOREIGN KEY (track_id) REFERENCES tracks (id)
);

CREATE TABLE pauses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  play_id INTEGER NOT NULL,
  FOREIGN KEY (play_id) REFERENCES plays (id)
);

CREATE TABLE resumes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  play_id INTEGER NOT NULL,
  FOREIGN KEY (play_id) REFERENCES plays (id)
);

CREATE TABLE seeks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  position INTEGER NOT NULL,
  play_id INTEGER NOT NULL,
  FOREIGN KEY (play_id) REFERENCES plays (id)
);
