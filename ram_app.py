import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBER = "9999"

# --- DATABASE LOGIC ---
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
    .stApp { background: #FFF5E6; }
    .stMarkdown, p, label, span, li, div, h1, h2, h3 { color: #3e2723 !important; font-weight: 500; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem; border-radius: 0 0 30px 30px;
        text-align: center; margin: -1rem -1rem 1rem -1rem;
    }
    .app-header * { color: white !important; }
    .stat-card { background: white; padding: 1.2rem; border-radius: 15px; text-align: center; border: 1px solid #FFE0B2; }
    .leader-row {
        background: white; padding: 12px; border-radius: 12px; margin-bottom: 8px;
        border-left: 6px solid #FF4D00; display: flex; justify-content: space-between;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
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
    
    # Daily Reset Logic
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    # --- TABS ---
    t_labels = ["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"]
    if st.session_state.user_session == ADMIN_NUMBER:
        t_labels.append("⚙️ एडमिन")
    
    tabs = st.tabs(t_labels)

    # TAB 1: MY SEVA
    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'>आज की माला<h1>{today_total // 108}</h1></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'>कुल जाप<h1>{int(df.at[user_idx, 'Total_Counts'])}</h1></div>", unsafe_allow_html=True)
        
        st.divider()
        mode = st.radio("प्रकार:", ["पूरी माला", "जाप संख्या"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1, value=(today_total // 108 if mode == "पूरी माला" else today_total))
        if st.button("✅ डेटा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if mode == "पूरी माला" else val
            old_jap = df.at[user_idx, 'Today_Count']
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_jap) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("सफलतापूर्वक अपडेट!")
            st.rerun()

    # TAB 2: LEADERBOARD
    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        if not leaders.empty:
            for i, (idx, row) in enumerate(leaders.iterrows()):
                st.markdown(f'<div class="leader-row"><span><b>#{i+1}</b> {row["Name"]}</span><span style="color:#FF4D00; font-weight:bold;">{row["Today_Count"] // 108} माला</span></div>', unsafe_allow_html=True)
        else:
            st.info("आज की सेवा अभी शुरू होनी है।")

    # TAB 3: CALENDAR
    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        cal = {"राम उत्सव": ["राम नवमी - 27 मार्च", "दीपावली - 9 नवंबर"], "एकादशी": ["षटतिला - 14 जन", "आमलकी - 14 मार्च"]}
        for k, v in cal.items():
            with st.expander(k):
                for e in v: st.write(f"🔸 {e}")

    # TAB 4: ADMIN
    if st.session_state.user_session == ADMIN_NUMBER:
        with tabs[3]:
            st.subheader("📊 एडमिन पैनल")
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel/CSV डाउनलोड करें", data=csv, file_name='shri_ram_data.csv', mime='text/csv')

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
