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
        "✅ Ich stimme der Verarbeitung der Daten meines Kindes zu. "
        "Die Daten werden ausschließlich für die Auswertung verwendet "
        "und nach 6 Monaten gelöscht. *",
        value=False
    )
    abschicken = st.form_submit_button("🎽 Jetzt anmelden!", use_container_width=True)

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
        fehler.append("Schulklasse muss eine Zahl enthalten (z.B. 2b)")

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
