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

# 2026 एकादशी एवं त्यौहार सम्पूर्ण डेटा (Updated with your list)
ALL_EVENTS_2026 = {
    "January": {"gap": 3, "days": 31, "events": {1: ("Pradosh Vrat (S)", "Trayodashi"), 3: ("Paush Purnima", "Vrat"), 6: ("Sankashti Chaturthi", "Ganesh Pujan"), 14: ("Shattila Ekadashi", "Makar Sankranti"), 16: ("Pradosh Vrat (K)", "Shivaratri"), 18: ("Magha Amavasya", "Mauni"), 23: ("Basant Panchmi", "Saraswati Puja"), 29: ("Jaya Ekadashi", "Bhami Ekadashi"), 30: ("Pradosh Vrat (S)", "Trayodashi")}},
    "February": {"gap": 6, "days": 28, "events": {1: ("Magha Purnima", "Vrat"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"), 13: ("Vijaya Ekadashi", "Kumbha Sankranti"), 14: ("Pradosh Vrat (K)", "Vrat"), 15: ("Mahashivratri", "Shivaratri"), 17: ("Phalguna Amavasya", "Vrat"), 27: ("Amalaki Ekadashi", "Vrat"), 28: ("Pradosh Vrat (S)", "Vrat")}},
    "March": {"gap": 6, "days": 31, "events": {3: ("Holika Dahan", "Purnima"), 4: ("Holi", "Colors"), 6: ("Sankashti Chaturthi", "Ganesh Pujan"), 15: ("Papmochani Ekadashi", "Sankranti"), 16: ("Pradosh Vrat (K)", "Vrat"), 17: ("Masik Shivaratri", "Vrat"), 19: ("Gudi Padwa", "Navratri Aarambh"), 26: ("Ram Navami", "Janmotsav"), 29: ("Kamada Ekadashi", "Vrat"), 30: ("Pradosh Vrat (S)", "Vrat")}},
    "April": {"gap": 2, "days": 30, "events": {2: ("Hanuman jayanti", "Purnima"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"), 13: ("Varuthini Ekadashi", "Vrat"), 14: ("Mesha Sankranti", "Solar New Year"), 19: ("Akshaya Tritiya", "Punya Day"), 27: ("Mohini Ekadashi", "Vrat"), 28: ("Pradosh Vrat (S)", "Vrat")}},
    "May": {"gap": 4, "days": 31, "events": {1: ("Vaishakha Purnima", "Vrat"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"), 13: ("Apara Ekadashi", "Vrat"), 14: ("Pradosh Vrat (K)", "Vrat"), 16: ("Jyeshtha Amavasya", "Vrat"), 27: ("Padmini Ekadashi", "Vrat"), 28: ("Pradosh Vrat (S)", "Vrat"), 31: ("Purnima Vrat", "Vrat")}},
    "June": {"gap": 0, "days": 30, "events": {3: ("Sankashti Chaturthi", "Ganesh Pujan"), 11: ("Parama Ekadashi", "Vrat"), 12: ("Pradosh Vrat (K)", "Vrat"), 15: ("Amavasya", "Sankranti"), 25: ("Nirjala Ekadashi", "Bhim Ekadashi"), 27: ("Pradosh Vrat (S)", "Vrat"), 29: ("Jyeshtha Purnima", "Vrat")}},
    "July": {"gap": 2, "days": 31, "events": {3: ("Sankashti Chaturthi", "Ganesh Pujan"), 10: ("Yogini Ekadashi", "Vrat"), 12: ("Masik Shivaratri", "Vrat"), 14: ("Ashadha Amavasya", "Deep Puja"), 16: ("Jagannath Rath Yatra", "Sankranti"), 25: ("Deva Shayani Ekadashi", "Ashadhi"), 29: ("Guru Purnima", "Purnima")}},
    "August": {"gap": 5, "days": 31, "events": {2: ("Sankashti Chaturthi", "Ganesh Pujan"), 9: ("Kamika Ekadashi", "Vrat"), 12: ("Shravana Amavasya", "Vrat"), 15: ("Hariyali Teej", "Vrat"), 17: ("Nag Panchami", "Sankranti"), 23: ("Shravana Putrada Ekadashi", "Vrat"), 28: ("Raksha Bandhan", "Purnima"), 31: ("Kajari Teej", "Vrat")}},
    "September": {"gap": 1, "days": 30, "events": {4: ("Janmashtami", "Krishna Janm"), 7: ("Aja Ekadashi", "Vrat"), 14: ("Ganesh Chaturthi", "Utsav"), 22: ("Parivartini Ekadashi", "Vrat"), 25: ("Anant Chaturdashi", "Visarjan"), 26: ("Bhadrapada Purnima", "Shradh Start")}},
    "October": {"gap": 3, "days": 31, "events": {6: ("Indira Ekadashi", "Vrat"), 10: ("Ashwin Amavasya", "Shradh End"), 11: ("Sharad Navratri", "Ghatasthapana"), 19: ("Durga Ashtami", "Maha Navami"), 20: ("Dussehra", "Vijayadashami"), 22: ("Papankusha Ekadashi", "Vrat"), 26: ("Ashwin Purnima", "Sharad Purnima"), 29: ("Karva Chauth", "Vrat")}},
    "November": {"gap": 6, "days": 30, "events": {5: ("Rama Ekadashi", "Vrat"), 6: ("Dhanteras", "Vrat"), 8: ("Diwali", "Laxmi Pujan"), 9: ("Kartik Amavasya", "Vrat"), 10: ("Govardhan Puja", "Utsav"), 11: ("Bhai Dooj", "Utsav"), 20: ("Devutthana Ekadashi", "Tulsi Vivah"), 24: ("Kartik Purnima", "Dev Diwali")}},
    "December": {"gap": 1, "days": 31, "events": {4: ("Utpanna Ekadashi", "Vrat"), 8: ("Margashirsha Amavasya", "Vrat"), 20: ("Mokshada Ekadashi", "Gita Jayanti"), 23: ("Margashirsha Purnima", "Dattatreya Jayanti")}}
}

def load_db():
    cols = ["Phone", "Name", "Total_Mala", "Total_Jaap", "Last_Active", "Today_Mala", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype={'Phone': str})
        for c in cols:
            if c not in df.columns: df[c] = 0 if "Jaap" in c or "Mala" in c else "India"
        return df
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
    .calendar-wrapper { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; background: white; padding: 15px; border-radius: 20px; }
    .date-cell { aspect-ratio: 1; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 500; position: relative; border: 1px solid #f0f0f0; transition: 0.3s; }
    .has-event { background: #FFF5E6; border: 1.5px solid #FF9933; color: #FF4D00; font-weight: bold; }
    .event-tip { visibility: hidden; width: 140px; background: #3e2723; color: white; text-align: center; border-radius: 8px; padding: 8px; position: absolute; bottom: 115%; left: 50%; margin-left: -70px; opacity: 0; transition: 0.3s; font-size: 10px; z-index: 10; }
    .date-cell:hover .event-tip { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- 1. LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम लिखें").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ सही विवरण भरें।")
        else:
            if u_phone in df['Phone'].values:
                st.session_state.user_session = u_phone
                st.rerun()
            else:
                loc = get_user_location()
                st.session_state.user_session = u_phone
                new_u = {"Phone": u_phone, "Name": u_name, "Total_Mala": 0, "Total_Jaap": 0, "Last_Active": today_str, "Today_Mala": 0, "Today_Jaap": 0, "Location": loc}
                df = pd.concat([df, pd.DataFrame([new_u])], ignore_index=True)
                save_db(df)
                st.rerun()
# --- 2. DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    with tabs[0]:
        if df.at[user_idx, 'Last_Active'] != today_str:
            df.at[user_idx, 'Today_Mala'] = 0
            df.at[user_idx, 'Today_Jaap'] = 0
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
        
        cur_j = int(df.at[user_idx, 'Today_Jaap'])
        st.markdown(f'<div class="metric-box"><h1 style="color:#FF4D00; font-size:4rem;">{cur_j // 108} माला</h1><p>आज की कुल सेवा</p></div>', unsafe_allow_html=True)
        
        mode = st.radio("इनपुट तरीका:", ["माला (1 = 108)", "जाप संख्या (सीधा)"], horizontal=True)
        val = st.number_input("संख्या लिखें:", min_value=0, step=1)
        
        if st.button("➕ सेवा जोड़ें", use_container_width=True):
            added = (val * 108) if mode == "माला (1 = 108)" else val
            df.at[user_idx, 'Today_Jaap'] += added
            df.at[user_idx, 'Total_Jaap'] += added
            df.at[user_idx, 'Today_Mala'] = df.at[user_idx, 'Today_Jaap'] // 108
            df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
            save_db(df)
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 जीवन भर के टॉप सेवक")
        # FIX: Showing TOTAL MALA so counts never vanish
        leaders = df.sort_values(by="Total_Jaap", ascending=False).head(10)
        for i, row in leaders.iterrows():
            rank = leaders.index.get_loc(i) + 1
            bg, medal = ("#FFD700", "🥇") if rank == 1 else ("#E0E0E0", "🥈") if rank == 2 else ("#CD7F32", "🥉") if rank == 3 else ("white", "💠")
            st.markdown(f'<div style="background:{bg}; padding:15px; border-radius:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 10px rgba(0,0,0,0.05);"><div style="display:flex; align-items:center; gap:12px;"><span>{medal}</span><div><b>{row["Name"]}</b><br><small>📍 {row["Location"]}</small></div></div><div style="color:#FF4D00; font-weight:bold;">{int(row["Total_Mala"])} कुल माला</div></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        sel_m = st.selectbox("महीना चुनें:", list(ALL_EVENTS_2026.keys()), index=datetime.now().month-1)
        m_info = ALL_EVENTS_2026[sel_m]
        
        cols = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            cols[i].markdown(f"<div style='text-align:center; font-weight:bold; color:#FF4D00;'>{d}</div>", unsafe_allow_html=True)
        
        grid_html = '<div class="calendar-wrapper">'
        for _ in range(m_info["gap"]): grid_html += '<div class="date-cell" style="border:none; opacity:0;"></div>'
        for d in range(1, m_info["days"] + 1):
            ev = m_info["events"].get(d)
            pk = "पूर्णिमा" if d == 15 else "अमावस्या" if d == m_info["days"] else ("शुक्ल" if d < 15 else "कृष्ण")
            cls = "has-event" if ev else ""
            tip = f'<div class="event-tip"><b>{ev[0]}</b><br>{ev[1]}</div>' if ev else ""
            grid_html += f'<div class="date-cell {cls}">{d}<div style="font-size:0.55rem; color:#888;">{pk}</div>{tip}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- ADMIN ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download", data=csv, file_name='ram_data.csv')
            
            inactive = df[df['Last_Active'] != today_str]
            if not inactive.empty:
                st.warning(f"⚠️ {len(inactive)} पेंडिंग")
                rem = st.selectbox("स्मरण भेजें:", ["--चुनें--"] + inactive['Name'].tolist())
                if rem != "--चुनें--":
                    u_row = inactive[inactive['Name'] == rem].iloc[0]
                    msg_u = urllib.parse.quote(f"जय श्री राम {rem} जी! आज की माला सेवा दर्ज करें। 🙏🚩")
                    st.markdown(f'<a href="https://wa.me/91{u_row["Phone"]}?text={msg_u}" target="_blank" style="background:#25D366; color:white; padding:10px; border-radius:10px; text-decoration:none; display:block; text-align:center;">💬 WhatsApp</a>', unsafe_allow_html=True)

    if st.sidebar.button("Logout 🚪"):
        st.session_state.user_session = None
        st.rerun()
