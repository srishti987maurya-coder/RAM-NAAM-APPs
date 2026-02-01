import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="श्री राम धाम",
    page_icon="🚩",
    layout="centered"
)

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBER = "9987621091" 

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

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF5E6; }
    .stMarkdown, p, label, span, li, div, h1, h2, h3 { color: #3e2723 !important; }
    
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem;
        border-radius: 0 0 40px 40px; text-align: center;
        margin: -1rem -1rem 1rem -1rem; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .app-header * { color: white !important; }

    /* Calendar Styling Fix */
    .cal-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
        gap: 12px;
        margin-top: 20px;
    }
    .cal-card {
        background: white; border: 2px solid #FF9933;
        border-radius: 15px; height: 90px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        position: relative; cursor: help;
        transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.05); }
    .cal-card:hover b, .cal-card:hover span { color: white !important; }

    .tooltip {
        visibility: hidden; width: 180px; background-color: #3e2723;
        color: white !important; text-align: center; border-radius: 8px;
        padding: 8px; position: absolute; z-index: 100;
        bottom: 110%; left: 50%; margin-left: -90px;
        opacity: 0; transition: 0.3s; font-size: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3); pointer-events: none;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    
    .stat-card {
        background: white; padding: 1.2rem; border-radius: 20px;
        text-align: center; border: 2px solid #FFE0B2;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका नाम")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10:
            loc = get_user_location()
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
            else:
                idx = df[df['Phone'] == u_phone].index[0]
                df.at[idx, 'Location'] = loc
            save_db(df)
            st.rerun()

# --- MAIN DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with t1:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'><small>आज की माला</small><h2>{today_total // 108}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'><small>कुल जाप</small><h2>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        
        st.divider()
        mode = st.radio("Mode:", ["माला", "संख्या"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1, value=(today_total // 108 if mode == "माला" else today_total))
        if st.button("✅ अपडेट करें", use_container_width=True):
            new_jap = val * 108 if mode == "माला" else val
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("अपडेट हो गया!")
            st.rerun()

    with t2:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; margin-bottom:5px; border-left:5px solid #FF9933; display:flex; justify-content:space-between;"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    with t3:
        st.subheader("📅 पावन उत्सव 2026")
        events = [
            ("14 Jan", "मकर संक्रांति", "सूर्य का उत्तरायण प्रवेश।"),
            ("15 Feb", "महाशिवरात्रि", "शिव-शक्ति मिलन का महापर्व।"),
            ("14 Mar", "होली", "रंगों का उत्सव।"),
            ("27 Mar", "राम नवमी", "प्रभु श्री राम जन्मोत्सव।"),
            ("02 Apr", "हनुमान जयंती", "बजरंगबली जन्मोत्सव।"),
            ("20 Oct", "दशहरा", "धर्म की विजय का पर्व।"),
            ("09 Nov", "दीपावली", "दीपों का महापर्व।")
        ]
        
        grid_html = '<div class="cal-grid">'
        for date, name, desc in events:
            grid_html += f'''
            <div class="cal-card">
                <b style="color:#FF4D00;">{date}</b>
                <span style="font-size:10px;">2026</span>
                <div class="tooltip"><b>{name}</b><br>{desc}</div>
            </div>
            '''
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    if st.session_state.user_session == ADMIN_NUMBER:
        st.sidebar.markdown("---")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📊 डेटा डाउनलोड", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
