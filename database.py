c.execute('''
    CREATE TABLE IF NOT EXISTS teilnehmer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startnummer INTEGER UNIQUE,
        vorname TEXT NOT NULL,
        nachname TEXT NOT NULL,
        geburtsjahr INTEGER NOT NULL,
        schulklasse TEXT NOT NULL,
        geschlecht TEXT NOT NULL,
        schulort TEXT NOT NULL,
        kategorie TEXT,
        angemeldet_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        datenschutz_zugestimmt BOOLEAN DEFAULT FALSE
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS zeiten (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startnummer INTEGER UNIQUE,
        zeit_sekunden REAL,
        zeit_anzeige TEXT,
        freigegeben BOOLEAN DEFAULT FALSE,
        erfasst_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (startnummer) REFERENCES teilnehmer(startnummer)
    )
''')

conn.commit()
conn.close()
