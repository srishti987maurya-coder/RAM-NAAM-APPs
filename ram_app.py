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
    # अब हम Jaap और Mala को अलग-अलग ट्रैक करने के लिए कॉलम जोड़ रहे हैं
    required = ["Phone", "Name", "Total_Jaap", "Total_Mala", "Last_Active", "Today_Count", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Count" in col or "Jaap" in col or "Mala" in col else "Unknown"
            return df
        except: pass
    return pd.DataFrame(columns=required)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    try:
        # IP के माध्यम से भक्त की लोकेशन ट्रैक करना
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
    except: return "India"

# --- PREMIUM UI STYLING (YOUR ORIGINAL DESIGN) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1.5rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .sankalp-card {
        background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 15px; text-align: center; border: 2px solid #FFD700;
    }
    .progress-bg { background: #eee; border-radius: 10px; height: 12px; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #FFD700, #FF4D00); height: 100%; }
    
    .cal-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding: 10px 0; }
    .cal-card {
        width: 85px; height: 85px; background: white; border: 1.5px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.1); z-index: 10; }
    .cal-card:hover b { color: white !important; }
    .tooltip {
        visibility: hidden; width: 180px; background: #3e2723; color: white !important;
        text-align: center; border-radius: 8px; padding: 10px; position: absolute;
        bottom: 115%; left: 50%; margin-left: -90px; opacity: 0; transition: 0.3s; font-size: 11px;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    
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

# --- LOGIN SCREEN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 भक्त प्रवेश")
    u_name = st.text_input("नाम").strip()
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10).strip()
    
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if not u_name or len(u_phone) != 10:
            st.error("❌ सही विवरण भरें।")
        else:
            # Rejection Logic
            if u_phone in df['Phone'].values:
                existing_name = df[df['Phone'] == u_phone]['Name'].values[0]
                if u_name.lower() != existing_name.lower():
                    st.error(f"❌ यह नंबर '{existing_name}' के नाम से है।")
                else:
                    st.session_state.user_session = u_phone
                    st.rerun()
            elif u_name.lower() in df['Name'].str.lower().values:
                st.error(f"❌ '{u_name}' नाम पहले से रजिस्टर्ड है।")
            else:
                loc = get_user_location()
                st.session_state.user_session = u_phone
                new_user = pd.DataFrame([[u_phone, u_name, 0, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
                st.rerun()

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.8rem; margin-top:5px;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    # Sankalp Progress
    total_all_jap = df['Total_Jaap'].sum()
    pct = min((total_all_jap / SANKALP_TARGET) * 100, 100)
    st.markdown(f"""<div class='sankalp-card'><b>🙏 सामूहिक संकल्प: {int(total_all_jap):,} / {SANKALP_TARGET:,}</b>
    <div class='progress-bg'><div class='progress-fill' style='width:{pct}%'></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        c1, c2 = st.columns(2)
        with c1: st.metric("आज की माला", f"{today_total // 108}")
        with c2: st.metric("कुल जाप (जीवनकाल)", f"{int(df.at[user_idx, 'Total_Jaap'])}")
        
        st.divider()
        mode = st.radio("अपडेट मोड:", ["माला", "जाप"], horizontal=True)
        val = st.number_input("संख्या दर्ज करें:", min_value=0, step=1)
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            add_jaap = val * 108 if mode == "माला" else val
            add_mala = val if mode == "माला" else val // 108
            
            df.at[user_idx, 'Total_Jaap'] += add_jaap
            df.at[user_idx, 'Total_Mala'] += add_mala
            df.at[user_idx, 'Today_Count'] += add_jaap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("आपकी सेवा दर्ज की गई!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 आज के टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:10px; border-radius:12px; margin-bottom:8px; border-left:6px solid #FFD700; display:flex; justify-content:space-between;"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन उत्सव कैलेंडर")
        events = [("14 Jan", "मकर संक्रांति", "सूर्य का उत्तरायण।"), ("27 Mar", "राम नवमी", "जन्मोत्सव।"), ("09 Nov", "दीपावली", "दीपोत्सव।")]
        grid_html = '<div class="cal-grid">'
        for d, n, desc in events:
            grid_html += f'<div class="cal-card"><b>{d}</b><div class="tooltip"><b>{n}</b><br>{desc}</div></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- ADMIN CONTROL ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन कंट्रोल")
            # डिलीट भक्त फीचर
            target = st.selectbox("डिलीट करने के लिए चुनें:", ["--चुनें--"] + list(df['Name'] + " (" + df['Phone'] + ")"))
            if target != "--चुनें--" and st.button("🗑️ भक्त हटाएं"):
                p = target.split("(")[1].replace(")", "")
                df = df[df['Phone'] != p]
                save_db(df)
                st.rerun()
            
            st.divider()
            # एक्सेल डाउनलोड (सभी ट्रैकिंग कॉलम के साथ)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 विस्तृत एक्सेल डाउनलोड", data=csv, file_name='shri_ram_dham_report.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.rerun()
