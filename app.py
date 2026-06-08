<<DOCUMENT:{"filename":"app.py","format":"txt"}>>
import streamlit as st
import pandas as pd
from database import (
init_db, teilnehmer_anmelden, zeit_erfassen,
zeit_freigeben, alle_freigeben, get_ergebnisse,
get_alle_teilnehmer, get_teilnehmer_by_startnummer,
get_statistik, teilnehmer_loeschen, export_ergebnisse_csv
)

st.set_page_config(
page_title="Kinderlauf Zeitmessung",
page_icon="🏃",
layout="wide",
initial_sidebar_state="expanded"
)

ADMIN_PASSWORT = "lauf2024"

init_db()

if "admin_eingeloggt" not in st.session_state:
st.session_state.admin_eingeloggt = False
if "seite" not in st.session_state:
st.session_state.seite = "anmeldung"

def sidebar():
with st.sidebar:
st.markdown("## Kinderlauf")
st.markdown("---")
st.markdown("### Navigation")
if st.button("Anmeldung", use_container_width=True):
st.session_state.seite = "anmeldung"
st.rerun()
if st.button("Live-Ergebnisse", use_container_width=True):
st.session_state.seite = "live"
st.rerun()
st.markdown("---")
st.markdown("### Admin-Bereich")
if not st.session_state.admin_eingeloggt:
passwort = st.text_input("Passwort", type="password", key="pw_input")
if st.button("Einloggen", use_container_width=True):
if passwort == ADMIN_PASSWORT:
st.session_state.admin_eingeloggt = True
st.success("Eingeloggt!")
st.rerun()
else:
st.error("Falsches Passwort")
else:
st.success("Admin eingeloggt")
if st.button("Zeiterfassung", use_container_width=True):
st.session_state.seite = "zeiterfassung"
st.rerun()
if st.button("Freigabe", use_container_width=True):
st.session_state.seite = "freigabe"
st.rerun()
if st.button("Teilnehmerliste", use_container_width=True):
st.session_state.seite = "teilnehmer"
st.rerun()
if st.button("Statistik", use_container_width=True):
st.session_state.seite = "statistik"
st.rerun()
st.markdown("---")
if st.button("Ausloggen", use_container_width=True):
st.session_state.admin_eingeloggt = False
st.session_state.seite = "anmeldung"
st.rerun()
st.markdown("---")
gesamt, mit_zeit, freigegeben = get_statistik()
st.write("Angemeldet:", gesamt)
st.write("Mit Zeit:", mit_zeit)
st.write("Freigegeben:", freigegeben)

def seite_anmeldung():
st.title("Kinderlauf Anmeldung")
st.write("Bitte alle Felder ausfuellen")

plaintext

Copy
with st.form("anmelde_formular", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        vorname = st.text_input("Vorname")
        nachname = st.text_input("Nachname")
        geburtsjahr = st.selectbox(
            "Geburtsjahr",
            options=list(range(2024, 2009, -1)),
            index=6
        )
    with col2:
        schulklasse = st.text_input(
            "Schulklasse",
            placeholder="z.B. 2b"
        )
        geschlecht = st.radio(
            "Geschlecht",
            options=["Maedchen", "Bursch"],
            horizontal=True
        )
        schulort = st.text_input("Schulort")

    st.markdown("---")
    datenschutz = st.checkbox(
        "Ich stimme der Verarbeitung der Daten meines Kindes zu. Die Daten werden nach 6 Monaten geloescht.",
        value=False
    )
    abschicken = st.form_submit_button("Jetzt anmelden!", use_container_width=True)

if abschicken:
    fehler = []
    if not vorname.strip():
        fehler.append("Vorname fehlt")
    if not nachname.strip():
        fehler.append("Nachname fehlt")
    if not schulklasse.strip():
        fehler.append("Schulklasse fehlt")
    if not schulort.strip():
        fehler.append("Schulort fehlt")
    if not datenschutz:
        fehler.append("Datenschutz-Zustimmung fehlt")
    klassenstufe = ''.join(filter(str.isdigit, schulklasse))
    if not klassenstufe:
        fehler.append("Schulklasse muss eine Zahl enthalten z.B. 2b")
    if fehler:
        for f in fehler:
            st.error(f)
    else:
        startnummer, fehler_db = teilnehmer_anmelden(
            vorname.strip(), nachname.strip(), geburtsjahr,
            schulklasse.strip().lower(), geschlecht,
            schulort.strip(), datenschutz
        )
        if startnummer:
            klassenstufe = ''.join(filter(str.isdigit, schulklasse))
            kategorie = geschlecht + " " + klassenstufe + ". Klasse"
            st.success("Anmeldung erfolgreich!")
            st.metric("Startnummer", f"{startnummer:03d}")
            st.info("Kategorie: " + kategorie + " | Klasse: " + schulklasse.upper() + " | Ort: " + schulort)
        else:
            st.error("Fehler bei der Anmeldung: " + str(fehler_db))
def seite_live_ergebnisse():
st.title("Live-Ergebnisse")
if st.button("Aktualisieren", use_container_width=True):
st.rerun()
df = get_ergebnisse(nur_freigegeben=True)
if df.empty:
st.info("Noch keine Ergebnisse freigegeben. Bitte warten...")
return
kategorien = sorted(df['kategorie'].unique())
tab_namen = ["Gesamt"] + list(kategorien)
tabs = st.tabs(tab_namen)
with tabs[0]:
st.markdown("### Gesamtranking")
gesamt_df = df.sort_values('zeit_sekunden').reset_index(drop=True)
gesamt_df.index += 1
_zeige_rangliste(gesamt_df, zeige_kategorie=True)
for i, kat in enumerate(kategorien):
with tabs[i + 1]:
st.markdown("### " + kat)
kat_df = df[df['kategorie'] == kat].sort_values('zeit_sekunden').reset_index(drop=True)
kat_df.index += 1
_zeige_rangliste(kat_df, zeige_kategorie=False)

def _zeige_rangliste(df, zeige_kategorie=False):
if df.empty:
st.info("Noch keine Ergebnisse in dieser Kategorie.")
return
podest_cols = st.columns(3)
plaetze = ["1. Platz", "2. Platz", "3. Platz"]
for i, (col, platz) in enumerate(zip(podest_cols, plaetze)):
if i < len(df):
row = df.iloc[i]
with col:
st.metric(
label=platz,
value=row['vorname'] + " " + row['nachname'],
delta=row['zeit_anzeige']
)
st.markdown("---")
spalten = ['startnummer', 'vorname', 'nachname', 'schulklasse', 'zeit_anzeige']
if zeige_kategorie:
spalten.insert(4, 'kategorie')
anzeige_df = df[spalten].copy()
anzeige_df.insert(0, 'Platz', range(1, len(anzeige_df) + 1))
if zeige_kategorie:
anzeige_df.columns = ['Platz', 'Nr', 'Vorname', 'Nachname', 'Klasse', 'Kategorie', 'Zeit']
else:
anzeige_df.columns = ['Platz', 'Nr', 'Vorname', 'Nachname', 'Klasse', 'Zeit']
st.dataframe(anzeige_df, use_container_width=True, hide_index=True)

def seite_zeiterfassung():
st.title("Zeiterfassung")
col1, col2 = st.columns([1, 1])
with col1:
st.markdown("### Neue Zeit eingeben")
with st.form("zeit_formular", clear_on_submit=True):
startnummer = st.number_input(
"Startnummer", min_value=1, max_value=9999, step=1, value=1
)
zeit = st.text_input(
"Zeit",
placeholder="z.B. 04:32 oder 04:32.15"
)
person = get_teilnehmer_by_startnummer(int(startnummer))
if person:
st.info(
"Person: " + person['vorname'] + " " + person['nachname'] +
" | Klasse: " + person['schulklasse'].upper() +
" | " + person['kategorie']
)
else:
st.warning("Startnummer nicht gefunden")
speichern = st.form_submit_button("Zeit speichern", use_container_width=True)
if speichern and zeit:
ok, msg = zeit_erfassen(int(startnummer), zeit.strip())
if ok:
st.success(msg)
else:
st.error(msg)
with col2:
st.markdown("### Noch nicht freigegebene Zeiten")
df = get_ergebnisse(nur_freigegeben=False)
if not df.empty:
nicht_freigegeben = df[df['freigegeben'] == False]
if nicht_freigegeben.empty:
st.success("Alle Zeiten sind freigegeben!")
else:
st.dataframe(
nicht_freigegeben[['startnummer', 'vorname', 'nachname', 'kategorie', 'zeit_anzeige']],
use_container_width=True, hide_index=True
)
else:
st.info("Noch keine Zeiten erfasst.")

def seite_freigabe():
st.title("Ergebnis-Freigabe")
df = get_ergebnisse(nur_freigegeben=False)
if df.empty:
st.info("Noch keine Zeiten erfasst.")
return
nicht_freigegeben = df[df['freigegeben'] == False]
freigegeben = df[df['freigegeben'] == True]
col1, col2 = st.columns(2)
with col1:
st.metric("Warten auf Freigabe", len(nicht_freigegeben))
with col2:
st.metric("Freigegeben", len(freigegeben))
if not nicht_freigegeben.empty:
if st.button("ALLE freigeben", type="primary", use_container_width=True):
alle_freigeben()
st.success("Alle Ergebnisse wurden freigegeben!")
st.rerun()
st.markdown("---")
st.markdown("### Warten auf Freigabe")
if nicht_freigegeben.empty:
st.success("Alle Zeiten sind bereits freigegeben!")
else:
for , row in nicht_freigegeben.iterrows():
col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
with col1:
st.write("Nr.", row['startnummer'])
with col2:
st.write(row['vorname'] + " " + row['nachname'])
with col3:
st.write(row['kategorie'])
with col4:
st.write(row['zeit_anzeige'])
with col5:
if st.button("OK", key="frei" + str(row['startnummer'])):
zeit_freigeben(row['startnummer'])
st.rerun()
if not freigegeben.empty:
st.markdown("---")
st.markdown("### Bereits freigegeben")
st.dataframe(
freigegeben[['startnummer', 'vorname', 'nachname', 'kategorie', 'zeit_anzeige']],
use_container_width=True, hide_index=True
)

def seite_teilnehmer():
st.title("Teilnehmerliste")
df = get_alle_teilnehmer()
if df.empty:
st.info("Noch keine Teilnehmer angemeldet.")
return
col1, col2, col3 = st.columns(3)
with col1:
filter_geschlecht = st.selectbox("Geschlecht", ["Alle", "Maedchen", "Bursch"])
with col2:
klassen = ["Alle"] + sorted(df['schulklasse'].unique().tolist())
filter_klasse = st.selectbox("Klasse", klassen)
with col3:
filter_ort = st.selectbox("Schulort", ["Alle"] + sorted(df['schulort'].unique().tolist()))
gefiltert = df.copy()
if filter_geschlecht != "Alle":
gefiltert = gefiltert[gefiltert['geschlecht'] == filter_geschlecht]
if filter_klasse != "Alle":
gefiltert = gefiltert[gefiltert['schulklasse'] == filter_klasse]
if filter_ort != "Alle":
gefiltert = gefiltert[gefiltert['schulort'] == filter_ort]
st.write(len(gefiltert), "Teilnehmer gefunden")
st.dataframe(gefiltert, use_container_width=True, hide_index=True)
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
csv = export_ergebnisse_csv()
st.download_button(
"Ergebnisse als CSV exportieren",
data=csv,
file_name="kinderlauf_ergebnisse.csv",
mime="text/csv",
use_container_width=True
)
with col2:
teilnehmer_csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
"Teilnehmerliste als CSV exportieren",
data=teilnehmer_csv,
file_name="kinderlauf_teilnehmer.csv",
mime="text/csv",
use_container_width=True
)

def seite_statistik():
st.title("Statistik")
gesamt, mit_zeit, freigegeben = get_statistik()
df = get_alle_teilnehmer()
if df.empty:
st.info("Noch keine Daten vorhanden.")
return
col1, col2, col3, col4 = st.columns(4)
with col1:
st.metric("Angemeldet", gesamt)
with col2:
st.metric("Mit Zeit", mit_zeit)
with col3:
st.metric("Freigegeben", freigegeben)
with col4:
st.metric("Ausstehend", gesamt - mit_zeit)
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
st.markdown("### Nach Kategorie")
if 'kategorie' in df.columns:
kat_count = df['kategorie'].value_counts().reset_index()
kat_count.columns = ['Kategorie', 'Anzahl']
st.dataframe(kat_count, use_container_width=True, hide_index=True)
with col2:
st.markdown("### Nach Schulort")
if 'schulort' in df.columns:
ort_count = df['schulort'].value_counts().reset_index()
ort_count.columns = ['Schulort', 'Anzahl']
st.dataframe(ort_count, use_container_width=True, hide_index=True)

def main():
sidebar()
seite = st.session_state.seite
if seite == "anmeldung":
seite_anmeldung()
elif seite == "live":
seite_live_ergebnisse()
elif seite == "zeiterfassung":
if st.session_state.admin_eingeloggt:
seite_zeiterfassung()
else:
st.warning("Bitte zuerst einloggen.")
elif seite == "freigabe":
if st.session_state.admin_eingeloggt:
seite_freigabe()
else:
st.warning("Bitte zuerst einloggen.")
elif seite == "teilnehmer":
if st.session_state.admin_eingeloggt:
seite_teilnehmer()
else:
st.warning("Bitte zuerst einloggen.")
elif seite == "statistik":
if st.session_state.admin_eingeloggt:
seite_statistik()
else:
st.warning("Bitte zuerst einloggen.")

if name == "main":
main()
<<>>
