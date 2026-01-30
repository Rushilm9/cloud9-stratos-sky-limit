import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from grid_client import (
    fetch_recent_tournaments,
    fetch_series_info_for_team,
    collect_team_data,
    discover_teams_from_tournament_list,
    discover_teams_from_tournament
)
from llm_analyzer import generate_scouting_report, generate_comparison_report
from report_generator import (
    generate_markdown_report, 
    generate_pdf_report,
    generate_comparison_markdown,
    generate_comparison_pdf
)


# Load environment variables
load_dotenv()
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

# Premium Scouting Dashboard Config
st.set_page_config(
    page_title="ELITE Strategic Scouting Studio",
    page_icon="🎖️",
    layout="wide"
)

# --- TOP LEVEL MISSION BRANDING ---
st.markdown("<h1 class='main-header'>Cloud9 AI Scouting Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00d4ff; font-family: Orbitron; font-size: 1.1rem; margin-top: -20px; margin-bottom: 30px;'>Automated Scouting Report Generator Powered by GRID Data & JetBrains AI</p>", unsafe_allow_html=True)

# Advanced CSS for Premium Aesthetic & High Contrast (Purple Void Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@400;600&display=swap');
    
    /* Global Background and Base Text */
    .stApp { 
        background-color: #050b1a; 
        color: #e1e1e1; 
        font-family: 'Inter', sans-serif; 
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Input Labels - Gray for Visibility */
    label, .stMarkdown p { 
        color: #cfcfcf !important; 
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Headers - High Contrast White/Blue */
    h1, h2, h3, .section-title { 
        color: #ffffff !important; 
    }
    
    .main-header {
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        background: linear-gradient(90deg, #0077ff 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        margin-bottom: 5px;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0, 119, 255, 0.3);
    }
    
    /* Input Widget Styling - Premium Deep Blue */
    .stSelectbox, .stSelectbox div[data-baseweb="select"], .stSelectbox [data-baseweb="expand"] {
        background-color: #0d1526 !important;
        border: none !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
        color: #ffffff !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        border: none !important; /* Managed by parent */
    }

    .stSelectbox:hover {
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
    }
    
    /* Dropdown Selected Text */
    .stSelectbox span, .stSelectbox div {
        color: #ffffff !important;
    }

    /* Input background specifically */
    div[data-baseweb="select"] > div {
        background-color: #0d1526 !important;
    }
    
    /* Placeholder Text */
    .stSelectbox div[data-baseweb="select"] div[data-testid="stMarkdownContainer"] p {
        color: #a3a3a3 !important;
    }

    /* Popover/Dropdown Menu Style */
    div[data-baseweb="popover"] {
        background-color: transparent !important;
    }
    
    div[data-baseweb="popover"] ul {
        background-color: #0d1526 !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="popover"] li {
        color: #ffffff !important;
        background-color: transparent !important;
        padding: 10px 15px !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-baseweb="popover"] li:hover {
        background-color: #1e3a5f !important;
        color: #00d4ff !important;
    }

    /* Mini Loader Animation */
    .loader-mini {
        width: 18px;
        height: 18px;
        border: 2px solid #1e3a5f;
        border-top: 2px solid #00d4ff;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        display: inline-block;
        vertical-align: middle;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Fullscreen Strategic Loader Overlay */
    .mission-loader-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw !important;
        height: 100vh !important;
        background-color: #050b1a !important;
        background: radial-gradient(circle at center, #0d1526 0%, #050b1a 100%) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 9999999 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .loader-large {
        width: 120px;
        height: 120px;
        border: 4px solid rgba(0, 212, 255, 0.1);
        border-top: 4px solid #00d4ff;
        border-radius: 50%;
        animation: spin 1s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        box-shadow: 0 0 50px rgba(0, 212, 255, 0.3);
    }
    
    .mission-text {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        margin-top: 40px;
        letter-spacing: 8px;
        font-size: 1.2rem;
        text-transform: uppercase;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(0.98); }
    }

    /* Remove white backgrounds from Status and Containers */
    /* Ultra-Aggressive Status Widget Overrides */
    div[data-testid="stStatusWidget"], 
    div[data-testid="stStatusWidget"] *, 
    div[data-testid="stStatusWidget"] [role="button"],
    div[data-testid="stStatusWidget"] summary {
        background-color: #0d1526 !important;
        background: #0d1526 !important;
        color: #00d4ff !important;
        border-color: #1e3a5f !important;
    }

    div[data-testid="stStatusWidget"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    div[data-testid="stStatusWidget"] svg {
        fill: #00d4ff !important;
        color: #00d4ff !important;
    }

    /* Ensuring the vertical blocks don't add white backgrounds */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: transparent !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(13, 21, 38, 0.6) !important;
        border: 1px solid #1e3a5f !important;
    }

    /* Tabs Styling - 30% Larger and High Contrast */
    div[data-testid="stTabs"] {
        background-color: #050b1a !important;
        border-bottom: 1px solid #1e3a5f !important;
    }
    
    button[data-baseweb="tab"] {
        background-color: rgba(30, 48, 80, 0.4) !important;
        color: #cfcfcf !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        font-size: 1.5rem !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 18px 35px !important;
        margin-right: 10px !important;
        border: 1px solid #1e3a5f !important;
        border-bottom: none !important;
        transition: all 0.3s ease !important;
    }
    
    button[data-baseweb="tab"]:hover {
        background-color: rgba(0, 119, 255, 0.2) !important;
        color: #00d4ff !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00d4ff !important;
        background-color: rgba(30, 48, 80, 0.8) !important;
        border-bottom: 2px solid #00d4ff !important;
    }

    /* Global container border color */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #1e3a5f !important;
        background-color: rgba(13, 21, 38, 0.3) !important;
    }
    
    /* Ensure no white flickering on sidebar or main content */
    section[data-testid="stSidebar"] {
        background-color: #050b1a !important;
    }
    
    .stAppViewBlockContainer {
        background-color: #050b1a !important;
    }

    .stTextInput input {
        background-color: #0d1526 !important;
        color: #ffffff !important;
        border: 1px solid #1e3a5f !important;
    }

    .report-block {
        padding: 25px;
        background: rgba(13, 21, 38, 0.4);
        border-radius: 15px;
        border: 1px solid #1e3a5f;
        margin-bottom: 20px;
        box-shadow: inset 0 0 20px rgba(0, 119, 255, 0.1);
    }
    
    .section-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        border-bottom: 2px solid #0077ff;
        padding-bottom: 12px;
        margin-top: 40px;
        margin-bottom: 30px;
        font-size: 2.2rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-shadow: 0 0 15px rgba(0, 119, 255, 0.4);
    }
    
    .metric-card {
        background: #0d1526;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #1e3a5f;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    .metric-card h2 {
        color: #00d4ff !important;
        margin: 5px 0;
    }
    
    
    .category-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 0.65rem;
        font-family: 'Orbitron', sans-serif;
        padding: 3px 8px;
        border-radius: 5px;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .cat-killer { background: rgba(255, 75, 75, 0.5); color: #ffffff !important; border: 1px solid #ff4b4b; font-weight: 800; }
    .cat-attacker { background: rgba(255, 165, 0, 0.5); color: #ffffff !important; border: 1px solid #ffa500; font-weight: 800; }
    .cat-defender { background: rgba(0, 242, 254, 0.5); color: #ffffff !important; border: 1px solid #00f2fe; font-weight: 800; }
    
    /* Labels - Bold Orbitron */
    label {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.85rem !important;
        color: #00d4ff !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-bottom: 8px !important;
    }

    .mini-card {
        background: rgba(0, 119, 255, 0.08);
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(0, 119, 255, 0.2);
    }
    
    .win-tag { color: #00d4ff !important; font-weight: bold; }
    .loss-tag { color: #ff4b4b !important; font-weight: bold; }
    
    .trend-box {
        background: rgba(0, 119, 255, 0.1);
        padding: 18px;
        border-radius: 12px;
        border-left: 5px solid #00d4ff;
        margin-bottom: 15px;
        border-right: 1px solid rgba(0, 119, 255, 0.2);
    }

    .counter-box {
        background: rgba(255, 75, 75, 0.08);
        padding: 18px;
        border-radius: 12px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 15px;
        border-right: 1px solid rgba(255, 75, 75, 0.1);
    }

    /* PREMIUM BLUE BUTTONS */
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, #0077ff 0%, #00d4ff 100%) !important;
        color: #ffffff !important;
        font-weight: 700;
        border: none !important;
        border-radius: 12px;
        padding: 12px 25px;
        width: 100%;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 4px 15px rgba(0, 119, 255, 0.4);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.6);
        color: #ffffff !important;
    }

    /* Table Styling for High Contrast */
    .stTable {
        background: rgba(13, 21, 38, 0.9) !important;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #1e3a5f;
    }
    
    .stTable thead th {
        background-color: #1e3a5f !important;
        color: #00d4ff !important;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        font-weight: bold;
    }

    .stTable td {
        color: #ffffff !important;
        background-color: rgba(13, 21, 38, 0.4) !important;
        border-bottom: 1px solid #1e3a5f !important;
    }

    /* Index (Sr) Styling */
    .stTable th {
        color: #ffffff !important;
    }

    /* Fix for notable names visibility in tables */
    .stTable [data-testid="stTableContent"] {
        color: #ffffff !important;
    }
    
    .player-card {
        background: linear-gradient(135deg, #0d1526 0%, #050b1a 100%);
        padding: 18px;
        border-radius: 12px;
        border-left: 5px solid #0077ff;
        margin-bottom: 15px;
        position: relative;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }

    .player-card:hover {
        transform: scale(1.02);
        border-left: 5px solid #00d4ff;
        box-shadow: 0 0 20px rgba(0, 119, 255, 0.2);
    }

    .comp-box-alpha {
        background: rgba(0, 119, 255, 0.1);
        border: 2px solid #0077ff;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
    }

    .comp-box-beta {
        background: rgba(255, 75, 75, 0.08);
        border: 2px solid #ff4b4b;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
    }
    
    div[data-testid="stExpander"] {
        background: rgba(13, 21, 38, 0.6);
        border: 1px solid #1e3a5f;
        border-radius: 10px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0510; }
    ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 10px; }

    /* AI Report Text Styling */
    .stMarkdown p, .stMarkdown li {
        line-height: 1.6;
        color: #e1e1e1 !important;
    }
    
    /* Ensure any remaining white backgrounds are gone */
    div[data-testid="stAppViewBlockContainer"] {
        background-color: transparent !important;
    }

    /* Hide Streamlit Header White Bar */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: transparent !important;
        border: none !important;
    }

    /* Hide Top Toolbar/Deploy Button */
    [data-testid="stToolbar"] {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)


def full_screen_loader(message="FETCHING DATA FROM GRID API"):
    """Renders a premium fullscreen blocking loader."""
    st.markdown(f"""
        <div class="mission-loader-overlay">
            <div class="loader-large"></div>
            <div class="mission-text">{message}</div>
            <p style="color:#ffffff; font-family:'Inter', sans-serif; margin-top:20px; opacity:0.5; letter-spacing:2px; font-size:0.8rem;">ESTABLISHING SECURE DATA LINK...</p>
        </div>
    """, unsafe_allow_html=True)

# --- GLOBAL INTEL SYNC (STARTUP ONLY) ---
if 'tours' not in st.session_state:
    # Use the premium fullscreen loader for initialization
    full_screen_loader("SYNCHRONIZING GLOBAL COMBAT DATA")
    
    # 1. Fetch Tournaments
    tours = fetch_recent_tournaments(limit=50)
    st.session_state['tours'] = tours
    
    # 2. Discover Universities (for search and comparison)
    # We use a limited set initially to keep startup fast, or full if user prefers
    # But for comparison we need a good list:
    rt_ids = [t['id'] for t in tours[:30]] # Use first 30 tours for team discovery
    univ = discover_teams_from_tournament_list(rt_ids)
    
    st.session_state['guniv'] = univ
    st.session_state['ca'] = univ
    st.session_state['cb'] = univ
    
    # Initialize other states
    if 'tteams' not in st.session_state: st.session_state['tteams'] = []
    
    # Finish Initialization
    st.rerun() # Refresh to show UI once data is locked in

@st.cache_data(show_spinner="Preparing Mission Dossier...")
def get_cached_pdf(t_name, ed, pb, sr, wt, cs):
    return generate_pdf_report(t_name, ed, pb, sr, wt, cs)

# --- CALLBACKS TO PREVENT JUMPING ---
def on_scout_tour_change():
    """Handles tournament selection in Tab 1."""
    sel_tn = st.session_state.get('scout_tour')
    if 'res_t1' in st.session_state: del st.session_state['res_t1']
    if not sel_tn:
        st.session_state['tteams'] = []
        st.session_state['last_tid'] = None
        return
    
    tours = st.session_state.get('tours', [])
    tid = next((t['id'] for t in tours if t['name'] == sel_tn), None)
    if tid:
        # We don't call full_screen_loader here as it's a callback
        # But we fetch the data so it's ready for the next render
        st.session_state['tteams'] = discover_teams_from_tournament(tid)
        st.session_state['last_tid'] = tid
        st.session_state['scout_team'] = None # Reset team selection

def on_global_change():
    """Reset global search results when search target changes."""
    if 'res_t2' in st.session_state: del st.session_state['res_t2']

def on_comp_change():
    """Reset comparison results when teams change."""
    if 'res_comp' in st.session_state: del st.session_state['res_comp']


def display_scouting_results(team_name, team_id, mode_key, data_pack):
    """Cleanly displays previously fetched scouting data."""
    enriched_data, playbook, structured_roster, winning_trends, counter_strategy = data_pack
    
    # If LLM analysis failed but we have GRID data, show what we have
    is_partial = playbook is None
    
    # --- 1. OVERVIEW ---
    st.markdown("<div class='section-title'>📊 Team Summary</div>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top: -20px; color: #888; font-size: 0.9rem;'>A quick look at the team's overall performance, win rates, and their primary playstyle as detected by AI.</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='trend-box'><span style='color:#00d4ff;font-family:Orbitron;font-size:0.8rem;'>WINNING PLAYSTYLE</span><br><p style='margin-top:8px; font-size:1.1rem; font-style:italic; color:#ffffff !important;'>{winning_trends or 'Analysis failed...'}</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='counter-box'><span style='color:#ff4b4b;font-family:Orbitron;font-size:0.8rem;'>KEY COUNTER STRATEGY</span><br><p style='margin-top:8px; font-size:1.1rem; font-style:italic; color:#ffffff !important;'>{counter_strategy or 'Insight unavailable...'}</p></div>", unsafe_allow_html=True)
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    twins = sum(1 for s in enriched_data["series"] if s["series_win"])
    tser = len(enriched_data["series"])
    wr = (twins/tser)*100 if tser > 0 else 0
    impact = enriched_data['top_players'][0]['impact_score'] if enriched_data['top_players'] else 0
    power_lv = round((wr * 0.4) + (impact * 0.6), 1)

    with m1: st.markdown(f"<div class='metric-card'>WIN RATE<br><h2 style='color:#00d4ff !important;'>{round(wr,1)}%</h2></div>", unsafe_allow_html=True)
    with m2: st.markdown(f"<div class='metric-card'>RECORD<br><h2 style='color:#ffffff !important;'>{twins}W - {tser-twins}L</h2></div>", unsafe_allow_html=True)
    with m3: st.markdown(f"<div class='metric-card'>TEAM POWER<br><h2 style='color:#7c3aed !important;'>{power_lv}</h2></div>", unsafe_allow_html=True)
    with m4: st.markdown(f"<div class='metric-card'>COMBAT RATING<br><h2 style='color:#ffffff !important;'>{round(sum(p['avg_kda'] for p in enriched_data['top_players'])/len(enriched_data['top_players']),1) if enriched_data['top_players'] else 0}</h2></div>", unsafe_allow_html=True)
    with m5: st.markdown(f"<div class='metric-card'>MAP WIN %<br><h2 style='color:#10b981 !important;'>{enriched_data.get('map_win_rate', 0)}%</h2></div>", unsafe_allow_html=True)
    with m6: st.markdown(f"<div class='metric-card'>STAR IMPACT<br><h2 style='color:#ffa500 !important;'>{impact}</h2></div>", unsafe_allow_html=True)

    # --- 2. PERFORMANCE PROFILE ---
    st.markdown("<div class='section-title'>⚔️ Recent Match Outcomes</div>", unsafe_allow_html=True)
    pro_c1, pro_c2 = st.columns(2)
    with pro_c1:
        st.markdown("<h4 style='color:#10b981 !important; font-family:Orbitron;'>✅ RECENT VICTORIES</h4>", unsafe_allow_html=True)
        if enriched_data["wins"]:
            for w in enriched_data["wins"][:5]:
                st.markdown(f"<div class='mini-card'><span style='color:#ffffff !important;'>{w['opponent']}</span><span class='win-tag'>VICTORY</span></div>", unsafe_allow_html=True)
        else: st.info("No recent victory data found.")
    with pro_c2:
        st.markdown("<h4 style='color:#ef4444 !important; font-family:Orbitron;'>⛔ RECENT DEFEATS</h4>", unsafe_allow_html=True)
        if enriched_data["losses"]:
            for l in enriched_data["losses"][:5]:
                st.markdown(f"<div class='mini-card'><span style='color:#ffffff !important;'>{l['opponent']}</span><span class='loss-tag'>DEFEAT</span></div>", unsafe_allow_html=True)
        else: st.info("No recent defeat data found.")

    # --- RECENT ENGAGEMENTS TABLE ---
    st.markdown("<div class='section-title'>📅 Recent Match History</div>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top: -20px; color: #888; font-size: 0.9rem;'>Details of the most recent matches including dates, opponents, and final scores retrieved from GRID.</p>", unsafe_allow_html=True)
    if enriched_data["series"]:
        match_data = []
        for s in enriched_data["series"]:
            match_data.append({
                "Date": s.get("date", "N/A"),
                "Opponent": s["opponent"],
                "Result": "🏆 WIN" if s["series_win"] else "❌ LOSS",
                "Map Score": s["game_stats"][0]["score"] if s["game_stats"] else "N/A",
                "Key Player": s.get("key_player", "N/A")
            })
        df = pd.DataFrame(match_data)
        df.index = df.index + 1
        df.index.name = "Sr"
        st.table(df)
    else:
        st.info("No engagement history discovered.")

    # --- 3. ROSTER ---
    st.markdown("<div class='section-title'>👥 Player Analysis</div>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top: -20px; color: #888; font-size: 0.9rem;'>Individual player performance breakdown, including combat ratings and specific tactical roles.</p>", unsafe_allow_html=True)
    if enriched_data['top_players']:
        # Normalize keys for robust matching
        ro_map = {p['name'].lower().strip(): p for p in structured_roster}
        
        r_cols = st.columns(len(enriched_data['top_players']))
        for i, pr in enumerate(enriched_data['top_players']):
            p_name_norm = pr['name'].lower().strip()
            pa = ro_map.get(p_name_norm)
            
            if not pa:
                for key, val in ro_map.items():
                    if key in p_name_norm or p_name_norm in key:
                        pa = val
                        break
            
            if not pa: pa = {}
            cat = pa.get('category', 'Combatant')
            with r_cols[i]:
                st.markdown(f"""
                <div class='player-card'>
                    <div class='category-badge cat-{cat.lower()}'>{cat}</div>
                    <b style='font-size:1.2rem; color:#ffffff !important;'>{pr['name']}</b><br>
                    <small style='color:#00d4ff !important;'>Avg KDA: {pr['avg_kda']} | Impact: {pr.get('impact_score', 0)}</small>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("VIEW INTEL"):
                    st.markdown(f"<p style='color:#10b981 !important;'><b>💪 STRENGTH:</b> {pa.get('strength', 'High impact')}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#ef4444 !important;'><b>⚠️ WEAKNESS:</b> {pa.get('weakness', 'Vulnerable')}</p>", unsafe_allow_html=True)

    # --- 4. PLAYBOOK ---
    st.markdown("<div class='section-title'>🧠 AI Strategic Playbook</div>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top: -20px; color: #888; font-size: 0.9rem;'>AI-generated scouting insights covering team weaknesses, player threats, and suggested match strategies.</p>", unsafe_allow_html=True)
    if is_partial:
        st.warning("⚠️ Insufficient data to build an AI Playbook for this target.")
    else:
        pk1, pk2 = st.columns(2)
        with pk1:
            with st.container(border=True):
                st.markdown("<h4 style='color:#ff4b4b !important;font-family:Orbitron;'>⚠️ Team Weaknesses</h4>", unsafe_allow_html=True)
                st.markdown(playbook.get('vulnerability', 'Loading...'))
            with st.container(border=True):
                st.markdown("<h4 style='color:#00d4ff !important;font-family:Orbitron;'>⚔️ Suggested Strategy</h4>", unsafe_allow_html=True)
                st.markdown(playbook.get('killer_strategy', 'Loading...'))
        with pk2:
            with st.container(border=True):
                st.markdown("<h4 style='color:orange !important;font-family:Orbitron;'>👥 Key Player Threats</h4>", unsafe_allow_html=True)
                st.markdown(playbook.get('roster_threats', 'Loading...'))
            with st.container(border=True):
                st.markdown("<h4 style='color:#10b981 !important;font-family:Orbitron;'>🏁 Recommended Execution</h4>", unsafe_allow_html=True)
                st.markdown(playbook.get('execution_plan', 'Loading...'))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 5. EXPORT OPTIONS ---
    if not is_partial:
        st.markdown("<div class='section-title'>📤 Download Report</div>", unsafe_allow_html=True)
        try:
            pdf_bytes = get_cached_pdf(team_name, enriched_data, playbook, structured_roster, winning_trends, counter_strategy)
            st.download_button(
                label="📕 DOWNLOAD SCOUTING REPORT (PDF)", 
                data=pdf_bytes, 
                file_name=f"{team_name}_scouting_report.pdf", 
                mime="application/pdf", 
                key=f"dl_pdf_{mode_key}_{team_id}"
            )
        except Exception as e:
            st.error(f"PDF Error: {e}")

    # ALWAYS SHOW DIAGNOSTICS if debug is on, OR if we had insufficient data
    if DEBUG_MODE or is_partial:
        with st.expander("🛠️ SYSTEM DIAGNOSTICS (DEBUG)", expanded=is_partial):
            if is_partial:
                st.error("⚠️ DATA ANOMALY: The GRID API returned series metadata, but the state data for these sessions was incompatible or missing.")
            st.json(enriched_data)

def run_scouting_workflow(team_name, team_id, tournament_id=None):
    """Core logic to handle data collection via status bar."""
    with st.status("⚡ INITIATING STRATEGIC DATA EXTRACTION...", expanded=True) as status:
        st.write("🛰️ Connecting to GRID Esports Data API...")
        s_info_list = fetch_series_info_for_team(team_id, tournament_id=tournament_id)
        
        if not s_info_list:
            status.update(label="❌ NO COMBAT DATA FOUND", state="error")
            st.error("⚠️ No recent data found for this team. Please select other teams.")
            return None
        
        st.write("🔬 Analyzing Match Statistics...")
        enriched_data = collect_team_data(team_name, s_info_list)
        
        # Double check if we have series data after enrichment
        if not enriched_data.get("series"):
            status.update(label="❌ INSUFFICIENT DATA", state="error")
            st.warning("⚠️ Data found, but it is too limited for AI modeling.")
            # Return empty LLM parts so display_scouting_results can still show the diagnostic JSON
            return (enriched_data, None, None, None, None)

        st.write("🧠 Generating AI Scouting Insights...")
        playbook, structured_roster, winning_trends, counter_strategy = generate_scouting_report(team_name, enriched_data)
        status.update(label=f"ANALYSIS COMPLETE: {team_name.upper()} REPORT GENERATED", state="complete")
        
        return (enriched_data, playbook, structured_roster, winning_trends, counter_strategy)

# --- UI TABS ---
t1, t2, t3 = st.tabs([" 🏆 Quick Scouting ", " 🌍 Global Team Search ", " ⚔️ Matchup Analysis "])

def reset_t1():
    if 'res_t1' in st.session_state: del st.session_state['res_t1']

def reset_t2():
    if 'res_t2' in st.session_state: del st.session_state['res_t2']

with t1:
    # 🎯 TARGET ACQUISITION (TOP FIXED)
    with st.container(border=True):
        sel_c1, sel_c2, sel_c3 = st.columns([1.5, 1.5, 0.8])
        
        with sel_c1:
            st.markdown("<label>Select Tournament</label>", unsafe_allow_html=True)
            tours = st.session_state.get('tours', [])
            sel_tn = st.selectbox(
                "Select Tournament", 
                [t['name'] for t in tours], 
                index=None, 
                placeholder="Choose a circuit...", 
                key="scout_tour", 
                on_change=on_scout_tour_change,
                label_visibility="collapsed"
            )
        
        with sel_c2:
            st.markdown("<label>Select Target Team</label>", unsafe_allow_html=True)
            tteams = st.session_state.get('tteams', [])
            sel_team = st.selectbox(
                "Select Target Team", 
                [t['name'] for t in tteams], 
                index=None, 
                placeholder="Target Team...", 
                key="scout_team", 
                on_change=reset_t1,
                label_visibility="collapsed"
            )

        with sel_c3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            execute_btn = st.button("🚀 Generate Report", use_container_width=True)

    # 🔄 CENTRAL PROCESSING & RESULTS
    main_area = st.empty()
    
    if execute_btn and sel_team:
        ite = next(t for t in tteams if t['name'] == sel_team)
        with main_area.container():
            st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
            # Center the status by putting it in a narrow col
            _, log_col, _ = st.columns([1, 2, 1])
            with log_col:
                dp = run_scouting_workflow(sel_team, ite['id'], st.session_state.get('last_tid'))
        
        if dp:
            st.session_state['res_t1'] = (sel_team, ite['id'], dp)
            # We don't call main_area.empty() here to avoid the "jumping" effect
            # Instead, the next block will overwrite the main_area content

    if 'res_t1' in st.session_state:
        n, i, data = st.session_state['res_t1']
        with main_area.container():
            display_scouting_results(n, i, "t1", data)
    else:
        with main_area.container():
            st.markdown("<div style='height:400px; display:flex; flex-direction:column; align-items:center; justify-content:center; border:2px dashed #1e3a5f; border-radius:20px;'><h3 style='color:#1e3a5f; font-family:Orbitron;'>Ready for Analysis</h3><p style='color:#1e3a5f;'>Select a tournament and team above to begin.</p></div>", unsafe_allow_html=True)


with t2:
    with st.container(border=True):
        st.markdown("<h4 style='color:#00d4ff; font-family:Orbitron; margin-bottom:10px;'>🌍 Global Team Search</h4>", unsafe_allow_html=True)
        gcol1, gcol2 = st.columns([2, 1])
        with gcol1:
            univ = st.session_state.get('guniv', [])
            st.markdown("<label>Search Global Teams</label>", unsafe_allow_html=True)
            sel_gu = st.selectbox("Search Global Teams", [t['display'] for t in univ], index=None, placeholder="Type a team name...", key="global_target", on_change=on_global_change, label_visibility="collapsed")
        with gcol2:
            st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
            g_execute = st.button("🚀 Start Global Analysis", use_container_width=True, key="btn_global")

    g_main = st.empty()
    
    if g_execute and sel_gu:
        ite = next(t for t in univ if t['display'] == sel_gu)
        with g_main.container():
            st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
            _, lcol, _ = st.columns([1, 2, 1])
            with lcol:
                dp = run_scouting_workflow(ite['name'], ite['id'])
        if dp:
            st.session_state['res_t2'] = (ite['name'], ite['id'], dp)
            g_main.empty()

    if 'res_t2' in st.session_state:
        n, i, data = st.session_state['res_t2']
        with g_main.container():
            display_scouting_results(n, i, "g2", data)
    else:
        with g_main.container():
            st.markdown("<div style='height:400px; display:flex; flex-direction:column; align-items:center; justify-content:center; border:2px dashed #1e3a5f; border-radius:20px;'><h3 style='color:#1e3a5f; font-family:Orbitron;'>Global Search Standby</h3><p style='color:#1e3a5f;'>Select a team to begin global analysis</p></div>", unsafe_allow_html=True)

# --- UI TABS ---

with t3:
    # Matchup Analysis now uses the pre-synchronized 'ca' and 'cb' lists
    st.markdown("<div class='section-title'>⚔️ Team Comparison Analysis</div>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top: -20px; color: #888; font-size: 0.9rem;'>Select two teams to compare their stats side-by-side and see an AI-generated battle verdict.</p>", unsafe_allow_html=True)
    with st.container(border=True):
        c_cols = st.columns([1, 1, 0.8])
        with c_cols[0]:
            sa = st.selectbox("TEAM ALPHA", [t['display'] for t in st.session_state.get('ca', [])], key="sa", placeholder="Select first team...", index=None, on_change=on_comp_change)
        with c_cols[1]:
            sb = st.selectbox("TEAM BETA", [t['display'] for t in st.session_state.get('cb', [])], key="sb", placeholder="Select second team...", index=None, on_change=on_comp_change)
        with c_cols[2]:
            st.markdown("<br>", unsafe_allow_html=True)
            c_execute = st.button("⚔️ Start Comparison", use_container_width=True, key="btn_matchup")

    c_main = st.empty()

    if c_execute and sa and sb:
        oa = next(t for t in st.session_state['ca'] if t['display'] == sa)
        ob = next(t for t in st.session_state['cb'] if t['display'] == sb)
        
        with c_main.container():
            st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
            _, c_log, _ = st.columns([1, 2, 1])
            with c_log:
                with st.status("⚔️ SIMULATING COMBAT ENGAGEMENT...", expanded=True) as status:
                    st.write(f"📊 Gathering {oa['name']} match data...")
                    da = collect_team_data(oa['name'], fetch_series_info_for_team(oa['id'], limit=10))
                    st.write(f"📊 Gathering {ob['name']} match data...")
                    db = collect_team_data(ob['name'], fetch_series_info_for_team(ob['id'], limit=10))
                    st.write("🧠 Comparing team playstyles...")
                    res = generate_comparison_report(oa['name'], da, ob['name'], db)
                    status.update(label="COMPARISON COMPLETE!", state="complete")
        
        if res:
            st.session_state['res_comp'] = (oa['name'], ob['name'], res, da, db)
            c_main.empty()

    if 'res_comp' in st.session_state:
        na, nb, res, da, db = st.session_state['res_comp']
        
        # Calculate Stats for Side-by-Side
        def get_brief_stats(data):
            twins = sum(1 for s in data["series"] if s["series_win"])
            tser = len(data["series"])
            wr = f"{round((twins/tser)*100,1) if tser > 0 else 0}%"
            kda = round(sum(p['avg_kda'] for p in data['top_players'])/len(data['top_players']),1) if data['top_players'] else 0
            return wr, tser, kda, data.get('map_win_rate', 0)

        wra, tsa, kdaa, mwra = get_brief_stats(da)
        wrb, tsb, kdab, mwrb = get_brief_stats(db)

        with c_main.container():
            st.markdown("<div class='section-title'>🥊 Matchup Analysis</div>", unsafe_allow_html=True)
            st.markdown("<p style='margin-top: -20px; color: #888; font-size: 0.9rem;'>Detailed side-by-side comparison of the two selected teams with AI-predicted outcomes.</p>", unsafe_allow_html=True)
            
            # --- SIDE BY SIDE STATS ---
            st.markdown("<div class='section-title' style='font-size:1.1rem; border-bottom: 1px solid #1e3a5f;'>📊 TACTICAL SIDE-BY-SIDE</div>", unsafe_allow_html=True)
            comparison_rows = [
                {"Metric": "Win Rate", na: str(wra), nb: str(wrb)},
                {"Metric": "Series Played", na: str(tsa), nb: str(tsb)},
                {"Metric": "Average KDA", na: str(kdaa), nb: str(kdab)},
                {"Metric": "Map Win %", na: f"{mwra}%", nb: f"{mwrb}%"}
            ]
            st.table(pd.DataFrame(comparison_rows).set_index("Metric"))

            # --- SIDE BY SIDE PLAYER COMPARISON ---
            st.markdown("<div class='section-title' style='font-size:1.1rem; border-bottom: 1px solid #1e3a5f;'>👥 TOP PROFILES COMPARISON</div>", unsafe_allow_html=True)
            pa_top = da['top_players'][:3]
            pb_top = db['top_players'][:3]
            
            p_comp_data = []
            for idx in range(3):
                p_comp_data.append({
                    "Rank": idx + 1,
                    f"{na} (Player)": pa_top[idx]['name'] if idx < len(pa_top) else "N/A",
                    f"{na} (KDA)": pa_top[idx]['avg_kda'] if idx < len(pa_top) else "-",
                    f"{nb} (Player)": pb_top[idx]['name'] if idx < len(pb_top) else "N/A",
                    f"{nb} (KDA)": pb_top[idx]['avg_kda'] if idx < len(pb_top) else "-",
                })
            st.table(pd.DataFrame(p_comp_data).set_index("Rank"))

            st.markdown(f"<div class='trend-box'><span style='color:#00d4ff;font-family:Orbitron;font-size:0.9rem;'>🏆 ANALYSIS VERDICT</span><br><p style='font-size:1.2rem; color:#ffffff !important;'>{res['verdict']}</p></div>", unsafe_allow_html=True)
            
            row1_c1, row1_c2 = st.columns(2)
            with row1_c1:
                with st.container(border=True):
                    st.markdown("<h4 style='color:orange !important; font-family:Orbitron;'>🎯 PLAYER WAR</h4>", unsafe_allow_html=True)
                    st.markdown(res['player_war'])
            with row1_c2:
                with st.container(border=True):
                    st.markdown("<h4 style='color:#ff4b4b !important; font-family:Orbitron;'>📉 TACTICAL GAP</h4>", unsafe_allow_html=True)
                    st.markdown(res['gap'])
            
            # --- Tabular Priority Targets ---
            st.markdown(f"<div class='counter-box' style='background:rgba(0, 212, 255, 0.05); border-left:5px solid #00d4ff;'><span style='color:#00d4ff;font-family:Orbitron;font-size:0.9rem;'>🎯 MISSION-CRITICAL TARGET ASSIGNMENTS</span><br></div>", unsafe_allow_html=True)
            
            p_data = res.get('priority', '')
            rows = []
            for line in p_data.split('\n'):
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        rows.append({"Attacking Team": parts[0], "Primary Target": parts[1], "Strategic Reason": parts[2]})
            
            if rows:
                pdf_df = pd.DataFrame(rows)
                pdf_df.index = pdf_df.index + 1
                pdf_df.index.name = "Sr"
                st.table(pdf_df)
            else:
                st.info("Directives pending AI calculation...")

            st.markdown(f"<div class='counter-box'><span style='color:#ff4b4b;font-family:Orbitron;font-size:0.9rem;'>⚔️ KILLER MATCH STRATEGY</span><br></div>", unsafe_allow_html=True)
            st.markdown(res['strategy'])
            
            # --- COMPARISON EXPORT ---
            st.markdown("<div class='section-title'>📤 Download Comparison Report</div>", unsafe_allow_html=True)
            st.markdown("<p style='margin-top: -20px; color: #888; font-size: 0.9rem;'>Export this head-to-head comparison as a professional PDF report.</p>", unsafe_allow_html=True)
            try:
                # Prepare stats bundle for PDF
                stats_bundle = {
                    "team_a": {"Win Rate": wra, "Series Played": tsa, "Average KDA": kdaa, "Map Win %": f"{mwra}%"},
                    "team_b": {"Win Rate": wrb, "Series Played": tsb, "Average KDA": kdab, "Map Win %": f"{mwrb}%"}
                }
                comp_pdf = generate_comparison_pdf(na, nb, res, stats_bundle)
                st.download_button(
                    label="📕 DOWNLOAD COMPARISON DOSSIER (PDF)",
                    data=comp_pdf,
                    file_name=f"{na}_vs_{nb}_scouting_report.pdf",
                    mime="application/pdf",
                    key="dl_comp_pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF Error: {e}")
    else:
        with c_main.container():
            st.markdown("<div style='height:400px; display:flex; flex-direction:column; align-items:center; justify-content:center; border:2px dashed #0077ff; border-radius:20px;'><h3 style='color:#0077ff; font-family:Orbitron;'>Comparison Engine Ready</h3><p style='color:#0077ff;'>Select two teams to begin analysis</p></div>", unsafe_allow_html=True)
