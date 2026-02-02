import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
# 'History' फाइल का उपयोग करें ताकि पुराना डेटा ओवरराइट न हो
DB_FILE = "ram_seva_history.csv"
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

# 2026 त्यौहार डेटा
CAL_DATA_2026 = {
    "January": {"gap": 3, "days": 31, "events": {14: ("षटतिला एकादशी", "मकर संक्रांति"), 29: ("जया एकादशी", "मोक्ष प्रदायिनी")}},
    "February": {"gap": 6, "days": 28, "events": {13: ("विजया एकादशी", "विजय प्राप्ति"), 27: ("आमलकी एकादशी", "शिवरात्रि")}},
    "March": {"gap": 6, "days": 31, "events": {14: ("पापमोचिनी एकादशी", "पापनाशिनी"), 26: ("राम नवमी", "जन्मोत्सव"), 29: ("कामदा एकादशी", "कामना पूर्ति")}},
    "April": {"gap": 2, "days": 30, "events": {2: ("Hanuman jayanti", "Chaitra Purnima"), 13: ("वरुथिनी एकादशी", "सौभाग्य"), 27: ("मोहनी एकादशी", "मोह नाशिनी")}},
    "May": {"gap": 4, "days": 31, "events": {12: ("अपरा एकादशी", "अपार पुण्य"), 27: ("निर्जला एकादशी", "भीमसेनी व्रत")}},
    "June": {"gap": 0, "days": 30, "events": {11: ("योगिनी एकादशी", "काया शोधन"), 25: ("Nirjala Ekadashi", "Bhim Ekadashi")}},
    "July": {"gap": 2, "days": 31, "events": {10: ("कामिका एकादशी", "संकट नाशिनी"), 25: ("Deva Shayani Ekadashi", "Ashadhi Ekadashi")}},
    "August": {"gap": 5, "days": 31, "events": {9: ("अजा एकादशी", "पुण्य प्रदायिनी"), 23: ("Shravana Putrada Ekadashi", "Progeny Luck"), 28: ("Raksha Bandhan", "Shravana Purnima")}},
    "September": {"gap": 1, "days": 30, "events": {4: ("Janmashtami", "Krishna Janm"), 22: ("Parivartini Ekadashi", "Vishnu side-turn")}},
    "October": {"gap": 3, "days": 31, "events": {6: ("Rama Ekadashi", "Diwali Prep"), 20: ("Dussehra", "Vijayadashami"), 22: ("Papankusha Ekadashi", "Shield from Sins")}},
    "November": {"gap": 6, "days": 30, "events": {8: ("Diwali", "Laxmi Pujan"), 20: ("Devutthana Ekadashi", "Tulsi Vivah"), 24: ("Kartik Purnima", "Dev Diwali")}},
    "December": {"gap": 1, "days": 31, "events": {4: ("Utpanna Ekadashi", "Birth of Ekadashi"), 20: ("Mokshada Ekadashi", "Gita Jayanti"), 23: ("Dattatreya Jayanti", "Margashirsha Purnima")}}
}

def load_db():
    cols = ["Date", "Phone", "Name", "Mala", "Jaap", "Location"]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'Phone': str})
    return pd.DataFrame(columns=cols)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_broadcast():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, "r", encoding="utf-8") as f: return f.read()
    return ""

def save_broadcast(msg):
    with open(MSG_FILE, "w", encoding="utf-8") as f: f.write(msg)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
    except: return "India"

# --- UI CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.4);
    }
    .metric-box { background: white; padding: 50px 20px; border-radius: 30px; text-align: center; border-top: 10px solid #FFD700; margin-bottom: 25px; }
    .calendar-container { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; background: white; padding: 20px; border-radius: 20px; }
    .date-box { aspect-ratio: 1; border: 1px solid #f8f8f8; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
    .event-day { background: #FFF5E6; border: 1.5px solid #FF9933; color: #FF4D00; font-weight: bold; cursor: pointer; }
    .hover-msg { visibility: hidden; width: 140px; background: #3e2723; color: white; text-align: center; border-radius: 8px; padding: 8px; position: absolute; bottom: 120%; left: 50%; margin-left: -70px; opacity: 0; transition: 0.3s; font-size: 10px; z-index: 100; }
    .date-box:hover .hover-msg { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम")
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
    if st.button("प्रवेश करें", use_container_width=True):
        if len(u_phone) == 10 and u_name:
            st.session_state.user_session = u_phone
            st.session_state.user_name = u_name
            st.rerun()

# --- DASHBOARD ---
else:
    u_phone = st.session_state.user_session
    u_name = st.session_state.user_name
    
    # कैलकुलेशन (History से)
    user_history = df[df['Phone'] == u_phone]
    today_mala = user_history[user_history['Date'] == today_str]['Mala'].sum()
    total_mala = user_history['Mala'].sum()

    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {u_name}</div></div>', unsafe_allow_html=True)
    
    b_msg = get_broadcast()
    if b_msg: st.info(f"📢 सन्देश: {b_msg}")
    
    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        st.markdown(f"""
            <div class="metric-box">
                <h1 style='color:#FF4D00; margin:0; font-size: 4rem;'>{int(today_mala)} माला</h1>
                <p style='color:#666; font-weight: bold;'>आज की सेवा ({today_str})</p>
                <hr style='border: 0.5px solid #eee;'>
                <h3 style='color:#FF9933;'>कुल सेवा (Lifetime): {int(total_mala)} माला</h3>
            </div>
        """, unsafe_allow_html=True)
        
        val = st.number_input("माला की संख्या जोड़ें (1 माला = 108 जाप):", min_value=0, step=1)
        if st.button("➕ सेवा जमा करें", use_container_width=True):
            if val > 0:
                loc = get_user_location()
                new_entry = {"Date": today_str, "Phone": u_phone, "Name": u_name, "Mala": val, "Jaap": val * 108, "Location": loc}
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_db(df)
                st.success("सेवा दर्ज कर ली गई है!")
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 टॉप सेवक (Life Time)")
        # ग्रुपिंग ताकि कल और आज का डेटा जुड़ जाए
        leaders = df.groupby(['Phone', 'Name', 'Location'])['Mala'].sum().reset_index()
        leaders = leaders.sort_values(by="Mala", ascending=False).head(15)
        for i, row in leaders.iterrows():
            rank = leaders.index.get_loc(i) + 1
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "💠"
            st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span>{medal}</span>
                        <div><b>{row['Name']}</b><br><small>📍 {row['Location']}</small></div>
                    </div>
                    <div style="color:#FF4D00; font-weight:bold; font-size:1.2rem;">{int(row['Mala'])} कुल माला</div>
                </div>
            """, unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        selected_m = st.selectbox("महीना चुनें:", list(CAL_DATA_2026.keys()), index=datetime.now().month-1)
        m_info = CAL_DATA_2026[selected_m]
        cols = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            cols[i].markdown(f"<div style='text-align:center; font-weight:bold; color:#FF4D00;'>{d}</div>", unsafe_allow_html=True)
        grid_html = '<div class="calendar-container">'
        for _ in range(m_info["gap"]): grid_html += '<div class="date-box" style="border:none; opacity:0;"></div>'
        for d in range(1, m_info["days"] + 1):
            ev = m_info["events"].get(d)
            pk = "पूर्णिमा" if d == 15 else "अमावस्या" if d == m_info["days"] else ("शुक्ल" if d < 15 else "कृष्ण")
            cls = "event-day" if ev else ""
            msg = f'<div class="hover-msg"><b>{ev[0]}</b><br>{ev[1]}</div>' if ev else ""
            grid_html += f'<div class="date-box {cls}">{d}<div style="font-size:0.55rem; color:#888;">{pk}</div>{msg}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- ADMIN SIDEBAR ---
    if u_phone in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download (All History)", data=csv, file_name=f'ram_seva_full_history.csv', use_container_width=True)
            
            st.divider()
            new_m = st.text_area("ब्रॉडकास्ट:", value=get_broadcast())
            if st.button("📢 अपडेट करें"):
                save_broadcast(new_m)
                st.rerun()

    if st.sidebar.button("Logout 🚪"):
        st.session_state.user_session = None
        st.rerun()
