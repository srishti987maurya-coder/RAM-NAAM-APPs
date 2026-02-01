import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 
SANKALP_TARGET = 1100000 

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

# --- PREMIUM UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 1rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .sankalp-card {
        background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 15px; text-align: center;
        border: 2px solid #FFD700; margin-bottom: 20px;
    }
    .progress-bg { background: #eee; border-radius: 10px; height: 12px; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #FFD700, #FF4D00); height: 100%; }

    .leader-row {
        background: white; padding: 12px 20px; border-radius: 15px;
        margin-bottom: 10px; border-left: 8px solid #FFD700;
        display: flex; justify-content: space-between; align-items: center;
    }

    .cal-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding: 10px 0; }
    .cal-card {
        width: 85px; height: 85px; background: white; border: 1.5px solid #FF9933;
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative;
        cursor: pointer; transition: 0.3s;
    }
    .cal-card:hover { background: #FF4D00 !important; transform: scale(1.15); z-index: 50; }
    .cal-card:hover b, .cal-card:hover span { color: white !important; }
    
    .tooltip {
        visibility: hidden; width: 180px; background-color: #3e2723;
        color: white !important; text-align: center; border-radius: 8px;
        padding: 8px; position: absolute; z-index: 100;
        bottom: 110%; left: 50%; margin-left: -90px;
        opacity: 0; transition: 0.3s; font-size: 11px; pointer-events: none;
        box-shadow: 0 8px 15px rgba(0,0,0,0.3); border: 1px solid #FFD700;
    }
    .cal-card:hover .tooltip { visibility: visible; opacity: 1; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("भक्त का नाम")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, "India"]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    # सामुदायिक संकल्प (Global Progress Bar)
    total_jap = df['Total_Counts'].sum()
    pct = min((total_jap / SANKALP_TARGET) * 100, 100)
    st.markdown(f"""<div class='sankalp-card'><b>🙏 सामुदायिक संकल्प: {int(total_jap):,} / {SANKALP_TARGET:,}</b>
    <div class='progress-bg'><div class='progress-fill' style='width:{pct}%'></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 पावन कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        c1, c2 = st.columns(2)
        # आज की माला और आज के कुल जाप दोनों दिखा रहे हैं
        with c1: st.metric("आज की माला", f"{today_total // 108}")
        with c2: st.metric("आज का कुल जाप", f"{today_total}")
        
        st.divider()
        st.subheader("📝 अपनी सेवा दर्ज करें")
        # जाप काउंट का विकल्प वापस जोड़ा गया
        mode = st.radio("अपडेट का प्रकार चुनें:", ["पूरी माला (108 जाप)", "जाप संख्या (Individual Count)"], horizontal=True)
        
        if mode == "पूरी माला (108 जाप)":
            val = st.number_input("माला की संख्या लिखें:", min_value=0, step=1, value=(today_total // 108))
            new_jap_calc = val * 108
        else:
            val = st.number_input("कुल जाप संख्या लिखें:", min_value=0, step=1, value=today_total)
            new_jap_calc = val

        if st.button("✅ सेवा सुरक्षित करें", use_container_width=True):
            # पुराने जाप को हटाकर नया जोड़ना (Overwrite current day)
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap_calc
            df.at[user_idx, 'Today_Count'] = new_jap_calc
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("आपकी सेवा सफलतापूर्वक दर्ज की गई!")
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 शीर्ष सेवक (आज)")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div class="leader-row"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Count"] // 108} माला ({row["Today_Count"]} जाप)</b></div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("📅 पावन उत्सव एवं एकादशी 2026")
        events = [
            ("14 Jan", "मकर संक्रांति / षटतिला एकादशी", "सूर्य उत्तरायण एवं पुण्यमयी एकादशी।"),
            ("15 Feb", "महाशिवरात्रि", "शिव-शक्ति मिलन का पावन महापर्व।"),
            ("28 Feb", "आमलकी एकादशी", "आंवले के वृक्ष की पूजा।"),
            ("14 Mar", "होली", "रंगों का उत्सव।"),
            ("27 Mar", "राम नवमी", "प्रभु श्री राम जन्मोत्सव।"),
            ("02 Apr", "हनुमान जयंती", "बजरंगबली का प्राकट्य दिवस।"),
            ("14 Apr", "वरुथिनी एकादशी", "सौभाग्य प्रदायक व्रत।"),
            ("13 May", "अपरा एकादशी", "अपार पुण्य प्रदायिनी।"),
            ("10 Jul", "कामिका एकादशी", "मनोकामना पूर्ति एकादशी।"),
            ("07 Aug", "अजा एकादशी", "दुखों का नाश करने वाली।"),
            ("05 Sep", "परिवर्तिनी एकादशी", "विष्णु जी की करवट।"),
            ("20 Oct", "विजयादशमी", "धर्म की विजय का महापर्व।"),
            ("04 Nov", "देवउठनी एकादशी", "मांगलिक कार्यों का आरंभ।"),
            ("09 Nov", "दीपावली", "अयोध्या दीपोत्सव महापर्व।"),
            ("20 Dec", "मोक्षदा एकादशी", "मोक्ष प्रदायिनी एकादशी।")
        ]
        
        grid_html = '<div class="cal-grid">'
        for date, name, desc in events:
            color = "#FF4D00" if "एकादशी" in name else "#FF9933"
            grid_html += f'''
            <div class="cal-card" style="border-color:{color};">
                <b style="color:{color}; font-size:12px;">{date}</b>
                <span style="font-size:10px;">2026</span>
                <div class="tooltip"><b>{name}</b><br><hr style="border:0.5px solid rgba(255,255,255,0.2); margin:4px 0;">{desc}</div>
            </div>'''
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन पैनल")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 डेटा एक्सेल", data=csv, file_name='ram_data.csv')
    
    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
