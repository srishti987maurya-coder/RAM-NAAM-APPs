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
SANKALP_TARGET = 1000000 

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

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'India')}"
    except: return "India"

# --- RESTORED PREMIUM UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .app-header h1 { color: white !important; font-weight: 800; }
    
    /* Global Sankalp Bar */
    .sankalp-card {
        background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 15px; text-align: center;
        border: 2px solid #FFD700; margin-bottom: 20px;
    }
    .progress-bg { background: #eee; border-radius: 10px; height: 12px; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #FFD700, #FF4D00); height: 100%; }

    /* Premium Leaderboard Card */
    .leader-row {
        background: white; padding: 12px 20px; border-radius: 15px;
        margin-bottom: 10px; border-left: 8px solid #FFD700;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    /* RESTORED INTERACTIVE CALENDAR GRID */
    .cal-grid { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; padding: 15px 0; }
    .cal-card {
        width: 90px; height: 90px; background: white; border: 2px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative;
        cursor: pointer; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.1); }
    .cal-card:hover b, .cal-card:hover span { color: white !important; }
    .tooltip {
        visibility: hidden; width: 180px; background-color: #3e2723;
        color: white !important; text-align: center; border-radius: 8px;
        padding: 10px; position: absolute; z-index: 100;
        bottom: 115%; left: 50%; margin-left: -90px;
        opacity: 0; transition: 0.3s; font-size: 12px; pointer-events: none;
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
    u_name = st.text_input("नाम")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("दिव्य प्रवेश", use_container_width=True):
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

    # Global Sankalp Header
    total_jap = df['Total_Counts'].sum()
    pct = min((total_jap / SANKALP_TARGET) * 100, 100)
    st.markdown(f"""<div class='sankalp-card'><b>🙏 सामूहिक संकल्प: {int(total_jap):,} / {SANKALP_TARGET:,}</b>
    <div class='progress-bg'><div class='progress-fill' style='width:{pct}%'></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        c1, c2 = st.columns(2)
        with c1: st.metric("आज की माला", f"{today_total // 108}")
        with c2: st.metric("कुल जाप", f"{int(df.at[user_idx, 'Total_Counts'])}")
        val = st.number_input("माला लिखें:", min_value=0, step=1, value=(today_total // 108))
        if st.button("✅ अपडेट", use_container_width=True):
            new_jap = val * 108
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div class="leader-row"><span><b>#{i+1}</b> {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन उत्सव 2026")
        events = [("15 Feb", "महाशिवरात्रि", "शिव-शक्ति मिलन।"), ("27 Mar", "राम नवमी", "प्रभु राम जन्मोत्सव।"), ("09 Nov", "दीपावली", "दीपोत्सव।")]
        grid_html = '<div class="cal-grid">'
        for date, name, desc in events:
            grid_html += f'<div class="cal-card"><b>{date}</b><span>2026</span><div class="tooltip"><b>{name}</b><br>{desc}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डेटा एक्सेल", data=csv, file_name='ram_data.csv')
    
    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
