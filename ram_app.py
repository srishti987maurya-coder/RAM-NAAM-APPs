import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

def load_db():
    required = ["Phone", "Name", "Total_Jaap", "Last_Active", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Jaap" in col else "India"
            return df
        except: pass
    return pd.DataFrame(columns=required)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
    except: return "India"

# --- PREMIUM UI ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .metric-box {
        background: white; padding: 20px; border-radius: 20px; text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05); border-top: 5px solid #FFD700; margin-bottom: 20px;
    }
    .cal-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding: 15px 0; }
    .cal-card {
        width: 85px; height: 85px; background: white; border: 1.5px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; color: white !important; transform: scale(1.1); }
    .tooltip {
        visibility: hidden; width: 160px; background: #3e2723; color: white !important;
        text-align: center; border-radius: 8px; padding: 8px; position: absolute;
        bottom: 115%; left: 50%; margin-left: -80px; opacity: 0; transition: 0.3s; font-size: 10px;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("अपना पावन नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    
    if st.button("दिव्य प्रवेश", use_container_width=True):
        if u_name and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                loc = get_user_location()
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    with tabs[0]:
        # Reset today's count if date changed
        if df.at[user_idx, 'Last_Active'] != today_str:
            df.at[user_idx, 'Today_Jaap'] = 0
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)

        today_jap = int(df.at[user_idx, 'Today_Jaap'])
        mala_display = today_jap // 108
        rem_jaap = today_jap % 108
        
        st.markdown(f"""
        <div class="metric-box">
            <h2 style='color:#FF4D00; margin:0;'>{mala_display} माला {rem_jaap} जाप</h2>
            <p style='color:#666;'>आज की कुल सेवा</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📝 नई सेवा जोड़ें")
        
        entry_mode = st.radio("इनपुट टाइप:", ["माला (108 जाप)", "सटीक जाप संख्या"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1)
        
        col_add, col_edit = st.columns(2)
        with col_add:
            if st.button("➕ सेवा जोड़ें", use_container_width=True):
                add_jaap = val * 108 if "माला" in entry_mode else val
                df.at[user_idx, 'Total_Jaap'] += add_jaap
                df.at[user_idx, 'Today_Jaap'] += add_jaap
                save_db(df)
                st.success(f"{add_jaap} जाप सफलतापूर्वक जोड़े गए!")
                st.rerun()
        
        with col_edit:
            if st.button("✏️ सुधार करें (Overwrite)", use_container_width=True):
                # This replaces today's total with the new value
                new_jap = val * 108 if "माला" in entry_mode else val
                df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - today_jap) + new_jap
                df.at[user_idx, 'Today_Jaap'] = new_jap
                save_db(df)
                st.warning("आज का डेटा संशोधित किया गया!")
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Jaap'] // 108} माला {row['Today_Jaap'] % 108} जाप")

    with tabs[2]:
        st.subheader("📅 पावन उत्सव कैलेंडर 2026")
        events = [("14 Jan", "मकर संक्रांति"), ("28 Feb", "आमलकी एकादशी"), ("27 Mar", "राम नवमी"), ("14 Apr", "वरुथिनी एकादशी"), ("02 Apr", "हनुमान जयंती"), ("09 Nov", "दीपावली")]
        grid_html = '<div class="cal-grid">'
        for d, n in events:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip">{n}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
