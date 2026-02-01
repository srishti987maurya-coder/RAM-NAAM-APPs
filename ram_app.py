import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & FILES ---
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
        with open(MSG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_broadcast(msg):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        f.write(msg)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
    except: return "India"

# --- PREMIUM UI CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .broadcast-box {
        background: #FFF9C4; color: #5D4037; padding: 12px; border-radius: 12px;
        border-left: 6px solid #FBC02D; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    .sankalp-card {
        background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 15px; text-align: center; border: 2px solid #FFD700;
    }
    .progress-bg { background: #eee; border-radius: 10px; height: 10px; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #FFD700, #FF4D00); height: 100%; }
    
    .cal-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding: 10px 0; }
    .cal-card {
        width: 82px; height: 82px; background: white; border: 1.5px solid #FF9933;
        border-radius: 12px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.1); z-index: 10; }
    .cal-card:hover b { color: white !important; }
    .tooltip {
        visibility: hidden; width: 170px; background: #3e2723; color: white !important;
        text-align: center; border-radius: 8px; padding: 8px; position: absolute;
        bottom: 115%; left: 50%; margin-left: -85px; opacity: 0; transition: 0.3s; font-size: 10px;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    .wa-btn {
        display: inline-block; padding: 5px 10px; background-color: #25D366;
        color: white !important; text-decoration: none; border-radius: 50px; font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ सही नाम और नंबर भरें।")
        else:
            if u_phone in df['Phone'].values:
                st.session_state.user_session = u_phone
                st.rerun()
            else:
                loc = get_user_location()
                st.session_state.user_session = u_phone
                new_user = pd.DataFrame([[u_phone, u_name, 0, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
                st.rerun()

# --- MAIN DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    msg = get_broadcast()
    if msg: st.markdown(f'<div class="broadcast-box">📢 {msg}</div>', unsafe_allow_html=True)

    total_jap_all = df['Total_Jaap'].sum()
    pct = min((total_jap_all / SANKALP_TARGET) * 100, 100)
    st.markdown(f"""<div class='sankalp-card'><b>🙏 सामूहिक संकल्प: {int(total_jap_all):,} / {SANKALP_TARGET:,}</b>
    <div class='progress-bg'><div class='progress-fill' style='width:{pct}%'></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        # --- EDITABLE COUNT LOGIC ---
        today_jap = int(df.at[user_idx, 'Today_Jaap'])
        st.subheader("📝 अपनी सेवा दर्ज/संशोधित करें")
        st.write(f"वर्तमान सेवा: **{today_jap // 108} माला ({today_jap} जाप)**")
        
        mode = st.radio("इनपुट टाइप चुनें:", ["माला (108)", "सटीक जाप संख्या"], horizontal=True)
        # Value is pre-filled with today's count to allow easy editing
        current_val = today_jap // 108 if "माला" in mode else today_jap
        val = st.number_input("संख्या बदलें या दर्ज करें:", min_value=0, step=1, value=current_val)
        
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if "माला" in mode else val
            new_mala = val if "माला" in mode else val // 108
            
            # Correcting the Total counts by removing old today and adding new
            df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - today_jap) + new_jap
            df.at[user_idx, 'Total_Mala'] = (df.at[user_idx, 'Total_Mala'] - (today_jap // 108)) + new_mala
            df.at[user_idx, 'Today_Jaap'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("आपकी सेवा सफलतापूर्वक अपडेट की गई!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:10px; border-radius:12px; margin-bottom:8px; border-left:6px solid #FFD700; display:flex; justify-content:space-between;"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Jaap"] // 108} माला</b></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन उत्सव एवं एकादशी 2026")
        events = [
            ("14 Jan", "मकर संक्रांति / षटतिला एकादशी", "पुण्य काल।"),
            ("15 Feb", "महाशिवरात्रि", "शिव मिलन।"),
            ("28 Feb", "आमलकी एकादशी", "आंवला पूजा।"),
            ("27 Mar", "राम नवमी", "जन्मोत्सव।"),
            ("02 Apr", "हनुमान जयंती", "बजरंगबली।"),
            ("14 Apr", "वरुथिनी एकादशी", "सौभाग्य व्रत।"),
            ("09 Nov", "दीपावली", "दीपोत्सव।"),
            ("20 Dec", "मोक्षदा एकादशी", "मोक्ष प्राप्ति।")
        ]
        grid_html = '<div class="cal-grid">'
        for d, n, desc in events:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip"><b>{n}</b><br>{desc}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- ADMIN FEATURES ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            # Message Update
            msg_input = st.text_area("ब्रॉडकास्ट संदेश लिखें:", value=msg)
            if st.button("📢 संदेश अपडेट"): save_broadcast(msg_input); st.rerun()
            
            st.divider()
            # Delete User
            target = st.selectbox("डिलीट भक्त:", ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")"))
            if target != "--चुनें--" and st.button("🗑️ डिलीट करें"):
                df = df[df['Phone'] != target.split("(")[1].replace(")", "")]
                save_db(df)
                st.rerun()
            
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 विस्तृत एक्सेल डाउनलोड", data=csv, file_name='shri_ram_dham_report.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
