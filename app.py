with st.form("anmelde_formular", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        vorname = st.text_input("Vorname *", placeholder="z.B. Anna")
        nachname = st.text_input("Nachname *", placeholder="z.B. Mayer")
        geburtsjahr = st.selectbox(
            "Geburtsjahr *",
            options=list(range(2024, 2009, -1)),
            index=6
        )
    with col2:
        schulklasse = st.text_input(
            "Schulklasse *",
            placeholder="z.B. 2b",
            help="Bitte Zahl + Buchstabe eingeben, z.B. 1a, 2b, 3c"
        )
        geschlecht = st.radio(
            "Geschlecht *",
            options=["Mädchen", "Bursch"],
            horizontal=True
        )
        schulort = st.text_input("Schulort *", placeholder="z.B. Linz")

    st.markdown("---")
    datenschutz = st.checkbox(
        "✅ Ich stimme der Verarbeitung der Daten meines Kindes für die "
        "Laufveranstaltung zu. Die Daten werden ausschließlich für die "
        "Auswertung verwendet und nach 6 Monaten gelöscht. *",
        value=False
    )
    abschicken = st.form_submit_button("🎽 Jetzt anmelden!", use_container_width=True)

if abschicken:
    fehler = []
    if not vorname.strip(): fehler.append("Vorname fehlt")
    if not nachname.strip(): fehler.append("Nachname fehlt")
    if not schulklasse.strip(): fehler.append("Schulklasse fehlt")
    if not schulort.strip(): fehler.append("Schulort fehlt")
    if not datenschutz: fehler.append("Datenschutz-Zustimmung fehlt")
    klassenstufe = ''.join(filter(str.isdigit, schulklasse))
    if not klassenstufe: fehler.append("Schulklasse muss eine Zahl enthalten (z.B. 2b)")

    if fehler:
        for f in fehler:
            st.error(f"❌ {f}")
    else:
        startnummer, fehler_db = teilnehmer_anmelden(
            vorname.strip(), nachname.strip(), geburtsjahr,
            schulklasse.strip().lower(), geschlecht,
            schulort.strip(), datenschutz
        )
        if startnummer:
            klassenstufe = ''.join(filter(str.isdigit, schulklasse))
            kategorie = f"{geschlecht} {klassenstufe}. Klasse"
            st.markdown(f"""
            <div class="success-box">
                <p>🎉 Anmeldung erfolgreich!</p>
                <p><strong>{vorname} {nachname}</strong></p>
                <p>Deine Startnummer:</p>
                <div class="startnummer-box">{startnummer:03d}</div>
                <br>
                <p>📌 Kategorie: <strong>{kategorie}</strong></p>
                <p>🏫 Klasse: <strong>{schulklasse.upper()}</strong> | 📍 {schulort}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"❌ Fehler bei der Anmeldung: {fehler_db}")
          df = get_ergebnisse(nur_freigegeben=True)
if df.empty:
    st.info("⏳ Noch keine Ergebnisse freigegeben. Bitte warten...")
    return

kategorien = sorted(df['kategorie'].unique())
tab_namen = ["🏅 Gesamt"] + [f"🏃 {k}" for k in kategorien]
tabs = st.tabs(tab_namen)

with tabs[0]:
    st.markdown("### 🏅 Gesamtranking")
    gesamt_df = df.sort_values('zeit_sekunden').reset_index(drop=True)
    gesamt_df.index += 1
    _zeige_rangliste(gesamt_df, zeige_kategorie=True)

for i, kat in enumerate(kategorien):
    with tabs[i + 1]:
        st.markdown(f"### 🏃 {kat}")
        kat_df = df[df['kategorie'] == kat].sort_values('zeit_sekunden').reset_index(drop=True)
        kat_df.index += 1
        _zeige_rangliste(kat_df, zeige_kategorie=False)
if len(df) >= 1:
    podest_cols = st.columns(3)
    medaillen = ["🥇", "🥈", "🥉"]
    for i, (col, medal) in enumerate(zip(podest_cols, medaillen)):
        if i < len(df):
            row = df.iloc[i]
            with col:
                st.markdown(f"""
                <div style='text-align:center; padding:1rem;
                     background:#f8f9fa; border-radius:10px;
                     border-top: 4px solid {"#FFD700" if i==0 else "#C0C0C0" if i==1 else "#CD7F32"}'>
                    <div style='font-size:2rem'>{medal}</div>
                    <div style='font-size:1.1rem; font-weight:bold'>
                        {row['vorname']} {row['nachname']}
                    </div>
                    <div style='font-size:1.5rem; color:#FF6B35; font-weight:bold'>
                        {row['zeit_anzeige']}
                    </div>
                    <div style='color:#666'>Nr. {row['startnummer']:03d}</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")
spalten = ['startnummer', 'vorname', 'nachname', 'schulklasse', 'zeit_anzeige']
if zeige_kategorie:
    spalten.insert(4, 'kategorie')
anzeige_df = df[spalten].copy()
anzeige_df.insert(0, 'Platz', range(1, len(anzeige_df) + 1))
anzeige_df.columns = (
    ['Platz', 'Nr.', 'Vorname', 'Nachname', 'Klasse', 'Kategorie', 'Zeit']
    if zeige_kategorie
    else ['Platz', 'Nr.', 'Vorname', 'Nachname', 'Klasse', 'Zeit']
)
st.dataframe(anzeige_df, use_container_width=True, hide_index=True)
  with col1:
    st.markdown("### Neue Zeit eingeben")
    with st.form("zeit_formular", clear_on_submit=True):
        startnummer = st.number_input(
            "Startnummer", min_value=1, max_value=9999,
            step=1, value=None, placeholder="z.B. 42"
        )
        zeit = st.text_input(
            "Zeit (MM:SS oder MM:SS.hh)",
            placeholder="z.B. 04:32 oder 04:32.15"
        )
        if startnummer:
            person = get_teilnehmer_by_startnummer(int(startnummer))
            if person:
                st.info(
                    f"👤 **{person['vorname']} {person['nachname']}** | "
                    f"Klasse {person['schulklasse'].upper()} | "
                    f"{person['kategorie']}"
                )
            else:
                st.warning("⚠️ Startnummer nicht gefunden")
        speichern = st.form_submit_button("💾 Zeit speichern", use_container_width=True)

    if speichern and startnummer and zeit:
        ok, msg = zeit_erfassen(int(startnummer), zeit.strip())
        if ok:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

with col2:
    st.markdown("### ⏳ Noch nicht freigegebene Zeiten")
    df = get_ergebnisse(nur_freigegeben=False)
    if not df.empty:
        nicht_freigegeben = df[df['freigegeben'] == False]
        if nicht_freigegeben.empty:
            st.success("Alle Zeiten sind freigegeben!")
        else:
            st.dataframe(
                nicht_freigegeben[['startnummer', 'vorname', 'nachname',
                                   'kategorie', 'zeit_anzeige']],
                use_container_width=True, hide_index=True
            )
    else:
        st.info("Noch keine Zeiten erfasst.")
      if df.empty:
    st.info("Noch keine Zeiten erfasst.")
    return

nicht_freigegeben = df[df['freigegeben'] == False]
freigegeben = df[df['freigegeben'] == True]

col1, col2 = st.columns(2)
with col1:
    st.metric("⏳ Warten auf Freigabe", len(nicht_freigegeben))
with col2:
    st.metric("✅ Freigegeben", len(freigegeben))

if not nicht_freigegeben.empty:
    if st.button("🚀 ALLE freigeben", type="primary", use_container_width=True):
        alle_freigeben()
        st.success("✅ Alle Ergebnisse wurden freigegeben!")
        st.rerun()

st.markdown("---")
st.markdown("### ⏳ Warten auf Freigabe")

if nicht_freigegeben.empty:
    st.success("Alle Zeiten sind bereits freigegeben!")
else:
    for _, row in nicht_freigegeben.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
        with col1:
            st.markdown(f"**#{row['startnummer']:03d}**")
        with col2:
            st.markdown(f"{row['vorname']} {row['nachname']}")
        with col3:
            st.markdown(f"📌 {row['kategorie']}")
        with col4:
            st.markdown(f"⏱️ **{row['zeit_anzeige']}**")
        with col5:
            if st.button("✅", key=f"frei_{row['startnummer']}", help="Freigeben"):
                zeit_freigeben(row['startnummer'])
                st.rerun()

if not freigegeben.empty:
    st.markdown("---")
    st.markdown("### ✅ Bereits freigegeben")
    st.dataframe(
        freigegeben[['startnummer', 'vorname', 'nachname',
                     'kategorie', 'zeit_anzeige']],
        use_container_width=True, hide_index=True
    )
if df.empty:
    st.info("Noch keine Teilnehmer angemeldet.")
    return

col1, col2, col3 = st.columns(3)
with col1:
    filter_geschlecht = st.selectbox("Geschlecht", ["Alle", "Mädchen", "Bursch"])
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

st.markdown(f"**{len(gefiltert)} Teilnehmer** gefunden")
st.dataframe(gefiltert, use_container_width=True, hide_index=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    csv = export_ergebnisse_csv()
    st.download_button(
        "📥 Ergebnisse als CSV exportieren",
        data=csv,
        file_name="kinderlauf_ergebnisse.csv",
        mime="text/csv",
        use_container_width=True
    )
with col2:
    teilnehmer_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Teilnehmerliste als CSV exportieren",
        data=teilnehmer_csv,
        file_name="kinderlauf_teilnehmer.csv",
        mime="text/csv",
        use_container_width=True
    )
if df.empty:
    st.info("Noch keine Daten vorhanden.")
    return

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("👥 Angemeldet", gesamt)
with col2: st.metric("⏱️ Mit Zeit", mit_zeit)
with col3: st.metric("✅ Freigegeben", freigegeben)
with col4: st.metric("⏳ Ausstehend", gesamt - mit_zeit)

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
      if seite == "anmeldung":
    seite_anmeldung()
elif seite == "live":
    seite_live_ergebnisse()
elif seite == "zeiterfassung":
    if st.session_state.admin_eingeloggt:
        seite_zeiterfassung()
    else:
        st.warning("🔐 Bitte zuerst einloggen.")
elif seite == "freigabe":
    if st.session_state.admin_eingeloggt:
        seite_freigabe()
    else:
        st.warning("🔐 Bitte zuerst einloggen.")
elif seite == "teilnehmer":
    if st.session_state.admin_eingeloggt:
        seite_teilnehmer()
    else:
        st.warning("🔐 Bitte zuerst einloggen.")
elif seite == "statistik":
    if st.session_state.admin_eingeloggt:
        seite_statistik()
    else:
        st.warning("🔐 Bitte zuerst einloggen.")
      
