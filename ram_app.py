import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Shri Ram Dham",
    page_icon="🚩",
    layout="centered"
)

# --- DATABASE SETUP (Robust Version) ---
DB_FILE = "ram_seva_data.csv"

def load_db():
    required = ["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Count" in col else "Global"
            return df
        except:
            pass
    return pd.DataFrame(columns=required)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Global')}"
    except:
        return "Global"

# --- STYLING (Fixed Visibility) ---
st.markdown("""
    <style>
    .stApp { background: #FFF5E6; }
    /* Dark text for visibility */
    .stMarkdown, p, label, span, li, div, h1, h2, h3 {
        color: #3e2723 !important;
    }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem;
        border-radius: 0 0 30px 30px; text-align: center;
        margin: -1rem -1rem 1rem -1rem;
    }
    .app-header * { color: white !important; }
    .stat-card {
        background: white; padding: 1.2rem; border-radius: 15px;
        text-align: center; border: 1px solid #FFE0B2;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .leader-row {
        background: white; padding: 10px; border-radius: 10px;
        margin-bottom: 5px; border-left: 5px solid #FF4D00;
        display: flex; justify-content: space-between;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 Shri Ram Dham </h1></div>', unsafe_allow_html=True)
    u_name = st.text_input("Full Name")
    u_phone = st.text_input("Mobile Number", max_chars=10)
    if st.button("Enter App", use_container_width=True):
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
    # Double check if user exists to prevent blank screen
    if st.session_state.user_session not in df['Phone'].values:
        st.session_state.user_session = None
        st.rerun()

    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Daily Reset
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    st.markdown(f'<div class="app-header"><h1>🚩 Shri Ram Dham</h1><div>Jai Shri Ram, {df.at[user_idx, "Name"]}</div><div style="font-size:0.8rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    # --- TABS ---
    t1, t2, t3 = st.tabs(["🏠 My Seva", "🏆 Leaderboard", "📅 Calendar"])

    with t1:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='stat-card'>Today's Malas<h1>{today_total // 108}</h1></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='stat-card'>Total Jaap<h1>{int(df.at[user_idx, 'Total_Counts'])}</h1></div>", unsafe_allow_html=True)
        
        st.divider()
        mode = st.radio("Mode:", ["Malas", "Counts"], horizontal=True)
        val = st.number_input("Enter Number:", min_value=0, step=1, value=(today_total // 108 if mode == "Malas" else today_total))
        
        if st.button("✅ Update Service", use_container_width=True):
            new_jap = val * 108 if mode == "Malas" else val
            old_jap = df.at[user_idx, 'Today_Count']
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_jap) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("Updated Successfully!")
            st.rerun()

    with t2:
        st.subheader("🏆 Today's Top Servants")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        if not leaders.empty:
            for i, (idx, row) in enumerate(leaders.iterrows()):
                st.markdown(f"""<div class="leader-row"><span><b>#{i+1}</b> {row['Name']}</span><span style="color:#FF4D00; font-weight:bold;">{row['Today_Count'] // 108} Malas</span></div>""", unsafe_allow_html=True)
        else:
            st.info("Be the first to start the service today!")

    with t3:
        st.subheader("📅 2026 Holy Calendar")
        st.markdown("""
        - 🔸 **Ram Navami:** 27 March
        - 🔸 **Deepawali:** 9 Nov
        - 🔸 **Mahashivratri:** 15 Feb
        - 🔸 **Holi:** 14 March
        """)

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
