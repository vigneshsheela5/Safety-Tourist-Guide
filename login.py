import streamlit as st
import sqlite3
import hashlib
import random
import string

st.set_page_config(page_title="Tourist Guardian", layout="centered")

# --- DATABASE LOGIC ---
def hash_pass(password): return hashlib.sha256(str.encode(password)).hexdigest()

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Schema: ID, Password, FullName, Phone (starts as None)
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT UNIQUE, password TEXT, fullname TEXT, phone TEXT)')
    conn.commit()
    conn.close()

def add_user(username, password, fullname):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users(username, password, fullname, phone) VALUES (?,?,?,?)', 
                  (username, hash_pass(password), fullname, None))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT fullname, phone FROM users WHERE username = ? AND password = ?', (username, hash_pass(password)))
    data = c.fetchone()
    conn.close()
    return data

# --- CYBER UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #020617; color: white; }
    .main-title { font-size: 45px; color: #00ffcc; text-align: center; font-family: monospace; text-shadow: 0 0 15px #00ffcc; font-weight: bold; }
    .sub-text { text-align: center; color: #94a3b8; font-family: monospace; margin-bottom: 30px; }
    .success-card { background: rgba(0, 255, 204, 0.1); border: 1px solid #00ffcc; padding: 25px; border-radius: 15px; text-align: center; margin-top: 20px; }
    div.stButton > button { width: 100%; background: transparent; color: #00ffcc; border: 2px solid #00ffcc; font-weight: bold; height: 50px; font-family: monospace; }
    div.stButton > button:hover { background: #00ffcc !important; color: #020617 !important; box-shadow: 0 0 20px #00ffcc; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [aria-selected="true"] { color: #00ffcc !important; border-bottom: 2px solid #00ffcc !important; }
    </style>
""", unsafe_allow_html=True)

init_db()
st.markdown('<div class="main-title">🛡️Tourist Guardian</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Tourist Safety</div>', unsafe_allow_html=True)

tab_login, tab_signup = st.tabs(["🔐LOGIN", "🆔 SIGN UP"])

with tab_login:
    l_id = st.text_input("ENTER UNIQUE ID (GRD-XXXXX)")
    l_pass = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        data = login_user(l_id, l_pass)
        if data:
            st.session_state.update({"logged_in": True, "username": l_id, "fullname": data[0], "phone": data[1]})
            st.switch_page("pages/dashboard4.py")
        else: st.error("ACCESS DENIED")

with tab_signup:
    s_name = st.text_input("FULLNAME")
    s_pass = st.text_input("PASSWORD", type="password")
    
    if st.button("GENERATE SECURITY IDENTITY"):
        if s_name and s_pass:
            new_id = "GRD-" + ''.join(random.choices(string.digits, k=5))
            if add_user(new_id, s_pass, s_name):
                st.markdown(f"""
                    <div class="success-card">
                        <h3 style="color:#00ffcc;">ENROLLMENT SUCCESSFUL</h3>
                        <p style="color:#94a3b8;">Welcome, {s_name}. Your Unique ID is:</p>
                        <h1 style="color:#ffffff; letter-spacing: 5px;">{new_id}</h1>
                        <p style="font-size:13px; color:#ef4444;">SAVE THIS ID TO ACCESS THE GRID.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()
            else: st.error("DATABASE COLLISION. RETRYING...")
        else: st.warning("ALL FIELDS REQUIRED FOR ENROLLMENT")