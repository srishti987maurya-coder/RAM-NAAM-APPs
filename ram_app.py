import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="श्री राम धाम",
    page_icon="🚩",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
# Updated Admin Number as per your request
ADMIN_NUMBER = "9987621091" 

def load_db():
    required = ["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            # Auto-repair missing columns if they don't exist
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Count" in col else "India"
            return df
        except:
            pass
    return pd.DataFrame(columns=required)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    """Fetches user city/country via IP."""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'India')}"
    except:
        return "India"
    return "India"

# --- GLOBAL STYLING ---
st.markdown("""
    <style>
    .stApp { background: #FFF5E6; }
    /* Visibility Fix: Dark Brown text */
    .stMarkdown, p, label, span, li, div, h1, h2, h3 {
        color: #3e2723 !important;
        font-weight: 500;
    }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem;
        border-radius: 0 0 30px 30px; text-align: center;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .app-header h1, .app-header div { color: white !important; }
    .stat-card {
        background: white; padding: 1.5rem; border-radius: 20px;
        text-align: center; border: 2px solid #FFE0B2;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .leader-row {
        background: white; padding: 12px; border-radius: 12px;
        margin-bottom: 8px; border-left: 6px solid #FF4D00;
        display: flex; justify-content: space-between;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* Calendar Grid Styles */
    .cal-container { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; padding: 20px 0; }
    .cal-day {
        width: 90px; height: 90px; background: white; border: 2px solid #FF9933; 
        border-radius: 18px; display: flex; flex-direction: column; 
        align-items: center; justify-content: center; position: relative; cursor: pointer;
        transition: all 0.3s ease;
    }
    .cal-day:hover { background: #FF4D00 !important; transform: scale(1.1); z-index: 10; }
    .cal-day:hover span { color: white !important; }
    .tooltip {
        visibility: hidden; width: 200px; background-color: #3e2723;
        color: #ffffff !important; text-align: center; border-radius: 10px; padding: 10px;
        position: absolute; z-index: 100; bottom: 110%; left: 50%; margin-left: -100px;
        opacity: 0; transition: opacity 0.3s; font-size: 13px; line-height: 1.4;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.3); pointer-events: none;
    }
    .cal-day:hover .tooltip { visibility: visible; opacity: 1; }
    input { color: #000 !important; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
    
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
        else:
            st.warning("कृपया नाम और 10 अंकों का मोबाइल नंबर सही भरें।")

# --- MAIN APP ---
else:
    if st.session_state.user_session not in df['Phone'].values:
        st.session_state.user_session = None
        st.rerun()

    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Daily Reset Logic
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)

    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem; margin-top:5px;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    # Tabs Configuration
    tabs_labels = ["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"]
    if st.session_state.user_session == ADMIN_NUMBER:
        tabs_labels.append("⚙️ एडमिन")
    
    tabs = st.tabs(tabs_labels)

    # --- TAB 1: MY SEVA ---
    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='stat-card'>आज की माला<h1>{today_total // 108}</h1></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='stat-card'>कुल जाप<h1>{int(df.at[user_idx, 'Total_Counts'])}</h1></div>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📝 सेवा दर्ज या सुधारें")
        mode = st.radio("प्रकार चुनें:", ["पूरी माला", "जाप संख्या"], horizontal=True)
        val = st.number_input("संख्या लिखें:", min_value=0, step=1, value=(today_total // 108 if mode == "पूरी माला" else today_total))
        
        if st.button("✅ डेटा अपडेट करें", use_container_width=True):
            new_jap = val * 108 if mode == "पूरी माला" else val
            old_jap = df.at[user_idx, 'Today_Count']
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_jap) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("सफलतापूर्वक अपडेट हो गया!")
            st.rerun()

    # --- TAB 2: LEADERBOARD ---
    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        if not leaders.empty:
            for i, (idx, row) in enumerate(leaders.iterrows()):
                st.markdown(f"""
                <div class="leader-row">
                    <span><b>#{i+1}</b> {row['Name']} <small>({row['Location']})</small></span>
                    <span style="color:#FF4D00; font-weight:bold;">{row['Today_Count'] // 108} माला</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("आज की सेवा अभी शुरू होनी है।")

    # --- TAB 3: INTERACTIVE CALENDAR ---
    with tabs[2]:
        st.subheader("📅 पावन वार्षिक कैलेंडर 2026")
        st.write("तिथि का महत्व जानने के लिए उस पर माउस ले जाएं (Hover करें):")
        
        html_calendar = """
        <div class="cal-container">
            <div class="cal-day">
                <span style="font-weight:bold; font-size:16px;">15 Feb</span>
                <span style="font-size:11px; opacity:0.8;">2026</span>
                <div class="tooltip"><b style="color:#FFD700;">महाशिवरात्रि</b><br><hr style='opacity:0.3;'>भगवान शिव और माता पार्वती का महापर्व।</div>
            </div>
            <div class="cal-day">
                <span style="font-weight:bold; font-size:16px;">14 Mar</span>
                <span style="font-size:11px; opacity:0.8;">2026</span>
                <div class="tooltip"><b style="color:#FFD700;">होली</b><br><hr style='opacity:0.3;'>रंगों का उत्सव और आमलकी एकादशी व्रत।</div>
            </div>
            <div class="cal-day">
                <span style="font-weight:bold; font-size:16px;">27 Mar</span>
                <span style="font-size:11px; opacity:0.8;">2026</span>
                <div class="tooltip"><b style="color:#FFD700;">श्री राम नवमी</b><br><hr style='opacity:0.3;'>भगवान श्री राम का पावन प्राकट्य उत्सव।</div>
            </div>
            <div class="cal-day">
                <span style="font-weight:bold; font-size:16px;">02 Apr</span>
                <span style="font-size:11px; opacity:0.8;">2026</span>
                <div class="tooltip"><b style="color:#FFD700;">हनुमान जयंती</b><br><hr style='opacity:0.3;'>पवनपुत्र हनुमान जी का जन्मोत्सव।</div>
            </div>
            <div class="cal-day">
                <span style="font-weight:bold; font-size:16px;">20 Oct</span>
                <span style="font-size:11px; opacity:0.8;">2026</span>
                <div class="tooltip"><b style="color:#FFD700;">विजयादशमी</b><br><hr style='opacity:0.3;'>अधर्म पर धर्म की विजय का प्रतीक दशहरा।</div>
            </div>
            <div class="cal-day">
                <span style="font-weight:bold; font-size:16px;">09 Nov</span>
                <span style="font-size:11px; opacity:0.8;">2026</span>
                <div class="tooltip"><b style="color:#FFD700;">दीपावली</b><br><hr style='opacity:0.3;'>श्री राम के अयोध्या आगमन पर दीपोत्सव।</div>
            </div>
        </div>
        """
        st.markdown(html_calendar, unsafe_allow_html=True)

    # --- TAB 4: ADMIN PANEL ---
    if st.session_state.user_session == ADMIN_NUMBER:
        with tabs[3]:
            st.subheader("📊 एडमिन डेटा मैनेजमेंट")
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Excel (CSV) फॉर्मेट में डाउनलोड करें",
                data=csv_data,
                file_name=f'ram_seva_data_{today_str}.csv',
                mime='text/csv',
            )

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
