import streamlit as st
import streamlit_sortables as sortables
import json, os, io, base64
from PIL import Image, ImageDraw, ImageFont
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import requests
import time
import random
import html  # Added for HTML sanitization
from streamlit import fragment
import streamlit.components.v1 as components

# ==========================================================
# 🖥️ DESKTOP FULL-WIDTH / WIDE LAYOUT CONFIGURATION
# This MUST be the first Streamlit command called in the script!
# ==========================================================
st.set_page_config(
    page_title="EPIC Singing VC Queue",
    page_icon="⚔️",
    layout="wide",  # Enables full horizontal screen utilization on desktop
    initial_sidebar_state="collapsed"
)

# ========== EPIC THE MUSICAL SONG DATA ==========
EPIC_SONGS = {
    "The Horse and the Infant": ["Odysseus", "Zeus", "Soldiers", "Infant Astyanax"],
    "Just a Man": ["Odysseus", "Zeus", "Ensemble"],
    "Full Speed Ahead": ["Odysseus", "Eurylochus", "Polites", "Crew"],
    "Open Arms": ["Polites", "Odysseus", "Lotus Eaters"],
    "Warrior of the Mind": ["Athena", "Young Odysseus", "Ensemble"],
    "Polyphemus": ["Odysseus", "Polyphemus", "Eurylochus", "Crew"],
    "Survive": ["Odysseus", "Polyphemus", "Crew"],
    "Remember Them": ["Odysseus", "Athena", "Polyphemus", "Crew"],
    "My Goodbye": ["Athena", "Odysseus"],
    "Storm": ["Odysseus", "Crew", "Poseidon"],
    "Luck Runs Out": ["Eurylochus", "Odysseus", "Crew"],
    "Keep Your Friends Close": ["Aeolus", "Odysseus", "Winions", "Crew"],
    "Ruthlessness": ["Poseidon", "Odysseus", "Crew"],
    "Puppeteer": ["Circe", "Odysseus", "Enchanted Crew"],
    "Wouldn't You Like": ["Hermes", "Odysseus"],
    "Done For": ["Circe", "Odysseus"],
    "There Are Other Ways": ["Circe", "Odysseus"],
    "The Underworld": ["Odysseus", "Dead Souls", "Anticlea", "Prophet Spirits"],
    "No Longer You": ["Tiresias", "Odysseus"],
    "Monster": ["Odysseus", "Ensemble"],
    "Suffering": ["Siren Penelope", "Odysseus", "Sirens"],
    "Different Beast": ["Odysseus", "Crew", "Sirens"],
    "Scylla": ["Odysseus", "Scylla", "Crew"],
    "Mutiny": ["Eurylochus", "Odysseus", "Crew"],
    "Thunder Bringer": ["Zeus", "Odysseus", "Crew"],
    "Legendary": ["Telemachus", "Suitors", "Ensemble"],
    "Little Wolf": ["Athena", "Telemachus", "Antinous"],
    "We'll Be Fine": ["Athena", "Telemachus"],
    "Love in Paradise": ["Calypso", "Odysseus"],
    "God Games": ["Athena", "Zeus", "Hera", "Aphrodite", "Ares", "Apollo", "Hephaestus"],
    "Not Sorry for Loving You": ["Calypso", "Odysseus"],
    "Dangerous": ["Hermes", "Odysseus"],
    "Charybdis": ["Odysseus", "Charybdis"],
    "Get in the Water": ["Poseidon", "Odysseus"],
    "Six Hundred Strike": ["Odysseus", "Poseidon", "Crew Spirits"],
    "The Challenge": ["Penelope", "Suitors", "Telemachus"],
    "Hold Them Down": ["Antinous", "Suitors"],
    "Odysseus": ["Odysseus", "Suitors", "Telemachus"],
    "I Can't Help but Wonder": ["Odysseus", "Telemachus"],
    "Would You Fall in Love with Me Again": ["Odysseus", "Penelope"],
    "Olive Tree": ["Odysseus", "Penelope"],
    "Your LIght": ["Odysseus", "Polites"]
}

KARAOKE_SONGS = [
    {"title": "The Horse and the Infant", "url": "https://www.youtube.com/watch?v=YZfPD0btgzA"},
    {"title": "Just a Man", "url": "https://www.youtube.com/watch?v=Y8dXa_OY7wU"},
    {"title": "Full Speed Ahead", "url": "https://www.youtube.com/watch?v=5rqbG4uHbgs"},
    {"title": "Open Arms", "url": "https://www.youtube.com/watch?v=McPwEM2E-kA"},
    {"title": "Warrior of the Mind", "url": "https://www.youtube.com/watch?v=2SZQ-C2od5I"},
    {"title": "Polyphemus", "url": "https://www.youtube.com/watch?v=V7J5leX5YSI"},
    {"title": "Survive", "url": "https://www.youtube.com/watch?v=0AAAQEPpC48"},
    {"title": "Remember Them", "url": "https://www.youtube.com/watch?v=m1cmIF-bOjE"},
    {"title": "My Goodbye", "url": "https://www.youtube.com/watch?v=6TUtiuD2S6I"},
    {"title": "Storm", "url": "https://www.youtube.com/watch?v=23sr9u6dWvc"},
    {"title": "Luck Runs Out", "url": "https://www.youtube.com/watch?v=ot_ZjHetnu8"},
    {"title": "Keep Your Friends Close", "url": "https://www.youtube.com/watch?v=uuLIWp5APb4"},
    {"title": "Ruthlessness", "url": "https://www.youtube.com/watch?v=R3qVgou4A9M"},
    {"title": "Puppeteer", "url": "https://www.youtube.com/watch?v=dOQdxdGRZts"},
    {"title": "Wouldn't You Like", "url": "https://www.youtube.com/watch?v=bcQge1DrhJ0"},
    {"title": "Done For", "url": "https://www.youtube.com/watch?v=YEnjUfILZks"},
    {"title": "There Are Other Ways", "url": "https://www.youtube.com/watch?v=DXyU4lgOdNg"},
    {"title": "The Underworld", "url": "https://www.youtube.com/watch?v=nPLCZTYa7X8"},
    {"title": "No Longer You", "url": "https://www.youtube.com/watch?v=54ubVuVJD7Y"},
    {"title": "Monster", "url": "https://www.youtube.com/watch?v=5xEbWoPh-aU"},
    {"title": "Suffering", "url": "https://www.youtube.com/watch?v=HvnMShpTeYY"},
    {"title": "Different Beast", "url": "https://www.youtube.com/watch?v=BnLkgJKEelI"},
    {"title": "Scylla", "url": "https://www.youtube.com/watch?v=-ZaYvNJ_nvY"},
    {"title": "Mutiny", "url": "https://www.youtube.com/watch?v=dFenHkaoyck"},
    {"title": "Thunder Bringer", "url": "https://www.youtube.com/watch?v=1AytyN8tHXA"},
    {"title": "Legendary", "url": "https://www.youtube.com/watch?v=fKFqyr5Z1GY"},
    {"title": "Little Wolf", "url": "https://www.youtube.com/watch?v=St0T0D3ArvY"},
    {"title": "We'll Be Fine", "url": "https://www.youtube.com/watch?v=ogBM4tCu7Lc"},
    {"title": "Love in Paradise", "url": "https://www.youtube.com/watch?v=wzwdfdB7fI8"},
    {"title": "God Games", "url": "https://www.youtube.com/watch?v=iYSgqR_STUE"},
    {"title": "Not Sorry for Loving You", "url": "https://www.youtube.com/watch?v=GFo4rNvfEgE"},
    {"title": "Dangerous", "url": "https://www.youtube.com/watch?v=5Vl-hHDu23M"},
    {"title": "Charybdis", "url": "https://www.youtube.com/watch?v=bHM8pjotMWw"},
    {"title": "Get in the Water", "url": "https://www.youtube.com/watch?v=0QkUmui4_Uw"},
    {"title": "Six Hundred Strike", "url": "https://www.youtube.com/watch?v=5i2U38ISj1c"},
    {"title": "The Challenge", "url": "https://www.youtube.com/watch?v=I-KlhO46puk"},
    {"title": "Hold Them Down", "url": "https://www.youtube.com/watch?v=LOgbDbrv2Q4"},
    {"title": "Odysseus", "url": "https://www.youtube.com/watch?v=S4C55xJmMDc"},
    {"title": "I Can't Help but Wonder", "url": "https://www.youtube.com/watch?v=v6qVpnoyLuk"},
    {"title": "Would You Fall in Love with Me Again", "url": "https://www.youtube.com/watch?v=GEyvmZqOv0g"},
    {"title": "Olive Tree", "url": "https://www.youtube.com/watch?v=xDG5VKScZDY"},  
    {"title": "Your Light", "url": "https://www.youtube.com/watch?v=JxpKzQqT5YM"}   
]

def find_best_karaoke_match(query):
    """Find best matching karaoke song using fuzzy token matching."""
    if not query:
        return None
    query_lower = query.lower()
    best_match = None
    best_score = 0
    for song in KARAOKE_SONGS:
        title_lower = song["title"].lower()
        if query_lower in title_lower:
            score = len(query_lower) / len(title_lower) * 100 + 50
        else:
            q_tokens = set(query_lower.split())
            t_tokens = set(title_lower.split())
            overlap = q_tokens & t_tokens
            score = len(overlap) / max(len(q_tokens), 1) * 100
        if score > best_score:
            best_score = score
            best_match = song
    return best_match if best_score > 0 else None

def get_youtube_embed_url(yt_url):
    """Convert YouTube watch URL to embed URL."""
    if "watch?v=" in yt_url:
        vid_id = yt_url.split("watch?v=")[1].split("&")[0]
        return f"https://www.youtube.com/embed/{vid_id}"
    return yt_url

SAVE_FILE = "queue.json"
TEMPLATES_DIR = "templates"
ADMIN_PASSCODE = "531246"
SYNC_CHECK_INTERVAL = 1  # Check for updates every 1 second

if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

DEFAULT_TEMPLATE = {
    "name": "Default EPIC",
    "title": "🏛️ 𝑬𝑷𝑰𝑪 𝑺𝒐𝒏𝒈 𝑸𝒖𝒆𝒖𝒆 🎭",
    "url": "<https://epic-queue.streamlit.app>",
    "currently_singing": "𝑪𝑼𝑹𝑹𝑬𝑵𝑻𝑳𝒀 𝑺𝑰𝑵𝑮𝑰𝑵𝑮",
    "current_symbol": "👑",
    "next_up": "𝑵𝑬𝑿𝑻 𝑼𝑷",
    "next_symbol": "🌟",
    "on_queue": "𝑶𝑵 𝑸𝑼𝑬𝑼𝑬",
    "queue_symbol": ":lollipop:",
    "away_calypso": "𝑨𝒘𝒂𝒚 𝒘𝒊𝒕𝒉 𝑪𝒂𝒍𝒚𝒑𝒔𝒐",
    "calypso_symbol": "🌴",
    "reactions": ":cheese: — Join the Queue\n:mouse_trap: — Leave the Queue\n📣 — Summon the Bard (Ping)\n⏳ — Place Me On Hold",
    "wheel_link": "<https://wheelofnames.com/jr7-eaa>"
}

def load_state(vc_id):
    """Load state for specific VC (vc1 or vc2)"""
    save_file = f"queue_{vc_id}.json"
    if os.path.exists(save_file):
        with open(save_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "queue": data.get("queue", []),
            "calypso": data.get("calypso", []),
            "pinged": set(data.get("pinged", [])),
            "current_manager": data.get("current_manager", ""),
            "current_template": data.get("current_template", "Default EPIC"),
            "last_modified": data.get("last_modified", 0),
            "selected_song": data.get("selected_song", ""),
            "role_assignments": data.get("role_assignments", {}),
        }
    return {
        "queue": [],
        "calypso": [],
        "pinged": set(),
        "current_manager": "",
        "current_template": "Default EPIC",
        "last_modified": time.time(),
        "selected_song": "",
        "role_assignments": {},
    }

def save_state(vc_id, state):
    """Save state for specific VC"""
    save_file = f"queue_{vc_id}.json"
    data = {
        "queue": state["queue"],
        "calypso": state["calypso"],
        "pinged": list(state["pinged"]),
        "current_manager": state["current_manager"],
        "current_template": state["current_template"],
        "last_modified": time.time(),
        "selected_song": state.get("selected_song", ""),
        "role_assignments": state.get("role_assignments", {}),
    }
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

def check_for_updates(vc_id, current_last_modified):
    """Check if file has been modified by another user"""
    save_file = f"queue_{vc_id}.json"
    if os.path.exists(save_file):
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            last_modified = data.get("last_modified", 0)
            return last_modified > current_last_modified
        except:
            return False
    return False

def load_template(template_name):
    """Load template from file or return default"""
    if template_name == "Default EPIC":
        return DEFAULT_TEMPLATE.copy()
    
    template_file = os.path.join(TEMPLATES_DIR, f"{template_name}.json")
    if os.path.exists(template_file):
        with open(template_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_TEMPLATE.copy()

def save_template(template_name, template_data):
    """Save template to file"""
    template_file = os.path.join(TEMPLATES_DIR, f"{template_name}.json")
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(template_data, f, indent=2)

def delete_template(template_name):
    # Strip out any directory traversal attempts like ../ or ..\
    clean_name = os.path.basename(template_name)
    
    # Alternatively, ensure it only points to a literal filename
    file_path = os.path.join(TEMPLATES_DIR, f"{clean_name}.json")
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            # If it still fails, check if the file literal name on disk is exactly the broken string
            fallback_path = os.path.join(TEMPLATES_DIR, f"{template_name}.json")
            if os.path.exists(fallback_path):
                os.remove(fallback_path)
                return True
            return False
    except Exception as e:
        st.error(f"Error removing file: {e}")
        return False

def get_available_templates():
    """Get list of available templates without duplicates"""
    templates = ["Default EPIC"]
    seen = {"Default EPIC"} # Track what we've already added
    
    if os.path.exists(TEMPLATES_DIR):
        for file in os.listdir(TEMPLATES_DIR):
            if file.endswith(".json"):
                name = file.replace(".json", "")
                if name not in seen:
                    templates.append(name)
                    seen.add(name)
    return templates

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_vc = "vc1"
    st.session_state.vc1_data = load_state("vc1")
    st.session_state.vc2_data = load_state("vc2")
    st.session_state.rev = 0
    st.session_state.current_user_vc1 = ""
    st.session_state.current_user_vc2 = ""
    st.session_state.show_manager_confirm = False
    st.session_state.manager_candidate = ""
    st.session_state.admin_authenticated = False
    for flag in ["show_leave", "show_hold", "show_return", "show_ping"]:
        st.session_state[flag] = False
    st.session_state.vc1_role_history = []
    st.session_state.vc2_role_history = []

# Auto-refresh for non-managers
is_manager_vc1 = st.session_state.current_user_vc1 == st.session_state.vc1_data["current_manager"]
is_manager_vc2 = st.session_state.current_user_vc2 == st.session_state.vc2_data["current_manager"]


st.markdown("<h1 style='text-align: center; font-weight: 700; margin-bottom: 1rem;'>EPIC KARAOKE MANAGER</h1>", unsafe_allow_html=True)

# ========== MAIN NAVIGATION ==========
selected_tab = st.segmented_control(
    "Select Section - Must use the dark theme from the top right triple dot setting !, use F11 for fullscreen",
    ["🎵 VC 1", "🎵 VC 2", "✨ Customize"],
    default=st.session_state.get("main_selected_tab"),
    key="main_selected_tab"
)

def render_vc_content(vc_id):
    """Render queue content for a specific VC"""
    
    if vc_id == "vc1":
        vc_data = st.session_state.vc1_data
        current_user_key = "current_user_vc1"
    else:
        vc_data = st.session_state.vc2_data
        current_user_key = "current_user_vc2"
    
    if check_for_updates(vc_id, vc_data["last_modified"]):
        updated_data = load_state(vc_id)
        if vc_id == "vc1":
            st.session_state.vc1_data = updated_data
            vc_data = updated_data
        else:
            st.session_state.vc2_data = updated_data
            vc_data = updated_data
        st.rerun()
    
    active_song = vc_data.get("selected_song", "")
    
    if vc_data["current_manager"]:
        st.info(f"💡 Currently managing: **{html.escape(vc_data['current_manager'])}**")
    else:
        st.info(f"💡 No one is managing {vc_id.upper()}. Press 'Manage Queue' to take control.")

    # ----------- Manager Name Input & Claim Button -----------
    claim_cols = st.columns([4, 1, 1])
    with claim_cols[0]:
        manager_name = st.text_input(
            "Type your name",
            max_chars=20,  # Enforce 20 char limit on input level
            key=f"{vc_id}_manager_input",
            label_visibility="collapsed",
            placeholder="Type your name (Max 20 chars)"
        ).strip()

    def really_claim_manager(name):
        name = name[:20] # Safeguard truncation
        vc_data["current_manager"] = name
        save_state(vc_id, vc_data)
        st.session_state[current_user_key] = name
        if vc_id == "vc1":
            st.session_state.vc1_data = vc_data
        else:
            st.session_state.vc2_data = vc_data
        st.success("You are now managing the queue.")
        st.session_state.show_manager_confirm = False
        st.session_state.manager_candidate = ""
        st.rerun()

    def handle_claim_request(name):
        current_manager = vc_data.get("current_manager", "")
        if name:
            if current_manager and current_manager != name:
                st.session_state.show_manager_confirm = True
                st.session_state.manager_candidate = name
            else:
                really_claim_manager(name)

    with claim_cols[1]:
        if st.button("🛠 Manage Queue", use_container_width=True, key=f"{vc_id}_claim_btn"):
            if manager_name:
                handle_claim_request(manager_name)
            else:
                st.warning("Type your name before claiming the queue.")

    with claim_cols[2]:
        if st.session_state[current_user_key] == vc_data["current_manager"] and vc_data["current_manager"]:
            if st.button("🔓 Release", use_container_width=True, key=f"{vc_id}_release_btn"):
                vc_data["current_manager"] = ""
                st.session_state[current_user_key] = ""
                save_state(vc_id, vc_data)
                if vc_id == "vc1":
                    st.session_state.vc1_data = vc_data
                else:
                    st.session_state.vc2_data = vc_data
                st.success("You have released manage rights.")
                st.rerun()

    if st.session_state.show_manager_confirm:
        st.warning(f"⚠️ You will REPLACE **{html.escape(vc_data['current_manager'])}** as manager. Are you sure?")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Yes, replace", key=f"{vc_id}_manager_yes_btn"):
                really_claim_manager(st.session_state.manager_candidate)
        with col_no:
            if st.button("No, cancel", key=f"{vc_id}_manager_no_btn"):
                st.session_state.show_manager_confirm = False
                st.session_state.manager_candidate = ""

    # ----------- YouTube Karaoke Player -----------
    st.markdown("---")
    
    yt_search_key = f"{vc_id}_yt_search"
    yt_url_key = f"{vc_id}_yt_current_url"
    yt_title_key = f"{vc_id}_yt_current_title"
    if yt_url_key not in st.session_state:
        st.session_state[yt_url_key] = ""
        st.session_state[yt_title_key] = ""

    def set_yt_from_song_title(song_title):
        match = find_best_karaoke_match(song_title)
        if match:
            st.session_state[yt_url_key] = get_youtube_embed_url(match["url"])
            st.session_state[yt_title_key] = match["title"]

    def handle_yt_search():
        query = st.session_state.get(yt_search_key, "").strip()
        if query:
            match = find_best_karaoke_match(query)
            if match:
                st.session_state[yt_url_key] = get_youtube_embed_url(match["url"])
                st.session_state[yt_title_key] = match["title"]
                matched_title = match["title"]
                if matched_title in EPIC_SONGS:
                    vc_data["selected_song"] = matched_title
                    vc_data["role_assignments"] = {}
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.session_state[f"{vc_id}_song_select"] = matched_title
            else:
                st.session_state[yt_title_key] = "No match found"
            st.session_state[yt_search_key] = ""

    if active_song and st.session_state.get(yt_title_key) != active_song:
        set_yt_from_song_title(active_song)

    yt_col, dummy_col, actions_col = st.columns([3, 0.1, 1])

    with yt_col:
        # ---- Song selector + Spin (moved here from Role Assignment panel) ----
        _song_list_yt = list(EPIC_SONGS.keys())
        _songs_with_none_yt = ["— Select a song —"] + _song_list_yt
        _is_manager_yt = st.session_state[current_user_key] == vc_data["current_manager"]

        # Handle spin triggered from this area
        _spin_triggered_yt = False
        if _is_manager_yt and st.session_state.get(f"{vc_id}_spin_btn"):
            _spinner_ph = st.empty()
            _spin_durations = [0.05]*10 + [0.1]*5 + [0.2]*3 + [0.4]*1
            for _dur in _spin_durations:
                _temp = random.choice(_song_list_yt)
                _spinner_ph.markdown(
                    f'<div style="text-align:center;padding:10px;background:#1e1e24;border:2px solid #ffaa00;border-radius:8px;">'
                    f'<h3 style="color:#ffaa00;margin:0;">🎰 Spinning... 🎰</h3>'
                    f'<p style="font-size:1.2rem;color:white;margin:5px 0 0 0;">✨ <b>{html.escape(_temp)}</b> ✨</p></div>',
                    unsafe_allow_html=True
                )
                time.sleep(_dur)
            _winning = random.choice(_song_list_yt)
            _spinner_ph.empty()
            history_key_yt = f"{vc_id}_role_history"
            st.session_state[history_key_yt].append({
                "selected_song": vc_data.get("selected_song", ""),
                "role_assignments": dict(vc_data.get("role_assignments", {}))
            })
            vc_data["selected_song"] = _winning
            vc_data["role_assignments"] = {}
            active_song = _winning
            save_state(vc_id, vc_data)
            if vc_id == "vc1":
                st.session_state.vc1_data = vc_data
            else:
                st.session_state.vc2_data = vc_data
            st.session_state[f"{vc_id}_song_select"] = _winning
            _yt_match = find_best_karaoke_match(_winning)
            if _yt_match:
                st.session_state[yt_url_key] = get_youtube_embed_url(_yt_match["url"])
                st.session_state[yt_title_key] = _yt_match["title"]
            st.toast(f"🎯 Landed on: {_winning}!")
            _spin_triggered_yt = True

        _current_song_yt = vc_data.get("selected_song", "")
        _default_idx_yt = _songs_with_none_yt.index(_current_song_yt) if _current_song_yt in _songs_with_none_yt else 0

        _song_spin_cols = st.columns([5, 1])
        with _song_spin_cols[0]:
            _chosen_song_yt = st.selectbox(
                "🎵 Song",
                _songs_with_none_yt,
                index=_default_idx_yt,
                key=f"{vc_id}_song_select",
                disabled=not _is_manager_yt,
                label_visibility="collapsed"
            )
        with _song_spin_cols[1]:
            st.button("🎰 Spin!", key=f"{vc_id}_spin_btn", disabled=not _is_manager_yt, use_container_width=True)

        # Handle manual song selection
        if _is_manager_yt and not _spin_triggered_yt and _chosen_song_yt != "— Select a song —" and _chosen_song_yt != _current_song_yt:
            _hist_key = f"{vc_id}_role_history"
            st.session_state[_hist_key].append({
                "selected_song": vc_data.get("selected_song", ""),
                "role_assignments": dict(vc_data.get("role_assignments", {}))
            })
            vc_data["selected_song"] = _chosen_song_yt
            vc_data["role_assignments"] = {}
            active_song = _chosen_song_yt
            _yt_match2 = find_best_karaoke_match(_chosen_song_yt)
            if _yt_match2:
                st.session_state[yt_url_key] = get_youtube_embed_url(_yt_match2["url"])
                st.session_state[yt_title_key] = _yt_match2["title"]
            save_state(vc_id, vc_data)
            if vc_id == "vc1":
                st.session_state.vc1_data = vc_data
            else:
                st.session_state.vc2_data = vc_data
            st.session_state[f"{vc_id}_auto_reaction"] = True
            st.rerun()

        if _spin_triggered_yt:
            st.session_state[f"{vc_id}_auto_reaction"] = True
            st.balloons()
            st.rerun()

        if st.session_state[yt_title_key]:
            st.caption(f"🎤 Now playing: **{html.escape(st.session_state[yt_title_key])}**")

        # ---- REACTION BUTTONS ----
        REACTIONS = [
            ("🔥", "LEGENDARY", ["#FFD700","#FFA500","#FF8C00","#FFEC8B","#FF6600"]),
            ("✨", "AMAZING",   ["#00FFFF","#00BFFF","#1E90FF","#87CEFA","#AADDFF"]),
            ("👑", "ICONIC",    ["#DA70D6","#FF69B4","#BA55D3","#EE82EE","#FFB6C1"]),
            ("💥", "EPIC",      ["#FF4500","#FF6347","#FF0000","#FF7F50","#FF3300"]),
            ("🎶", "CHEESE APPROVED", ["#7FFF00","#ADFF2F","#00FA9A","#98FB98","#00FF88"]),
            ("⚡", "GODLIKE",   ["#FFD700","#FF69B4","#00FFFF","#7FFF00","#FF4500"]),
        ]

        # Auto-trigger a silent random reaction after song change to consume the forced iframe reload
        if st.session_state.pop(f"{vc_id}_auto_reaction", False):
            _auto = random.choice(REACTIONS)
            reaction_triggered = _auto[1]
            reaction_colors = _auto[2]
        else:
            reaction_triggered = None
            reaction_colors = None

        rcols = st.columns(len(REACTIONS))
        for idx, (emoji, word, _colors) in enumerate(REACTIONS):
            with rcols[idx]:
                if st.button(f"{emoji} {word}", key=f"{vc_id}_react_{word}", use_container_width=True):
                    reaction_triggered = word
                    reaction_colors = _colors

        # Inject fireworks into the MAIN page via components.html + window.parent
        # No st.rerun() — we fire immediately in the same render pass so the iframe is never rebuilt
        if reaction_triggered:
            _colors_js = str(reaction_colors)
            _word_js = reaction_triggered
            # --- FIX: ALWAYS RENDER THE COMPONENT TO STABILIZE THE DOM TREE ---
        import streamlit.components.v1 as _components
        
        fireworks_injection = ""
        
        if reaction_triggered:
            _colors_js = str(reaction_colors)
            _word_js = reaction_triggered
            fireworks_injection = f"""<script>
            (function() {{
              var doc = window.parent.document;
              var COLORS = {_colors_js};
              var WORD = "{_word_js}";
            
              // Remove any existing overlays
              ['__rx_canvas','__rx_word','__rx_kf'].forEach(function(id){{
                var el = doc.getElementById(id); if(el) el.remove();
              }});
            
              var canvas = doc.createElement('canvas');
              canvas.id = '__rx_canvas';
              canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:2147483647;';
              canvas.width = window.parent.innerWidth;
              canvas.height = window.parent.innerHeight;
              doc.body.appendChild(canvas);
              var ctx = canvas.getContext('2d');
            
              var wordEl = doc.createElement('div');
              wordEl.id = '__rx_word';
              var c1=COLORS[0], c2=COLORS[Math.floor(COLORS.length/2)];
              wordEl.innerText = WORD;
              wordEl.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) scale(0);' +
                'font-size:clamp(3rem,10vw,7rem);font-weight:900;letter-spacing:0.1em;pointer-events:none;' +
                'z-index:2147483647;white-space:nowrap;font-family:Georgia,serif;' +
                'background:linear-gradient(135deg,'+c1+','+c2+');-webkit-background-clip:text;' +
                '-webkit-text-fill-color:transparent;background-clip:text;' +
                'filter:drop-shadow(0 0 20px '+c1+') drop-shadow(0 0 40px '+c2+');' +
                'animation:__rxPop 3.2s ease forwards;';
              doc.body.appendChild(wordEl);
            
              if (!doc.getElementById('__rx_kf')) {{
                var s = doc.createElement('style'); s.id='__rx_kf';
                s.textContent = '@keyframes __rxPop {{' +
                  '0%{{transform:translate(-50%,-50%) scale(0) rotate(-8deg);opacity:0}}' +
                  '15%{{transform:translate(-50%,-50%) scale(1.35) rotate(3deg);opacity:1}}' +
                  '30%{{transform:translate(-50%,-50%) scale(1.0) rotate(0);opacity:1}}' +
                  '72%{{transform:translate(-50%,-50%) scale(1.0) rotate(0);opacity:1}}' +
                  '100%{{transform:translate(-50%,-50%) scale(0.5) rotate(5deg);opacity:0}}' +
                '}}';
                doc.head.appendChild(s);
              }}
            
              var P=[];
              function rnd(a,b){{return a+Math.random()*(b-a);}}
              function burst(x,y,n){{
                for(var i=0;i<n;i++){{
                  var angle=(Math.PI*2*i)/n+rnd(-0.4,0.4), speed=rnd(3,15);
                  P.push({{x:x,y:y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,
                    alpha:1,size:rnd(4,11),color:COLORS[Math.floor(Math.random()*COLORS.length)],
                    type:Math.random()<0.5?'star':'circle',grav:rnd(0.1,0.35),decay:rnd(0.013,0.025)}});
                }}
              }}
              function sparkle(x,y){{
                for(var i=0;i<6;i++){{
                  var a=Math.random()*Math.PI*2,sp=rnd(1,5);
                  P.push({{x:x,y:y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp-rnd(1,3),
                    alpha:1,size:rnd(2,7),color:COLORS[Math.floor(Math.random()*COLORS.length)],
                    type:'plus',grav:0.05,decay:rnd(0.025,0.05)}});
                }}
              }}
              function dStar(x,y,r,color,alpha){{
                ctx.save();ctx.globalAlpha=alpha;ctx.fillStyle=color;ctx.shadowColor=color;ctx.shadowBlur=10;
                ctx.beginPath();
                for(var i=0;i<5;i++){{
                  var oa=(Math.PI*2*i)/5-Math.PI/2,ia=oa+Math.PI/5;
                  i===0?ctx.moveTo(x+Math.cos(oa)*r,y+Math.sin(oa)*r):ctx.lineTo(x+Math.cos(oa)*r,y+Math.sin(oa)*r);
                  ctx.lineTo(x+Math.cos(ia)*r*.45,y+Math.sin(ia)*r*.45);
                }}
                ctx.closePath();ctx.fill();ctx.restore();
              }}
              function dPlus(x,y,r,color,alpha){{
                ctx.save();ctx.globalAlpha=alpha;ctx.strokeStyle=color;ctx.shadowColor=color;ctx.shadowBlur=12;ctx.lineWidth=2.5;
                ctx.beginPath();
                ctx.moveTo(x-r,y);ctx.lineTo(x+r,y);ctx.moveTo(x,y-r);ctx.lineTo(x,y+r);
                ctx.moveTo(x-r*.7,y-r*.7);ctx.lineTo(x+r*.7,y+r*.7);ctx.moveTo(x+r*.7,y-r*.7);ctx.lineTo(x-r*.7,y+r*.7);
                ctx.stroke();ctx.restore();
              }}
            
              var W=canvas.width,H=canvas.height;
              burst(W*.5,H*.3,65);burst(W*.2,H*.4,30);burst(W*.8,H*.4,30);burst(W*.15,H*.7,25);burst(W*.85,H*.7,25);
              var bT=0,sT=0,elapsed=0,DUR=3400,last=performance.now();
            
              function frame(now){{
                var dt=now-last;last=now;elapsed+=dt;
                ctx.clearRect(0,0,W,H);
                bT+=dt; if(bT>280&&elapsed<DUR*.75){{bT=0;burst(rnd(W*.05,W*.95),rnd(H*.05,H*.6),rnd(18,38));}}
                sT+=dt; if(sT>70&&elapsed<DUR*.8){{sT=0;sparkle(rnd(30,W-30),rnd(30,H-30));}}
                for(var i=P.length-1;i>=0;i--){{
                  var p=P[i];
                  p.vy+=p.grav;p.x+=p.vx;p.y+=p.vy;p.vx*=.98;p.alpha-=p.decay;
                  var a=Math.max(0,p.alpha);
                  if(p.type==='star')dStar(p.x,p.y,p.size,p.color,a);
                  else if(p.type==='plus')dPlus(p.x,p.y,p.size,p.color,a);
                  else{{ctx.save();ctx.globalAlpha=a;ctx.fillStyle=p.color;ctx.shadowColor=p.color;ctx.shadowBlur=6;
                    ctx.beginPath();ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill();ctx.restore();}}
                  if(p.alpha<=0)P.splice(i,1);
                }}
                if(elapsed<DUR+500)requestAnimationFrame(frame);
                else{{canvas.remove();wordEl.remove();}}
              }}
              requestAnimationFrame(frame);
            }})();
            </script>"""

        # We execute this component unconditionally. If there's no reaction, it injects an empty string.
        # This keeps the YouTube iframe locked in its exact React index!
        _components.html(fireworks_injection, height=0, scrolling=False)
        # ------------------------------------------------------------------, height=0, scrolling=False)

        if st.session_state[yt_url_key]:
            _iframe_url = html.escape(st.session_state[yt_url_key], quote=True)
            
            components.html(
                f"""
                <iframe
                    src="{_iframe_url}"
                    width="100%"
                    height="800"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write;
                           encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen>
                </iframe>
                """,
                height=800,
            )

    with actions_col:
        # ----------- Visual Queue Display -----------
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**🎭 Up Next**")

        queue = vc_data.get("queue", [])
        calypso = vc_data.get("calypso", [])
        pinged = vc_data.get("pinged", set())
        role_assignments_vq = vc_data.get("role_assignments", {})
        person_to_roles_vq = {}
        for role_vq, people_vq in role_assignments_vq.items():
            pool_vq = people_vq if isinstance(people_vq, list) else ([people_vq] if people_vq else [])
            for p_vq in pool_vq:
                if p_vq and p_vq != "— Unassigned —":
                    person_to_roles_vq.setdefault(p_vq, []).append(role_vq)

        def _vq_pb(person):
            return ' <span style="font-size:0.65rem;background:#39ff14;color:white;border-radius:4px;padding:1px 4px;">📣</span>' if person in pinged else ""

        def _vq_rt(person):
            roles = person_to_roles_vq.get(person, [])
            # Escape role strings to keep them secure
            escaped_roles = [html.escape(r) for r in roles]
            return f'<div style="font-size:0.9rem;color:#00ff88;margin:0;line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{", ".join(escaped_roles)}</div>' if roles else ""

        if queue:
            cards_html = '<div style="display:flex;flex-direction:column;gap:5px;margin-top:4px;">'

            # #1 SINGING NOW — full width, gold (CENTERED)
            p = queue[0]
            escaped_p = html.escape(p)
            cards_html += f'''
            <div style="background:linear-gradient(135deg,#2a1a00,#5c3a00);border:1.5px solid #ffaa00;border-radius:8px;padding:7px 9px;text-align:center;">
              <div style="font-size:1.58rem;color:#ffaa00;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;line-height:1.1;">👑 SINGING NOW</div>
              <div style="font-size:1.88rem;font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2;margin:2px 0;">{escaped_p}{_vq_pb(p)}</div>
              <div style="display:flex;justify-content:center;width:100%;line-height:1.1;">{_vq_rt(p)}</div>
            </div>'''

            # #2 NEXT UP — full width, blue (CENTERED)
            if len(queue) >= 2:
                p = queue[1]
                escaped_p = html.escape(p)
                cards_html += f'''
                <div style="background:linear-gradient(135deg,#0d1f2d,#1a3a50);border:1.5px solid #4fc3f7;border-radius:8px;padding:7px 9px;text-align:center;">
                  <div style="font-size:1.38rem;color:#4fc3f7;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;line-height:1.1;">🌟 NEXT UP</div>
                  <div style="font-size:1.68rem;font-weight:600;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2;margin:2px 0;">{escaped_p}{_vq_pb(p)}</div>
                  <div style="display:flex;justify-content:center;width:100%;line-height:1.1;">{_vq_rt(p)}</div>
                </div>'''

            # #3+ — 2-column grid, number inline with name, same font size, not bold
            rest = queue[2:]
            if rest:
                cards_html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">'
                for j, p in enumerate(rest):
                    num = j + 3
                    escaped_p = html.escape(p)
                    cards_html += f'''
                    <div style="background:linear-gradient(135deg,#111118,#1a1a2e);border:1.5px solid #444466;border-radius:7px;padding:6px 8px;min-width:0;">
                      <div style="font-size:1.00rem;font-weight:400;color:#ddd;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2;"><span style="color:#888899;margin-right:4px;">#{num}</span>{escaped_p}{_vq_pb(p)}</div>
                      {_vq_rt(p)}
                    </div>'''
                cards_html += '</div>'

            cards_html += '</div>'

            # Calypso — 2-column grid, inline name
            if calypso:
                cards_html += '<div style="margin-top:8px;font-size:1.05rem;color:#888;text-transform:uppercase;letter-spacing:0.08em;">🌴 Away with Calypso</div>'
                cards_html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-top:3px;">'
                for person in calypso:
                    escaped_person = html.escape(person)
                    cards_html += f'''
                    <div style="background:linear-gradient(135deg,#0d1a0d,#1a2d1a);border:1.5px solid #2d5a2d;border-radius:7px;padding:6px 8px;min-width:0;">
                      <div style="font-size:1.00rem;font-weight:400;color:#aaffaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">🌴 {escaped_person}{_vq_pb(person)}</div>
                    </div>'''
                cards_html += '</div>'

            st.html(cards_html)
        else:
            st.markdown('<div style="color:#666;font-size:0.85rem;text-align:center;padding:16px 0;">Queue is empty</div>', unsafe_allow_html=True)
            
        # Add people inside actions column
        st.markdown("---")
        st.markdown("**Add to Queue**")
        def join_on_enter_side():
            name = st.session_state.get(f"{vc_id}_name_input_side", "").strip()
            name = name[:20]  # Hard enforcement of 20 chars maximum
            if name and name not in vc_data["queue"] and name not in vc_data["calypso"]:
                vc_data["queue"].append(name)
                st.session_state[f"{vc_id}_name_input_side"] = ""
                save_state(vc_id, vc_data)
                if vc_id == "vc1":
                    st.session_state.vc1_data = vc_data
                else:
                    st.session_state.vc2_data = vc_data
                #st.rerun()

        input_col, button_col = st.columns([3, 1])

        with input_col:
            st.text_input(
                "",
                max_chars=20,  # Enforce limit on browser side too
                key=f"{vc_id}_name_input_side",
                on_change=join_on_enter_side,
                label_visibility="collapsed",
                placeholder="Add people (Max 20 chars)"
            )
            
        with button_col:
            st.button("🎤 Join", on_click=join_on_enter_side, use_container_width=True, key=f"{vc_id}_join_btn_side")

        # ----------- Main Actions Section -----------
        st.markdown("**Main Actions**", unsafe_allow_html=True)
        
        if st.button("⏩ Advance", use_container_width=True, key=f"{vc_id}_advance"):
            if st.session_state[current_user_key] == vc_data["current_manager"]:
                if vc_data["queue"]:
                    first = vc_data["queue"].pop(0)
                    vc_data["queue"].append(first)
                    vc_data["selected_song"] = ""
                    vc_data["role_assignments"] = {}
                    st.session_state[yt_url_key] = ""
                    st.session_state[yt_title_key] = ""
                    history_key_adv = f"{vc_id}_role_history"
                    st.session_state[history_key_adv] = []
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.rerun()
            else:
                st.warning("Not managing.")
                
        if st.button("🧹 Clear All", use_container_width=True, key=f"{vc_id}_clear"):
            if st.session_state[current_user_key] == vc_data["current_manager"]:
                vc_data["queue"].clear()
                vc_data["calypso"].clear()
                vc_data["pinged"].clear()
                save_state(vc_id, vc_data)
                if vc_id == "vc1":
                    st.session_state.vc1_data = vc_data
                else:
                    st.session_state.vc2_data = vc_data
                st.rerun()
            else:
                st.warning("Not managing.")
                
        if st.button("🔄 Refresh", use_container_width=True, key=f"{vc_id}_refresh"):
            st.rerun()

    # ----------- Quick Actions + Template -----------
    qa_header_cols = st.columns([3, 1])
    with qa_header_cols[0]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("#### Quick Actions")
    with qa_header_cols[1]:
        st.markdown("<br>Select Template", unsafe_allow_html=True)
        available_templates_qa = get_available_templates()
        selected_template_qa = st.selectbox(
            "Template",
            available_templates_qa,
            index=available_templates_qa.index(vc_data["current_template"]) if vc_data["current_template"] in available_templates_qa else 0,
            key=f"{vc_id}_template_select",
            label_visibility="collapsed"
        )
        if selected_template_qa != vc_data["current_template"]:
            vc_data["current_template"] = selected_template_qa
            save_state(vc_id, vc_data)
            if vc_id == "vc1":
                st.session_state.vc1_data = vc_data
            else:
                st.session_state.vc2_data = vc_data
            st.rerun()
    qa = st.columns(4)

    def render_names(names, action_key):
        cols = st.columns(2, gap="small")
        for i, person in enumerate(names):
            col = cols[i % 2]
            with col:
                st.markdown('<div class="name-btn">', unsafe_allow_html=True)
                # Display escaped name on structural buttons safely
                if st.button(person, key=f"{action_key}_{i}", use_container_width=True):
                    return person
                st.markdown('</div>', unsafe_allow_html=True)
        return None

    if st.session_state[current_user_key] == vc_data["current_manager"]:
        with qa[0]:
            if st.button("➖ Leave", use_container_width=True, key=f"{vc_id}_leave"):
                st.session_state.show_leave = not st.session_state.show_leave
                for flag in ["show_hold", "show_return", "show_ping"]:
                    st.session_state[flag] = False
            if st.session_state.show_leave:
                person = render_names(vc_data["queue"], f"{vc_id}_Leave")
                if person:
                    vc_data["queue"].remove(person)
                    vc_data["pinged"].discard(person)
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.rerun()
        with qa[1]:
            if st.button("⏳ Hold", use_container_width=True, key=f"{vc_id}_hold"):
                st.session_state.show_hold = not st.session_state.show_hold
                for flag in ["show_leave", "show_return", "show_ping"]:
                    st.session_state[flag] = False
            if st.session_state.show_hold:
                person = render_names(vc_data["queue"], f"{vc_id}_Hold")
                if person:
                    vc_data["queue"].remove(person)
                    vc_data["calypso"].append(person)
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.rerun()
        with qa[2]:
            if st.button("🏝️ Return", use_container_width=True, key=f"{vc_id}_return"):
                st.session_state.show_return = not st.session_state.show_return
                for flag in ["show_leave", "show_hold", "show_ping"]:
                    st.session_state[flag] = False
            if st.session_state.show_return:
                person = render_names(vc_data["calypso"], f"{vc_id}_Return")
                if person:
                    vc_data["calypso"].remove(person)
                    vc_data["queue"].append(person)
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.rerun()
        with qa[3]:
            if st.button("📣 Ping/Unping", use_container_width=True, key=f"{vc_id}_ping"):
                st.session_state.show_ping = not st.session_state.show_ping
                for flag in ["show_leave", "show_hold", "show_return"]:
                    st.session_state[flag] = False
            if st.session_state.show_ping:
                names = vc_data["queue"] + vc_data["calypso"]
                person = render_names(names, f"{vc_id}_Ping")
                if person:
                    if person in vc_data["pinged"]:
                        vc_data["pinged"].remove(person)
                    else:
                        vc_data["pinged"].add(person)
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.rerun()
    else:
        st.info("⚠️ You are not managing the queue. Press 'Manage Queue' to interact with it.")

    # ----------- Layout: Reorder + Output -----------
    if vc_data["queue"]:

        queue_panel_col, empty_spacer_col, roles_panel_col = st.columns([1.5, 1.0, 1.8], gap="xxsmall")
        
        with empty_spacer_col:
            st.markdown("---")

        # =========================================================
        # 👈 LEFT MAIN COLUMN: QUEUE MANAGER
        # =========================================================
        with queue_panel_col:
            st.markdown("---")
            st.markdown("### Queue Manager")

            role_assignments = vc_data.get("role_assignments", {})
            person_to_roles = {}
            for role, people in role_assignments.items():
                loop_pool = people if isinstance(people, list) else ([people] if people else [])
                for person in loop_pool:
                    if person and person != "— Unassigned —":
                        person_to_roles.setdefault(person, []).append(role)

            def fmt_name_plain(name):
                ping = " 📣" if name in vc_data["pinged"] else ""
                roles_for = person_to_roles.get(name, [])
                role_tag = " [" + ", ".join(roles_for) + "]" if roles_for else ""
                return f"{name}{ping}{role_tag}"

            left, right = st.columns([1, 2])
            with left:
                st.markdown("#### 🔀 Reorder")
                if st.session_state[current_user_key] == vc_data["current_manager"]:
                    display_items = [f"{p} 📣" if p in vc_data["pinged"] else p for p in vc_data["queue"]]

                    sortable_key = f"sortable_{vc_id}_{len(vc_data['queue'])}_{hash(tuple(vc_data['queue']))}_{st.session_state.rev}"

                    reordered_display = sortables.sort_items(
                        display_items,
                        direction="vertical",
                        key=sortable_key
                    )
                    display_to_name = {
                        (f"{p} 📣" if p in vc_data["pinged"] else p): p for p in vc_data["queue"]
                    }
                    
                    reordered_names = [display_to_name.get(d, d) for d in reordered_display]
                    if reordered_names != vc_data["queue"]:
                        vc_data["queue"] = reordered_names
                        save_state(vc_id, vc_data)
                        if vc_id == "vc1":
                            st.session_state.vc1_data = vc_data
                        else:
                            st.session_state.vc2_data = vc_data
                        st.rerun()
                else:
                    st.info("🔹 Only the manager can reorder.")

            with right:
                current_template = load_template(vc_data["current_template"])

                # Sanitize template variables before formatting codeblock presentation block
                t_title = html.escape(current_template.get('title', ''))
                t_url = current_template.get('url', '')
                t_tmpl = html.escape(vc_data['current_template'])
                t_mngr = html.escape(vc_data['current_manager'] if vc_data['current_manager'] else '-')
                t_song = html.escape(active_song)

                output = f"{t_title}\n"
                output += f"{t_url}\n"
                output += f"Template by: {t_tmpl}\n"
                output += f"Managed by: {t_mngr}\n"
                if active_song:
                    output += f"🎵 {t_song}\n"
                output += "-# ------------------\n"
                output += f"{current_template['currently_singing']}\n{current_template['current_symbol']} {fmt_name_plain(vc_data['queue'][0]) if len(vc_data['queue'])>=1 else '-'}\n"
                output += "-# ------------------\n"
                output += f"{current_template['next_up']}\n{current_template['next_symbol']} {fmt_name_plain(vc_data['queue'][1]) if len(vc_data['queue'])>=2 else '-'}\n"
                output += "-# ------------------\n" + current_template['on_queue'] + "\n"
                if len(vc_data["queue"]) > 2:
                    for person in vc_data["queue"][2:]:
                        output += f"{current_template['queue_symbol']} {fmt_name_plain(person)}\n"
                else:
                    output += "- None\n"
                output += "-# ------------------\n" + current_template['away_calypso'] + "\n"
                if vc_data["calypso"]:
                    for person in vc_data["calypso"]:
                        output += f"{current_template['calypso_symbol']} {fmt_name_plain(person)}\n"
                else:
                    output += "- None\n"
                output += "-# ------------------\nReact to join the legend:\n" + current_template['reactions'] + "\n"
                output += "-# ------------------\n"
                output += f"{current_template['wheel_link']}\n"
                st.code(output, language="text")

        # =========================================================
        # 👉 RIGHT MAIN COLUMN: ROLE ASSIGNMENT
        # =========================================================
        with roles_panel_col:
            st.markdown("---")
            st.markdown("### 🎭 Role Assignment")

            history_key = f"{vc_id}_role_history"
            is_manager = st.session_state[current_user_key] == vc_data["current_manager"]
            song_list = list(EPIC_SONGS.keys())

            current_song = vc_data.get("selected_song", "")

            if active_song and active_song in EPIC_SONGS:
                roles = EPIC_SONGS[active_song]
                
                raw_assignments = vc_data.get("role_assignments", {})
                assignments = {}
                for k, v in raw_assignments.items():
                    if isinstance(v, list):
                        assignments[k] = v
                    else:
                        assignments[k] = [v] if v and v != "— Unassigned —" else []

                all_people = vc_data["queue"]
                st.markdown(f"**Assigning roles for:** *{html.escape(active_song)}*")

                def role_icon(role):
                    r = role.lower()
                    if any(x in r for x in ["zeus", "poseidon", "athena", "hermes", "hera", "aphrodite", "ares", "apollo", "hephaestus"]):
                        return "⚡"
                    if any(x in r for x in ["odysseus", "telemachus", "penelope", "antinous"]):
                        return "⚔️"
                    if any(x in r for x in ["circe", "calypso", "siren", "scylla", "charybdis"]):
                        return "🌊"
                    if any(x in r for x in ["crew", "ensemble", "suitors", "soldiers", "souls", "spirits"]):
                        return "👥"
                    if any(x in r for x in ["polyphemus", "cyclops", "monster", "beast"]):
                        return "👁️"
                    return "🎶"

                changed = False
                war_triggered = False
                new_assignments = dict(assignments)

                for role in roles:
                    current_assigned = assignments.get(role, [])
                    default_assigned = [person for person in current_assigned if person in all_people]
                    
                    if len(default_assigned) != len(current_assigned):
                        changed = True
                        new_assignments[role] = default_assigned

                    war_btn_key = f"{vc_id}_war_{role}_{active_song}"
                    row_col1, row_col2, row_col3 = st.columns([2, 3, 1])
                    
                    with row_col1:
                        st.write("")
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(f"##### {role_icon(role)} {html.escape(role)}")
                    
                    with row_col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        picked_list = st.multiselect(
                            f"Assign {role}",
                            options=all_people,
                            default=default_assigned,
                            key=f"{vc_id}_role_multi_{role}_{active_song}_{st.session_state.rev}",
                            disabled=not is_manager,
                            label_visibility="collapsed"
                        )
                        if not war_triggered and set(picked_list) != set(default_assigned):
                            changed = True
                            new_assignments[role] = picked_list

                    with row_col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        war_disabled = (len(picked_list) < 2 or not is_manager)
                        war_clicked = st.button("💥 War!", key=war_btn_key, disabled=war_disabled, use_container_width=True)

                    if war_clicked:
                        war_triggered = True
                        
                        anime_gifs = [
                            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXF0OTd1b2N2bTViZnJqbngwY3F5MmN0M3A1ZWx2czllM3ZzOGlraiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/iqkCNZIzSSXSM/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXF0OTd1b2N2bTViZnJqbngwY3F5MmN0M3A1ZWx2czllM3ZzOGlraiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/6ULDGyRw0uhECEhAaQ/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWwwbm4weXVhbmJqaWxhYW9keGp3MWJ6MTduNDFueG91bDg3aXZtbyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/qLErpwsfLyY6RSTJlJ/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWwwbm4weXVhbmJqaWxhYW9keGp3MWJ6MTduNDFueG91bDg3aXZtbyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/iRDkNp3c0FXem0lCCF/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnV0Y3QycHUwOHE3aHBydDBmZXNibDZramp2dTM3ZzVoMHJ4MGFtYyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/cLjmtVDE8RXOPnviKv/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3YTNlbjk5NnFrZzltNzNpcHBjazUwa3h4dHV4a2Z4NjZwdnI0bXltYiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/VDZDQWaCR2YhQ0qeUo/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3azUyaTV4M3Q0bG9mdjN3bmxrd3hmeXRleGYzaHducmwxdDY3cXh0MiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QN7yjB1My4sNhzNTg4/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3YXU0ZnR4dngxOWxxOWxhZDRmcHMyNGI3czM5ODV5eHNoMnV0MGpubyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/mmp8mYjezjgfi1SXW9/giphy.gif",
                            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWp6ajJoc2MxNTAxdDc5aXcycXExenp3N3g3enVtOWljbmtpMjdlYSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ecotXu1Vhklym7D8rG/giphy.gif",
                            "https://media1.tenor.com/m/oe62qCQfpS4AAAAd/tsue-to-tsurugi-no-wistoria-wistoria-wand-and-sword.gif",
                            "https://media1.tenor.com/m/pTehBNi86LMAAAAC/my-hero-academia-boku-no-hero-academia.gif",
                            "https://media1.tenor.com/m/CEUEYMWI8eEAAAAC/%E5%8B%87%E8%80%85%E4%B9%8B%E6%B8%A3-scum-of-the-brave.gif",
                            "https://media1.tenor.com/m/fdillqOJN1MAAAAC/%E5%8B%87%E8%80%85%E4%B9%8B%E6%B8%A3-scum-of-the-brave.gif"
                        ]
                        
                        if "gif_pool" not in st.session_state or not st.session_state.gif_pool:
                            st.session_state.gif_pool = list(anime_gifs)
                            random.shuffle(st.session_state.gif_pool)
                        
                        chosen_anime = st.session_state.gif_pool.pop()
                        battle_placeholder = st.empty()
                        
                        for timer in range(5, 0, -1):
                            battle_placeholder.markdown(
                                f"""
                                <div style="text-align: center; padding: 8px; background-color: #0c0c0c; border: 2px dashed #ff4b4b; border-radius: 8px; margin: 5px 0;">
                                    <h4 style="color: #ff4b4b; margin: 0; font-family: sans-serif; font-size: 1.1rem; text-shadow: 0 0 5px #ff0000;">🔥 ROLE WAR FOR {html.escape(role.upper())}! 🔥</h4>
                                    <p style="font-size: 0.95rem; font-weight: bold; color: white; margin: 4px 0;">Clashing finishes in {timer}...</p>
                                    <img src="{chosen_anime}" style="width: 100%; max-width: 470px; border-radius: 6px; border: 1.5px solid #fff;"/>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            time.sleep(1.0)
                        
                        winner = random.choice(picked_list)
                        battle_placeholder.empty()
                        
                        st.session_state[history_key].append({
                            "selected_song": active_song,
                            "role_assignments": dict(vc_data.get("role_assignments", {}))
                        })
                        
                        new_assignments[role] = [winner]
                        vc_data["role_assignments"] = new_assignments
                        st.session_state.rev += 1
                        save_state(vc_id, vc_data)
                        
                        if vc_id == "vc1":
                            st.session_state.vc1_data = vc_data
                        else:
                            st.session_state.vc2_data = vc_data
                            
                        st.toast(f"🏆 {html.escape(winner)} won the fight for {html.escape(role)}!")
                        st.balloons()
                        st.rerun()

                if is_manager and changed and not war_triggered:
                    st.session_state[history_key].append({
                        "selected_song": active_song,
                        "role_assignments": dict(assignments)
                    })
                    vc_data["role_assignments"] = new_assignments
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.rerun()

                if is_manager:
                    clear_col, _ = st.columns([1, 3])
                    with clear_col:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Clear Roles", use_container_width=True, key=f"{vc_id}_role_clear"):
                            st.session_state[history_key].append({
                                "selected_song": active_song,
                                "role_assignments": dict(vc_data.get("role_assignments", {}))
                            })
                            
                            vc_data["role_assignments"] = {}
                            st.session_state.rev += 1
                            
                            save_state(vc_id, vc_data)
                            if vc_id == "vc1":
                                st.session_state.vc1_data = vc_data
                            else:
                                st.session_state.vc2_data = vc_data
                            st.rerun()
            elif active_song:
                st.info("Song not found in database.")
            else:
                if is_manager:
                    st.info("Search, select, or spin a song above to assign roles.")
                else:
                    st.info("The manager hasn't selected a song yet.")
                
# Render selected section
if selected_tab == "🎵 VC 1":
    render_vc_content("vc1")

elif selected_tab == "🎵 VC 2":
    render_vc_content("vc2")

elif selected_tab == "✨ Customize":
    # ----------- CUSTOMIZE TAB CONTENT -----------
    st.header("✨ Customize Queue Template")
    
    st.markdown("**Select or create a template to customize the queue appearance.**")
    
    available_templates = get_available_templates()
    selected_template = st.selectbox(
        "Select Template",
        available_templates,
        index=0
    )
    
    template = load_template(selected_template)
    
    st.markdown("---")
    st.subheader("Edit Template Fields")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Title", value=template.get("title", ""), key="tmpl_title", max_chars=100)
        st.text_input("URL", value=template.get("url", ""), key="tmpl_url", max_chars=100)
        st.text_input("Currently Singing Text", value=template.get("currently_singing", ""), key="tmpl_currently_singing", max_chars=100)
        st.text_input("Currently Singing Symbol", value=template.get("current_symbol", ""), key="tmpl_current_symbol", max_chars=50)
        st.text_input("Next Up Text", value=template.get("next_up", ""), key="tmpl_next_up", max_chars=100)
        st.text_input("Next Up Symbol", value=template.get("next_symbol", ""), key="tmpl_next_symbol", max_chars=50)
    
    with col2:
        st.text_input("On Queue Text", value=template.get("on_queue", ""), key="tmpl_on_queue", max_chars=100)
        st.text_input("Queue Symbol", value=template.get("queue_symbol", ""), key="tmpl_queue_symbol", max_chars=50)
        st.text_input("Away with Calypso Text", value=template.get("away_calypso", ""), key="tmpl_away_calypso", max_chars=100)
        st.text_input("Calypso Symbol", value=template.get("calypso_symbol", ""), key="tmpl_calypso_symbol", max_chars=50)
        st.text_area("Reactions Info", value=template.get("reactions", ""), key="tmpl_reactions", height=80, max_chars=500)
        st.text_input("Wheel Link", value=template.get("wheel_link", ""), key="tmpl_wheel_link", max_chars=100)
    
    st.markdown("---")
    
    # Preview
    st.subheader("📋 Preview")
    preview_template = {
        "title": st.session_state.tmpl_title,
        "url": st.session_state.tmpl_url,
        "currently_singing": st.session_state.tmpl_currently_singing,
        "current_symbol": st.session_state.tmpl_current_symbol,
        "next_up": st.session_state.tmpl_next_up,
        "next_symbol": st.session_state.tmpl_next_symbol,
        "on_queue": st.session_state.tmpl_on_queue,
        "queue_symbol": st.session_state.tmpl_queue_symbol,
        "away_calypso": st.session_state.tmpl_away_calypso,
        "calypso_symbol": st.session_state.tmpl_calypso_symbol,
        "reactions": st.session_state.tmpl_reactions,
        "wheel_link": st.session_state.tmpl_wheel_link
    }
    
    # Escape fields explicitly so they render harmlessly in the preview text area
    p_title = html.escape(preview_template['title'])
    p_url = preview_template['url']
    p_curr_sing = html.escape(preview_template['currently_singing'])
    p_curr_sym = html.escape(preview_template['current_symbol'])
    p_next_up = html.escape(preview_template['next_up'])
    p_next_sym = html.escape(preview_template['next_symbol'])
    p_on_q = html.escape(preview_template['on_queue'])
    p_q_sym = html.escape(preview_template['queue_symbol'])
    p_away = html.escape(preview_template['away_calypso'])
    p_cal_sym = html.escape(preview_template['calypso_symbol'])
    p_react = html.escape(preview_template['reactions'])
    p_wheel = html.escape(preview_template['wheel_link'])

    preview_output = f"{p_title}\n"
    preview_output += f"{p_url}\n"
    preview_output += f"Template by: {html.escape(selected_template)}\n"
    preview_output += "Managed by: [Manager Name]\n"
    preview_output += "-# ------------------\n"
    preview_output += f"{p_curr_sing}\n{p_curr_sym} [Person 1]\n"
    preview_output += "-# ------------------\n"
    preview_output += f"{p_next_up}\n{p_next_sym} [Person 2]\n"
    preview_output += "-# ------------------\n" + p_on_q + "\n"
    preview_output += f"{p_q_sym} [Person 3]\n"
    preview_output += "-# ------------------\n" + p_away + "\n"
    preview_output += f"{p_cal_sym} [Person 4]\n"
    preview_output += "-# ------------------\nReact to join the legend:\n" + p_react + "\n"
    preview_output += "-# ------------------\n"
    preview_output += f"{p_wheel}\n"
    
    st.code(preview_output, language="text")
    
    st.markdown("---")
    st.subheader("💾 Save Template")
        
    # Where you accept the new template name input
    new_template_name = st.text_input("Template Name")
    
    if st.button("💾 Save Template"):
        # Security & Path Sanitation check
        if ".." in new_template_name or "/" in new_template_name or "\\" in new_template_name:
            st.error("❌ Invalid template name. Do not use slashes or dots.")
        elif not new_template_name.strip():
            st.error("❌ Template name cannot be empty.")
        else:
            # Proceed with saving your template normally
            save_template(new_template_name.strip(), current_config)
    
    st.markdown("---")
    st.subheader("📚 Available Templates")
    
    cols = st.columns(min(len(available_templates), 3))
    for idx, tmpl_name in enumerate(available_templates):
        with cols[idx % 3]:
            st.button(f"📌 {html.escape(tmpl_name)}", use_container_width=True, key=f"load_tmpl_{tmpl_name}", disabled=True)
    
    st.markdown("---")
    st.subheader("🗑️ Delete Templates")
    
    st.warning("⚠️ **This section requires a passcode. Only admins can delete templates.**")
    
    delete_col1, delete_col2 = st.columns([2, 2])
    
    with delete_col1:
        passcode_input = st.text_input(
            "Enter Admin Passcode",
            type="password",
            placeholder="Enter passcode to delete templates",
            key="delete_passcode"
        )
    
    if passcode_input:
        if passcode_input == ADMIN_PASSCODE:
            st.session_state.admin_authenticated = True
        else:
            st.session_state.admin_authenticated = False
    
    if st.session_state.admin_authenticated and passcode_input == ADMIN_PASSCODE:
        st.success("✅ Admin passcode correct!")
        
        deletable_templates = [t for t in available_templates if t != "Default EPIC"]
        
        if deletable_templates:
            with delete_col2:
                template_to_delete = st.selectbox(
                    "Select template to delete",
                    deletable_templates,
                    key="template_to_delete"
                )
            
            delete_btn_col1, delete_btn_col2 = st.columns(2)
            
            with delete_btn_col1:
                if st.button("🗑️ Delete Selected Template", use_container_width=True, key="delete_tmpl_btn"):
                    if delete_template(template_to_delete):
                        st.success(f"✅ Template '{html.escape(template_to_delete)}' has been deleted!")
                        st.rerun()
                    else:
                        st.error(f"Could not delete template '{html.escape(template_to_delete)}'")
        else:
            st.info("ℹ️ No custom templates to delete. Only the Default EPIC template exists.")
    elif passcode_input and not st.session_state.admin_authenticated:
        st.error("❌ Incorrect passcode!")

# --- Custom Styling for small UI elements ---
st.markdown("""
    <style>
    .name-btn button {
        font-size: clamp(8px, 1.2vw, 12px) !important;
        padding: 6px 8px !important;
        margin: 2px !important;
        border-radius: 10px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    div[data-testid="stHorizontalBlock"] { gap: 6px !important; }
    div[data-testid="stVerticalBlock"] { gap: 4px !important; }

    /* Reaction pill buttons */
    button[data-testid^="baseButton"] {
        line-height: 1.3 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Auto-select-all text in Streamlit selectbox on click
import streamlit.components.v1 as _components_global
_components_global.html("""<script>
(function() {
  function attachSelectAll() {
    var inputs = window.parent.document.querySelectorAll('[data-baseweb="select"] input');
    inputs.forEach(function(inp) {
      if (!inp.__rxSelectAll) {
        inp.__rxSelectAll = true;
        inp.addEventListener('click', function() { this.select(); });
        inp.addEventListener('focus', function() { this.select(); });
      }
    });
  }
  // Run on load and watch for new elements
  attachSelectAll();
  var obs = new MutationObserver(attachSelectAll);
  obs.observe(window.parent.document.body, {childList: true, subtree: true});
})();
</script>""", height=0)
