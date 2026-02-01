import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

# एकादशी तिथियां (2026) - संदेश भेजने के लिए डेटाबेस
EKADASHI_2026 = ["14 Jan", "28 Feb", "27 Mar", "14 Apr", "13 May", "10 Jul", "07 Aug", "05 Sep", "04 Nov", "20 Dec"]

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
    .reminder-box {
        background: #E3F2FD; padding: 15px; border-radius: 15px;
        border-left: 5px solid #2196F3; margin-bottom: 20px; color: #0D47A1;
    }
    .cal-card {
        width: 85px; height: 85px; background: white; border: 1.5px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.1); }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_dm = datetime.now().strftime("%d %b")
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("भक्त का नाम")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, "India"]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    # एकादशी अलर्ट (Inside App)
    if today_dm in EKADASHI_2026:
        st.markdown(f'<div class="reminder-box">✨ आज <b>एकादशी</b> है! विशेष जाप करें और ऐप में दर्ज करना न भूलें।</div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        c1, c2 = st.columns(2)
        with c1: st.metric("आज की माला", f"{today_total // 108}")
        with c2: st.metric("आज का कुल जाप", f"{today_total}")
        
        mode = st.radio("प्रकार चुनें:", ["पूरी माला", "जाप संख्या"], horizontal=True)
        val = st.number_input("संख्या लिखें:", min_value=0, step=1, value=(today_total // 108 if mode == "पूरी माला" else today_total))
        
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if mode == "पूरी माला" else val
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("अपडेट हो गया!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Count'] // 108} माला")

    with tabs[2]:
        st.subheader("📅 पावन उत्सव कैलेंडर 2026")
        events = [("14 Jan", "षटतिला एकादशी"), ("15 Feb", "महाशिवरात्रि"), ("28 Feb", "आमलकी एकादशी"), ("27 Mar", "राम नवमी"), ("02 Apr", "हनुमान जयंती"), ("09 Nov", "दीपावली")]
        cols = st.columns(3)
        for i, (d, n) in enumerate(events):
            with cols[i % 3]:
                st.markdown(f"<div class='cal-card'><b style='color:#FF4D00;'>{d}</b><br><small>{n}</small></div>", unsafe_allow_html=True)

    # --- ADMIN REMINDER CONTROL (For Outside Messages) ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            st.write("---")
            st.write("📢 **WhatsApp रिमाइन्डर भेजें**")
            
            # संदेश का प्रारूप (Message Draft)
            reminder_msg = "जय श्री राम! आज एकादशी है। कृपया अपनी माला पूर्ण करें और 'श्री राम धाम' ऐप में अपनी सेवा दर्ज करें। धन्यवाद!"
            
            # प्रत्येक भक्त के लिए WhatsApp लिंक बनाना
            for i, row in df.iterrows():
                if row['Phone'] not in ADMIN_NUMBERS: # खुद को न भेजें
                    encoded_msg = urllib.parse.quote(f"प्रणाम {row['Name']}, {reminder_msg}")
                    wa_link = f"https://wa.me/91{row['Phone']}?text={encoded_msg}"
                    st.markdown(f"👉 [{row['Name']} को भेजें]({wa_link})")
            
            st.write("---")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डेटा एक्सेल डाउनलोड", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
