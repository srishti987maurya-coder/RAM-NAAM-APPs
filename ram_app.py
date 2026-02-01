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
    # टैब 3: पावन कैलेंडर (Interactive Hover Design)
    with tabs[2]:
        st.subheader("📅 पावन वार्षिक कैलेंडर 2026")
        
        # कैलेंडर डेटा
        holy_events = {
            "2026-01-14": {"event": "षटतिला एकादशी", "desc": "तिल के दान और भगवान विष्णु की पूजा का दिन।"},
            "2026-02-15": {"event": "महाशिवरात्रि", "desc": "भगवान शिव और माता पार्वती के मिलन का महापर्व।"},
            "2026-03-14": {"event": "होली / आमलकी एकादशी", "desc": "रंगों का उत्सव और आंवले के वृक्ष की पूजा।"},
            "2026-03-27": {"event": "श्री राम नवमी", "desc": "मर्यादा पुरुषोत्तम भगवान श्री राम का प्राकट्य उत्सव।"},
            "2026-04-02": {"event": "हनुमान जयंती", "desc": "पवनपुत्र हनुमान जी का जन्मोत्सव।"},
            "2026-10-20": {"event": "विजयादशमी", "desc": "अधर्म पर धर्म की विजय का प्रतीक (दशहरा)।"},
            "2026-11-09": {"event": "दीपावली", "desc": "श्री राम के अयोध्या आगमन पर दीपों का उत्सव।"}
        }

        # CSS for Hover Effect and Grid
        st.markdown("""
            <style>
            .cal-container { 
                display: flex; 
                flex-wrap: wrap; 
                gap: 15px; 
                justify-content: center; 
                padding: 10px;
            }
            .cal-day {
                width: 90px; height: 90px; 
                background: #ffffff; 
                border: 2px solid #FF9933; 
                border-radius: 18px;
                display: flex; flex-direction: column; 
                align-items: center; justify-content: center; 
                position: relative; cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            }
            .cal-day:hover { 
                background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%); 
                color: white !important; 
                transform: scale(1.15);
                z-index: 5;
                box-shadow: 0 8px 16px rgba(255, 77, 0, 0.3);
            }
            .cal-day span { color: inherit; transition: color 0.3s; }
            
            /* Tooltip Style */
            .tooltip {
                visibility: hidden; width: 180px; 
                background-color: #3e2723;
                color: #ffffff !important; text-align: center; 
                border-radius: 10px; padding: 10px;
                position: absolute; z-index: 100;
                bottom: 115%; left: 50%; 
                margin-left: -90px;
                opacity: 0; transition: opacity 0.4s, transform 0.4s;
                font-size: 13px; line-height: 1.4;
                box-shadow: 0px 10px 20px rgba(0,0,0,0.3);
                pointer-events: none;
            }
            .cal-day:hover .tooltip { 
                visibility: visible; 
                opacity: 1;
                transform: translateY(-5px);
            }
            /* Tooltip Arrow */
            .tooltip::after {
                content: ""; position: absolute;
                top: 100%; left: 50%; margin-left: -8px;
                border-width: 8px; border-style: solid;
                border-color: #3e2723 transparent transparent transparent;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<p style='text-align:center;'>तिथियों पर माउस ले जाएँ (Hover करें) महत्व जानने के लिए:</p>", unsafe_allow_html=True)
        
        # HTML Grid Generation
        html_code = '<div class="cal-container">'
        # Sorting dates
        sorted_dates = sorted(holy_events.keys())
        
        for date_str in sorted_dates:
            info = holy_events[date_str]
            d = datetime.strptime(date_str, "%Y-%m-%d")
            day_display = d.strftime("%d %b")
            
            html_code += f'''
            <div class="cal-day">
                <span style="font-weight:bold; font-size:16px;">{day_display}</span>
                <span style="font-size:11px; opacity:0.8;">2026</span>
                <div class="tooltip">
                    <b style="color:#FFD700;">{info['event']}</b><br>
                    <hr style="margin:5px 0; border:0.5px solid rgba(255,255,255,0.2);">
                    {info['desc']}
                </div>
            </div>
            '''
        html_code += '</div>'
        
        st.markdown(html_code, unsafe_allow_html=True)
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


