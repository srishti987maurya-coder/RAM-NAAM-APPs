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

# --- PREMIUM DIVINE UI & INTERACTIVE CALENDAR CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }

    /* Header Styling */
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem;
        border-radius: 0 0 50px 50px; text-align: center;
        margin: -1rem -1rem 2rem -1rem; box-shadow: 0 15px 30px rgba(255, 77, 0, 0.3);
        border-bottom: 5px solid #FFD700;
    }
    .app-header h1 { color: white !important; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }

    /* Calendar Grid Design */
    .cal-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 15px;
        padding: 20px 0;
    }
    .cal-card {
        background: white;
        border: 2px solid #FFD700;
        border-radius: 20px;
        height: 110px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .cal-card:hover {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        transform: scale(1.1) translateY(-5px);
        box-shadow: 0 15px 30px rgba(255, 77, 0, 0.25);
    }
    .cal-card:hover span { color: white !important; }
    .cal-card b { font-size: 1.1rem; color: #FF4D00; transition: 0.3s; }
    .cal-card:hover b { color: white !important; }

    /* Tooltip Popup */
    .info-tip {
        visibility: hidden; width: 200px; background-color: #3e2723;
        color: #fff !important; text-align: center; border-radius: 12px;
        padding: 12px; position: absolute; z-index: 100;
        bottom: 125%; left: 50%; margin-left: -100px;
        opacity: 0; transition: opacity 0.4s, transform 0.4s;
        font-size: 0.85rem; line-height: 1.4;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.3); pointer-events: none;
    }
    .cal-card:hover .info-tip { visibility: visible; opacity: 1; transform: translateY(-5px); }
    .info-tip::after {
        content: ""; position: absolute; top: 100%; left: 50%; 
        margin-left: -8px; border-width: 8px; border-style: solid;
        border-color: #3e2723 transparent transparent transparent;
    }

    /* Tabs & Buttons */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stButton>button {
        background: linear-gradient(90deg, #FF4D00, #FFD700);
        color: white !important; border-radius: 50px; border: none; font-weight: bold;
    }
    input { color: #000 !important; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>राम नाम जाप सेवा • 2026</div></div>', unsafe_allow_html=True)
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

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    # --- TAB 1: SEVA ---
    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div style='background:white; padding:20px; border-radius:20px; text-align:center; border:2px solid #FFD700;'><small>आज की माला</small><h2 style='color:#FF4D00; margin:0;'>{today_total // 108}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div style='background:white; padding:20px; border-radius:20px; text-align:center; border:2px solid #FFD700;'><small>कुल जाप</small><h2 style='color:#FF4D00; margin:0;'>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        
        st.divider()
        mode = st.radio("अपडेट मोड:", ["पूरी माला", "जाप संख्या"], horizontal=True)
        val = st.number_input("यहाँ संख्या लिखें:", min_value=0, step=1, value=(today_total // 108 if mode == "पूरी माला" else today_total))
        if st.button("✅ डेटा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if mode == "पूरी माला" else val
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.balloons()
            st.rerun()

    # --- TAB 2: LEADERBOARD ---
    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:12px 20px; border-radius:15px; margin-bottom:8px; border-left:6px solid #FFD700; display:flex; justify-content:space-between;"><span><b>#{i+1}</b> {row["Name"]}</span><span style="color:#FF4D00; font-weight:bold;">{row["Today_Count"] // 108} माला</span></div>', unsafe_allow_html=True)

    # --- TAB 3: FULL INTERACTIVE CALENDAR ---
    with tabs[2]:
        st.subheader("📅 पावन वार्षिक कैलेंडर 2026")
        st.write("तिथि पर माउस ले जाएं (Hover करें) महत्व जानने के लिए:")
        
        events = [
            ("14 Jan", "मकर संक्रांति", "सूर्य का उत्तरायण प्रवेश और दान का महापर्व।"),
            ("14 Jan", "षटतिला एकादशी", "तिल के छह प्रकार के उपयोग से पाप मुक्ति।"),
            ("15 Feb", "महाशिवरात्रि", "शिव-शक्ति मिलन और कल्याणकारी रात्रि।"),
            ("14 Mar", "होली", "बुराई पर अच्छाई की जीत और रंगों का उत्सव।"),
            ("14 Mar", "आमलकी एकादशी", "आंवले के वृक्ष की पूजा और श्री विष्णु कृपा।"),
            ("27 Mar", "श्री राम नवमी", "मर्यादा पुरुषोत्तम प्रभु श्री राम जन्मोत्सव।"),
            ("02 Apr", "हनुमान जयंती", "संकटमोचन पवनपुत्र हनुमान का प्राकट्य।"),
            ("20 Oct", "विजयादशमी", "अधर्म पर धर्म की विजय (दशहरा)।"),
            ("09 Nov", "दीपावली", "प्रभु राम के आगमन पर दीपों का महाउत्सव।")
        ]
        
        # Grid building
        grid_html = '<div class="cal-grid">'
        for date, name, desc in events:
            grid_html += f'''
            <div class="cal-card">
                <b>{date}</b>
                <span style="font-size:12px; color:#666;">2026</span>
                <div class="info-tip"><b style="color:#FFD700;">{name}</b><br><hr style="border:0.5px solid rgba(255,255,255,0.2); margin:5px 0;">{desc}</div>
            </div>
            '''
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # Admin Panel (Side feature)
    if st.session_state.user_session == ADMIN_NUMBER:
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ एडमिन")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📊 डेटा एक्सेल डाउनलोड", data=csv, file_name='ram_data.csv', mime='text/csv')

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
