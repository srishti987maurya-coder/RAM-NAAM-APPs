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
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Global')}"
    except:
        return "Global"

# --- UI CSS ---
st.markdown("""
    <style>
    .stApp, .stMarkdown, p, label, .stHeader, span, li, div {
        color: #3e2723 !important;
        font-weight: 500;
    }
    .stApp { background: #FFF5E6; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem;
        border-radius: 0px 0px 40px 40px; text-align: center;
        margin: -1rem -1rem 2rem -1rem; box-shadow: 0 10px 25px rgba(255, 77, 0, 0.3);
    }
    .app-header h1, .app-header div { color: white !important; }
    .stat-card {
        background: white; padding: 1.5rem; border-radius: 20px;
        text-align: center; border: 2px solid #FFE0B2;
    }
    .leaderboard-item {
        background: white; padding: 12px; border-radius: 12px;
        margin-bottom: 8px; border-left: 5px solid #FF9933;
        display: flex; justify-content: space-between; align-items: center;
    }
    input { color: #000 !important; }
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

# ---
