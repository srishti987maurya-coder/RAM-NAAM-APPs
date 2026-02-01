import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

def load_db():
    required = ["Phone", "Name", "Total_Jaap", "Total_Mala", "Last_Active", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Jaap" in col or "Mala" in col else "Unknown"
            return df
        except: pass
    return pd.DataFrame(columns=required)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_broadcast():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, "r", encoding="utf-8") as f: return f.read()
    return ""

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        return f"{response.json().get('city', 'Unknown')}, {response.json().get('region', 'Unknown')}"
    except: return "India"

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .cal-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding: 10px 0; }
    .cal-card {
        width: 82px; height: 82px; background: white; border: 1.5px solid #FF9933;
        border-radius: 12px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative;
    }
    .cal-card:hover { background: #FF4D00 !important; color: white !important; transform: scale(1.1); }
    .tooltip {
        visibility: hidden; width: 170px; background: #3e2723; color: white !important;
        text-align: center; border-radius: 8px; padding: 8px; position: absolute;
        bottom: 115%; left: 50%; margin-left: -85px; opacity: 0; transition: 0.3s; font-size: 10px;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN FIX ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("अपना नाम लिखें").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    
    if st.button("प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            # यदि नंबर नया है, तो रजिस्टर करें
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, 0, today_str, 0, get_user_location()]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
        else:
            st.error("❌ कृपया नाम और 10 अंकों का नंबर भरें।")

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    # Broadcast
    msg = get_broadcast()
    if msg: st.warning(f"📢 {msg}")

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        # आज का डेटा रीसेट करना यदि दिन बदल गया हो
        if df.at[user_idx, 'Last_Active'] != today_str:
            df.at[user_idx, 'Today_Jaap'] = 0
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)

        today_jap = int(df.at[user_idx, 'Today_Jaap'])
        st.subheader("📝 सेवा दर्ज या संशोधित करें")
        st.info(f"आज की वर्तमान सेवा: {today_jap // 108} माला ({today_jap} जाप)")
        
        mode = st.radio("इनपुट टाइप:", ["माला (108)", "जाप (Individual)"], horizontal=True)
        # Edit Feature: Pre-fill with existing count
        default_val = today_jap // 108 if "माला" in mode else today_jap
        val = st.number_input("संख्या बदलें (मिटाने के लिए 0 लिखें):", min_value=0, step=1, value=default_val)
        
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if "माला" in mode else val
            new_mala = val if "माला" in mode else val // 108
            
            # Update Logic: Subtract old today count and add new one
            df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - today_jap) + new_jap
            df.at[user_idx, 'Total_Mala'] = (df.at[user_idx, 'Total_Mala'] - (today_jap // 108)) + new_mala
            df.at[user_idx, 'Today_Jaap'] = new_jap
            save_db(df)
            st.success("डेटा अपडेट हो गया!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        st.table(leaders[['Name', 'Today_Jaap']])

    with tabs[2]:
        st.subheader("📅 उत्सव एवं एकादशी 2026")
        events = [
            ("14 Jan", "मकर संक्रांति"), ("14 Jan", "षटतिला एकादशी"),
            ("15 Feb", "महाशिवरात्रि"), ("28 Feb", "आमलकी एकादशी"),
            ("27 Mar", "राम नवमी"), ("14 Apr", "वरुथिनी एकादशी")
        ]
        grid_html = '<div class="cal-grid">'
        for d, n in events:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip">{n}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
