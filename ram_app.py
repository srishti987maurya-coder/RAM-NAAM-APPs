import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
# एक्सेल में हिस्ट्री रखने के लिए नई फाइल का नाम
DB_FILE = "ram_seva_history.csv" 
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

# 2026 एकादशी एवं त्यौहार सम्पूर्ण डेटा
ALL_EVENTS_2026 = {
    "January": {"gap": 3, "days": 31, "events": {1: ("Pradosh Vrat (S)", "Trayodashi"), 3: ("Paush Purnima", "Purnima Vrat"), 6: ("Sankashti Chaturthi", "Ganesh Pujan"), 14: ("Shattila Ekadashi", "Makar Sankranti"), 16: ("Pradosh Vrat (K)", "Masik Shivaratri"), 18: ("Magha Amavasya", "Mauni Amavasya"), 23: ("Basant Panchmi", "Saraswati Puja"), 29: ("Jaya Ekadashi", "Bhami Ekadashi"), 30: ("Pradosh Vrat (S)", "Trayodashi")}},
    "February": {"gap": 6, "days": 28, "events": {1: ("Magha Purnima", "Vrat"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"), 13: ("Vijaya Ekadashi", "Kumbha Sankranti"), 14: ("Pradosh Vrat (K)", "Vrat"), 15: ("Mahashivratri", "Shivaratri"), 17: ("Phalguna Amavasya", "Vrat"), 27: ("Amalaki Ekadashi", "Vrat"), 28: ("Pradosh Vrat (S)", "Vrat")}},
    "March": {"gap": 6, "days": 31, "events": {3: ("Holika Dahan", "Purnima"), 4: ("Holi", "Colors"), 6: ("Sankashti Chaturthi", "Ganesh Pujan"), 15: ("Papmochani Ekadashi", "Sankranti"), 16: ("Pradosh Vrat (K)", "Vrat"), 17: ("Masik Shivaratri", "Vrat"), 19: ("Gudi Padwa", "Ghatasthapana"), 20: ("Cheti Chand", "Jhulelal Jayanti"), 26: ("Ram Navami", "Janmotsav"), 29: ("Kamada Ekadashi", "Vrat"), 30: ("Pradosh Vrat (S)", "Vrat")}},
    "April": {"gap": 2, "days": 30, "events": {2: ("Hanuman jayanti", "Purnima"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"), 13: ("Varuthini Ekadashi", "Vrat"), 14: ("Mesha Sankranti", "Solar New Year"), 19: ("Akshaya Tritiya", "Vrat"), 27: ("Mohini Ekadashi", "Vrat"), 28: ("Pradosh Vrat (S)", "Vrat")}},
    "May": {"gap": 4, "days": 31, "events": {1: ("Vaishakha Purnima", "Vrat"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"), 13: ("Apara Ekadashi", "Vrat"), 14: ("Pradosh Vrat (K)", "Vrat"), 16: ("Jyeshtha Amavasya", "Vrat"), 27: ("Padmini Ekadashi", "Vrat"), 28: ("Pradosh Vrat (S)", "Vrat"), 31: ("Purnima Vrat", "Vrat")}},
    "June": {"gap": 0, "days": 30, "events": {3: ("Sankashti Chaturthi", "Ganesh Pujan"), 11: ("Parama Ekadashi", "Vrat"), 12: ("Pradosh Vrat (K)", "Vrat"), 15: ("Amavasya", "Sankranti"), 25: ("Nirjala Ekadashi", "Bhim Ekadashi"), 27: ("Pradosh Vrat (S)", "Vrat"), 29: ("Jyeshtha Purnima", "Vrat")}},
    "July": {"gap": 2, "days": 31, "events": {3: ("Sankashti Chaturthi", "Ganesh Pujan"), 10: ("Yogini Ekadashi", "Vrat"), 12: ("Masik Shivaratri", "Vrat"), 14: ("Ashadha Amavasya", "Deep Puja"), 16: ("Jagannath Rath Yatra", "Sankranti"), 25: ("Deva Shayani Ekadashi", "Ashadhi"), 29: ("Guru Purnima", "Purnima")}},
    "August": {"gap": 5, "days": 31, "events": {2: ("Sankashti Chaturthi", "Ganesh Pujan"), 9: ("Kamika Ekadashi", "Vrat"), 12: ("Shravana Amavasya", "Vrat"), 15: ("Hariyali Teej", "Vrat"), 17: ("Nag Panchami", "Sankranti"), 23: ("Shravana Putrada Ekadashi", "Vrat"), 28: ("Raksha Bandhan", "Purnima"), 31: ("Kajari Teej", "Vrat")}},
    "September": {"gap": 1, "days": 30, "events": {4: ("Janmashtami", "Krishna Janm"), 7: ("Aja Ekadashi", "Vrat"), 14: ("Ganesh Chaturthi", "Utsav"), 22: ("Parivartini Ekadashi", "Vrat"), 25: ("Anant Chaturdashi", "Visarjan"), 26: ("Bhadrapada Purnima", "Shradh Start")}},
    "October": {"gap": 3, "days": 31, "events": {6: ("Indira Ekadashi", "Vrat"), 10: ("Ashwin Amavasya", "Shradh End"), 11: ("Sharad Navratri", "Ghatasthapana"), 19: ("Durga Ashtami", "Maha Navami"), 20: ("Dussehra", "Vijayadashami"), 22: ("Papankusha Ekadashi", "Vrat"), 26: ("Ashwin Purnima", "Sharad Purnima"), 29: ("Karva Chauth", "Vrat")}},
    "November": {"gap": 6, "days": 30, "events": {5: ("Rama Ekadashi", "Vrat"), 6: ("Dhanteras", "Vrat"), 8: ("Diwali", "Laxmi Pujan"), 9: ("Kartik Amavasya", "Vrat"), 10: ("Govardhan Puja", "Utsav"), 11: ("Bhai Dooj", "Utsav"), 20: ("Devutthana Ekadashi", "Tulsi Vivah"), 24: ("Kartik Purnima", "Dev Diwali")}},
    "December": {"gap": 1, "days": 31, "events": {4: ("Utpanna Ekadashi", "Vrat"), 8: ("Margashirsha Amavasya", "Vrat"), 20: ("Mokshada Ekadashi", "Gita Jayanti"), 23: ("Margashirsha Purnima", "Dattatreya Jayanti")}}
}

def load_db():
    # अब डेटा का ढांचा तारीख-वार होगा ताकि पुराना डेटा डिलीट न हो
    cols = ["Date", "Phone", "Name", "Mala", "Jaap", "Location"]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'Phone': str})
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

# --- UI CSS ---
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
    .calendar-container {
        display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px;
        background: white; padding: 20px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .day-header { text-align: center; font-weight: bold; color: #FF4D00; font-size: 0.8rem; }
    .date-box {
        aspect-ratio: 1; border: 1px solid #f8f8f8; border-radius: 12px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 500; position: relative; transition: 0.2s; font-size: 1rem;
    }
    .paksha-txt { font-size: 0.55rem; color: #888; margin-top: 2px; }
    .event-day { background: #FFF5E6; border: 1.5px solid #FF9933; color: #FF4D00; font-weight: bold; cursor: pointer; }
    .date-box:hover { transform: scale(1.1); z-index: 5; box-shadow: 0 8px 20px rgba(0,0,0,0.1); background: #FFF; }
    .event-day:hover { background: #FF4D00 !important; color: white !important; }
    .hover-msg {
        visibility: hidden; width: 150px; background: #3e2723; color: white;
        text-align: center; border-radius: 8px; padding: 8px; position: absolute;
        bottom: 120%; left: 50%; margin-left: -75px; opacity: 0; transition: 0.3s;
        font-size: 10px; z-index: 100; line-height: 1.3;
    }
    .date-box:hover .hover-msg { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- 1. LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ कृपया सही विवरण भरें।")
        else:
            # एक्सेल लॉजिक: चेक करें कि क्या यूजर पहले से है
            if u_phone in df['Phone'].values:
                st.session_state.user_session = u_phone
                st.session_state.user_name = df[df['Phone'] == u_phone]['Name'].iloc[0]
            else:
                st.session_state.user_session = u_phone
                st.session_state.user_name = u_name
            st.rerun()

# --- 2. DASHBOARD ---
else:
    u_phone = st.session_state.user_session
    u_name = st.session_state.user_name
    
    # एक्सेल लॉजिक: यूजर का डेटा कैलकुलेट करना
    user_history = df[df['Phone'] == u_phone]
    today_mala = user_history[user_history['Date'] == today_str]['Mala'].sum()
    total_mala = user_history['Mala'].sum()

    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {u_name}</div></div>', unsafe_allow_html=True)

    b_msg = get_broadcast()
    if b_msg: st.info(f"📢 सन्देश: {b_msg}")
    
    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    with tabs[0]:
        st.markdown(f"""
            <div class="metric-box">
                <h1 style='color:#FF4D00; margin:0; font-size: 4rem;'>{int(today_mala)} माला</h1>
                <p style='color:#666; font-weight: bold;'>आज की सेवा ({today_str})</p>
                <hr style='border: 0.5px solid #eee;'>
                <h3 style='color:#FF9933;'>कुल सेवा (Lifetime): {int(total_mala)} माला</h3>
            </div>
        """, unsafe_allow_html=True)
        
        mode = st.radio("इनपुट तरीका:", ["माला (1 = 108)", "जाप संख्या (सीधा)"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1)
        
        if st.button("➕ सेवा जमा करें", use_container_width=True):
            if val > 0:
                loc = get_user_location()
                # एक्सेल लॉजिक: नई एंट्री जोड़ना (Purana data overwite nahi hoga)
                added_mala = val if mode == "माला (1 = 108)" else (val // 108)
                added_jaap = (val * 108) if mode == "माला (1 = 108)" else val
                
                new_entry = {
                    "Date": today_str,
                    "Phone": u_phone,
                    "Name": u_name,
                    "Mala": added_mala,
                    "Jaap": added_jaap,
                    "Location": loc
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_db(df)
                st.success("भगवान श्री राम आपकी सेवा स्वीकार करें!")
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 पावन लीडरबोर्ड (कुल सेवा)")
        # एक्सेल लॉजिक: ग्रुपिंग करके टोटल दिखाना ताकि लीडरबोर्ड सही रहे
        leaders = df.groupby(['Phone', 'Name', 'Location'])['Mala'].sum().reset_index()
        leaders = leaders.sort_values(by="Mala", ascending=False).head(15)
        
        if leaders.empty:
            st.info("🙏 अभी सेवा का आरंभ होना शेष है।")
        else:
            for i, row in leaders.iterrows():
                rank = leaders.index.get_loc(i) + 1
                bg, medal = ("#FFD700", "🥇") if rank == 1 else ("#E0E0E0", "🥈") if rank == 2 else ("#CD7F32", "🥉") if rank == 3 else ("white", "💠")
                
                st.markdown(f"""
                    <div style="background:{bg}; padding:15px; border-radius:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:1.5rem;">{medal}</span>
                            <div>
                                <b style="font-size:1.1rem; color:#333;">{row['Name']}</b><br>
                                <small style="color:#666;">📍 {row['Location']}</small>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:#FF4D00; font-weight:bold; font-size:1.2rem;">{int(row['Mala'])}</span>
                            <span style="font-size:0.9rem; color:#444;"> कुल माला</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन तिथि कैलेंडर 2026")
        selected_m = st.selectbox("महीना चुनें:", list(ALL_EVENTS_2026.keys()), index=datetime.now().month-1)
        m_info = ALL_EVENTS_2026[selected_m]

        cols = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            cols[i].markdown(f"<div class='day-header'>{d}</div>", unsafe_allow_html=True)

        grid_html = '<div class="calendar-container">'
        for _ in range(m_info["gap"]):
            grid_html += '<div class="date-box" style="border:none; opacity:0;"></div>'
            
        for d in range(1, m_info["days"] + 1):
            ev = m_info["events"].get(d)
            paksha = "शुक्ल पक्ष" if d <= 15 else "कृष्ण पक्ष"
            if d == 15: paksha = "पूर्णिमा"
            if d == m_info["days"]: paksha = "अमावस्या"
            
            if ev:
                name, info = ev
                msg = f'<div class="hover-msg"><b>{name}</b><br>{info}</div>'
                grid_html += f'<div class="date-box event-day">{d}<div class="paksha-txt">{paksha}</div>{msg}</div>'
            else:
                grid_html += f'<div class="date-box">{d}<div class="paksha-txt">{paksha}</div></div>'
                
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
        st.caption("🚩 टीप: नारंगी बॉर्डर वाले दिनों पर माउस ले जाएं।")

    # --- ADMIN SIDEBAR ---
    if u_phone in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            # एक्सेल लॉजिक: पूरी हिस्ट्री डाउनलोड करना
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Download Excel Report (History)", data=csv, file_name=f'ram_seva_history_{today_str}.csv', use_container_width=True)
            
            st.divider()
            new_m = st.text_area("ब्रॉडकास्ट सन्देश:", value=get_broadcast())
            if st.button("📢 सन्देश अपडेट करें"):
                save_broadcast(new_m)
                st.rerun()
            
            st.divider()
            # रिमाइंडर लॉजिक (जो आज हिस्ट्री में नहीं हैं)
            entered_today = df[df['Date'] == today_str]['Phone'].unique()
            all_users = df.groupby('Phone').last().reset_index()
            pending = all_users[~all_users['Phone'].isin(entered_today)]

            if not pending.empty:
                st.warning(f"⚠️ {len(pending)} पेंडिंग")
                rem_user_sel = st.selectbox("स्मरण भेजें:", ["--चुनें--"] + pending['Name'].tolist())
                if rem_user_sel != "--चुनें--":
                    u_row = pending[pending['Name'] == rem_user_sel].iloc[0]
                    u_ph = "91" + str(u_row['Phone'])
                    msg_txt = urllib.parse.quote(f"जय श्री राम {rem_user_sel} जी! आज की माला सेवा रिकॉर्ड नहीं हुई है। 🙏🚩")
                    st.markdown(f'<a href="https://wa.me/{u_ph}?text={msg_txt}" target="_blank" style="background:#25D366; color:white; padding:10px; border-radius:10px; text-decoration:none; display:block; text-align:center; font-weight:bold;">💬 WhatsApp</a>', unsafe_allow_html=True)

    if st.sidebar.button("Logout 🚪"):
        st.session_state.user_session = None
        st.rerun()
