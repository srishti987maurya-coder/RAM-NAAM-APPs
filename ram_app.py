import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBERS = ["9987621091", "8169513359"] 

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

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF5E6 0%, #FFDCA9 100%); }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2.5rem 1rem; border-radius: 0 0 50px 50px;
        text-align: center; margin: -1rem -1rem 2rem -1rem; box-shadow: 0 10px 30px rgba(255, 77, 0, 0.3);
    }
    .otp-display {
        background: #FFF9C4; padding: 15px; border-radius: 10px;
        border: 2px dashed #FBC02D; text-align: center; font-size: 1.5rem;
        font-weight: bold; color: #5D4037; margin: 10px 0;
    }
    .wa-btn {
        display: inline-block; padding: 6px 12px; background-color: #25D366;
        color: white !important; text-decoration: none; border-radius: 50px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- SESSION STATES ---
if 'user_session' not in st.session_state:
    st.session_state.user_session = None
if 'system_otp' not in st.session_state:
    st.session_state.system_otp = None
if 'step' not in st.session_state:
    st.session_state.step = "login"

# --- LOGIN & OTP LOGIC ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>प्रमाणित भक्ति प्रवेश</div></div>', unsafe_allow_html=True)
    
    if st.session_state.step == "login":
        st.write("### 🙏 लॉगिन करें")
        u_name = st.text_input("आपका नाम")
        u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
        
        if st.button("OTP जेनरेट करें", use_container_width=True):
            if u_name and len(u_phone) == 10 and u_phone.isdigit():
                st.session_state.system_otp = str(random.randint(100000, 999999))
                st.session_state.temp_name = u_name
                st.session_state.temp_phone = u_phone
                st.session_state.step = "verify"
                st.rerun()
            else:
                st.error("कृपया सही नाम और 10 अंकों का नंबर डालें।")

    elif st.session_state.step == "verify":
        st.write("### 🔐 सुरक्षा सत्यापन")
        st.markdown(f"""
            <div class='otp-display'>
                आपका दिव्य कोड: {st.session_state.system_otp}
            </div>
        """, unsafe_allow_html=True)
        
        user_otp = st.text_input("ऊपर दिया गया 6-अंकों का कोड यहाँ भरें", max_chars=6)
        
        if st.button("सत्यापन पूर्ण करें", use_container_width=True):
            if user_otp == st.session_state.system_otp:
                st.session_state.user_session = st.session_state.temp_phone
                if st.session_state.temp_phone not in df['Phone'].values:
                    new_user = pd.DataFrame([[st.session_state.temp_phone, st.session_state.temp_name, 0, today_str, 0, "India"]], columns=df.columns)
                    df = pd.concat([df, new_user], ignore_index=True)
                    save_db(df)
                st.success("प्रमाणन सफल! जय श्री राम।")
                st.rerun()
            else:
                st.error("गलत कोड! कृपया सही कोड दर्ज करें।")
        
        if st.button("⬅️ वापस जाएं"):
            st.session_state.step = "login"
            st.rerun()

# --- MAIN APP (LoggedIn) ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        st.metric("आज का जाप", f"{today_total}")
        val = st.number_input("माला संख्या (1 माला = 108):", min_value=0, step=1, value=(today_total // 108))
        if st.button("✅ अपडेट करें", use_container_width=True):
            new_jap = val * 108
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.rerun()

    with tabs[1]:
        st.subheader("🏆 टॉप सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.write(f"#{i+1} {row['Name']} — {row['Today_Count'] // 108} माला")

    with tabs[2]:
        # --- FULL CALENDAR RESTORED ---
        st.subheader("📅 पावन कैलेंडर 2026")
        events = [
            ("14 Jan", "मकर संक्रांति"), ("15 Feb", "महाशिवरात्रि"), 
            ("28 Feb", "आमलकी एकादशी"), ("27 Mar", "राम नवमी"),
            ("02 Apr", "हनुमान जयंती"), ("09 Nov", "दीपावली")
        ]
        grid_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for d, n in events:
            grid_html += f'<div style="background:white; border:1px solid #FF9933; padding:10px; border-radius:10px; width:100px; text-align:center;"><b>{d}</b><br><small>{n}</small></div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- ADMIN WHATSAPP CONTROL ---
    if st.session_state.user_session in ADMIN_NUMBERS:
        with st.sidebar:
            st.subheader("⚙️ एडमिन")
            for i, row in df.iterrows():
                if row['Phone'] not in ADMIN_NUMBERS:
                    msg = f"प्रणाम {row['Name']} जी, आज एकादशी है। माला पूर्ण करें। धन्यवाद!"
                    wa_url = f"https://wa.me/91{row['Phone']}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"{row['Name']}: <a href='{wa_url}' class='wa-btn' target='_blank'>WA</a>", unsafe_allow_html=True)
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Excel Download", data=csv, file_name='ram_data.csv')

    if st.sidebar.button("Logout"):
        st.session_state.user_session = None
        st.session_state.step = "login"
        st.rerun()
