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

# --- DATABASE SETUP (Auto-Fix Columns) ---
DB_FILE = "ram_seva_data.csv"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            # Ensure all columns exist to avoid KeyError
            required = ["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"]
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Count" in col else "Global"
            return df
        except:
            pass
    return pd.DataFrame(columns=["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"])

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    """Attempts to fetch location using two different services"""
    try:
        # Try Service 1
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        if 'city' in data:
            return f"{data['city']}, {data['country_name']}"
    except:
        try:
            # Backup Service 2
            response = requests.get('http://ip-api.com/json/', timeout=3)
            data = response.json()
            return f"{data.get('city', 'Unknown')}, {data.get('country', 'Global')}"
        except:
            return "Global (Network Restricted)"
    return "Global"

# --- UI CSS (High Visibility & interactive) ---
st.markdown("""
    <style>
    /* Dark font color for all text to prevent white-on-white issues */
    .stApp, .stMarkdown, p, label, .stHeader, span, li, div {
        color: #3e2723 !important;
        font-weight: 500;
    }
    
    .stApp {
        background: linear-gradient(135deg, #FFE5B4 0%, #FFF5E6 50%, #FFE0B2 100%);
    }

    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important;
        padding: 2.5rem 1rem;
        border-radius: 0px 0px 40px 40px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 10px 25px rgba(255, 77, 0, 0.3);
    }

    .app-header h1, .app-header div, .app-header span {
        color: white !important;
    }

    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        border: 2px solid #FFE0B2;
    }

    /* Fixed white text in input boxes */
    input { color: #000 !important; }

    .calendar-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        border-left: 5px solid #FF4D00;
        margin-bottom: 5px;
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
    st.markdown(f"""<div class="app-header"><h1>🚩 श्री राम धाम 🚩</h1><div>जय श्री राम | राम नाम जाप सेवा</div><div style="margin-top:15px; font-weight:bold;">📅 {display_date}</div></div>""", unsafe_allow_html=True)
    u_name = st.text_input("आपका नाम (Name)")
    u_phone = st.text_input("मोबाइल नंबर (Mobile)", max_chars=10)

    if st.button("🚪 प्रवेश करें (Login)", use_container_width=True):
        if u_name and len(u_phone) == 10:
            user_location = get_user_location()
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, user_location]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
            else:
                idx = df[df['Phone'] == u_phone].index[0]
                df.at[idx, 'Location'] = user_location
            save_db(df)
            st.rerun()

# --- MAIN DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Header showing Location Pin
    st.markdown(f"""
        <div class="app-header">
            <h1 style="margin:0;">🚩 श्री राम धाम 🚩</h1>
            <div style="font-weight:bold; font-size:1.4rem; margin-top:5px;">जय श्री राम, {df.at[user_idx, 'Name']}!</div>
            <div style="font-size:0.95rem; margin-top:5px; background: rgba(0,0,0,0.1); display: inline-block; padding: 2px 10px; border-radius: 10px;">
                📍 {df.at[user_idx, 'Location']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    today_total = int(df.at[user_idx, 'Today_Count'])
    total_life_jap = int(df.at[user_idx, 'Total_Counts'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='stat-card'><div>आज की माला</div><h1 style='color:#FF4D00;'>{today_total // 108}</h1></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'><div>कुल जाप</div><h1 style='color:#FF4D00;'>{total_life_jap}</h1></div>", unsafe_allow_html=True)

    st.divider()

    # Entry Section with Rectification
    st.subheader("📝 सेवा अपडेट करें")
    mode = st.radio("प्रकार:", ["📿 माला (Malas)", "🔢 संख्या (Counts)"], horizontal=True)
    val = st.number_input("यहाँ संख्या लिखें:", min_value=0, step=1, value=(today_total // 108 if "माला" in mode else today_total))

    if st.button("✅ डेटा सुरक्षित करें", use_container_width=True):
        new_jap = val * 108 if "माला" in mode else val
        old_jap = df.at[user_idx, 'Today_Count']
        
        # Adjust Total count based on correction
        df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_jap) + new_jap
        df.at[user_idx, 'Today_Count'] = new_jap
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)
        st.success("सफलतापूर्वक अपडेट किया गया!")
        st.rerun()

    # --- CALENDAR SECTION (Tabs) ---
    st.markdown("<br><h3 style='text-align:center;'>📅 वार्षिक कैलेंडर 2026</h3>", unsafe_allow_html=True)
    cal_data = {
        "राम उत्सव 🚩": ["राम नवमी - 27 मार्च", "हनुमान जयंती - 12 अप्रैल", "विजयादशमी - 20 अक्टूबर", "दीपावली - 9 नवंबर"],
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
