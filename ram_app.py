import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

def load_db():
    # कॉलम की लिस्ट को बिल्कुल स्थिर (Strict) रखना ताकि ValueError न आए
    cols = ["Phone", "Name", "Total_Jaap", "Last_Active", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            # यदि कोई कॉलम कम है तो उसे जोड़ें
            for c in cols:
                if c not in df.columns:
                    df[c] = 0 if "Jaap" in c else "India"
            return df[cols] # केवल आवश्यक कॉलम ही लोड करें
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

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #FFF5E6; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00, #FF9933);
        color: white !important; padding: 2rem 1rem; border-radius: 0 0 40px 40px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem;
    }
    .metric-box {
        background: white; padding: 30px 20px; border-radius: 20px; text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05); border-top: 5px solid #FFD700;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN / AUTHENTICATION SECTION ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1></div>', unsafe_allow_html=True)
    
    u_name = st.text_input("आपका पावन नाम लिखें").strip()
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10).strip()

    # यहाँ आपका कोड ब्लॉक आएगा:
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10 or not u_phone.isdigit():
            st.error("❌ कृपया सही नाम और 10 अंकों का मोबाइल नंबर भरें।")
        else:
            # 1. मोबाइल नंबर की जाँच (Strict Match)
            if u_phone in df['Phone'].values:
                existing_name = df[df['Phone'] == u_phone]['Name'].values[0]
                if u_name.lower() != existing_name.lower():
                    st.error(f"❌ यह नंबर पहले से ही '{existing_name}' के नाम से रजिस्टर्ड है।")
                else:
                    st.session_state.user_session = u_phone
                    st.rerun()
            
            # 2. नाम की जाँच (Unique Name per Number)
            elif u_name.lower() in df['Name'].str.lower().values:
                st.error(f"❌ '{u_name}' नाम पहले से रजिस्टर्ड है। कृपया अपना पुराना नंबर उपयोग करें।")
            
            # 3. सफल नया रजिस्ट्रेशन
            else:
                loc = get_user_location()
                st.session_state.user_session = u_phone
                new_data = {
                    "Phone": [u_phone], "Name": [u_name], "Total_Jaap": [0],
                    "Last_Active": [today_str], "Today_Jaap": [0], "Location": [loc]
                }
                df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
                save_db(df)
                st.rerun()

# --- MAIN APP SECTION ---
else:
    # यहाँ से आपका डैशबोर्ड शुरू होता है (Tabs, Leaderboard, etc.)
    ...
# --- MAIN DASHBOARD ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        if df.at[user_idx, 'Last_Active'] != today_str:
            df.at[user_idx, 'Today_Jaap'] = 0
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)

        today_jap = int(df.at[user_idx, 'Today_Jaap'])
        
        st.markdown(f"""
        <div class="metric-box">
            <h2 style='color:#FF4D00; margin:0;'>{(today_jap/108):.2f} माला</h2>
            <p style='color:#666; font-weight: bold;'>आज की कुल सेवा</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        val = st.number_input("माला जोड़ें (1 माला = 108 जाप):", min_value=0.0, step=1.0)
        
        if st.button("➕ सेवा जोड़ें (Add)", use_container_width=True):
            add_jaap = val * 108
            df.at[user_idx, 'Total_Jaap'] += add_jaap
            df.at[user_idx, 'Today_Jaap'] += add_jaap
            save_db(df)
            st.success("माला जोड़ दी गई!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {(row['Today_Jaap']/108):.2f} माला")

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()

