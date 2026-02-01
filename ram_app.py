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

# --- ADVANCED DIVINE UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%);
    }

    /* Floating Header */
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important;
        padding: 3rem 1rem;
        border-radius: 0 0 60px 60px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 20px 40px rgba(255, 77, 0, 0.3);
        border-bottom: 5px solid #FFD700;
    }
    
    .app-header h1 { 
        color: #FFFFFF !important; 
        font-weight: 800;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }

    /* Divine Quote Card */
    .quote-card {
        background: rgba(255, 255, 255, 0.4);
        border-radius: 20px;
        padding: 15px;
        font-style: italic;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }

    /* Glass Stat Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(15px);
        padding: 20px;
        border-radius: 30px;
        text-align: center;
        border: 2px solid #FFD700;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        transition: 0.4s ease;
    }
    .stat-card:hover { transform: scale(1.05); box-shadow: 0 15px 45px rgba(255, 128, 0, 0.2); }

    /* Progress Bar */
    .progress-container {
        background-color: #f1f1f1;
        border-radius: 20px;
        margin: 20px 0;
        height: 15px;
        overflow: hidden;
        border: 1px solid #FFD700;
    }
    .progress-bar {
        background: linear-gradient(90deg, #FFD700, #FF4D00);
        height: 100%;
        border-radius: 20px;
        transition: width 1s ease-in-out;
    }

    /* Leaderboard Premium Items */
    .leader-row {
        background: white;
        padding: 15px;
        border-radius: 25px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #FFE0B2;
        box-shadow: 0 5px 15px rgba(0,0,0,0.03);
    }

    /* Interactive Calendar Buttons */
    .cal-day {
        width: 95px; height: 95px;
        background: white;
        border: 2px solid #FFD700;
        border-radius: 25px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        transition: 0.3s;
        cursor: help;
    }
    .cal-day:hover { background: #FFD700 !important; color: white !important; }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #FF4D00, #FFD700);
        color: white !important;
        border-radius: 50px;
        font-weight: 700;
        letter-spacing: 1px;
        border: none;
        padding: 10px 25px;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- QUOTE OF THE DAY ---
quotes = [
    "जिसके हृदय में राम नाम है, उसके लिए संसार का हर काम आसान है।",
    "राम का नाम लो, जीवन का कल्याण करो।",
    "प्रेम और भक्ति का संगम है - श्री राम धाम।",
    "मन को शांत रखो, और राम नाम का जाप करो।"
]

# --- LOGIN / DASHBOARD ---
if 'user_session' not in st.session_state:
    st.session_state.user_session = None

if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>आध्यात्मिक उन्नति का मार्ग</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="quote-card">“{quotes[0]}”</div>', unsafe_allow_html=True)
    
    with st.container():
        u_name = st.text_input("आपका नाम", placeholder="उदा. राम भक्त")
        u_phone = st.text_input("मोबाइल नंबर", max_chars=10, placeholder="99xxxxxxxx")
        
        if st.button("दिव्य प्रवेश करें", use_container_width=True):
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

else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Daily Reset
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div style="font-size:1.2rem;">जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मुख्य", "🏆 रैंकिंग", "📅 कैलेंडर"])

    with tabs[0]:
        # Progress Bar Logic (Target: 108 Malas)
        today_total = int(df.at[user_idx, 'Today_Count'])
        progress_pct = min((today_total / (108 * 108)) * 100, 100)
        
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'><small>आज की माला</small><h2 style='color:#FF4D00;'>{today_total // 108}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'><small>कुल जाप</small><h2 style='color:#FF4D00;'>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <p style='margin-bottom:5px; font-weight:bold;'>दैनिक लक्ष्य प्रगति:</p>
            <div class="progress-container"><div class="progress-bar" style="width: {progress_pct}%"></div></div>
        """, unsafe_allow_html=True)

        mode = st.radio("अपडेट प्रकार:", ["माला", "संख्या"], horizontal=True)
        val = st.number_input("विवरण लिखें:", min_value=0, step=1, value=(today_total // 108 if mode == "माला" else today_total))
        if st.button("✨ डेटा सुरक्षित करें", use_container_width=True):
            new_jap = val * 108 if mode == "माला" else val
            old_jap = df.at[user_idx, 'Today_Count']
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_jap) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.balloons()
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष भक्त")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(5)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            icon = "👑" if i==0 else "⭐"
            st.markdown(f'<div class="leader-row"><span>{icon} <b>{row["Name"]}</b></span><span>{row["Today_Count"] // 108} माला</span></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन उत्सव 2026")
        cal_html = """<div style="display:flex; flex-wrap:wrap; gap:10px; justify-content:center;">
            <div class="cal-day"><b>27 Mar</b><small>राम नवमी</small></div>
            <div class="cal-day"><b>02 Apr</b><small>हनुमान जयंती</small></div>
            <div class="cal-day"><b>09 Nov</b><small>दीपावली</small></div>
        </div>"""
        st.markdown(cal_html, unsafe_allow_html=True)

    # Admin View (Visible only to your number)
    if st.session_state.user_session == ADMIN_NUMBER:
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ एडमिन")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📊 डेटा डाउनलोड", data=csv, file_name='ram_data.csv', mime='text/csv')

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
