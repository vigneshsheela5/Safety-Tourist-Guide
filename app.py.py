import streamlit as st
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
from geopy.distance import geodesic
import urllib.parse
import requests

# ================== TELEGRAM ==================
BOT_TOKEN = "8619500229:AAHoxspqzLeoyWCtyfQYm6sckgZtuncIieQ"
CHAT_ID = "5597556872"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ================== AUTH ==================
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ ACCESS DENIED")
    st.stop()

st.set_page_config(layout="wide")

# ================== STYLE ==================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#020617,#0f172a);
    color: white;
}
h2 {
    color: #00ffcc;
    text-shadow: 0 0 10px #00ffcc;
}
div.stButton > button {
    width: 100%;
    height: 55px;
    background: #ef4444;
    color: white;
    font-weight: bold;
    border-radius: 10px;
}
.sms-btn {
    background:#f59e0b;
    padding:12px;
    display:block;
    text-align:center;
    border-radius:8px;
    color:black;
    font-weight:bold;
    text-decoration:none;
}
</style>
""", unsafe_allow_html=True)

# ================== PLACE NAME ==================
def get_place_name(lat, lng):
    try:
        geolocator = Nominatim(user_agent="guardian_ai")
        location = geolocator.reverse((lat, lng), language='en')
        
        if location and location.raw.get("address"):
            address = location.raw["address"]
            return (
                address.get("village")
                or address.get("town")
                or address.get("city")
                or address.get("county")
                or "Unknown Location"
            )
        return "Unknown Location"
    except:
        return "Location Error"

# ================== LOCATION ==================
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = 17.3450
    st.session_state.user_lng = 78.3000

lat = st.session_state.user_lat
lng = st.session_state.user_lng
place_name = get_place_name(lat, lng)

# ================== ZONES ==================
ZONES = {
    "WATER": [
        {"name": "OSMAN SAGAR", "coords": [17.3775, 78.3015], "radius": 1600},
        {"name": "HIMAYAT SAGAR", "coords": [17.3195, 78.3541], "radius": 1800}
    ],
    "DANGER": [
        {"name": "MOINABAD", "coords": [17.3211, 78.2736], "radius": 1100},
        {"name": "CHEVELLA", "coords": [17.3075, 78.1365], "radius": 1500},
        {"name": "KISMATPUR", "coords": [17.3486, 78.3712], "radius": 900},
    ]
}

# ================== SMART STATUS ==================
in_danger = False
near_danger = False
in_water = False

for z in ZONES["DANGER"]:
    dist = geodesic([lat, lng], z["coords"]).meters
    if dist < z["radius"]:
        in_danger = True
    elif dist < z["radius"] + 500:
        near_danger = True

for z in ZONES["WATER"]:
    dist = geodesic([lat, lng], z["coords"]).meters
    if dist < z["radius"]:
        in_water = True

# ================== HEADER ==================
st.markdown("## 🛡️ Tourist Guardian")
st.info(f"📍 {place_name} | 🌐 Lat: {lat:.5f} | 📡 Lng: {lng:.5f}")
st.divider()

# ================== LAYOUT ==================
left, right = st.columns([3, 1])

# ================== MAP ==================
with left:
    st.markdown("### 🗺️ LIVE LOCATION")

    m = folium.Map(location=[lat, lng], zoom_start=13, tiles="OpenStreetMap")

    for w in ZONES["WATER"]:
        folium.Circle(
            location=w["coords"],
            radius=w["radius"],
            color='blue',
            fill=True,
            fill_opacity=0.3
        ).add_to(m)

    for d in ZONES["DANGER"]:
        folium.Circle(
            location=d["coords"],
            radius=d["radius"],
            color='red',
            fill=True,
            fill_opacity=0.3
        ).add_to(m)

    folium.CircleMarker(
        [lat, lng],
        radius=12,
        color='green',
        fill=True,
        fill_color='green'
    ).add_to(m)

    folium.Marker(
        [lat, lng],
        popup="📍 YOU",
        icon=folium.Icon(color="green")
    ).add_to(m)

    st_folium(m, height=700, use_container_width=True)

# ================== SIDE PANEL ==================
with right:
    st.subheader("🚨 SOS")

    if st.button("TRIGGER SOS"):
        st.error("🚨 EMERGENCY SIGNAL SENT")

        msg = f"""
🚨 SOS ALERT 🚨
USER: {st.session_state.get('username')}
📍 PLACE: {place_name}
🌐 LAT: {lat}
📡 LNG: {lng}
📌 MAP:
https://maps.google.com/?q={lat},{lng}
"""
        send_telegram(msg)
        st.success("✅ ALERT SENT")

    # ================== AUTO SOS ==================
    if "sos_sent" not in st.session_state:
        st.session_state.sos_sent = False

    if in_danger and not st.session_state.sos_sent:
        msg = f"""
🚨 AUTO SOS ALERT 🚨
USER: {st.session_state.get('username')}
📍 PLACE: {place_name}
🌐 LAT: {lat}
📡 LNG: {lng}
📌 MAP:
https://maps.google.com/?q={lat},{lng}
"""
        send_telegram(msg)
        st.session_state.sos_sent = True

    if not in_danger:
        st.session_state.sos_sent = False

    st.divider()

    # ================== OFFLINE SMS ==================
    st.subheader("📡 DEAD ZONE DEFENSE")
    st.info("Works only on mobile")

    phone = st.session_state.get("phone", "911")

    sms_body = f"SOS! LOCATION: https://maps.google.com/?q={lat},{lng}"
    encoded = urllib.parse.quote(sms_body)

    st.markdown(
        f'<a href="sms:{phone}?body={encoded}" class="sms-btn">📲 SEND SMS SOS</a>',
        unsafe_allow_html=True
    )

    st.divider()

    # ================== STATUS DISPLAY ==================
    if in_danger:
        st.error("🔴 DANGER ZONE")
    elif near_danger:
        st.warning("⚠️ APPROACHING DANGER ZONE")
    elif in_water:
        st.info("🔵 WATER ZONE")
    else:
        st.success("🟢 SAFE ZONE")

# ================== SOUND ALERT ==================
if in_danger or near_danger:
    st.markdown("""
    <audio autoplay>
    <source src="https://www.soundjay.com/buttons/sounds/beep-07.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)