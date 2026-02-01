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

# एकादशी तिथियां 2026
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
    .sms-btn {
        display: inline-block; padding: 5px 10px; background-color: #4CAF50;
        color: white !important; text-decoration: none; border-radius: 5px; font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_dm = datetime.now().strftime("%d %b")
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN & MAIN LOGIC ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("भक्त का नाम")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("दिव्य प्रवेश"):
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

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        st.metric("आज का कुल जाप", f"{today_total}")
        val = st.number_input("माला संख्या (1 माला = 108):", min_value=0, step=1, value=(today_total // 108))
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            new_jap = val * 108
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("अपडेट सफल!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Count'] // 108} माला")

    with tabs[2]:
        st.subheader("📅 कैलेंडर 2026")
        events = [("14 Jan", "एकादशी"), ("15 Feb", "महाशिवरात्रि"), ("27 Mar", "राम नवमी")]
        for d, n in events: st.write(f"🚩 {d} — {n}")

    # --- ADMIN SMS REMINDER ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन पैनल")
            st.write("📢 **SMS रिमाइन्डर भेजें**")
            
            sms_body = "Jai Shri Ram! Aaj Ekadashi hai. Kripya apni mala purn kare aur Shri Ram Dham app me darj kare. Dhanyawad!"
            
            for i, row in df.iterrows():
                if row['Phone'] not in ADMIN_NUMBERS:
                    # SMS URL Scheme (sms:+91...;?&body=...)
                    safe_msg = urllib.parse.quote(sms_body)
                    sms_link = f"sms:+91{row['Phone']}?body={safe_msg}"
                    st.markdown(f"📩 {row['Name']}: [SMS भेजें]({sms_link})")
            
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डेटा एक्सेल", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
