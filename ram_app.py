import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
DB_FILE = "ram_seva_data.csv"
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

# 2026 एकादशी एवं त्यौहार तिथियां
EVENTS_2026 = [
    ("14 Jan", "मकर संक्रांति", "सूर्य उत्तरायण प्रवेश"),
    ("14 Jan", "षटतिला एकादशी", "पापनाशिनी एकादशी"),
    ("28 Feb", "आमलकी एकादशी", "आंवला वृक्ष पूजन"),
    ("27 Mar", "राम नवमी", "प्रभु श्री राम जन्मोत्सव"),
    ("02 Apr", "हनुमान जयंती", "बजरंगबली जन्मोत्सव"),
    ("14 Apr", "वरुथिनी एकादशी", "सौभाग्य प्रदायिनी"),
    ("09 Nov", "दीपावली", "अयोध्या दीपोत्सव महापर्व"),
    ("20 Dec", "मोक्षदा एकादशी", "गीता जयंती एवं मोक्षदा")
]

def load_db():
    cols = ["Phone", "Name", "Total_Jaap", "Last_Active", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for c in cols:
                if c not in df.columns:
                    df[c] = 0 if "Jaap" in c else "India"
            return df[cols]
        except: pass
    return pd.DataFrame(columns=cols)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_broadcast():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, "r", encoding="utf-8") as f: return f.read()
    return ""

def save_broadcast(msg):
    with open(MSG_FILE, "w", encoding="utf-8") as f: f.write(msg)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
    except: return "India"

# --- PREMIUM INTERACTIVE UI CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .metric-box {
        background: white; padding: 30px; border-radius: 20px; text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05); border-top: 6px solid #FFD700; margin-bottom: 20px;
    }
    /* CALENDAR GRID */
    .cal-grid { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; padding: 15px 0; }
    .cal-card {
        width: 85px; height: 85px; background: white; border: 1.5px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.1); z-index: 10; cursor: pointer; }
    .cal-card:hover b { color: white !important; }
    .tooltip {
        visibility: hidden; width: 160px; background: #3e2723; color: white !important;
        text-align: center; border-radius: 8px; padding: 8px; position: absolute;
        bottom: 115%; left: 50%; margin-left: -80px; opacity: 0; transition: 0.3s; font-size: 10px;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    .ekadashi-banner {
        background: #FFD700; padding: 15px; border-radius: 15px; border-left: 8px solid #FF4D00;
        text-align: center; font-weight: bold; color: #5D4037; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- 1. STRICT LOGIN SECTION ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम").strip()
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ कृपया सही नाम और नंबर भरें।")
        else:
            if u_phone in df['Phone'].values:
                existing_name = df[df['Phone'] == u_phone]['Name'].values[0]
                if u_name.lower() != existing_name.lower():
                    st.error(f"❌ यह नंबर '{existing_name}' के नाम से रजिस्टर्ड है।")
                else:
                    st.session_state.user_session = u_phone
                    st.rerun()
            elif u_name.lower() in df['Name'].str.lower().values:
                st.error(f"❌ '{u_name}' नाम पहले से रजिस्टर्ड है।")
            else:
                loc = get_user_location()
                st.session_state.user_session = u_phone
                new_data = {"Phone": [u_phone], "Name": [u_name], "Total_Jaap": [0], "Last_Active": [today_str], "Today_Jaap": [0], "Location": [loc]}
                df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
                save_db(df)
                st.rerun()

# --- 2. DASHBOARD SECTION ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    # Ekadashi Check
    ekadashi_dates = ["2026-01-14", "2026-02-13", "2026-02-27", "2026-03-29"] # List can be expanded
    if today_str in ekadashi_dates:
        st.markdown('<div class="ekadashi-banner">📢 आज पावन एकादशी है! अपनी सेवा रिकॉर्ड करना न भूलें। 🙏</div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        if df.at[user_idx, 'Last_Active'] != today_str:
            df.at[user_idx, 'Today_Jaap'] = 0
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)

        today_jap = int(df.at[user_idx, 'Today_Jaap'])
        
        # Metric Box: No Jaap count on top, only Mala
        st.markdown(f"""
        <div class="metric-box">
            <h2 style='color:#FF4D00; margin:0;'>{today_jap // 108} माला {today_jap % 108} जाप</h2>
            <p style='color:#666; font-weight: bold;'>आज की कुल सेवा</p>
        </div>
        """, unsafe_allow_html=True)

        mode = st.radio("अपडेट मोड:", ["माला", "जाप"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ जोड़ें", use_container_width=True):
                added = val * 108 if mode == "माला" else val
                df.at[user_idx, 'Total_Jaap'] += added
                df.at[user_idx, 'Today_Jaap'] += added
                save_db(df)
                st.rerun()
        with c2:
            if st.button("✏️ सुधारें (Edit)", use_container_width=True):
                new_v = val * 108 if mode == "माला" else val
                df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - today_jap) + new_v
                df.at[user_idx, 'Today_Jaap'] = new_v
                save_db(df)
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Jaap'] // 108} माला")

    with tabs[2]:
        st.subheader("📅 पावन उत्सव ग्रिड 2026")
        grid_html = '<div class="cal-grid">'
        for d, n, desc in EVENTS_2026:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip"><b>{n}</b><br>{desc}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # ADMIN PANEL
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            u_list = ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")")
            target = st.selectbox("डिलीट यूजर:", u_list)
            if target != "--चुनें--" and st.button("🗑️ डिलीट करें"):
                df = df[df['Phone'] != target.split("(")[1].replace(")", "")]
                save_db(df)
                st.rerun()
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
