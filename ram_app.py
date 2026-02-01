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

# --- PREMIUM UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .sankalp-card {
        background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 15px; text-align: center; border: 2px solid #FFD700;
    }
    .progress-bg { background: #eee; border-radius: 10px; height: 12px; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #FFD700, #FF4D00); height: 100%; }
    .wa-btn {
        display: inline-block; padding: 6px 12px; background-color: #25D366;
        color: white !important; text-decoration: none; border-radius: 50px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN (WITH VALIDATION) ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 भक्त प्रवेश")
    
    u_name = st.text_input("आपका पावन नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10 and u_phone.isdigit():
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, "India"]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
        else:
            st.error("❌ कृपया सही नाम और 10 अंकों का मोबाइल नंबर भरें।")

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    # सामुदायिक संकल्प (Sankalp Bar)
    total_jap = df['Total_Counts'].sum()
    pct = min((total_jap / SANKALP_TARGET) * 100, 100)
    st.markdown(f"""<div class='sankalp-card'><b>🙏 सामूहिक संकल्प: {int(total_jap):,} / {SANKALP_TARGET:,}</b>
    <div class='progress-bg'><div class='progress-fill' style='width:{pct}%'></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        c1, c2 = st.columns(2)
        with c1: st.metric("आज की माला", f"{today_total // 108}")
        with c2: st.metric("कुल जाप", f"{int(df.at[user_idx, 'Total_Counts'])}")
        
        mode = st.radio("अपडेट मोड:", ["माला", "जाप संख्या"], horizontal=True)
        val = st.number_input("संख्या लिखें:", min_value=0, step=1, value=(today_total // 108 if mode == "माला" else today_total))
        
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if mode == "माला" else val
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("सफलतापूर्वक अपडेट!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:10px; border-radius:12px; margin-bottom:8px; border-left:6px solid #FFD700; display:flex; justify-content:space-between;"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        events = [
            ("14 Jan", "मकर संक्रांति / षटतिला एकादशी", "दान पुण्य का दिन।"),
            ("15 Feb", "महाशिवरात्रि", "शिव-शक्ति मिलन।"),
            ("28 Feb", "आमलकी एकादशी", "आंवले की पूजा।"),
            ("27 Mar", "राम नवमी", "प्रभु राम जन्मोत्सव।"),
            ("09 Nov", "दीपावली", "दीपोत्सव।")
        ]
        cols = st.columns(2)
        for i, (d, n, desc) in enumerate(events):
            with cols[i % 2]:
                with st.expander(f"🚩 {d} - {n}"):
                    st.write(desc)

    # --- ADMIN CONTROL (WhatsApp Reminders) ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            st.write("📢 **WhatsApp रिमाइन्डर**")
            for i, row in df.iterrows():
                if row['Phone'] not in ADMIN_NUMBERS:
                    msg = f"प्रणाम {row['Name']} जी, आज एकादशी है। कृपया अपनी माला पूर्ण करें और ऐप में दर्ज करें। धन्यवाद!"
                    wa_url = f"https://wa.me/91{row['Phone']}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"{row['Name']}: <a href='{wa_url}' class='wa-btn' target='_blank'>भेजें</a>", unsafe_allow_html=True)
            
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डेटा एक्सेल", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
