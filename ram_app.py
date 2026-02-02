import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
# अब हम 'History' फाइल का उपयोग करेंगे ताकि हर दिन का रिकॉर्ड अलग रहे
DB_FILE = "ram_seva_history.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

def load_db():
    cols = ["Date", "Phone", "Name", "Mala", "Jaap", "Location"]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'Phone': str})
    return pd.DataFrame(columns=cols)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        return f"{response.json().get('city', 'Unknown')}, India"
    except: return "India"

# --- UI CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .metric-box { background: white; padding: 40px; border-radius: 30px; text-align: center; border-top: 10px solid #FFD700; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .leader-card { background: white; padding: 12px; border-radius: 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
if st.session_state.user_session is None:
    st.markdown("<h1 style='text-align:center;'>🚩 श्री राम धाम</h1>", unsafe_allow_html=True)
    u_name = st.text_input("आपका नाम")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("प्रवेश करें", use_container_width=True):
        if len(u_phone) == 10 and u_name:
            st.session_state.user_session = u_phone
            st.session_state.user_name = u_name
            st.rerun()
# --- DASHBOARD ---
else:
    u_phone = st.session_state.user_session
    u_name = st.session_state.user_name
    
    # यूजर का आज का और कुल डेटा कैलकुलेट करें
    user_history = df[df['Phone'] == u_phone]
    today_data = user_history[user_history['Date'] == today_str]
    
    today_mala = today_data['Mala'].sum()
    total_mala = user_history['Mala'].sum()

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        st.markdown(f"""
            <div class="metric-box">
                <h1 style="color:#FF4D00; font-size:4rem;">{int(today_mala)} माला</h1>
                <p style="font-weight:bold; color:#666;">आज की सेवा ({today_str})</p>
                <hr>
                <h3 style="color:#FF9933;">कुल सेवा (Lifetime): {int(total_mala)} माला</h3>
            </div>
        """, unsafe_allow_html=True)
        
        val = st.number_input("माला की संख्या जोड़ें (1 माला = 108 जाप):", min_value=0, step=1)
        if st.button("➕ सेवा जमा करें", use_container_width=True):
            if val > 0:
                loc = get_user_location()
                new_entry = {
                    "Date": today_str,
                    "Phone": u_phone,
                    "Name": u_name,
                    "Mala": val,
                    "Jaap": val * 108,
                    "Location": loc
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_db(df)
                st.success("आपकी सेवा सफलतापूर्वक दर्ज की गई!")
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के श्रेष्ठ सेवक")
        # आज के टॉप सेवक
        t_leaders = df[df['Date'] == today_str].groupby(['Name', 'Location'])['Mala'].sum().reset_index()
        t_leaders = t_leaders.sort_values(by="Mala", ascending=False).head(10)
        
        for i, row in t_leaders.iterrows():
            st.markdown(f'<div class="leader-card"><div><b>{row["Name"]}</b></div><div>{int(row["Mala"])} माला</div></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        st.info("कैलेंडर और त्यौहार की जानकारी यहाँ दिखाई देगी।")

    # --- ADMIN SIDEBAR ---
    if u_phone in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन पैनल")
            # एक्सेल में अब हर दिन का अलग रिकॉर्ड दिखेगा
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डाउनलोड सेवा रिपोर्ट (Daily History)", data=csv_data, file_name=f'ram_seva_history_{today_str}.csv', use_container_width=True)
            
            st.divider()
            if st.button("Logout 🚪", use_container_width=True):
                st.session_state.user_session = None
                st.rerun()
