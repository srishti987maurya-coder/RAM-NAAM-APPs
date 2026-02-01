import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE & CONFIG ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

# 2026 एकादशी एवं त्यौहार तिथियां
EVENTS_2026 = [
    ("14 Jan", "मकर संक्रांति", "सूर्य उत्तरायण प्रवेश"), ("14 Jan", "षटतिला एकादशी", "पापनाशिनी एकादशी"),
    ("28 Feb", "आमलकी एकादशी", "आंवला वृक्ष पूजन"), ("27 Mar", "राम नवमी", "प्रभु श्री राम जन्मोत्सव"),
    ("02 Apr", "हनुमान जयंती", "बजरंगबली जन्मोत्सव"), ("14 Apr", "वरुथिनी एकादशी", "सौभाग्य प्रदायिनी"),
    ("09 Nov", "दीपावली", "अयोध्या दीपोत्सव महापर्व"), ("20 Dec", "मोक्षदा एकादशी", "गीता जयंती")
]

def load_db():
    cols = ["Phone", "Name", "Total_Mala", "Total_Jaap", "Last_Active", "Today_Mala", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for c in cols:
                if c not in df.columns:
                    df[c] = 0 if "Mala" in c or "Jaap" in c else "India"
            return df[cols]
        except: pass
    return pd.DataFrame(columns=cols)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
    except: return "India"

# --- INTERACTIVE UI CSS ---
st.markdown("""
    <style>
    /* मुख्य बैकग्राउंड और फॉन्ट */
    .stApp {
        background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%);
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    /* हेडर स्टाइल */
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important;
        padding: 3rem 1rem;
        border-radius: 0 0 60px 60px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 15px 35px rgba(255, 77, 0, 0.4);
    }
    
    /* मुख्य माला डिस्प्ले बॉक्स */
    .metric-box {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 50px 20px;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 2px solid #FFFFFF;
        border-top: 10px solid #FFD700;
        margin-bottom: 30px;
        transition: transform 0.3s ease;
    }
    .metric-box:hover {
        transform: translateY(-5px);
    }
    
    /* बटन स्टाइल */
    .stButton>button {
        background: linear-gradient(90deg, #FF4D00, #FF9933);
        color: white !important;
        border: none;
        border-radius: 15px;
        padding: 0.6rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 77, 0, 0.2);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(255, 77, 0, 0.4);
        border: none;
    }
    
    /* इनपुट फील्ड्स */
    .stNumberInput, .stTextInput {
        border-radius: 12px !important;
    }
    
    /* टैब्स स्टाइल */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #FF4D00;
    }
    
    /* अलर्ट और बैनर */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)
df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- 1. LOGIN SECTION (STRICT) ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम लिखें").strip()
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ कृपया सही नाम और नंबर भरें।")
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
                new_user = {
                    "Phone": [u_phone], "Name": [u_name], "Total_Mala": [0], "Total_Jaap": [0],
                    "Last_Active": [today_str], "Today_Mala": [0], "Today_Jaap": [0], "Location": [loc]
                }
                df = pd.concat([df, pd.DataFrame(new_user)], ignore_index=True)
                save_db(df)
                st.rerun()

# --- 2. DASHBOARD SECTION ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        if df.at[user_idx, 'Last_Active'] != today_str:
            df.at[user_idx, 'Today_Mala'] = 0
            df.at[user_idx, 'Today_Jaap'] = 0
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)

        current_jaap = int(df.at[user_idx, 'Today_Jaap'])
        current_mala = current_jaap // 108
        
        # Display: ONLY MALA (Clean UI)
        st.markdown(f"""
        <div class="metric-box">
            <h1 style='color:#FF4D00; margin:0; font-size: 4.5rem;'>{current_mala} माला</h1>
            <p style='color:#666; font-weight: bold; margin-top:15px; font-size: 1.2rem;'>आज की कुल सेवा</p>
        </div>
        """, unsafe_allow_html=True)

        mode = st.radio("इनपुट तरीका चुनें:", ["जाप संख्या (सीधा)", "माला (1 = 108)"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ सेवा जोड़ें", use_container_width=True):
                added_jaap = val if mode == "जाप संख्या (सीधा)" else (val * 108)
                df.at[user_idx, 'Today_Jaap'] += added_jaap
                df.at[user_idx, 'Today_Mala'] = df.at[user_idx, 'Today_Jaap'] // 108
                df.at[user_idx, 'Total_Jaap'] += added_jaap
                df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
                save_db(df)
                st.rerun()
        with c2:
            if st.button("✏️ सुधार करें (Reset)", use_container_width=True):
                new_jaap = val if mode == "जाप संख्या (सीधा)" else (val * 108)
                df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - current_jaap) + new_jaap
                df.at[user_idx, 'Total_Mala'] = df.at[user_idx, 'Total_Jaap'] // 108
                df.at[user_idx, 'Today_Jaap'] = new_jaap
                df.at[user_idx, 'Today_Mala'] = new_jaap // 108
                save_db(df)
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Mala']} माला")

    with tabs[2]:
        st.subheader("📅 पावन उत्सव ग्रिड 2026")
        grid_html = '<div class="cal-grid">'
        for d, n, desc in EVENTS_2026:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip"><b>{n}</b><br>{desc}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- ADMIN SIDEBAR ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन पैनल")
            u_list = ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")")
            target = st.selectbox("यूजर डिलीट करें:", u_list)
            if target != "--चुनें--" and st.button("🗑️ डिलीट"):
                df = df[df['Phone'] != target.split("(")[1].replace(")", "")]
                save_db(df)
                st.rerun()
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download", data=csv, file_name='ram_seva_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()

