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

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF5E6; }
    .stMarkdown, p, label, span, li, div, h1, h2, h3 { color: #3e2723 !important; font-family: 'Poppins', sans-serif; }
    
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem;
        border-radius: 0 0 40px 40px; text-align: center;
        margin: -1rem -1rem 1rem -1rem; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .app-header * { color: white !important; }
    
    .stat-card {
        background: white; padding: 1.2rem; border-radius: 20px;
        text-align: center; border: 2px solid #FFE0B2;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    /* Elegant Calendar Box Style */
    .cal-box {
        background: white; border: 2px solid #FF9933;
        border-radius: 15px; padding: 15px;
        text-align: center; margin-bottom: 10px;
        transition: 0.3s;
    }
    .cal-box:hover { border-color: #FF4D00; background: #FFF9F5; transform: translateY(-3px); }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा • 2026</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 स्वागत है")
    u_name = st.text_input("आपका पावन नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
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

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    # --- TAB 1: MY SEVA ---
    with t1:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'><small>आज की माला</small><h2 style='color:#FF4D00;'>{today_total // 108}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'><small>कुल जाप</small><h2 style='color:#FF4D00;'>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        
        st.divider()
        mode = st.radio("अपडेट मोड:", ["पूरी माला", "जाप संख्या"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1, value=(today_total // 108 if mode == "पूरी माला" else today_total))
        if st.button("✅ डेटा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if mode == "पूरी माला" else val
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("डेटा अपडेट हो गया!")
            st.rerun()

    # --- TAB 2: LEADERBOARD ---
    with t2:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:12px; border-radius:15px; margin-bottom:8px; border-left:6px solid #FF9933; display:flex; justify-content:space-between;"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    # --- TAB 3: STABLE CALENDAR (No Errors) ---
    with t3:
        st.subheader("📅 पावन वार्षिक कैलेंडर 2026")
        
        events = [
            {"date": "14 Jan", "name": "मकर संक्रांति", "desc": "सूर्य देव का उत्तरायण में प्रवेश।"},
            {"date": "15 Feb", "name": "महाशिवरात्रि", "desc": "भगवान शिव और माता पार्वती का महापर्व।"},
            {"date": "14 Mar", "name": "होली / आमलकी एकादशी", "desc": "रंगों का उत्सव और आंवले के वृक्ष की पूजा।"},
            {"date": "27 Mar", "name": "श्री राम नवमी", "desc": "मर्यादा पुरुषोत्तम भगवान श्री राम का जन्मोत्सव।"},
            {"date": "02 Apr", "name": "हनुमान जयंती", "desc": "पवनपुत्र हनुमान जी का पावन जन्मोत्सव।"},
            {"date": "20 Oct", "name": "विजयादशमी", "desc": "बुराई पर अच्छाई की जीत (दशहरा)।"},
            {"date": "09 Nov", "name": "दीपावली", "desc": "प्रभु राम के आगमन पर दीपों का महापर्व।"}
        ]

        # Using Native Streamlit Columns for stability
        for event in events:
            with st.container():
                col_date, col_info = st.columns([1, 3])
                with col_date:
                    st.markdown(f"<div class='cal-box'><b style='color:#FF4D00;'>{event['date']}</b><br><small>2026</small></div>", unsafe_allow_html=True)
                with col_info:
                    with st.expander(f"✨ {event['name']}"):
                        st.write(event['desc'])

    # Admin Panel
    if st.session_state.user_session == ADMIN_NUMBER:
        st.sidebar.markdown("---")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📊 डेटा एक्सेल डाउनलोड", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
