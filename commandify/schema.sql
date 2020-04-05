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

CREATE TABLE songs (
  id TEXT PRIMARY KEY NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE plays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time_started INTEGER NOT NULL,
  time_ended INTEGER NOT NULL,
  song_id TEXT NOT NULL,
  FOREIGN KEY (song_id) REFERENCES songs (id)
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
