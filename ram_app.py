import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
# हमने फाइल का नाम बदला है ताकि पुराना फॉर्मेट ओवरलैप न हो
DB_FILE = "ram_seva_history_v2.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

def load_db():
    # अब डेटा का ढांचा तारीख-वार होगा
    cols = ["Date", "Phone", "Name", "Mala_Added", "Total_Jaap_Added", "Location"]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'Phone': str})
    return pd.DataFrame(columns=cols)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

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
    .metric-card {
        background: white; padding: 40px; border-radius: 30px; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); border-top: 10px solid #FFD700; margin-bottom: 25px;
    }
    .leader-row {
        background: white; padding: 12px; border-radius: 12px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #FF4D00;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- 1. LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<h1 style="text-align:center;">🚩 श्री राम धाम</h1>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
    
    if st.button("प्रवेश करें", use_container_width=True):
        if len(u_phone) == 10 and u_name:
            st.session_state.user_session = u_phone
            st.session_state.user_name = u_name
            st.rerun()
        else:
            st.error("कृपया सही नाम और मोबाइल नंबर भरें।")

# --- 2. DASHBOARD ---
else:
    u_phone = st.session_state.user_session
    u_name = st.session_state.user_name
    
    # यूजर का डेटा कैलकुलेट करें
    u_df = df[df['Phone'] == u_phone]
    today_mala = u_df[u_df['Date'] == today_str]['Mala_Added'].sum()
    total_mala = u_df['Mala_Added'].sum()

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    with tabs[0]:
        st.markdown(f"""
            <div class="metric-card">
                <h1 style='color:#FF4D00; margin:0; font-size: 4rem;'>{int(today_mala)} माला</h1>
                <p style='color:#666; font-weight: bold;'>आज की सेवा ({today_str})</p>
                <hr style='border: 0.5px solid #eee;'>
                <h3 style='color:#FF9933;'>कुल सेवा (Lifetime): {int(total_mala)} माला</h3>
            </div>
        """, unsafe_allow_html=True)
        
        val = st.number_input("आज कितनी माला जोड़ी?", min_value=0, step=1)
        if st.button("➕ सेवा जमा करें", use_container_width=True):
            if val > 0:
                loc = get_user_location()
                new_entry = {
                    "Date": today_str,
                    "Phone": u_phone,
                    "Name": u_name,
                    "Mala_Added": val,
                    "Total_Jaap_Added": val * 108,
                    "Location": loc
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_db(df)
                st.success(f"भगवान श्री राम आपकी सेवा स्वीकार करें! {val} माला दर्ज की गई।")
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 पावन लीडरबोर्ड")
        # आज के टॉप सेवक
        st.write("**आज के अग्रणी सेवक:**")
        today_leaders = df[df['Date'] == today_str].groupby('Name')['Mala_Added'].sum().reset_index()
        today_leaders = today_leaders.sort_values(by="Mala_Added", ascending=False).head(10)
        
        if today_leaders.empty:
            st.info("आज की सेवा का खाता खुलना अभी बाकी है।")
        else:
            for _, row in today_leaders.iterrows():
                st.markdown(f'<div class="leader-row"><b>{row["Name"]}</b> <span>{int(row["Mala_Added"])} माला</span></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        st.write("2026 की सभी एकादशी और त्यौहार यहाँ अपडेटेड हैं।")
        # यहाँ आप अपना पुराना कैलेंडर लॉजिक डाल सकते हैं।

    # --- ADMIN ---
    if u_phone in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            # एक्सेल में अब तारीख के साथ सारा इतिहास दिखेगा
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डाउनलोड एक्सेल (Full History)", data=csv, file_name=f'ram_seva_full_report.csv', use_container_width=True)
            
            st.divider()
            if st.button("Logout 🚪", use_container_width=True):
                st.session_state.user_session = None
                st.rerun()
