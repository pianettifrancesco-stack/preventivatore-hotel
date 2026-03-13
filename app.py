import streamlit as st
import pandas as pd
from datetime import date

# PAGE CONFIGURATION
st.set_page_config(page_title="Hotel AI Quote Generator", layout="wide")

# PUBLIC CSV LINK
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2cZ1oYAvs5JmpKNvuBIFj-RgXRCBnyfrujMM6Wej5lphqpTGU27Yd2gmH9XeBhzl3bjEo_OHLW0OW/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_pricing_data(url):
    try:
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def get_season(checkin_date):
    """Determines the season based on the check-in date."""
    month = checkin_date.month
    day = checkin_date.day
    
    # TOP SEASON: Dec 21 - Jan 06
    if (month == 12 and day >= 21) or (month == 1 and day <= 6):
        return "Top"
    # LOW SEASON: May 01 - July 31
    elif 5 <= month <= 7:
        return "Low"
    # MEDIUM SEASON: Everything else
    else:
        return "Mid"

df_raw = load_pricing_data(URL_FOGLIO)

st.title("🏨 Automated Hotel Quote System")

# --- SECURITY ---
# Ho inserito la password che hai richiesto
password = st.sidebar.text_input("Access Password", type="password")
if password != "Rafiki15":
    st.warning("Please enter the correct password to access the system.")
    st.stop()

if df_raw is not None:
    # --- SIDEBAR: STAY DETAILS ---
    st.sidebar.header("Stay Details")
    
    currency = st.sidebar.selectbox("Currency", ["EURO", "DOLLAR"])
    is_agency = st.sidebar.toggle("Agency Rate?", value=False)
    
    # DATE SELECTION
    today = date.today()
    col_in, col_out = st.sidebar.columns(2)
    with col_in:
        checkin = st.date_input("Check-in date", today)
    with col_out:
        checkout = st.date_input("Check-out date", today.replace(day=today.day+1) if today.day < 28 else today)
    
    n_nights = (checkout - checkin).days
    if n_nights <= 0:
        st.sidebar.error("Check-out must be after check-in.")
        st.stop()
    
    # AUTO SEASON DETECTION
    season = get_season(checkin)
    st.sidebar.info(f"Detected Season: **{season}**")

    # --- PRICING LOGIC ---
    if currency == "EURO":
        symbol = "€"
        if is_agency:
            prices = {"Standard room": [160, 185, 380], "Superior": [175, 200, 380], "Junior Suite": [210, 230, 420], "Suite": [260, 285, 480]}
            sup_hb, sup_fb = 25, 50
        else:
            prices = {"Standard room": [215, 250, 480], "Superior": [230, 265, 480], "Junior Suite": [275, 310, 520], "Suite": [345, 380, 600]}
            sup_hb, sup_fb = 35, 70
    else:
        symbol = "$"
        if is_agency:
            prices = {"Standard room": [185, 215, 440], "Superior": [200, 230, 440], "Junior Suite": [240, 270, 480], "Suite": [300, 330, 560]}
            sup_hb, sup_fb = 30, 60
        else:
            prices = {"Standard room": [250, 290, 550], "Superior": [270, 310, 550], "Junior Suite": [320, 360, 600], "Suite": [400, 440, 700]}
            sup_hb, sup_fb = 40, 80

    # --- OTHER INPUTS ---
    room_type = st.sidebar.selectbox("Room Category", list(prices.keys()))
    n_rooms = st.sidebar.number_input("Number of Rooms", min_value=1, value=1)
    n_pax_total = st.sidebar.number_input("Total Number of People", min_value=1, value=2)
    meal_plan = st.sidebar.radio("Meal Plan", ["BB", "HB", "FB"])

    # --- CALCULATION ---
    col_idx = 0 if season == "Low" else (1 if season == "Mid" else 2)
    base_room_price = prices[room_type][col_idx]

    meal_supplement = 0
    if season == "Top":
        if meal_plan == "FB": meal_supplement = sup_fb - sup_hb
        else: meal_supplement = 0
    else:
        if meal_plan == "HB": meal_supplement = sup_hb
        elif meal_plan == "FB": meal_supplement = sup_fb

    total_rooms = (base_room_price * n_rooms)
    total_meals = (meal_supplement * n_pax_total)
    grand_total = (total_rooms + total_meals) * n_nights

    # --- DISPLAY ---
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📊 Quote Summary")
        st.write(f"**Stay:** {checkin} to {checkout} ({n_nights} nights)")
        st.write(f"**Season:** {season} Season")
        st.metric("Total Base Price", f"{symbol} {grand_total:,.2f}")

    with c2:
        st.subheader("🤖 Final Quotation")
        discount = st.number_input("Special Discount (%)", 0.0, 100.0, 0.0, 0.5)
        final_price = grand_total * (1 - discount/100)
        
        # Etichetta dinamica basata su Agency o Direct
        label_prezzo = "Net Agency Rate" if is_agency else "Total Amount"
        
        final_text = f"""Dear {'Partner' if is_agency else 'Guest'},

We are pleased to offer you the following quotation for your upcoming stay:

🏨 Accommodation: {n_rooms} {room_type}
📅 Period: from {checkin} to {checkout} ({n_nights} nights)
🍽 Meal Plan: {meal_plan}
👥 Occupancy: {n_pax_total} person(s)

✅ {label_prezzo}: {symbol} {final_price:,.2f}

(Standard list rate: {symbol}{grand_total:,.2f})

We look forward to hearing from you. 
Best regards."""

        st.text_area("Copy and send via Email/WhatsApp:", final_text, height=300)