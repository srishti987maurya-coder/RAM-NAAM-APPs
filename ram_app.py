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
            # Ensure all required columns exist to prevent KeyErrors
            for col in ['Phone', 'Name', 'Total_Counts', 'Last_Active', 'Today_Count', 'Location']:
                if col not in df.columns:
                    df[col] = 0 if 'Count' in col else "Global"
            return df
        except: pass
    return pd.DataFrame(columns=["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"])

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    """Fetches user city/country via IP. Shows 'Global' if local."""
    try:
        # Using a reliable third-party API
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('city', 'Unknown City')}, {data.get('country_name', 'India')}"
    except:
        return "Global"
    return "Global"

# --- INTERACTIVE UI CSS ---
st.markdown("""
    <style>
    /* Darken all prose text for better readability */
    .stMarkdown, p, label, .stHeader, span, li {
        color: #4A2C00 !important;
        font-weight: 500;
    }
    
    .stApp {
        background: linear-gradient(135deg, #FFE5B4 0%, #FFF5E6 50%, #FFE0B2 100%);
    }

    /* Vibrant Saffron Header */
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important;
        padding: 2.5rem 1rem;
        border-radius: 0px 0px 40px 40px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 10px 25px rgba(255, 77, 0, 0.3);
    }

    .app-header h1, .app-header div {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }

    /* Glassmorphism Stat Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        border: 2px solid #FFE0B2;
        transition: 0.3s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(255, 77, 0, 0.15);
    }

    /* Beautiful Calendar Cards */
    .calendar-card {
        background: white;
        padding: 12px;
        border-radius: 12px;
        border-left: 6px solid #FF4D00;
        margin-bottom: 8px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
    }

    /* Input focus colors */
    input { color: #000 !important; }
    
    .stButton > button {
        background: linear-gradient(90deg, #FF4D00, #FF9933);
        color: white !important;
        border-radius: 15px;
        height: 3rem;
        font-weight: bold;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")
display_date = datetime.now().strftime("%A, %d %B %Y")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if not st.session_state.user_session:
    st.markdown(f"""
        <div class="app-header">
            <h1 style="font-size: 2.5rem; margin-bottom: 0;">🚩 श्री राम धाम 🚩</h1>
            <div style="font-size: 1.1rem; opacity: 0.9;">जय श्री राम | राम नाम जाप सेवा</div>
            <div style="margin-top: 15px; font-weight: bold;">📅 {display_date}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center;'>भक्त लॉगिन</h3>", unsafe_allow_html=True)
    u_name = st.text_input("आपका नाम (Name)", placeholder="e.g. Shruti Maurya")
    u_phone = st.text_input("मोबाइल नंबर (Mobile)", placeholder="10 Digit Number", max_chars=10)

    if st.button("🚪 प्रवेश करें (Login)", use_container_width=True):
        if u_name and len(u_phone) == 10:
            user_location = get_user_location()
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, user_location]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
            else:
                idx = df[df['Phone'] == u_phone].index[0]
                df.at[idx, 'Location'] = user_location # Update location on login
            save_db(df)
            st.rerun()

# --- MAIN DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Daily Reset Logic
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    # Header with Location
    st.markdown(f"""
        <div class="app-header">
            <h1 style="margin:0;">🚩 श्री राम धाम 🚩</h1>
            <div style="font-weight:bold; font-size:1.4rem; margin-top:5px;">जय श्री राम, {df.at[user_idx, 'Name']}!</div>
            <div style="font-size:0.9rem; margin-top:5px;">📍 {df.at[user_idx, 'Location']}</div>
        </div>
    """, unsafe_allow_html=True)

    # Stats Row
    today_total = int(df.at[user_idx, 'Today_Count'])
    total_life_jap = int(df.at[user_idx, 'Total_Counts'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='stat-card'><div style='font-size:0.9rem;'>आज की माला</div><h1 style='color:#FF4D00;'>{today_total // 108}</h1></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'><div style='font-size:0.9rem;'>कुल जाप</div><h1 style='color:#FF4D00;'>{total_life_jap}</h1></div>", unsafe_allow_html=True)

    st.divider()

    # Entry Section
    st.subheader("📝 सेवा अपडेट करें")
    mode = st.radio("प्रकार चुनें (Mode):", ["📿 माला (Malas)", "🔢 संख्या (Counts)"], horizontal=True)
    val = st.number_input("विवरण दर्ज करें:", min_value=0, step=1, value=(today_total // 108 if "माला" in mode else today_total))

    if st.button("✅ डेटा सुरक्षित करें", use_container_width=True):
        new_jap = val * 108 if "माला" in mode else val
        old_jap = df.at[user_idx, 'Today_Count']
        
        # Rectification logic
        df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_jap) + new_jap
        df.at[user_idx, 'Today_Count'] = new_jap
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)
        st.balloons()
        st.success("आपकी सेवा सफलतापूर्वक अपडेट हो गई!")
        st.rerun()

    # --- CALENDAR TABS ---
    st.markdown("<br><h3 style='text-align:center;'>📅 वार्षिक कैलेंडर 2026</h3>", unsafe_allow_html=True)
    cal_data = {
        "राम उत्सव 🚩": ["राम नवमी - 27 मार्च", "हनुमान जयंती - 12 अप्रैल", "दीपावली - 9 नवंबर"],
        "एकादशी 🙏": ["षटतिला एकादशी - 14 जनवरी", "जया एकादशी - 29 जनवरी", "आमलकी एकादशी - 14 मार्च"],
        "पावन व्रत 🌙": ["महाशिवरात्रि - 15 फरवरी", "होली - 14 मार्च", "गणेश चतुर्थी - 27 अगस्त"]
    }
    
    tabs = st.tabs(list(cal_data.keys()))
    for i, tab in enumerate(tabs):
        with tab:
            for event in cal_data[list(cal_data.keys())[i]]:
                st.markdown(f"<div class='calendar-card'>🔸 {event}</div>", unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
