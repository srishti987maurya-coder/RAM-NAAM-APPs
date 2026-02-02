import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
DB_FILE = "ram_seva_data.csv"
MSG_FILE = "broadcast_msg.txt"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

# 2026 एकादशी एवं त्यौहार सम्पूर्ण डेटा (As per your list)
ALL_EVENTS_2026 = {
    "January": {
        "gap": 3, "days": 31,
        "events": {
            1: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
            3: ("Paush Purnima Vrat", "Satyanarayan Puja"),
            6: ("Sankashti Chaturthi", "Ganesh Pujan"),
            14: ("Shattila Ekadashi", "Pongal, Uttarayan, Makar Sankranti"),
            16: ("Pradosh Vrat (K)", "Masik Shivaratri"),
            18: ("Magha Amavasya", "Mauni Amavasya"),
            23: ("Basant Panchmi", "Saraswati Puja"),
            29: ("Jaya Ekadashi", "Bhami Ekadashi"),
            30: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi")
        }
    },
    "February": {
        "gap": 6, "days": 28,
        "events": {
            1: ("Magha Purnima Vrat", "Purnima Seva"),
            5: ("Sankashti Chaturthi", "Ganesh Pujan"),
            13: ("Vijaya Ekadashi", "Kumbha Sankranti"),
            14: ("Pradosh Vrat (K)", "Krishna Paksha"),
            15: ("Mahashivratri", "Masik Shivaratri"),
            17: ("Phalguna Amavasya", "Amavasya Seva"),
            27: ("Amalaki Ekadashi", "Amla Tree Worship"),
            28: ("Pradosh Vrat (S)", "Shukla Paksha")
        }
    },
    "March": {
        "gap": 6, "days": 31,
        "events": {
            3: ("Holika Dahan", "Phalguna Purnima"), 4: ("Holi", "Dhulivandan"),
            6: ("Sankashti Chaturthi", "Ganesh Pujan"), 15: ("Papmochani Ekadashi", "Meena Sankranti"),
            16: ("Pradosh Vrat (K)", "Krishna Paksha"), 17: ("Masik Shivaratri", "Shiv Seva"),
            19: ("Gudi Padwa", "Chaitra Navratri, Ugadi, Ghatasthapana"),
            20: ("Cheti Chand", "Jhulelal Jayanti"), 26: ("Ram Navami", "Prabhu Shri Ram Janmotsav"),
            27: ("Navratri Parana", "Navratri Conclusion"), 29: ("Kamada Ekadashi", "Fulfillment of Desires"),
            30: ("Pradosh Vrat (S)", "Shukla Paksha")
        }
    },
    "April": {
        "gap": 2, "days": 30,
        "events": {
            2: ("Hanuman jayanti", "Chaitra Purnima"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"),
            13: ("Varuthini Ekadashi", "Fortune Seva"), 14: ("Mesha Sankranti", "Solar New Year"),
            15: ("Pradosh Vrat (K)", "Masik Shivaratri"), 17: ("Vaishakha Amavasya", "Amavasya Seva"),
            19: ("Akshaya Tritiya", "Gold buying & Charity"), 27: ("Mohini Ekadashi", "Vishnu Mohini Avatar"),
            28: ("Pradosh Vrat (S)", "Shukla Paksha")
        }
    },
    "May": {
        "gap": 4, "days": 31,
        "events": {
            1: ("Vaishakha Purnima Vrat", "Purnima Seva"), 5: ("Sankashti Chaturthi", "Ganesh Pujan"),
            13: ("Apara Ekadashi", "Infinite Merits"), 14: ("Pradosh Vrat (K)", "Krishna Paksha"),
            15: ("Masik Shivaratri", "Vrishabha Sankranti"), 16: ("Jyeshtha Amavasya", "Amavasya Seva"),
            27: ("Padmini Ekadashi", "Kamala Ekadashi"), 28: ("Pradosh Vrat (S)", "Shukla Paksha"),
            31: ("Purnima Vrat", "Jyeshtha Purnima")
        }
    },
    "June": {
        "gap": 0, "days": 30,
        "events": {
            3: ("Sankashti Chaturthi", "Ganesh Pujan"), 11: ("Parama Ekadashi", "Adhik Maas Special"),
            12: ("Pradosh Vrat (K)", "Krishna Paksha"), 13: ("Masik Shivaratri", "Shiv Seva"),
            15: ("Amavasya", "Mithuna Sankranti"), 25: ("Nirjala Ekadashi", "Pandav Bhim Ekadashi"),
            27: ("Pradosh Vrat (S)", "Shukla Paksha"), 29: ("Jyeshtha Purnima Vrat", "Purnima Seva")
        }
    },
    "July": {
        "gap": 2, "days": 31,
        "events": {
            3: ("Sankashti Chaturthi", "Ganesh Pujan"), 10: ("Yogini Ekadashi", "Health Seva"),
            12: ("Masik Shivaratri", "Pradosh Vrat (K)"), 14: ("Ashadha Amavasya", "Deep Puja"),
            16: ("Jagannath Rath Yatra", "Karka Sankranti"), 25: ("Deva Shayani Ekadashi", "Ashadhi Ekadashi"),
            26: ("Pradosh Vrat (S)", "Shukla Paksha"), 29: ("Guru Purnima", "Ashadha Purnima")
        }
    },
    "August": {
        "gap": 5, "days": 31,
        "events": {
            2: ("Sankashti Chaturthi", "Ganesh Pujan"), 9: ("Kamika Ekadashi", "Ashadha Special"),
            10: ("Pradosh Vrat (K)", "Krishna Paksha"), 11: ("Masik Shivaratri", "Shiv Seva"),
            12: ("Shravana Amavasya", "Pithori Amavasya"), 15: ("Hariyali Teej", "Independence Day"),
            17: ("Nag Panchami", "Simha Sankranti"), 23: ("Shravana Putrada Ekadashi", "Progeny Luck"),
            25: ("Pradosh Vrat (S)", "Shukla Paksha"), 26: ("Onam", "Thiruvonam"),
            28: ("Raksha Bandhan", "Shravana Purnima"), 31: ("Sankashti Chaturthi", "Kajari Teej")
        }
    },
    "September": {
        "gap": 1, "days": 30,
        "events": {
            4: ("Janmashtami", "Shri Krishna Janmotsav"), 7: ("Aja Ekadashi", "Punya Seva"),
            8: ("Pradosh Vrat (K)", "Krishna Paksha"), 9: ("Masik Shivaratri", "Shiv Seva"),
            11: ("Bhadrapada Amavasya", "Shradh Start"), 14: ("Ganesh Chaturthi", "Hartalika Teej"),
            17: ("Kanya Sankranti", "Vishwakarma Puja"), 22: ("Parivartini Ekadashi", "Vishnu side-turn date"),
            24: ("Pradosh Vrat (S)", "Shukla Paksha"), 25: ("Anant Chaturdashi", "Ganesh Visarjan"),
            26: ("Bhadrapada Purnima Vrat", "Shradh Start"), 29: ("Sankashti Chaturthi", "Ganesh Pujan")
        }
    },
    "October": {
        "gap": 3, "days": 31,
        "events": {
            6: ("Indira Ekadashi", "Ancestors Salvation"), 8: ("Pradosh Vrat (K)", "Masik Shivaratri"),
            10: ("Ashwin Amavasya", "Sarva Pitru Amavasya"), 11: ("Sharad Navratri", "Ghatasthapana"),
            16: ("Kalparambha", "Durga Puja Start"), 17: ("Tula Sankranti", "Navpatrika Puja"),
            19: ("Durga Maha Navami Puja", "Navami Seva"), 20: ("Dussehra", "Vijayadashami"),
            21: ("Durga Visarjan", "Sindoor Khela"), 22: ("Papankusha Ekadashi", "Shield from Sins"),
            23: ("Pradosh Vrat (S)", "Shukla Paksha"), 26: ("Ashwin Purnima Vrat", "Sharad Purnima"),
            29: ("Sankashti Chaturthi", "Karva Chauth")
        }
    },
    "November": {
        "gap": 6, "days": 30,
        "events": {
            5: ("Rama Ekadashi", "Diwali Prep"), 6: ("Dhanteras", "Pradosh Vrat (K)"),
            7: ("Masik Shivaratri", "Shiv Seva"), 8: ("Diwali", "Laxmi Pujan"),
            9: ("Kartik Amavasya", "Amavasya Seva"), 10: ("Govardhan Puja", "Annakut"),
            11: ("Bhai Dooj", "Yama Dwitiya"), 15: ("Chhath Puja", "Sun Worship"),
            16: ("Vrischika Sankranti", "Solar Entry"), 20: ("Devutthana Ekadashi", "Tulsi Vivah"),
            22: ("Pradosh Vrat (S)", "Shukla Paksha"), 24: ("Kartik Purnima Vrat", "Dev Diwali"),
            27: ("Sankashti Chaturthi", "Ganesh Pujan")
        }
    },
    "December": {
        "gap": 1, "days": 31,
        "events": {
            4: ("Utpanna Ekadashi", "Ekadashi Devi Birth"), 6: ("Pradosh Vrat (K)", "Krishna Paksha"),
            7: ("Masik Shivaratri", "Shiv Seva"), 8: ("Margashirsha Amavasya", "Amavasya Seva"),
            16: ("Dhanu Sankranti", "Solar Entry"), 20: ("Mokshada Ekadashi", "Gita Jayanti"),
            21: ("Pradosh Vrat (S)", "Shukla Paksha"), 23: ("Margashirsha Purnima Vrat", "Dattatreya Jayanti"),
            26: ("Sankashti Chaturthi", "Ganesh Pujan")
        }
    }
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

# --- 1. LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ कृपया सही नाम और 10 अंकों का नंबर भरें।")
        else:
            if u_phone in df['Phone'].values:
                st.session_state.user_session = u_phone
                st.rerun()
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
            if st.button("➕ सेवा जोड़ें", key="add_btn", use_container_width=True):
                added = val if mode == "जाप संख्या (सीधा)" else (val * 108)
                df.at[user_idx, 'Today_Jaap'] += added
                df.at[user_idx, 'Today_Mala'] = df.at[user_idx, 'Today_Jaap'] // 108
                df.at[user_idx, 'Total_Jaap'] += added
                df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
                save_db(df)
                st.rerun()
        with c2:
            if st.button("✏️ सुधार करें (Reset)", key="reset_btn", use_container_width=True):
                new_j = val if mode == "जाप संख्या (सीधा)" else (val * 108)
                df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - current_j) + new_j
                df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
                df.at[user_idx, 'Today_Jaap'] = new_j
                df.at[user_idx, 'Today_Mala'] = new_j // 108
                save_db(df)
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के श्रेष्ठ सेवक")
        ld_df = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        if ld_df.empty:
            st.info("🙏 अभी आज की सेवा का आरंभ होना शेष है।")
        else:
            for i, row in ld_df.iterrows():
                rank = ld_df.index.get_loc(i) + 1
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "💠"
                st.markdown(f"""
                    <div style="background:white; padding:15px; border-radius:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:1.5rem;">{medal}</span>
                            <div><b>{row['Name']}</b><br><small>📍 {row['Location']}</small></div>
                        </div>
                        <div style="color:#FF4D00; font-weight:bold;">{int(row['Today_Mala'])} माला</div>
                    </div>
                """, unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन तिथि कैलेंडर 2026")
        sel_m = st.selectbox("महीना चुनें:", list(ALL_EVENTS_2026.keys()), index=datetime.now().month-1)
        m_info = ALL_EVENTS_2026[sel_m]
        cols = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            cols[i].markdown(f"<div class='day-label' style='text-align:center; font-weight:bold; color:#FF4D00;'>{d}</div>", unsafe_allow_html=True)
        
        grid_html = '<div class="calendar-wrapper">'
        for _ in range(m_info["gap"]): grid_html += '<div class="date-cell" style="border:none; opacity:0;"></div>'
        for d in range(1, m_info["days"] + 1):
            ev = m_info["events"].get(d)
            pk = "पूर्णिमा" if d == 15 else "अमावस्या" if d == m_info["days"] else ("शुक्ल पक्ष" if d < 15 else "कृष्ण पक्ष")
            cls = "has-event" if ev else ""
            tip = f'<div class="event-tip"><b>{ev[0]}</b><br>{ev[1]}</div>' if ev else ""
            grid_html += f'<div class="date-cell {cls}">{d}<div style="font-size:0.55rem; color:#888;">{pk}</div>{tip}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- ADMIN ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन")
            u_del = st.selectbox("यूजर डिलीट:", ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")"))
            if u_del != "--चुनें--" and st.button("🗑️ डिलीट"):
                df = df[df['Phone'] != u_del.split("(")[1].replace(")", "")]
                save_db(df)
                st.rerun()
            st.divider()
            new_msg = st.text_area("ब्रॉडकास्ट:", value=get_broadcast())
            if st.button("📢 अपडेट करें"):
                save_broadcast(new_msg)
                st.rerun()
            st.divider()
            in_act = df[df['Last_Active'] != today_str]
            if not in_act.empty:
                st.warning(f"⚠️ {len(in_act)} पेंडिंग")
                rem = st.selectbox("रिमाइंडर:", ["--चुनें--"] + in_act['Name'].tolist())
                if rem != "--चुनें--":
                    row = in_act[in_act['Name'] == rem].iloc[0]
                    msg_url = urllib.parse.quote(f"जय श्री राम {rem} जी! आज की माला सेवा दर्ज करें। 🙏🚩")
                    st.markdown(f'<a href="https://wa.me/91{row["Phone"]}?text={msg_url}" target="_blank" style="background:#25D366; color:white; padding:10px; border-radius:10px; text-decoration:none; display:block; text-align:center;">💬 WhatsApp</a>', unsafe_allow_html=True)
            st.divider()
            st.download_button("📥 Excel", data=df.to_csv(index=False).encode('utf-8-sig'), file_name='ram_data.csv')

    if st.sidebar.button("Logout 🚪"):
        st.session_state.user_session = None
        st.rerun()
