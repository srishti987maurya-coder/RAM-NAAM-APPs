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
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

def load_db():
    required = ["Phone", "Name", "Total_Jaap", "Last_Active", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Jaap" in col else "Unknown"
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
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .metric-card {
        background: white; padding: 15px; border-radius: 15px; text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-bottom: 4px solid #FF4D00;
    }
    .cal-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding: 10px 0; }
    .cal-card {
        width: 85px; height: 85px; background: white; border: 1.5px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
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
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("नाम").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश", use_container_width=True):
        if u_name and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, get_user_location()]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_jaap = int(df.at[user_idx, 'Today_Jaap'])
        
        # Smart Display Logic
        mala = today_jaap // 108
        extra_jaap = today_jaap % 108
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric-card'><small>आज की सेवा</small><br><b style='font-size:1.2rem;'>{mala} माला, {extra_jaap} जाप</b></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><small>कुल जाप</small><br><b style='font-size:1.2rem;'>{int(df.at[user_idx, 'Total_Jaap'])}</b></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("📝 सेवा अपडेट/संशोधित करें")
        
        input_mode = st.radio("अपडेट का तरीका:", ["माला द्वारा", "सीधा जाप संख्या द्वारा"], horizontal=True)
        
        if input_mode == "माला द्वारा":
            val = st.number_input("माला की संख्या (108 जाप प्रति माला):", min_value=0, step=1, value=mala)
            final_jaap = val * 108
        else:
            val = st.number_input("कुल जाप संख्या लिखें:", min_value=0, step=1, value=today_jaap)
            final_jaap = val

        if st.button("✅ सेवा सुरक्षित करें", use_container_width=True):
            # Erase and Update Logic
            df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - today_jaap) + final_jaap
            df.at[user_idx, 'Today_Jaap'] = final_jaap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("डेटा अपडेट हो गया!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f"<div style='background:white; padding:10px; margin-bottom:5px; border-radius:10px;'>#{i+1} {row['Name']} — {row['Today_Jaap'] // 108} माला, {row['Today_Jaap'] % 108} जाप</div>", unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        # विस्तृत एकादशी तिथियां
        events = [("14 Jan", "षटतिला एकादशी"), ("28 Feb", "आमलकी एकादशी"), ("27 Mar", "राम नवमी"), ("14 Apr", "वरुथिनी एकादशी"), ("09 Nov", "दीपावली")]
        grid_html = '<div class="cal-grid">'
        for d, n in events:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip">{n}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # ADMIN PANEL
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन")
            target = st.selectbox("डिलीट यूजर:", ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")"))
            if target != "--चुनें--" and st.button("🗑️ डिलीट"):
                p = target.split("(")[1].replace(")", "")
                df = df[df['Phone'] != p]
                save_db(df)
                st.rerun()
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
