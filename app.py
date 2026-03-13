import streamlit as st
import pandas as pd

# CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Hotel Booking System", layout="wide")

# LINK CSV PUBBLICO
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2cZ1oYAvs5JmpKNvuBIFj-RgXRCBnyfrujMM6Wej5lphqpTGU27Yd2gmH9XeBhzl3bjEo_OHLW0OW/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def carica_listino(url):
    try:
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"Errore di connessione al foglio: {e}")
        return None

df_raw = carica_listino(URL_FOGLIO)

st.title("🏨 Preventivatore Professional con Opzione Agency")

if df_raw is not None:
    # --- SIDEBAR: PARAMETRI DI INPUT ---
    st.sidebar.header("Dati Soggiorno")
    
    valuta = st.sidebar.selectbox("Valuta", ["EURO", "DOLLAR"])
    is_agency = st.sidebar.toggle("È un'Agenzia?", value=False)
    
    # --- LOGICA SELEZIONE LISTINO ---
    # Definiamo i prezzi in base a Valuta + Agency (dati presi dal tuo screenshot)
    if valuta == "EURO":
        simbolo = "€"
        if is_agency:
            # INTERNATIONAL AGENCY EURO
            prezzi = {
                "Standard room": [160, 185, 380],
                "Superior": [175, 200, 380],
                "Junior Suite": [210, 230, 420],
                "Suite": [260, 285, 480]
            }
            sup_hb, sup_fb = 25, 50
        else:
            # INTERNATIONAL EURO (Direct)
            prezzi = {
                "Standard room": [215, 250, 480],
                "Superior": [230, 265, 480],
                "Junior Suite": [275, 310, 520],
                "Suite": [345, 380, 600]
            }
            sup_hb, sup_fb = 35, 70
    else:
        simbolo = "$"
        if is_agency:
            # INTERNATIONAL AGENCY DOLLAR (Rif. blocco 185-215-440)
            prezzi = {
                "Standard room": [185, 215, 440],
                "Superior": [200, 230, 440],
                "Junior Suite": [240, 270, 480],
                "Suite": [300, 330, 560]
            }
            sup_hb, sup_fb = 30, 60
        else:
            # INTERNATIONAL DOLLAR (Rif. blocco 250-290-550)
            prezzi = {
                "Standard room": [250, 290, 550],
                "Superior": [270, 310, 550],
                "Junior Suite": [320, 360, 600],
                "Suite": [400, 440, 700]
            }
            sup_hb, sup_fb = 40, 80

    # --- SELEZIONE INPUT ---
    tipo_camera = st.sidebar.selectbox("Tipologia Camera", list(prezzi.keys()))
    n_camere = st.sidebar.number_input("Numero di Camere", min_value=1, value=1, step=1)
    stagione = st.sidebar.select_slider("Stagionalità", options=["Low", "Mid", "Top"])
    n_notti = st.sidebar.number_input("Numero di Notti", min_value=1, value=1)
    n_persone_tot = st.sidebar.number_input("Numero Persone Totali", min_value=1, value=2)
    trattamento = st.sidebar.radio("Trattamento", ["BB", "HB", "FB"])

    # --- LOGICA DI CALCOLO ---
    col_idx = 0 if stagione == "Low" else (1 if stagione == "Mid" else 2)
    prezzo_camera_notte = prezzi[tipo_camera][col_idx]

    supplemento_persona = 0
    if stagione == "Top":
        if trattamento == "FB":
            supplemento_persona = sup_fb - sup_hb
        else:
            supplemento_persona = 0
    else:
        if trattamento == "HB":
            supplemento_persona = sup_hb
        elif trattamento == "FB":
            supplemento_persona = sup_fb

    totale_camere = (prezzo_camera_notte * n_camere)
    totale_pasti = (supplemento_persona * n_persone_tot)
    totale_soggiorno = (totale_camere + totale_pasti) * n_notti

    # --- VISUALIZZAZIONE ---
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        tipo_cliente = "AGENZIA" if is_agency else "DIRETTO"
        st.subheader(f"📊 Preventivo {tipo_cliente}")
        st.write(f"**Listino:** {valuta} - {tipo_cliente}")
        st.write(f"**Camera:** {n_camere}x {tipo_camera} ({stagione})")
        
        st.metric("Totale Lordo", f"{simbolo} {totale_soggiorno:,.2f}")

    with c2:
        st.subheader("🤖 Generazione Offerta")
        valore_sconto = st.number_input("Sconto (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
        prezzo_finale = totale_soggiorno * (1 - valore_sconto/100)
        
        testo_offerta = f"""Gentile {'Partner' if is_agency else 'Ospite'},
abbiamo il piacere di inviarvi la quotazione richiesta:

🏨 Sistemazione: {n_camere} {tipo_camera}
🌙 Durata: {n_notti} notti
🍽 Trattamento: {trattamento}
👥 Occupazione: {n_persone_tot} persone

Prezzo totale: {simbolo} {prezzo_finale:,.2f}
{'Netto Agenzia' if is_agency else 'Prezzo Finale'}

Restiamo a disposizione per la conferma."""

        st.text_area("Testo da copiare:", testo_offerta, height=250)