import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="श्री राम धाम",
    page_icon="🚩",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            if 'Location' not in df.columns: df['Location'] = "Global"
            if 'Today_Count' not in df.columns: df['Today_Count'] = 0
            if 'Total_Counts' not in df.columns: df['Total_Counts'] = 0
            return df
        except: pass
    return pd.DataFrame(columns=["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"])

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    """Improved IP-based location fetching"""
    try:
        # Using a highly reliable backup API
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown City')
            country = data.get('country_name', 'Global')
            return f"{city}, {country}"
    except:
        return "Spiritual World"
    return "Global"

# --- UI CSS FIXES (For Visibility) ---
st.markdown("""
    <style>
    /* Force text to be visible and dark */
    .stMarkdown, p, label, span, .stHeader {
        color: #3e2723 !important;
        font-weight: 500;
    }
    
    .stApp {
        background: linear-gradient(135deg, #FFE5B4 0%, #FFF5E6 50%, #FFE0B2 100%);
    }

    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important;
        padding: 2rem 1rem;
        border-radius: 0px 0px 30px 30px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }

    .app-header h1, .app-header div, .app-header span {
        color: white !important;
    }

    .stat-card {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255, 77, 0, 0.1);
        border: 1px solid #FFCCBC;
    }

    .calendar-card {
        background: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid #FF9933;
        margin-bottom: 10px;
        color: #3e2723 !important;
    }
    
    /* Fix for white text on input fields */
    input { color: black !important; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")
display_date = datetime.now().strftime("%d %B %Y, %A")

# Calendar Data
calendar_data = {
    "राम उत्सव 🚩": ["राम नवमी - 27 मार्च", "हनुमान जयंती - 12 अप्रैल", "विजयादशमी - 20 अक्टूबर", "दीपावली - 9 नवंबर"],
    "एकादशी 🙏": ["षटतिला एकादशी - 14 जनवरी", "जया एकादशी - 29 जनवरी", "आमलकी एकादशी - 14 मार्च"],
    "पावन व्रत 🌙": ["महाशिवरात्रि - 15 फरवरी", "होली - 14 मार्च", "गणेश चतुर्थी - 27 अगस्त"]
}

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
if not st.session_state.user_session:
    st.markdown(f"""<div class="app-header"><h1>🚩 श्री राम धाम 🚩</h1><div>राम नाम जाप सेवा</div><div style="font-size:0.9rem; margin-top:5px;">📅 {display_date}</div></div>""", unsafe_allow_html=True)
    
    u_name = st.text_input("आपका पावन नाम (Name)", placeholder="e.g. Ram Kumar")
    u_phone = st.text_input("मोबाइल नंबर (Mobile)", placeholder="10 Digit Number", max_chars=10)

    if st.button("🚪 प्रवेश करें (Login)", type="primary", use_container_width=True):
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

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Header
    st.markdown(f"""
        <div class="app-header">
            <h1 style="margin:0;">🚩 श्री राम धाम 🚩</h1>
            <div style="font-weight:bold; font-size:1.2rem;">जय श्री राम, {df.at[user_idx, 'Name']}!</div>
            <div style="font-size:0.85rem; opacity:0.9;">📍 {df.at[user_idx, 'Location']}</div>
        </div>
    """, unsafe_allow_html=True)

    # Stats
    today_total = int(df.at[user_idx, 'Today_Count'])
    total_jap = int(df.at[user_idx, 'Total_Counts'])
    
    st.markdown(f"""
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <div class="stat-card" style="flex:1;">
                <div style="font-size:0.8rem; color:#666;">आज की माला</div>
                <div style="font-size:1.8rem; font-weight:900; color:#FF4D00;">{today_total // 108}</div>
            </div>
            <div class="stat-card" style="flex:1;">
                <div style="font-size:0.8rem; color:#666;">कुल जाप</div>
                <div style="font-size:1.8rem; font-weight:900; color:#FF4D00;">{total_jap}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Entry
    st.markdown("<div style='font-weight:bold; margin-bottom:5px;'>📝 जाप दर्ज करें:</div>", unsafe_allow_html=True)
    mode = st.radio("Mode:", ["📿 माला", "🔢 संख्या"], horizontal=True, label_visibility="collapsed")
    val = st.number_input("Enter count:", min_value=0, step=1, value=(today_total // 108 if mode == "📿 माला" else today_total))

    if st.button("✅ डेटा अपडेट करें", use_container_width=True):
        new_count = val * 108 if mode == "📿 माला" else val
        old_count = df.at[user_idx, 'Today_Count']
        df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_count) + new_count
        df.at[user_idx, 'Today_Count'] = new_count
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)
        st.success("सफलतापूर्वक अपडेट किया गया!")
        st.rerun()

    # --- CALENDAR (Fixed & Organized) ---
    st.markdown("<br><div style='font-weight:bold; font-size:1.1rem;'>📅 पावन वार्षिक कैलेंडर 2026</div>", unsafe_allow_html=True)
    tabs = st.tabs(list(calendar_data.keys()))
    for i, tab in enumerate(tabs):
        with tab:
            for event in calendar_data[list(calendar_data.keys())[i]]:
                st.markdown(f"<div class='calendar-card'>🔸 {event}</div>", unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
