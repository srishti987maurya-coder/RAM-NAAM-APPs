import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

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

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF5E6; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem; border-radius: 0 0 40px 40px;
        text-align: center; margin: -1rem -1rem 1rem -1rem;
    }
    .stat-card { background: white; padding: 1.2rem; border-radius: 20px; border: 2px solid #FFE0B2; text-align:center; }
    .cal-item { background: white; border-radius: 15px; padding: 10px; margin-bottom: 10px; border-left: 6px solid #FF4D00; display: flex; align-items: center; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- SESSION HANDLING (The "No Repeat Login" Fix) ---
if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा • जय श्री राम</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 भक्त प्रवेश")
    u_name = st.text_input("आपका नाम")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    
    if st.button("दिव्य प्रवेश", use_container_width=True):
        if u_name and len(u_phone) == 10:
            loc = get_user_location()
            # Save to session
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
            else:
                idx = df[df['Phone'] == u_phone].index[0]
                df.at[idx, 'Location'] = loc
            save_db(df)
            st.rerun()
        else:
            st.error("कृपया सही नाम और 10 अंकों का नंबर डालें।")

# --- MAIN APP (LoggedIn State) ---
else:
    # Ensure user still exists in DB
    if st.session_state.user_session not in df['Phone'].values:
        st.session_state.user_session = None
        st.rerun()

    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Daily Reset
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    # Sidebar Logout
    if st.sidebar.button("🚪 लॉगआउट (Logout)"):
        st.session_state.user_session = None
        st.rerun()

    t_labels = ["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"]
    if st.session_state.user_session in ADMIN_NUMBERS:
        t_labels.append("⚙️ एडमिन")
    
    tabs = st.tabs(t_labels)

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'><small>आज की माला</small><h2>{today_total // 108}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'><small>कुल जाप</small><h2>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        
        st.divider()
        val = st.number_input("माला की संख्या लिखें:", min_value=0, step=1, value=(today_total // 108))
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            new_jap = val * 108
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("अपडेट हो गया!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; margin-bottom:5px; border-left:5px solid #FF9933; display:flex; justify-content:space-between;"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        events = [("27 Mar", "श्री राम नवमी"), ("02 Apr", "हनुमान जयंती"), ("09 Nov", "दीपावली")]
        for date, name in events:
            st.markdown(f'<div class="cal-item"><b>{date}</b> — {name}</div>', unsafe_allow_html=True)

    if st.session_state.user_session in ADMIN_NUMBERS:
        with tabs[3]:
            st.subheader("📊 एडमिन पैनल")
            search_term = st.text_input("🔍 किसी भक्त को ढूंढें (नाम या नंबर)")
            if search_term:
                filtered_df = df[df['Name'].str.contains(search_term, case=False) | df['Phone'].contains(search_term)]
                st.dataframe(filtered_df)
            else:
                st.dataframe(df)
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel डाउनलोड", data=csv, file_name='ram_data.csv')
