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

# --- PREMIUM UI STYLING ---
st.markdown("""
    <style>
    /* Background Gradient */
    .stApp {
        background: linear-gradient(180deg, #FFF5E6 0%, #FFECCC 100%);
    }

    /* Primary Text Color */
    .stMarkdown, p, label, span, li, div, h1, h2, h3 {
        color: #5D4037 !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }

    /* Premium Header */
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF8000 100%);
        color: white !important;
        padding: 3rem 1rem;
        border-radius: 0 0 50px 50px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 15px 35px rgba(255, 77, 0, 0.25);
        border-bottom: 4px solid #FFD700;
    }
    .app-header h1 { color: #FFFFFF !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-size: 2.5rem; }
    .app-header div { color: #FFEB3B !important; font-weight: bold; letter-spacing: 1px; }

    /* Glassmorphism Stat Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 25px;
        text-align: center;
        border: 2px solid #FFD700;
        box-shadow: 0 8px 32px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 12px 40px rgba(255, 128, 0, 0.15); }

    /* Premium Leaderboard Rows */
    .leader-row {
        background: white;
        padding: 15px 20px;
        border-radius: 20px;
        margin-bottom: 12px;
        border-left: 8px solid #FFD700;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* Calendar Grid Styles */
    .cal-container { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; padding: 20px 0; }
    .cal-day {
        width: 100px; height: 100px;
        background: white;
        border: 2px solid #FFD700;
        border-radius: 20px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        position: relative; cursor: pointer;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .cal-day:hover { background: #FFD700 !important; color: #5D4037 !important; transform: scale(1.1); }
    
    .tooltip {
        visibility: hidden; width: 220px; background-color: #3e2723;
        color: #ffffff !important; text-align: center; border-radius: 12px; padding: 12px;
        position: absolute; z-index: 100; bottom: 120%; left: 50%; margin-left: -110px;
        opacity: 0; transition: 0.3s; font-size: 14px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.3); pointer-events: none;
    }
    .cal-day:hover .tooltip { visibility: visible; opacity: 1; }

    /* Login & Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #FF8000, #FF4D00);
        color: white !important;
        border: none;
        border-radius: 15px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background: linear-gradient(90deg, #FF4D00, #FF8000); transform: scale(1.02); }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border: 1px solid #FFD700;
        border-radius: 10px 10px 0 0;
        padding: 8px 16px;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- LOGIN / DASHBOARD LOGIC ---
if 'user_session' not in st.session_state:
    st.session_state.user_session = None

if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>राम नाम जाप सेवा • जय श्री राम</div></div>', unsafe_allow_html=True)
    with st.container():
        st.write("### 🙏 स्वागत है")
        u_name = st.text_input("आपका पावन नाम", placeholder="उदा. राहुल शर्मा")
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
                st.error("कृपया सही जानकारी दर्ज करें।")
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Daily Reset
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:1rem; margin-top:8px;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    t_labels = ["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"]
    if st.session_state.user_session == ADMIN_NUMBER:
        t_labels.append("⚙️ एडमिन")
    
    tabs = st.tabs(t_labels)

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'><small>आज की सेवा</small><h2 style='color:#FF4D00;'>{today_total // 108} माला</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'><small>कुल जाप</small><h2 style='color:#FF4D00;'>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("✨ सेवा अपडेट करें", expanded=True):
            mode = st.radio("प्रकार:", ["पूरी माला", "जाप संख्या"], horizontal=True)
            val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1, value=(today_total // 108 if mode == "पूरी माला" else today_total))
            if st.button("✅ डेटा सुरक्षित करें", use_container_width=True):
                new_jap = val * 108 if mode == "पूरी माला" else val
                old_jap = df.at[user_idx, 'Today_Count']
                df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_jap) + new_jap
                df.at[user_idx, 'Today_Count'] = new_jap
                df.at[user_idx, 'Last_Active'] = today_str
                save_db(df)
                st.success("सफलतापूर्वक अपडेट!")
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        if not leaders.empty:
            for i, (idx, row) in enumerate(leaders.iterrows()):
                crown = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"#{i+1}"
                st.markdown(f'<div class="leader-row"><span><b>{crown}</b> {row["Name"]}</span><span style="color:#FF4D00; font-weight:bold;">{row["Today_Count"] // 108} माला</span></div>', unsafe_allow_html=True)
        else:
            st.info("आज की सेवा अभी शुरू होनी है।")

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        cal_html = """<div class="cal-container">
            <div class="cal-day"><b>15 Feb</b><span style="font-size:10px;">2026</span><div class="tooltip"><b style="color:#FFD700;">महाशिवरात्रि</b><br>शिव-शक्ति मिलन का महापर्व।</div></div>
            <div class="cal-day"><b>14 Mar</b><span style="font-size:10px;">2026</span><div class="tooltip"><b style="color:#FFD700;">होली</b><br>रंगों का उत्सव।</div></div>
            <div class="cal-day"><b>27 Mar</b><span style="font-size:10px;">2026</span><div class="tooltip"><b style="color:#FFD700;">राम नवमी</b><br>प्रभु श्री राम जन्मोत्सव।</div></div>
            <div class="cal-day"><b>02 Apr</b><span style="font-size:10px;">2026</span><div class="tooltip"><b style="color:#FFD700;">हनुमान जयंती</b><br>बजरंगबली जन्मोत्सव।</div></div>
            <div class="cal-day"><b>20 Oct</b><span style="font-size:10px;">2026</span><div class="tooltip"><b style="color:#FFD700;">विजयादशमी</b><br>धर्म की विजय का पर्व।</div></div>
            <div class="cal-day"><b>09 Nov</b><span style="font-size:10px;">2026</span><div class="tooltip"><b style="color:#FFD700;">दीपावली</b><br>दीपों का महाउत्सव।</div></div>
        </div>"""
        st.markdown(cal_html, unsafe_allow_html=True)

    if st.session_state.user_session == ADMIN_NUMBER:
        with tabs[3]:
            st.subheader("📊 एडमिन डेटा")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel डाउनलोड करें", data=csv, file_name='shri_ram_data.csv', mime='text/csv')

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
