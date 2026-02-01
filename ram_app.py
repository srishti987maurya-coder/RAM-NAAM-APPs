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
    cols = ["Phone", "Name", "Total_Jaap", "Last_Active", "Today_Jaap", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for c in cols:
                if c not in df.columns:
                    df[c] = 0 if "Jaap" in c else "India"
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

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #FFF5E6; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00, #FF9933);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .metric-box {
        background: white; padding: 30px 20px; border-radius: 20px; text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05); border-top: 5px solid #FFD700;
    }
    .wa-btn {
        display: inline-block; padding: 6px 12px; background-color: #25D366;
        color: white !important; text-decoration: none; border-radius: 50px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN WITH STRICT REJECTION ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 भक्त प्रवेश")
    
    u_name = st.text_input("अपना पावन नाम लिखें").strip()
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10 or not u_phone.isdigit():
            st.error("❌ कृपया सही नाम और 10 अंकों का मोबाइल नंबर भरें।")
        else:
            # सुरक्षा जाँच 1: क्या यह फोन नंबर पहले से किसी और नाम से है?
            if u_phone in df['Phone'].values:
                existing_name = df[df['Phone'] == u_phone]['Name'].values[0]
                if u_name.lower() != existing_name.lower():
                    st.error(f"❌ यह नंबर पहले से ही '{existing_name}' के नाम से रजिस्टर्ड है।")
                else:
                    st.session_state.user_session = u_phone
                    st.rerun()
            
            # सुरक्षा जाँच 2: क्या यह नाम पहले से किसी और नंबर से है?
            elif u_name.lower() in df['Name'].str.lower().values:
                st.error(f"❌ '{u_name}' नाम पहले से रजिस्टर्ड है। कृपया अपना पुराना नंबर उपयोग करें।")
            
            # नया यूजर रजिस्ट्रेशन (ValueError-Free)
            else:
                loc = get_user_location()
                st.session_state.user_session = u_phone
                new_data = {
                    "Phone": [u_phone], "Name": [u_name], "Total_Jaap": [0],
                    "Last_Active": [today_str], "Today_Jaap": [0], "Location": [loc]
                }
                new_user_df = pd.DataFrame(new_data)
                df = pd.concat([df, new_user_df], ignore_index=True)
                save_db(df)
                st.rerun()
                # 2. एकादशी ऑटोमेशन चेक (Tabs से ठीक पहले डालें)
    today = datetime.now().strftime("%Y-%m-%d")
    if today in EKADASHI_2026:
        st.markdown("""
            <div style="background-color: #FFD700; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4D00; text-align: center; margin-bottom: 20px;">
                <h4 style="margin:0; color: #5D4037;">🙏 जय श्री राम! आज पावन एकादशी है।</h4>
                <p style="margin:0; color: #5D4037;">भगवान विष्णु की कृपा आप पर बनी रहे। अपना जाप और सेवा रिकॉर्ड करना न भूलें! 🚩</p>
            </div>
        """, unsafe_allow_html=True)

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
        val = st.number_input("माला संख्या (1 माला = 108 जाप):", min_value=0.0, step=1.0)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ जोड़ें", use_container_width=True):
                df.at[user_idx, 'Total_Jaap'] += (val * 108)
                df.at[user_idx, 'Today_Jaap'] += (val * 108)
                save_db(df)
                st.rerun()
        with c2:
            if st.button("✏️ सुधारें", use_container_width=True):
                new_j = val * 108
                df.at[user_idx, 'Total_Jaap'] = (df.at[user_idx, 'Total_Jaap'] - today_jap) + new_j
                df.at[user_idx, 'Today_Jaap'] = new_j
                save_db(df)
                st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Jaap", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {(row['Today_Jaap']/108):.2f} माला")

    with tabs[2]:
        st.subheader("📅 उत्सव एवं एकादशी 2026")
        events = [("14 Jan", "मकर संक्रांति"), ("28 Feb", "आमलकी एकादशी"), ("27 Mar", "राम नवमी")]
        for d, n in events: st.info(f"🚩 {d} — {n}")

   # --- ADMIN SECTION (डैशबोर्ड के नीचे या साइडबार के अंत में) ---
if st.session_state.user_session in ADMIN_NUMBERS:
    with st.sidebar:
        # यहाँ आपका एडमिन कोड आएगा:
        st.subheader("⚙️ एडमिन पैनल")
        
        # ड्रॉपडाउन जिससे आप भक्तों को चुन सकें
        user_list = ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")")
        target = st.selectbox("हटाने के लिए भक्त चुनें:", user_list)
        
        if target != "--चुनें--" and st.button("🗑️ भक्त डिलीट करें", use_container_width=True):
            # "Name (Phone)" स्ट्रिंग से फोन नंबर निकालना
            target_phone = target.split("(")[1].replace(")", "")
            
            # डेटाबेस से उस फोन नंबर को हटाना
            df = df[df['Phone'] != target_phone]
            save_db(df)
            
            st.success("भक्त को सफलतापूर्वक हटा दिया गया है।")
            st.rerun() # ऐप को रिफ्रेश करने के लिए ताकि लिस्ट अपडेट हो जाए
            
        st.divider()
        
        # आप यहाँ अपना Excel डाउनलोड बटन भी रख सकते हैं
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 डेटा एक्सेल डाउनलोड", data=csv, file_name='ram_data.csv')


