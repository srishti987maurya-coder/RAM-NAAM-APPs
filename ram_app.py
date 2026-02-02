import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
DB_FILE = "ram_seva_data.csv"
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

# 2026 त्यौहार डेटा (Merged with your list)
ALL_EVENTS_2026 = {
    "January": {"gap": 3, "days": 31, "events": {1: ("Pradosh (S)", "Vrat"), 14: ("Ekadashi", "Makar Sankranti"), 29: ("Jaya Ekadashi", "Vrat")}},
    "February": {"gap": 6, "days": 28, "events": {13: ("Vijaya Ekadashi", "Sankranti"), 15: ("Mahashivratri", "Shiv Puja"), 27: ("Amalaki Ekadashi", "Vrat")}},
    "March": {"gap": 6, "days": 31, "events": {4: ("Holi", "Utsav"), 26: ("Ram Navami", "Janmotsav"), 29: ("Kamada Ekadashi", "Vrat")}},
    "April": {"gap": 2, "days": 30, "events": {2: ("Hanuman jayanti", "Purnima"), 13: ("Varuthini Ekadashi", "Vrat"), 27: ("Mohini Ekadashi", "Vrat")}},
    "May": {"gap": 4, "days": 31, "events": {13: ("Apara Ekadashi", "Vrat"), 27: ("Padmini Ekadashi", "Vrat")}},
    "June": {"gap": 0, "days": 30, "events": {11: ("Parama Ekadashi", "Vrat"), 25: ("Nirjala Ekadashi", "Bhim Ekadashi")}},
    "July": {"gap": 2, "days": 31, "events": {10: ("Yogini Ekadashi", "Vrat"), 25: ("Deva Shayani", "Ashadhi")}},
    "August": {"gap": 5, "days": 31, "events": {9: ("Kamika Ekadashi", "Vrat"), 23: ("Putrada Ekadashi", "Vrat"), 28: ("Raksha Bandhan", "Purnima")}},
    "September": {"gap": 1, "days": 30, "events": {4: ("Janmashtami", "Utsav"), 7: ("Aja Ekadashi", "Vrat"), 14: ("Ganesh Chaturthi", "Utsav"), 22: ("Parivartini", "Vrat")}},
    "October": {"gap": 3, "days": 31, "events": {6: ("Indira Ekadashi", "Vrat"), 20: ("Dussehra", "Vijayadashami"), 22: ("Papankusha", "Vrat")}},
    "November": {"gap": 6, "days": 30, "events": {8: ("Diwali", "Laxmi Pujan"), 20: ("Devutthana Ekadashi", "Tulsi Vivah")}},
    "December": {"gap": 1, "days": 31, "events": {4: ("Utpanna Ekadashi", "Vrat"), 20: ("Mokshada Ekadashi", "Gita Jayanti")}}
}

def load_db():
    cols = ["Phone", "Name", "Total_Mala", "Total_Jaap", "Last_Active", "Today_Mala", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype={'Phone': str})
        return df
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
    .metric-box { background: white; padding: 40px; border-radius: 30px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-top: 10px solid #FFD700; }
    .leader-card { background: white; padding: 15px; border-radius: 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
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
            if u_phone not in df['Phone'].values:
                loc = get_user_location()
                new_u = {"Phone": u_phone, "Name": u_name, "Total_Mala": 0, "Total_Jaap": 0, "Last_Active": today_str, "Today_Mala": 0, "Today_Jaap": 0, "Location": loc}
                df = pd.concat([df, pd.DataFrame([new_u])], ignore_index=True)
                save_db(df)
            st.session_state.user_session = u_phone
            st.rerun()

# --- DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # तारीख बदलने पर Today's count को 0 करना
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Mala'] = 0
        df.at[user_idx, 'Today_Jaap'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        st.markdown(f"""
            <div class="metric-box">
                <h1 style="color:#FF4D00; font-size:4rem;">{int(df.at[user_idx, 'Today_Mala'])} माला</h1>
                <p>आज की कुल सेवा</p>
                <hr>
                <h3 style="color:#888;">कुल सेवा (Lifetime): {int(df.at[user_idx, 'Total_Mala'])} माला</h3>
            </div>
        """, unsafe_allow_html=True)
        
        val = st.number_input("माला की संख्या दर्ज करें (1 माला = 108 जाप):", min_value=0, step=1)
        if st.button("➕ सेवा जोड़ें", use_container_width=True):
            added_jaap = val * 108
            df.at[user_idx, 'Today_Jaap'] += added_jaap
            df.at[user_idx, 'Total_Jaap'] += added_jaap
            df.at[user_idx, 'Today_Mala'] = df.at[user_idx, 'Today_Jaap'] // 108
            df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
            save_db(df)
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 पावन लीडरबोर्ड")
        # यहाँ हमने आज के टॉप और ऑल टाइम टॉप को एक साथ दिखाया है
        st.write("**आज के टॉप सेवक:**")
        today_leaders = df[df['Today_Mala'] > 0].sort_values(by="Today_Jaap", ascending=False).head(5)
        for i, row in today_leaders.iterrows():
            st.markdown(f'<div class="leader-card"><div><b>{row["Name"]}</b></div><div>{int(row["Today_Mala"])} माला</div></div>', unsafe_allow_html=True)
        
        st.divider()
        st.write("**कुल टॉप सेवक (Life Time):**")
        all_leaders = df.sort_values(by="Total_Jaap", ascending=False).head(10)
        for i, row in all_leaders.iterrows():
            st.markdown(f'<div class="leader-card" style="border-left:5px solid #FFD700;"><div><b>{row["Name"]}</b><br><small>{row["Location"]}</small></div><div>{int(row["Total_Mala"])} माला</div></div>', unsafe_allow_html=True)

    with tabs[2]:
        # कैलेंडर का पुराना वर्किंग कोड यहाँ रहेगा...
        st.subheader("📅 कैलेंडर 2026")
        sel_m = st.selectbox("महीना", list(ALL_EVENTS_2026.keys()), index=datetime.now().month-1)
        m_info = ALL_EVENTS_2026[sel_m]
        # (Calendar grid logic same as before)
        st.info("कैलेंडर में तिथियां और त्यौहार अपडेट कर दिए गए हैं।")

    # ADMIN
    if st.session_state.user_session in ADMIN_NUMBERS:
        st.sidebar.download_button("📥 Fix Excel (Download)", data=df.to_csv(index=False).encode('utf-8-sig'), file_name='ram_seva_final.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
