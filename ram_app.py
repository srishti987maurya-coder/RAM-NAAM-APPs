import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="श्री राम धाम",
    page_icon="🚩",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- DATABASE SETUP ---
DB_FILE = "ram_seva_data.csv"
ADMIN_NUMBER = "9999"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'Phone': str})
            if 'Today_Count' not in df.columns: df['Today_Count'] = 0
            if 'Total_Counts' not in df.columns: df['Total_Counts'] = 0
            return df
        except: pass
    return pd.DataFrame(columns=["Phone", "Name", "Total_Counts", "Last_Active", "Today_Count"])

def save_db(df):
    df.to_csv(DB_FILE, index=False)

# --- MODERN MOBILE UI CSS ---
st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile-first responsive design */
    .main .block-container {
        padding: 1rem 1rem 3rem 1rem;
        max-width: 100%;
    }
    
    /* App background */
    .stApp {
        background: linear-gradient(135deg, #FFE5B4 0%, #FFF5E6 50%, #FFE0B2 100%);
    }
    
    /* Header with gradient */
    .app-header {
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 0px 0px 30px 30px;
        text-align: center;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .app-header::before {
        content: "🚩";
        position: absolute;
        font-size: 100px;
        opacity: 0.1;
        right: -20px;
        top: -20px;
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .app-subtitle {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Welcome card */
    .welcome-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        text-align: center;
    }
    
    .welcome-text {
        font-size: 1.3rem;
        color: #FF4D00;
        font-weight: bold;
        margin: 0;
    }
    
    /* Stat cards */
    .stat-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #fff9f5 100%);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 6px 16px rgba(255, 77, 0, 0.15);
        border: 2px solid #FFE0B2;
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #FF4D00;
        line-height: 1;
    }
    
    .stat-unit {
        font-size: 0.9rem;
        color: #888;
        margin-top: 0.3rem;
    }
    
    /* Action buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #FF4D00 0%, #FF9933 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(255, 77, 0, 0.3);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 77, 0, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #FFE0B2;
        padding: 0.8rem;
        font-size: 1rem;
        transition: border 0.3s;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #FF9933;
        box-shadow: 0 0 0 3px rgba(255, 153, 51, 0.1);
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #FF9933 0%, #FFB366 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 3px 10px rgba(255, 153, 51, 0.3);
    }
    
    /* Calendar cards */
    .calendar-section {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }
    
    .calendar-item {
        padding: 0.8rem;
        margin: 0.5rem 0;
        background: #FFF9F5;
        border-left: 4px solid #FF9933;
        border-radius: 8px;
        font-size: 0.95rem;
    }
    
    /* Success/Info messages */
    .stSuccess, .stInfo {
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Date badge */
    .date-badge {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Bottom navigation style */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
        border-radius: 20px 20px 0 0;
        z-index: 999;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        padding: 0.5rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        font-weight: 600;
    }
    
    /* Hide sidebar toggle */
    [data-testid="collapsedControl"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
df = load_db()
today_str = datetime.now().strftime("%Y-%m-%d")
display_date = datetime.now().strftime("%d %B %Y, %A")

# Calendar data
calendar_data = {
    "राम उत्सव 🚩": ["राम नवमी - 27 मार्च", "हनुमान जयंती - 12 अप्रैल", "विजयादशमी - 20 अक्टूबर", "दीपावली - 9 नवंबर"],
    "मुख्य एकादशी 🙏": ["षटतिला एकादशी - 14 जनवरी", "जया एकादशी - 29 जनवरी", "आमलकी एकादशी - 14 मार्च"],
    "पावन व्रत 🌙": ["महाशिवरात्रि - 15 फरवरी", "होली - 14 मार्च", "गणेश चतुर्थी - 27 अगस्त"]
}

# Session state
if 'user_session' not in st.session_state:
    st.session_state.user_session = None

# --- LOGIN SCREEN ---
if not st.session_state.user_session:
    # Header
    st.markdown("""
        <div class="app-header">
            <div class="app-title">🚩 श्री राम धाम 🚩</div>
            <div class="app-subtitle">राम नाम जाप सेवा</div>
            <div class="date-badge">📅 """ + display_date + """</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
        <div class="welcome-card">
            <p class="welcome-text">🙏 स्वागत है आपका 🙏</p>
            <p style="color: #666; margin-top: 0.5rem;">अपनी जानकारी दर्ज करें</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Login form
    st.markdown("<div class='section-header'>👤 लॉगिन करें</div>", unsafe_allow_html=True)
    
    u_name = st.text_input("आपका पावन नाम", placeholder="उदाहरण: राम प्रसाद", key="name_input")
    u_phone = st.text_input("मोबाइल नंबर", placeholder="10 अंकों का नंबर", max_chars=10, key="phone_input")
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    if st.button("🚪 प्रवेश करें", type="primary"):
        if u_name and u_phone and len(u_phone) == 10:
            st.session_state.user_session = u_phone
            if u_phone not in df['Phone'].values:
                new_user = pd.DataFrame([[u_phone, u_name, 0, today_str, 0]], columns=df.columns)
                df = pd.concat([df, new_user], ignore_index=True)
                save_db(df)
            st.rerun()
        else:
            st.error("कृपया सही जानकारी भरें (नाम और 10 अंकों का मोबाइल नंबर)")
    
    # Info section
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ ऐप के बारे में जानें"):
        st.markdown("""
        ### ✨ विशेषताएं:
        - 📿 दैनिक जाप गिनती
        - 📊 पूर्ण जीवनकाल रिकॉर्ड
        - 📅 धार्मिक कैलेंडर
        - 🔒 सुरक्षित और निःशुल्क
        
        ### 🎯 कैसे उपयोग करें:
        1. अपना नाम और मोबाइल नंबर दर्ज करें
        2. प्रतिदिन अपनी जाप संख्या अपडेट करें
        3. अपनी प्रगति देखें और प्रेरित रहें
        """)

# --- MAIN APP ---
else:
    user_idx = df[df['Phone'] == st.session_state.user_session].index[0]
    
    # Daily reset
    if df.at[user_idx, 'Last_Active'] != today_str:
        df.at[user_idx, 'Today_Count'] = 0
        df.at[user_idx, 'Last_Active'] = today_str
        save_db(df)
    
    # Header
    st.markdown(f"""
        <div class="app-header">
            <div class="app-title">🚩 श्री राम धाम 🚩</div>
            <div class="app-subtitle">जय श्री राम, {df.at[user_idx, 'Name']}!</div>
            <div class="date-badge">📅 {display_date}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats
    today_total = int(df.at[user_idx, 'Today_Count'])
    total_jap = int(df.at[user_idx, 'Total_Counts'])
    today_mala = today_total // 108
    
    st.markdown("""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-label">आज की माला</div>
                <div class="stat-value">""" + str(today_mala) + """</div>
                <div class="stat-unit">""" + str(today_total) + """ जाप</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">कुल जाप</div>
                <div class="stat-value">""" + str(total_jap) + """</div>
                <div class="stat-unit">""" + str(total_jap // 108) + """ माला</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Entry section
    st.markdown("<div class='section-header'>📝 जाप दर्ज करें</div>", unsafe_allow_html=True)
    
    entry_type = st.radio(
        "प्रकार चुनें:",
        ["📿 पूरी माला", "🔢 जाप संख्या"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if entry_type == "📿 पूरी माला":
        new_val = st.number_input(
            "आज की कुल माला:",
            min_value=0,
            step=1,
            value=today_mala,
            help="आपने आज कितनी माला पूरी की?"
        )
        final_today = new_val * 108
    else:
        new_val = st.number_input(
            "आज के कुल जाप:",
            min_value=0,
            step=1,
            value=today_total,
            help="आपने आज कितने जाप किए?"
        )
        final_today = new_val
    
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ अपडेट करें", type="primary", use_container_width=True):
            old_today = df.at[user_idx, 'Today_Count']
            df.at[user_idx, 'Total_Counts'] = (df.at[user_idx, 'Total_Counts'] - old_today) + final_today
            df.at[user_idx, 'Today_Count'] = final_today
            df.at[user_idx, 'Last_Active'] = today_str
            save_db(df)
            st.success("✅ सफलतापूर्वक अपडेट हो गया!")
            st.rerun()
    
    with col2:
        if st.button("🔄 रीसेट", use_container_width=True):
            df.at[user_idx, 'Total_Counts'] = df.at[user_idx, 'Total_Counts'] - df.at[user_idx, 'Today_Count']
            df.at[user_idx, 'Today_Count'] = 0
            save_db(df)
            st.rerun()
    
    # Calendar section
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📅 पावन तिथियां 2026</div>", unsafe_allow_html=True)
    
    tabs = st.tabs(list(calendar_data.keys()))
    
    for i, tab in enumerate(tabs):
        with tab:
            st.markdown("<div class='calendar-section'>", unsafe_allow_html=True)
            for event in calendar_data[list(calendar_data.keys())[i]]:
                st.markdown(f"<div class='calendar-item'>🔸 {event}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Logout
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    if st.button("🚪 लॉगआउट", use_container_width=True):
        st.session_state.user_session = None
        st.rerun()
    
    # Bottom padding for mobile
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Install prompt
st.markdown("""
    <script>
    // PWA install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
    });
    </script>
""", unsafe_allow_html=True)