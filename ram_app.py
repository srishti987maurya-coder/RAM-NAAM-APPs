import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
import requests
import urllib.parse

# --- CONFIGURATION ---
# अपनी API Key यहाँ डालें: https://www.fast2sms.com/dashboard/dev-api
API_KEY = "YOUR_FAST2SMS_API_KEY" 

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'Phone': str})
    return pd.DataFrame(columns=["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"])

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def send_otp_sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {"variables_values": otp, "route": "otp", "numbers": phone}
    headers = {"authorization": API_KEY}
    try:
        response = requests.get(url, headers=headers, params=payload, timeout=5)
        return response.json()
    except: return {"return": False}

# --- PREMIUM UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #FFF5E6; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00, #FF9933);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 2rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .sankalp-card {
        background: white; border-radius: 20px; padding: 15px; text-align: center;
        border: 2px solid #FFD700; margin-bottom: 20px;
    }
    .cal-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
    .cal-card {
        width: 85px; height: 85px; background: white; border: 1.5px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.1); z-index: 10; }
    .cal-card:hover b { color: white !important; }
    .tooltip {
        visibility: hidden; width: 180px; background: #3e2723; color: white !important;
        text-align: center; border-radius: 8px; padding: 10px; position: absolute;
        bottom: 115%; left: 50%; margin-left: -90px; opacity: 0; transition: 0.3s; font-size: 11px;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- LOGIN LOGIC ---
if 'user_session' not in st.session_state: st.session_state.user_session = None
if 'otp_step' not in st.session_state: st.session_state.otp_step = "login"

if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>सुरक्षित भक्ति प्रवेश</div></div>', unsafe_allow_html=True)
    
    if st.session_state.otp_step == "login":
        u_name = st.text_input("आपका पावन नाम")
        u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
        if st.button("OTP प्राप्त करें", use_container_width=True):
            if len(u_phone) == 10 and u_phone.isdigit():
                otp = str(random.randint(1000, 9999))
                res = send_otp_sms(u_phone, otp)
                if res.get("return"):
                    st.session_state.generated_otp = otp
                    st.session_state.temp_phone = u_phone
                    st.session_state.temp_name = u_name
                    st.session_state.otp_step = "verify"
                    st.rerun()
                else:
                    st.error("SMS भेजने में विफल। कृपया Fast2SMS पर API Key या बैलेंस चेक करें।")
            else: st.error("सही नंबर डालें।")
            
    else:
        user_otp = st.text_input("4-अंकों का OTP भरें", max_chars=4)
        if st.button("सत्यापित करें", use_container_width=True):
            if user_otp == st.session_state.generated_otp:
                st.session_state.user_session = st.session_state.temp_phone
                if st.session_state.temp_phone not in df['Phone'].values:
                    new_user = pd.DataFrame([[st.session_state.temp_phone, st.session_state.temp_name, 0, today_str, 0, "India"]], columns=df.columns)
                    df = pd.concat([df, new_user], ignore_index=True)
                    save_db(df)
                st.rerun()
            else: st.error("गलत OTP")

# --- DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    # Global Sankalp
    total_jap = df['Total_Counts'].sum()
    pct = min((total_jap / SANKALP_TARGET) * 100, 100)
    st.markdown(f"<div class='sankalp-card'><b>🙏 सामूहिक संकल्प: {int(total_jap):,} जाप</b><br><small>{int(pct)}% पूर्ण</small></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🏠 सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with t1:
        today_total = int(df.at[user_idx, 'Today_Count'])
        st.metric("आज की माला", f"{today_total // 108}")
        mode = st.radio("इनपुट टाइप:", ["माला", "जाप"], horizontal=True)
        val = st.number_input("संख्या:", min_value=0, step=1)
        if st.button("Update"):
            add = val * 108 if mode == "माला" else val
            df.at[user_idx, 'Today_Count'] += add
            df.at[user_idx, 'Total_Counts'] += add
            save_db(df)
            st.rerun()

    with t2:
        st.subheader("🏆 टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Count'] // 108} माला")

    with t3:
        st.subheader("📅 उत्सव एवं एकादशी 2026")
        events = [
            ("14 Jan", "मकर संक्रांति", "सूर्य का उत्तरायण प्रवेश।"),
            ("28 Feb", "आमलकी एकादशी", "आंवले के वृक्ष की पूजा।"),
            ("27 Mar", "राम नवमी", "प्रभु श्री राम जन्मोत्सव।"),
            ("09 Nov", "दीपावली", "अयोध्या दीपोत्सव।"),
            ("20 Dec", "मोक्षदा एकादशी", "मोक्ष प्रदायिनी एकादशी।")
        ]
        grid_html = '<div class="cal-grid">'
        for d, n, desc in events:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip"><b>{n}</b><br>{desc}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.session_state.otp_step = "login"
        st.rerun()
