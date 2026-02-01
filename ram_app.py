import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="श्री राम धाम", page_icon="🚩", layout="centered")

# --- डेटाबेस सेटअप ---
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

def get_user_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'India')}"
    except: return "India"

# --- सुरक्षित CSS (नो-एरर डिज़ाइन) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF5E6; }
    .stMarkdown, p, label, span, li, div, h1, h2, h3 { color: #3e2723 !important; }
    
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white !important; padding: 2rem; border-radius: 0 0 40px 40px;
        text-align: center; margin: -1rem -1rem 1rem -1rem;
    }
    .app-header h1 { color: white !important; margin:0; }
    
    .stat-card { 
        background: white; padding: 1rem; border-radius: 15px; 
        text-align: center; border: 2px solid #FFE0B2; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* कैलेंडर बॉक्स डिज़ाइन */
    .cal-box {
        background: white; border: 2px solid #FF9933;
        border-radius: 12px; padding: 10px; text-align: center;
        margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")

if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- लॉगिन स्क्रीन ---
if st.session_state.user_session is None:
    st.markdown('<div class="app-header"><h1>🚩 श्री राम धाम </h1><div>राम नाम जाप सेवा</div></div>', unsafe_allow_html=True)
    st.write("### 🙏 भक्त प्रवेश")
    u_name = st.text_input("आपका पावन नाम लिखें")
    u_phone = st.text_input("मोबाइल नंबर", max_chars=10)
    if st.button("दिव्य प्रवेश करें", use_container_width=True):
        if u_name and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                loc = get_user_location()
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0, loc]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
        else:
            st.error("कृपया नाम और मोबाइल नंबर सही भरें।")

# --- मुख्य डैशबोर्ड ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    st.markdown(f'<div class="app-header"><h1>🚩 श्री राम धाम</h1><div>जय श्री राम, {df.at[user_idx, "Name"]}</div><div style="font-size:0.8rem;">📍 {df.at[user_idx, "Location"]}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🏠 मेरी सेवा", "🏆 लीडरबोर्ड", "📅 कैलेंडर"])

    # टैब 1: मेरी सेवा
    with tabs[0]:
        today_total = int(df.at[user_idx, 'Today_Count'])
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stat-card'><small>आज की माला</small><h2>{today_total // 108}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-card'><small>कुल जाप</small><h2>{int(df.at[user_idx, 'Total_Counts'])}</h2></div>", unsafe_allow_html=True)
        
        st.divider()
        val = st.number_input("माला की संख्या लिखें:", min_value=0, step=1, value=(today_total // 108))
        if st.button("✅ सेवा अपडेट करें", use_container_width=True):
            new_jap = val * 108
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - today_total) + new_jap
            df.at[user_idx, 'Today_Count'] = new_jap
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("सफलतापूर्वक अपडेट!")
            st.rerun()

    # टैब 2: लीडरबोर्ड
    with tabs[1]:
        st.subheader("🏆 आज के शीर्ष सेवक")
        leaders = df[df['Last_Active'] == today_str].sort_values(by="Today_Count", ascending=False).head(10)
        for i, (idx, row) in enumerate(leaders.iterrows()):
            st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; margin-bottom:5px; border-left:5px solid #FF9933; display:flex; justify-content:space-between;"><span>#{i+1} {row["Name"]}</span><b>{row["Today_Count"] // 108} माला</b></div>', unsafe_allow_html=True)

    # टैब 3: कैलेंडर (ERROR-FREE VERSION)
    with tabs[2]:
        st.subheader("📅 पावन उत्सव 2026")
        st.write("उत्सव के बारे में जानने के लिए उस पर क्लिक करें:")
        
        events = [
            ("14 Jan", "मकर संक्रांति", "सूर्य का उत्तरायण प्रवेश और दान का महापर्व।"),
            ("15 Feb", "महाशिवरात्रि", "शिव-शक्ति मिलन का महापर्व।"),
            ("14 Mar", "होली", "रंगों का पावन उत्सव।"),
            ("27 Mar", "राम नवमी", "मर्यादा पुरुषोत्तम प्रभु राम का जन्मोत्सव।"),
            ("02 Apr", "हनुमान जयंती", "बजरंगबली का पावन प्राकट्य दिवस।"),
            ("20 Oct", "विजयादशमी", "अधर्म पर धर्म की विजय (दशहरा)।"),
            ("09 Nov", "दीपावली", "अयोध्या में प्रभु राम के आगमन का उत्सव।")
        ]

        # हम यहाँ Columns का उपयोग कर रहे हैं जो कभी एरर नहीं देते
        for date, name, desc in events:
            col_d, col_n = st.columns([1, 3])
            with col_d:
                st.markdown(f"<div class='cal-box'><b style='color:#FF4D00;'>{date}</b></div>", unsafe_allow_html=True)
            with col_n:
                with st.expander(f"✨ {name}"):
                    st.write(desc)

    # एडमिन सेटिंग्स
    if st.session_state.user_session in ADMIN_NUMBERS:
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ एडमिन पैनल")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📊 डेटा डाउनलोड", data=csv, file_name='ram_data.csv')
    
    if st.sidebar.button("लॉगआउट"):
        st.session_state.user_session = None
        st.rerun()
