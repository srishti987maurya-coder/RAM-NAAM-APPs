import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse
from twilio.rest import Client # pip install twilio

# --- CONFIGURATION (Twilio Credentials) ---
# इन्हें अपने Twilio डैशबोर्ड से बदलें
TWILIO_ACCOUNT_SID = 'YOUR_ACCOUNT_SID'
TWILIO_AUTH_TOKEN = 'YOUR_AUTH_TOKEN'
TWILIO_VERIFY_SID = 'YOUR_VERIFY_SERVICE_ID'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

def load_db():
    required = ["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Count" in col else "India"
            return df
        except: pass
    return pd.DataFrame(columns=required)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1rem -1rem;
    }
    .otp-box { background: white; padding: 20px; border-radius: 15px; border: 2px solid #FFD700; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False

# --- LOGIN WITH OTP ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित भक्ति प्रवेश</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 लॉगिन करें")
    
    u_name = st.text_input("भक्त का नाम लिखें", disabled=st.session_state.otp_sent)
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10, disabled=st.session_state.otp_sent)

    if not st.session_state.otp_sent:
        if st.button("OTP भेजें", use_container_width=True):
            if u_name and len(u_phone) == 10:
                try:
                    # Twilio के माध्यम से OTP भेजना
                    client.verify.v2.services(TWILIO_VERIFY_SID).verifications.create(to=f"+91{u_phone}", channel="sms")
                    st.session_state.otp_sent = True
                    st.session_state.temp_name = u_name
                    st.session_state.temp_phone = u_phone
                    st.rerun()
                except Exception as e:
                    st.error(f"OTP भेजने में त्रुटि: {e}")
            else:
                st.warning("कृपया नाम और सही मोबाइल नंबर दर्ज करें।")
    
    else:
        st.markdown("<div class='otp-box'>", unsafe_allow_html=True)
        otp_code = st.text_input("आपके मोबाइल पर आया 6-अंकों का OTP दर्ज करें", max_chars=6)
        
        col_verify, col_reset = st.columns(2)
        with col_verify:
            if st.button("Verify & Login", use_container_width=True):
                try:
                    verification_check = client.verify.v2.services(TWILIO_VERIFY_SID).verification_checks.create(to=f"+91{st.session_state.temp_phone}", code=otp_code)
                    
                    if verification_check.status == "approved":
                        st.session_state.user_session = st.session_state.temp_phone
                        if st.session_state.temp_phone not in df['Phone'].values:
                            new_user = pd.DataFrame([[st.session_state.temp_phone, st.session_state.temp_name, 0, today_str, 0, "India"]], columns=df.columns)
                            df = pd.concat([df, new_user], ignore_index=True)
                            save_db(df)
                        st.success("प्रमाणन सफल!")
                        st.rerun()
                    else:
                        st.error("गलत OTP, कृपया पुनः प्रयास करें।")
                except Exception as e:
                    st.error("वेरिफिकेशन फेल हो गया।")
        
        with col_reset:
            if st.button("नंबर बदलें", use_container_width=True):
                st.session_state.otp_sent = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- MAIN DASHBOARD (Login Hone ke Baad) ---
else:
    # ... (यहाँ आपका पिछला 'मेरी सेवा', 'लीडरबोर्ड' और 'WhatsApp रिमाइंडर' वाला पूरा कोड आएगा)
    st.write(f"जय श्री राम, {st.session_state.user_session} के रूप में प्रमाणित लॉगिन।")
    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.session_state.otp_sent = False
        st.rerun()
