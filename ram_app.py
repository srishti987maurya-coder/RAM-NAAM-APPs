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

# --- PREMIUM INTERACTIVE UI (CSS ONLY) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    /* Background with soft spiritual gradient */
    .stApp {
        background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%);
    }

    /* Floating Premium Header */
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important;
        padding: 3rem 1rem;
        border-radius: 0 0 50px 50px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 15px 35px rgba(255, 77, 0, 0.3);
        border-bottom: 5px solid #FFD700;
    }
    .app-header h1 { color: white !important; font-weight: 800; text-shadow: 2px 2px 8px rgba(0,0,0,0.2); }
    
    /* Glassmorphism Stat Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 25px;
        text-align: center;
        border: 2px solid #FFD700;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        transition: 0.3s ease-in-out;
    }
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(255, 128, 0, 0.2); }

    /* Interactive Calendar List Design */
    .cal-box {
        background: white;
        border: 2px solid #FF9933;
        border-radius: 15px;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        color: #FF4D00 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #FFE0B2 !important;
        font-weight: 600 !important;
    }

    /* Buttons with Gold Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #FF4D00, #FFD700);
        color: white !important;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 2rem;
        font-weight: bold;
        box-shadow: 0 8px 15px rgba(255, 77, 0, 0.2);
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.03); box-shadow: 0 12px 20px rgba(255, 77, 0, 0.3); }

    /* Input Field Styling */
    input { border-radius: 15px !important; }
    
    /* Leaderboard Style */
    .leader-item {
        background: white;
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        border-left: 8px solid #FFD700;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- APP LOGIC (UNCHANGED AS REQUESTED) ---
df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा • 2026</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 दिव्य प्रवेश")
    u_name = st.text_input("आपका पावन नाम लिखें", placeholder="उदा. राम भक्त")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10, placeholder="99xxxxxxxx")
    if st.button("प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                loc = get_user_location()
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem; margin-top:5px;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'><small>आज की माला</small><h2>{today_total // 108}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'><small>कुल जाप</small><h2>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        st.divider()
        val = st.number_input("संख्या लिखें:", min_value=0, step=1, value=(today_total // 108))
        if st.button("✅ डेटा अपडेट करें", use_container_width=True):
            new_jap = val * 108
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("अपडेट हो गया!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div class="leader-item"><span><b>#{i+1}</b> {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन उत्सव 2026")
        events = [
            ("14 Jan", "मकर संक्रांति", "सूर्य का उत्तरायण प्रवेश।"),
            ("15 Feb", "महाशिवरात्रि", "शिव-शक्ति मिलन का महापर्व।"),
            ("14 Mar", "होली", "रंगों का उत्सव।"),
            ("27 Mar", "श्री राम नवमी", "प्रभु राम का जन्मोत्सव।"),
            ("02 Apr", "हनुमान जयंती", "बजरंगबली जन्मोत्सव।"),
            ("20 Oct", "दशहरा", "धर्म की विजय का पर्व।"),
            ("09 Nov", "दीपावली", "दीपों का महापर्व।")
        ]
        for date, name, desc in events:
            c1, c2 = st.columns([1, 3])
            with c1: st.markdown(f"<div class='cal-box'>{date}</div>", unsafe_allow_html=True)
            with c2: 
                with st.expander(f"✨ {name}"):
                    st.write(desc)

    if st.session_state.user_session in ADMIN_NUMBERS:
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ एडमिन")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📊 डेटा डाउनलोड", data=csv, file_name='ram_data.csv')
    
    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
