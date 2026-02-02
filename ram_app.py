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
            if st.button("✏️ सुधार करें (Reset)", use_container_width=True):
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
        
        if leaders.empty:
            st.info("🙏 अभी आज की सेवा का आरंभ होना शेष है।")
        else:
            for i, row in leaders.iterrows():
                rank = leaders.index.get_loc(i) + 1
                bg, medal, brd = ("#FFD700", "🥇", "3px solid #DAA520") if rank == 1 else \
                                 ("#E0E0E0", "🥈", "2px solid #C0C0C0") if rank == 2 else \
                                 ("#CD7F32", "🥉", "2px solid #A0522D") if rank == 3 else \
                                 ("white", "💠", "1px solid #eee")
                
                st.markdown(f"""
                    <div style="background:{bg}; padding:15px; border-radius:15px; border:{brd}; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:1.5rem;">{medal}</span>
                            <div>
                                <b style="font-size:1.1rem; color:#333;">{row['Name']}</b><br>
                                <small style="color:#666;">📍 {row['Location']}</small>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:#FF4D00; font-weight:bold; font-size:1.2rem;">{int(row['Today_Mala'])}</span>
                            <span style="font-size:0.9rem; color:#444;"> माला</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with tabs[2]:
        st.subheader("📅 पावन तिथि कैलेंडर 2026")
        
        # Sarv san ani Ekadashi chi yadi (Tumhi dilelya data nusar)
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
                    1: ("Magha Purnima Vrat", "Holy Bath & Charity"),
                    5: ("Sankashti Chaturthi", "Ganesh Pujan"),
                    13: ("Vijaya Ekadashi", "Kumbha Sankranti"),
                    14: ("Pradosh Vrat (K)", "Krishna Paksha Trayodashi"),
                    15: ("Mahashivratri", "Masik Shivaratri - Bholenath Utsav"),
                    17: ("Phalguna Amavasya", "Pitru Tarpan"),
                    27: ("Amalaki Ekadashi", "Amla Tree Worship"),
                    28: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi")
                }
            },
            "March": {
                "gap": 6, "days": 31,
                "events": {
                    3: ("Holika Dahan", "Phalguna Purnima"),
                    4: ("Holi", "Dhulivandan - Festival of Colors"),
                    6: ("Sankashti Chaturthi", "Ganesh Pujan"),
                    15: ("Papmochani Ekadashi", "Meena Sankranti"),
                    16: ("Pradosh Vrat (K)", "Krishna Paksha Trayodashi"),
                    17: ("Masik Shivaratri", "Shiv Aradhana"),
                    19: ("Gudi Padwa", "Chaitra Navratri, Ugadi, Ghatasthapana"),
                    20: ("Cheti Chand", "Jhulelal Jayanti"),
                    26: ("Ram Navmi", "Prabhu Shri Ram Janmotsav"),
                    27: ("Navratri Parana", "Navratri Conclusion"),
                    29: ("Kamada Ekadashi", "Fulfillment of Desires"),
                    30: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi")
                }
            },
            "April": {
                "gap": 2, "days": 30,
                "events": {
                    2: ("Hanuman Jayanti", "Chaitra Purnima Vrat"),
                    5: ("Sankashti Chaturthi", "Ganesh Pujan"),
                    13: ("Varuthini Ekadashi", "Fortune & Prosperity"),
                    14: ("Mesha Sankranti", "Solar New Year"),
                    15: ("Pradosh Vrat (K)", "Masik Shivaratri"),
                    17: ("Vaishakha Amavasya", "Shani Jayanti (South)"),
                    19: ("Akshaya Tritiya", "Gold Buying & Charity"),
                    27: ("Mohini Ekadashi", "Vishnu Mohini Avatar"),
                    28: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi")
                }
            },
            "May": {
                "gap": 4, "days": 31,
                "events": {
                    1: ("Vaishakha Purnima Vrat", "Buddha Purnima"),
                    5: ("Sankashti Chaturthi", "Ganesh Pujan"),
                    13: ("Apara Ekadashi", "Infinite Merits"),
                    14: ("Pradosh Vrat (K)", "Krishna Paksha Trayodashi"),
                    15: ("Masik Shivaratri", "Vrishabha Sankranti"),
                    16: ("Jyeshtha Amavasya", "Vat Savitri Vrat (Amavasyant)"),
                    27: ("Padmini Ekadashi", "Kamala Ekadashi"),
                    28: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    31: ("Purnima Vrat", "Jyeshtha Purnima")
                }
            },
            "June": {
                "gap": 0, "days": 30,
                "events": {
                    3: ("Sankashti Chaturthi", "Ganesh Pujan"),
                    11: ("Parama Ekadashi", "Adhik Maas Special"),
                    12: ("Pradosh Vrat (K)", "Krishna Paksha Trayodashi"),
                    13: ("Masik Shivaratri", "Shiv Puja"),
                    15: ("Amavasya", "Mithuna Sankranti"),
                    25: ("Nirjala Ekadashi", "Pandav Bhim Ekadashi"),
                    27: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    29: ("Jyeshtha Purnima Vrat", "Vat Purnima")
                }
            },
            "July": {
                "gap": 2, "days": 31,
                "events": {
                    3: ("Sankashti Chaturthi", "Ganesh Pujan"),
                    10: ("Yogini Ekadashi", "Health & Well-being"),
                    12: ("Pradosh Vrat (K)", "Masik Shivaratri"),
                    14: ("Ashadha Amavasya", "Deep Puja"),
                    16: ("Jagannath Rath Yatra", "Karka Sankranti"),
                    25: ("Deva Shayani Ekadashi", "Ashadhi Ekadashi - Chaturmas Aarambh"),
                    26: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    29: ("Guru Purnima", "Ashadha Purnima Vrat")
                }
            },
            "August": {
                "gap": 5, "days": 31,
                "events": {
                    2: ("Sankashti Chaturthi", "Ganesh Pujan"),
                    9: ("Kamika Ekadashi", "Ashadha/Shravan Special"),
                    10: ("Pradosh Vrat (K)", "Krishna Paksha Trayodashi"),
                    11: ("Masik Shivaratri", "Shiv Aradhana"),
                    12: ("Shravana Amavasya", "Pithori Amavasya"),
                    15: ("Hariyali Teej", "Independence Day"),
                    17: ("Nag Panchami", "Simha Sankranti"),
                    23: ("Shravana Putrada Ekadashi", "Progeny Luck"),
                    25: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    26: ("Onam", "Thiruvonam"),
                    28: ("Raksha Bandhan", "Shravana Purnima Vrat"),
                    31: ("Sankashti Chaturthi", "Kajari Teej")
                }
            },
            "September": {
                "gap": 1, "days": 30,
                "events": {
                    4: ("Janmashtami", "Shri Krishna Janmotsav"),
                    7: ("Aja Ekadashi", "King Harishchandra Story"),
                    8: ("Pradosh Vrat (K)", "Krishna Paksha Trayodashi"),
                    9: ("Masik Shivaratri", "Shiv Aradhana"),
                    11: ("Bhadrapada Amavasya", "Pitra Paksha Start"),
                    14: ("Ganesh Chaturthi", "Hartalika Teej"),
                    17: ("Kanya Sankranti", "Vishwakarma Puja"),
                    22: ("Parivartini Ekadashi", "Vishnu side-turn date"),
                    24: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    25: ("Anant Chaturdashi", "Ganesh Visarjan"),
                    26: ("Bhadrapada Purnima Vrat", "Shradh Start"),
                    29: ("Sankashti Chaturthi", "Ganesh Pujan")
                }
            },
            "October": {
                "gap": 3, "days": 31,
                "events": {
                    6: ("Indira Ekadashi", "Ancestors Salvation"),
                    8: ("Pradosh Vrat (K)", "Masik Shivaratri"),
                    10: ("Ashwin Amavasya", "Sarva Pitru Amavasya"),
                    11: ("Ghatasthapana", "Sharad Navratri Start"),
                    16: ("Kalparambha", "Durga Puja Start"),
                    17: ("Tula Sankranti", "Navpatrika Puja"),
                    19: ("Durga Ashtami", "Maha Navami Puja"),
                    20: ("Dussehra", "Sharad Navratri Parana - Vijayadashami"),
                    21: ("Durga Visarjan", "Sindoor Khela"),
                    22: ("Papankusha Ekadashi", "Shield from Sins"),
                    23: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    26: ("Ashwin Purnima Vrat", "Kojagari Lakshmi Puja"),
                    29: ("Karva Chauth", "Sankashti Chaturthi")
                }
            },
            "November": {
                "gap": 6, "days": 30,
                "events": {
                    5: ("Rama Ekadashi", "Diwali Preparation"),
                    6: ("Dhanteras", "Pradosh Vrat (K)"),
                    7: ("Masik Shivaratri", "Shiv Aradhana"),
                    8: ("Diwali", "Narak Chaturdashi - Festival of Lights"),
                    9: ("Kartik Amavasya", "Laxmi Pujan"),
                    10: ("Govardhan Puja", "Annakut"),
                    11: ("Bhai Dooj", "Yama Dwitiya"),
                    15: ("Chhath Puja", "Sun Worship"),
                    16: ("Vrischika Sankranti", "Solar Entry"),
                    20: ("Devutthana Ekadashi", "Tulsi Vivah Start"),
                    22: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    24: ("Kartik Purnima Vrat", "Dev Diwali"),
                    27: ("Sankashti Chaturthi", "Ganesh Pujan")
                }
            },
            "December": {
                "gap": 1, "days": 31,
                "events": {
                    4: ("Utpanna Ekadashi", "Birth of Ekadashi Devi"),
                    6: ("Pradosh Vrat (K)", "Krishna Paksha Trayodashi"),
                    7: ("Masik Shivaratri", "Shiv Aradhana"),
                    8: ("Margashirsha Amavasya", "Pitru Tarpan"),
                    16: ("Dhanu Sankranti", "Solar Entry"),
                    20: ("Mokshada Ekadashi", "Gita Jayanti"),
                    21: ("Pradosh Vrat (S)", "Shukla Paksha Trayodashi"),
                    23: ("Margashirsha Purnima Vrat", "Dattatreya Jayanti"),
                    26: ("Sankashti Chaturthi", "Ganesh Pujan")
                }
            }
        }

        # Mahina Selector
        selected_m = st.selectbox("महीना चुनें:", list(ALL_EVENTS_2026.keys()), index=datetime.now().month-1)
        m_info = ALL_EVENTS_2026[selected_m]

        # Calendar CSS
        st.markdown("""
            <style>
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

        # Days Header
        cols = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            cols[i].markdown(f"<div class='day-header'>{d}</div>", unsafe_allow_html=True)

        # Calendar HTML Grid
        cal_html = '<div class="calendar-container">'
        
        # 1. Start Gap
        for _ in range(m_info["gap"]):
            cal_html += '<div class="date-box" style="border:none; opacity:0;"></div>'
            
        # 2. All Dates
        for d in range(1, m_info["days"] + 1):
            ev = m_info["events"].get(d)
            paksha = "शुक्ल पक्ष" if d <= 15 else "कृष्ण पक्ष"
            if d == 15: paksha = "पूर्णिमा"
            if d == m_info["days"]: paksha = "अमावस्या"
            
            if ev:
                name, info = ev
                msg = f'<div class="hover-msg"><b>{name}</b><br>{info}</div>'
                cal_html += f'<div class="date-box event-day">{d}<div class="paksha-txt">{paksha}</div>{msg}</div>'
            else:
                cal_html += f'<div class="date-cell date-box">{d}<div class="paksha-txt">{paksha}</div></div>'
                
        cal_html += '</div>'
        st.markdown(cal_html, unsafe_allow_html=True)
        st.caption("🚩 टीप: ज्या तारखेला नारंगी बॉर्डर आहे त्यावर माउस नेल्यास सणांची माहिती दिसेल.")

    # --- ADMIN SIDEBAR ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            u_list = ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")")
            target = st.selectbox("यूजर डिलीट करें:", u_list)
            if target != "--चुनें--" and st.button("🗑️ डिलीट"):
                df = df[df['Phone'] != target.split("(")[1].replace(")", "")]
                save_db(df)
                st.rerun()
            
            st.divider()
            new_m = st.text_area("ब्रॉडकास्ट सन्देश:", value=get_broadcast())
            if st.button("📢 सन्देश अपडेट करें"):
                save_broadcast(new_m)
                st.rerun()
            
            st.divider()
            st.subheader("🔔 सेवा स्मरण (Reminders)")
            inactive_today = df[df['Last_Active'] != today_str]
            if not inactive_today.empty:
                st.warning(f"⚠️ {len(inactive_today)} ने सेवा नहीं जोड़ी है।")
                rem_user_sel = st.selectbox("स्मरण भेजें:", ["--भक्त चुनें--"] + inactive_today['Name'].tolist())
                if rem_user_sel != "--भक्त चुनें--":
                    u_row = inactive_today[inactive_today['Name'] == rem_user_sel].iloc[0]
                    u_ph = "91" + str(u_row['Phone'])
                    msg_txt = urllib.parse.quote(f"जय श्री राम {rem_user_sel} जी! आज आपकी माला सेवा रिकॉर्ड नहीं हुई है। 🙏🚩")
                    st.markdown(f'<a href="https://wa.me/{u_ph}?text={msg_txt}" target="_blank" style="background:#25D366; color:white; padding:10px; border-radius:10px; text-decoration:none; display:block; text-align:center; font-weight:bold;">💬 WhatsApp Reminder</a>', unsafe_allow_html=True)

            st.divider()
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download", data=csv, file_name='ram_data.csv', use_container_width=True)

    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.user_session = None
        st.rerun()

