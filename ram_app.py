import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBER = "9999"  # आपका एडमिन मोबाइल नंबर

def load_db():
    required = ["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count", "Location"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            for col in required:
                if col not in df.columns:
                    df[col] = 0 if "Count" in col else "Global"
            return df
        except: pass
    return pd.DataFrame(columns=required)

def save_db(df):
    df.to_csv(DB_FILE, index=False)

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Global')}"
    except: return "Global"

# --- स्टाइलिंग ---
st.markdown("""
    <style>
    .stApp { background: #FFF5E6; }
    .stMarkdown, p, label, span, li, div, h1, h2, h3 { color: #3e2723 !important; font-weight: 500; }
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem; border-radius: 0 0 30px 30px;
        text-align: center; margin: -1rem -1rem 1rem -1rem;
    }
    .app-header * { color: white !important; }
    .stat-card { background: white; padding: 1.2rem; border-radius: 15px; text-align: center; border: 1px solid #FFE0B2; }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- लॉगिन स्क्रीन ---
if not st.session_state.user_session:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    u_name = st.text_input("आपका पावन नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर (10 अंक)", max_chars=10)
    
    if st.button("प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10:
            loc = get_user_location()
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
            else:
                idx = df[df['Phone'] == u_phone].index[0]
                df.at[idx, 'Location'] = loc
            save_db(df)
            st.rerun()

# --- मुख्य ऐप ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.9rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    # एडमिन के लिए विशेष टैब
    tab_list = ["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"]
    if st.session_state.user_session == ADMIN_NUMBER:
        tab_list.append("⚙️ एडमिन पैनल")
    
    tabs = st.tabs(tab_list)

    # टैब 1 & 2 & 3 (पुराना लॉजिक यथावत रहेगा...)
    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'>आज की माला<h1>{today_total // 108}</h1></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'>कुल जाप<h1>{int(df.at[user_idx, 'Total_Counts'])}</h1></div>", unsafe_allow_html=True)
        
        st.subheader("📝 सेवा अपडेट करें")
        mode = st.radio("प्रकार:", ["पूरी माला", "जाप संख्या"], horizontal=True)
        val = st.number_input("संख्या:", min_value=0, step=1, value=(today_total // 108 if mode == "पूरी माला" else today_total))
        if st.button("✅ अपडेट करें"):
            new_jap = val * 108 if mode == "पूरी माला" else val
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.rerun()

    # --- एडमिन पैनल (डेटा एक्सपोर्ट फीचर) ---
    if st.session_state.user_session == ADMIN_NUMBER:
        with tabs[3]:
            st.subheader("📊 सभी भक्तों का डेटा")
            st.dataframe(df)  # स्क्रीन पर टेबल दिखाएं
            
            # Excel/CSV में एक्सपोर्ट करने का बटन
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Excel (CSV) फॉर्मेट में डाउनलोड करें",
                data=csv_data,
                file_name=f'shri_ram_dham_data_{today_str}.csv',
                mime='text/csv',
            )
            st.info("यह फाइल आप Excel में खोलकर प्रिंट भी निकाल सकते हैं।")

    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
