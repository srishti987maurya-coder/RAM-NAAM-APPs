import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests  # Required to get location data

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
            # Ensure Location column exists
            if 'Location' not in df.columns: df['Location'] = "Unknown"
            if 'Today_Count' not in df.columns: df['Today_Count'] = 0
            if 'Total_Counts' not in df.columns: df['Total_Counts'] = 0
            return df
        except: pass
    return pd.DataFrame(columns=["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"])

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    """Fetches City and Country based on IP address"""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}"
    except:
        return "Global"

# --- UI CSS FIXES ---
st.markdown("""
    <style>
    /* FIX: Ensure all text is dark/readable on the light background */
    .stMarkdown, p, label, .stHeader, span {
        color: #4A2C00 !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #FFE5B4 0%, #FFF5E6 50%, #FFE0B2 100%);
    }

    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; /* Keep header text white */
        padding: 2rem 1rem;
        border-radius: 0px 0px 30px 30px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }

    .app-header div, .app-header span, .app-header h1 {
        color: white !important; /* Force white for header components */
    }

    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 6px 16px rgba(255, 77, 0, 0.15);
        border: 2px solid #FFE0B2;
    }

    /* Input text color fix */
    input { color: black !important; }

    .welcome-text {
        font-size: 1.3rem;
        color: #FF4D00 !important;
        font-weight: bold;
    }

    .calendar-item {
        color: #4A2C00 !important;
        background: #FFF9F5;
        border-left: 4px solid #FF9933;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")
display_date = datetime.now().strftime("%d %B %Y, %A")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if not st.session_state.user_session:
    st.markdown(f"""
        <div class="app-header">
            <h1 style="margin:0;">🚩 श्री राम धाम 🚩</h1>
            <div style="margin-top:10px;">राम नाम जाप सेवा</div>
            <div class="date-badge">📅 {display_date}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='welcome-card'><p class='welcome-text'>🙏 स्वागत है आपका 🙏</p></div>", unsafe_allow_html=True)
    
    u_name = st.text_input("आपका पावन नाम", placeholder="उदाहरण: राम प्रसाद")
    u_phone = st.text_input("मोबाइल नंबर", placeholder="10 अंकों का नंबर", max_chars=10)

    if st.button("🚪 प्रवेश करें", type="primary"):
        if u_name and len(u_phone) == 10:
            location = get_user_location() # Capture location on login
            st.session_state.user_session = u_phone
            
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, location]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            else:
                # Update location for existing users
                idx = df[df['Phone'] == u_phone].index[0]
                df.at[idx, 'Location'] = location
                save_db(df)
            st.rerun()

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Header
    st.markdown(f"""
        <div class="app-header">
            <h1 style="margin:0;">🚩 श्री राम धाम 🚩</h1>
            <div style="font-weight:bold;">जय श्री राम, {df.at[user_idx, 'Name']}!</div>
            <div style="font-size:0.8rem; opacity:0.8;">📍 {df.at[user_idx, 'Location']}</div>
        </div>
    """, unsafe_allow_html=True)

    # Stats
    today_total = int(df.at[user_idx, 'Today_Count'])
    total_jap = int(df.at[user_idx, 'Total_Counts'])
    
    st.markdown(f"""
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <div class="stat-card" style="flex:1;">
                <div style="font-size:0.8rem;">आज की माला</div>
                <div style="font-size:2rem; font-weight:900; color:#FF4D00;">{today_total // 108}</div>
            </div>
            <div class="stat-card" style="flex:1;">
                <div style="font-size:0.8rem;">कुल जाप</div>
                <div style="font-size:2rem; font-weight:900; color:#FF4D00;">{total_jap}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Update Logic
    entry_type = st.radio("प्रकार:", ["📿 माला", "🔢 जाप"], horizontal=True)
    val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1, value=(today_total // 108 if entry_type == "📿 माला" else today_total))

    if st.button("✅ सेव करें", use_container_width=True):
        final_today = val * 108 if entry_type == "📿 माला" else val
        old_today = df.at[user_idx, 'Today_Count']
        
        df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_today) + final_today
        df.at[user_idx, 'Today_Count'] = final_today
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)
        st.success("डाटा अपडेट हो गया!")
        st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()