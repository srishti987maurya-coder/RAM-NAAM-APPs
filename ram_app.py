import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1000000  # 10 लाख जाप का सामूहिक संकल्प

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

# --- UI STYLING (PREMIUM INTERACTIVE) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 2rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .broadcast-bar {
        background: #FFF9C4; color: #5D4037; padding: 10px; border-radius: 10px;
        border-left: 5px solid #FBC02D; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    .sankalp-card {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #FFD700; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 25px;
    }
    .progress-bg { background: #eee; border-radius: 10px; height: 12px; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #FFD700, #FF4D00); height: 100%; transition: 0.5s; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("प्रवेश करें", use_container_width=True):
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

    # 1. ADMIN BROADCAST (सूचना केंद्र)
    if os.path.exists("broadcast.txt"):
        with open("broadcast.txt", "r", encoding="utf-8") as f:
            msg = f.read()
            if msg:
                st.markdown(f'<div class="broadcast-bar">📢 सूचना: {msg}</div>', unsafe_allow_html=True)

    # 2. GLOBAL SANKALP (सामूहिक संकल्प)
    total_global_jap = df['Total_Counts'].sum()
    progress_pct = min((total_global_jap / SANKALP_TARGET) * 100, 100)
    
    st.markdown(f"""
    <div class="sankalp-card">
        <h3 style="margin:0; color:#FF4D00;">🙏 सामूहिक संकल्प</h3>
        <p style="margin:5px 0;">लक्ष्य: 10 लाख जाप | अब तक: <b>{int(total_global_jap):,}</b></p>
        <div class="progress-bg"><div class="progress-fill" style="width:{progress_pct}%"></div></div>
        <small>{int(progress_pct)}% संकल्प पूर्ण</small>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.metric("आज की माला", f"{today_total // 108}")
        with col2: st.metric("कुल जाप", f"{int(df.at[user_idx, 'Total_Counts'])}")
        
        val = st.number_input("माला संख्या:", min_value=0, step=1, value=(today_total // 108))
        if st.button("✅ अपडेट करें", use_container_width=True):
            new_jap = val * 108
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("सफलतापूर्वक अपडेट!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Count'] // 108} माला")

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        events = [("27 Mar", "श्री राम नवमी"), ("02 Apr", "हनुमान जयंती"), ("09 Nov", "दीपावली")]
        for date, name in events:
            st.info(f"🚩 {date} — {name}")

    # 3. ADMIN PANEL (BROADCAST CONTROL)
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन पैनल")
            new_msg = st.text_area("भक्तों के लिए संदेश लिखें:", placeholder="उदा: कल विशेष जाप दिवस है...")
            if st.button("📢 संदेश भेजें"):
                with open("broadcast.txt", "w", encoding="utf-8") as f:
                    f.write(new_msg)
                st.success("संदेश अपडेट हुआ!")
            
            if st.button("🗑️ संदेश हटाएं"):
                open("broadcast.txt", "w").close()
                st.rerun()
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डेटा एक्सेल", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
