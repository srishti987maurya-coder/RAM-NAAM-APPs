import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
import requests
import urllib.parse

# --- CONFIGURATION ---
API_KEY = "YOUR_FAST2SMS_API_KEY"  # यहाँ अपनी Fast2SMS API Key डालें

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'Phone': str})
    return pd.DataFrame(columns=["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"])

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def send_otp_sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "variables_values": otp,
        "route": "otp",
        "numbers": phone,
    }
    headers = {"authorization": API_KEY}
    response = requests.get(url, headers=headers, params=payload)
    return response.json()

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background: #FFF5E6; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00, #FF9933);
        color: white; padding: 2rem; border-radius: 0 0 40px 40px; text-align: center; margin-bottom: 2rem;
    }
    .stButton>button { background: #FF4D00; color: white; border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- SESSION STATES ---
if 'user_session' not in st.session_state: st.session_state.user_session = None
if 'otp_step' not in st.session_state: st.session_state.otp_step = "get_phone"
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = None

# --- AUTHENTICATION UI ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>SMS OTP सत्यापन</div></div>', unsafe_allow_html=True)
    
    if st.session_state.otp_step == "get_phone":
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
                    st.session_state.otp_step = "verify_otp"
                    st.rerun()
                else:
                    st.error("SMS भेजने में विफल। कृपया API Key या बैलेंस चेक करें।")
            else:
                st.error("सही 10 अंकों का नंबर डालें।")

    elif st.session_state.otp_step == "verify_otp":
        st.info(f"OTP आपके नंबर {st.session_state.temp_phone} पर भेजा गया है।")
        user_otp = st.text_input("4-अंकों का OTP दर्ज करें", max_chars=4)
        
        if st.button("सत्यापित करें", use_container_width=True):
            if user_otp == st.session_state.generated_otp:
                st.session_state.user_session = st.session_state.temp_phone
                if st.session_state.temp_phone not in df['Phone'].values:
                    new_user = pd.DataFrame([[st.session_state.temp_phone, st.session_state.temp_name, 0, today_str, 0, "India"]], columns=df.columns)
                    df = pd.concat([df, new_user], ignore_index=True)
                    save_db(df)
                st.success("सत्यापन सफल!")
                st.rerun()
            else:
                st.error("गलत OTP!")
        
        if st.button("नंबर बदलें"):
            st.session_state.otp_step = "get_phone"
            st.rerun()

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])
    
    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        st.metric("आज का जाप", today_total)
        val = st.number_input("माला (108 जाप):", min_value=0, step=1)
        if st.button("Update"):
            df.at[user_idx, 'Today_Count'] += (val * 108)
            df.at[user_idx, 'Total_Counts'] += (val * 108)
            save_db(df)
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 टॉप सेवक")
        st.table(df[['Name', 'Total_Counts']].sort_values('Total_Counts', ascending=False).head(10))

    with tabs[2]:
        st.subheader("📅 उत्सव 2026")
        events = [("27 Mar", "राम नवमी"), ("02 Apr", "हनुमान जयंती"), ("09 Nov", "दीपावली")]
        for d, e in events: st.write(f"🚩 {d}: {e}")

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
