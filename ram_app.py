import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
DB_FILE = "ram_seva_data.csv"
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

# 2026 एकादशी एवं त्यौहार सम्पूर्ण डेटा
CAL_DATA_2026 = {
    "January": {"gap": 3, "days": 31, "events": {14: ("षटतिला एकादशी", "मकर संक्रांति"), 29: ("जया एकादशी", "मोक्ष प्रदायिनी")}},
    "February": {"gap": 6, "days": 28, "events": {13: ("विजया एकादशी", "विजय प्राप्ति"), 27: ("आमलकी एकादशी", "शिवरात्रि")}},
    "March": {"gap": 6, "days": 31, "events": {14: ("पापमोचिनी एकादशी", "पापनाशिनी"), 27: ("राम नवमी", "जन्मोत्सव"), 29: ("कामदा एकादशी", "कामना पूर्ति")}},
    "April": {"gap": 2, "days": 30, "events": {2: ("हनुमान जयंती", "बजरंगबली जन्मोत्सव"), 13: ("वरुथिनी एकादशी", "सौभाग्य"), 28: ("मोहिनी एकादशी", "मोह नाशिनी")}},
    "May": {"gap": 4, "days": 31, "events": {12: ("अपरा एकादशी", "अपार पुण्य"), 27: ("निर्जला एकादशी", "भीमसेनी व्रत")}},
    "June": {"gap": 0, "days": 30, "events": {11: ("योगिनी एकादशी", "काया शोधन"), 26: ("शयनी एकादशी", "चातुर्मास आरंभ")}},
    "July": {"gap": 2, "days": 31, "events": {10: ("कामिका एकादशी", "संकट नाशिनी"), 26: ("पुत्रदा एकादशी", "संतान सुख")}},
    "August": {"gap": 5, "days": 31, "events": {9: ("अजा एकादशी", "पुण्य प्रदायिनी"), 24: ("पार्श्व एकादशी", "परिवर्तिनी")}},
    "September": {"gap": 1, "days": 30, "events": {7: ("इन्दिरा एकादशी", "पितृ मुक्ति"), 22: ("पापांकुशा एकादशी", "पाप मुक्ति")}},
    "October": {"gap": 3, "days": 31, "events": {7: ("रमा एकादशी", "लक्ष्मी पूजन"), 21: ("प्रबोधिनी एकादशी", "देव उत्थान - तुलसी विवाह")}},
    "November": {"gap": 6, "days": 30, "events": {5: ("उत्पन्ना एकादशी", "एकादशी जन्म"), 20: ("मोक्षदा एकादशी", "गीता जयंती")}},
    "December": {"gap": 1, "days": 31, "events": {5: ("सफला एकादशी", "सफलता हेतु"), 20: ("पुत्रदा एकादशी", "पावन पौष व्रत")}}
}

def load_db():
    cols = ["Phone", "Name", "Total_Mala", "Total_Jaap", "Last_Active", "Today_Mala", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype={'Phone': str})
        for c in cols:
            if c not in df.columns: df[c] = 0 if "Jaap" in c or "Mala" in c else "India"
        return df
    return pd.DataFrame(columns=cols)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_broadcast():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, "r", encoding="utf-8") as f: return f.read()
    return ""

def save_broadcast(msg):
    with open(MSG_FILE, "w", encoding="utf-8") as f: f.write(msg)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
    except: return "India"

# --- PREMIUM INTERACTIVE UI CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.4);
    }
    .metric-box {
        background: white; padding: 50px 20px; border-radius: 30px; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); border-top: 10px solid #FFD700; margin-bottom: 25px;
    }
    .calendar-wrapper { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; background: white; padding: 15px; border-radius: 20px; }
    .day-label { text-align: center; font-weight: bold; color: #FF4D00; font-size: 0.8rem; padding-bottom: 5px; }
    .date-cell { aspect-ratio: 1; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 500; position: relative; border: 1px solid #f0f0f0; transition: 0.3s; }
    .has-event { background: #FFF5E6; border: 1.5px solid #FF9933; color: #FF4D00; cursor: pointer; font-weight: bold; }
    .date-cell:hover { transform: scale(1.1); z-index: 10; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .event-tip { visibility: hidden; width: 140px; background: #3e2723; color: white; text-align: center; border-radius: 8px; padding: 8px; position: absolute; bottom: 115%; left: 50%; margin-left: -70px; opacity: 0; transition: 0.3s; font-size: 10px; z-index: 10; }
    .date-cell:hover .event-tip { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- 1. STRICT LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ कृपया सही नाम और 10 अंकों का नंबर भरें।")
        else:
            if u_phone in df['Phone'].values:
                existing_name = df[df['Phone'] == u_phone]['Name'].values[0]
                if u_name.lower() != existing_name.lower():
                    st.error(f"❌ यह नंबर '{existing_name}' के नाम से रजिस्टर्ड है।")
                else:
                    st.session_state.user_session = u_phone
                    st.rerun()
            elif u_name.lower() in df['Name'].str.lower().values:
                st.error(f"❌ '{u_name}' नाम पहले से रजिस्टर्ड है।")
            else:
                loc = get_user_location()
                st.session_state.user_session = u_phone
                new_user = {"Phone": u_phone, "Name": u_name, "Total_Mala": 0, "Total_Jaap": 0, "Last_Active": today_str, "Today_Mala": 0, "Today_Jaap": 0, "Location": loc}
                df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
                save_db(df)
                st.rerun()

# --- 2. DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    # Ekadashi/Broadcast Alert
    b_msg = get_broadcast()
    if b_msg: st.info(f"📢 सन्देश: {b_msg}")
    
    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    with tabs[0]:
        if df.at[user_idx, 'Last_Active'] != today_str:
            df.at[user_idx, 'Today_Mala'] = 0
            df.at[user_idx, 'Today_Jaap'] = 0
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)

        current_j = int(df.at[user_idx, 'Today_Jaap'])
        st.markdown(f"""
            <div class="metric-box">
                <h1 style='color:#FF4D00; margin:0; font-size: 4rem;'>{current_j // 108} माला</h1>
                <p style='color:#666; font-weight: bold;'>आज की कुल सेवा</p>
            </div>
        """, unsafe_allow_html=True)
        
        mode = st.radio("इनपुट तरीका:", ["जाप संख्या (सीधा)", "माला (1 = 108)"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ सेवा जोड़ें", use_container_width=True):
                added = val if mode == "जाप संख्या (सीधा)" else (val * 108)
                df.at[user_idx, 'Today_Jaap'] += added
                df.at[user_idx, 'Today_Mala'] = df.at[user_idx, 'Today_Jaap'] // 108
                df.at[user_idx, 'Total_Jaap'] += added
                df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
                save_db(df)
                st.rerun()
        with c2:
            if st.button("✏️ सुधारें (Reset)", use_container_width=True):
                new_j = val if mode == "जाप संख्या (सीधा)" else (val * 108)
                df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - current_j) + new_j
                df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
                df.at[user_idx, 'Today_Jaap'] = new_j
                df.at[user_idx, 'Today_Mala'] = new_j // 108
                save_db(df)
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के श्रेष्ठ सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, row in leaders.iterrows():
            st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:15px; border-left:5px solid #FF4D00; margin-bottom:10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); display:flex; justify-content:space-between;">
                    <b>{row['Name']} ({row['Location']})</b>
                    <span style="color:#FF4D00; font-weight:bold;">{row['Today_Mala']} माला</span>
                </div>
            """, unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन कैलेंडर 2026")
        sel_m = st.selectbox("महीना चुनें:", list(CAL_DATA_2026.keys()), index=datetime.now().month-1)
        m_info = CAL_DATA_2026[sel_m]
        cols = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            cols[i].markdown(f"<div class='day-label'>{d}</div>", unsafe_allow_html=True)
        grid_html = '<div class="calendar-wrapper">'
        for _ in range(m_info["gap"]): grid_html += '<div class="date-cell" style="border:none;"></div>'
        for d in range(1, m_info["days"] + 1):
            ev = m_info["events"].get(d)
            cls = "has-event" if ev else ""
            tip = f'<div class="event-tip"><b>{ev[0]}</b><br>{ev[1]}</div>' if ev else ""
            grid_html += f'<div class="date-cell {cls}">{d}{tip}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

 # --- ADMIN SIDEBAR ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            
            # 1. यूजर डिलीट करें
            u_list = ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")")
            target = st.selectbox("यूजर डिलीट करें:", u_list)
            if target != "--चुनें--" and st.button("🗑️ डिलीट"):
                df = df[df['Phone'] != target.split("(")[1].replace(")", "")]
                save_db(df)
                st.rerun()
            
            st.divider()
            
            # 2. ब्रॉडकास्ट सन्देश
            new_m = st.text_area("ब्रॉडकास्ट सन्देश:", value=get_broadcast())
            if st.button("📢 सन्देश अपडेट करें"):
                save_broadcast(new_m)
                st.rerun()
                
            st.divider()
            
            # 3. रिमाइंडर फीचर (जिन्होंने आज माला नहीं जोड़ी)
            st.subheader("🔔 सेवा स्मरण (Reminders)")
            inactive_today = df[df['Last_Active'] != today_str]
            
            if not inactive_today.empty:
                st.warning(f"⚠️ {len(inactive_today)} भक्तों ने आज माला नहीं जोड़ी है।")
                
                # चुनिंदा भक्त को WhatsApp मैसेज भेजने का विकल्प
                rem_user = st.selectbox("स्मरण भेजने के लिए चुनें:", ["--भक्त चुनें--"] + inactive_today['Name'].tolist())
                
                if rem_user != "--भक्त चुनें--":
                    u_row = inactive_today[inactive_today['Name'] == rem_user].iloc[0]
                    u_phone = "91" + str(u_row['Phone'])
                    msg = urllib.parse.quote(f"जय श्री राम {rem_user} जी! आज आपकी माला सेवा अभी तक रिकॉर्ड नहीं हुई है। कृपया अपनी सेवा श्री राम धाम ऐप पर दर्ज करें। 🙏🚩")
                    wa_link = f"https://wa.me/{u_phone}?text={msg}"
                    
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn" style="display: block; text-align: center; background: #25D366; color: white; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold;">💬 WhatsApp पर याद दिलाएं</a>', unsafe_allow_html=True)
            else:
                st.success("✅ आज सभी ने सेवा दर्ज की है!")

            st.divider()
            
            # 4. एक्सेल डाउनलोड
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download", data=csv, file_name='ram_data.csv', use_container_width=True)

    # Logout Button
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.user_session = None
        st.rerun()

