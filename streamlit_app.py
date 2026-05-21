import streamlit as st
import streamlit_sortables as sortables
import json, os, io, base64
from PIL import Image, ImageDraw, ImageFont
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import requests
import time

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
}

SAVE_FILE = "queue.json"
TEMPLATES_DIR = "templates"
ADMIN_PASSCODE = "531246"
SYNC_CHECK_INTERVAL = 1  # Check for updates every 1 second

# Ensure templates directory exists
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

# Default template
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
    """Delete template file"""
    if template_name == "Default EPIC":
        return False
    
    template_file = os.path.join(TEMPLATES_DIR, f"{template_name}.json")
    if os.path.exists(template_file):
        os.remove(template_file)
        return True
    return False

def get_available_templates():
    """Get list of available templates"""
    templates = ["Default EPIC"]
    if os.path.exists(TEMPLATES_DIR):
        for file in os.listdir(TEMPLATES_DIR):
            if file.endswith(".json"):
                templates.append(file.replace(".json", ""))
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
if not is_manager_vc1 and not is_manager_vc2:
    st_autorefresh(interval=3000)

st.title("⚔️EPIC Singing VC Queue🎭")

# ========== MAIN NAVIGATION ==========
selected_tab = st.segmented_control(
    "Select Section",
    ["🎵 VC 1", "🎵 VC 2", "✨ Customize"],
    default=st.session_state.get("main_selected_tab", "🎵 VC 1"),
    key="main_selected_tab"
)

def render_vc_content(vc_id):
    """Render queue content for a specific VC"""
    
    # Load current VC data
    if vc_id == "vc1":
        vc_data = st.session_state.vc1_data
        current_user_key = "current_user_vc1"
    else:
        vc_data = st.session_state.vc2_data
        current_user_key = "current_user_vc2"
    
    # Check for updates from other users
    if check_for_updates(vc_id, vc_data["last_modified"]):
        updated_data = load_state(vc_id)
        if vc_id == "vc1":
            st.session_state.vc1_data = updated_data
            vc_data = updated_data
        else:
            st.session_state.vc2_data = updated_data
            vc_data = updated_data
        st.rerun()
    
    if vc_data["current_manager"]:
        st.info(f"💡 Currently managing: **{vc_data['current_manager']}**")
    else:
        st.info(f"💡 No one is managing {vc_id.upper()}. Press 'Manage Queue' to take control.")

    # ----------- Manager Name Input & Claim Button -----------
    claim_cols = st.columns([4, 1, 1])
    with claim_cols[0]:
        manager_name = st.text_input(
            "Type your name",
            key=f"{vc_id}_manager_input",
            label_visibility="collapsed",
            placeholder="Type your name"
        )

    def really_claim_manager(name):
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

    # Prompt for manager replacement
    if st.session_state.show_manager_confirm:
        st.warning(f"⚠️ You will REPLACE **{vc_data['current_manager']}** as manager. Are you sure?")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Yes, replace", key=f"{vc_id}_manager_yes_btn"):
                really_claim_manager(st.session_state.manager_candidate)
        with col_no:
            if st.button("No, cancel", key=f"{vc_id}_manager_no_btn"):
                st.session_state.show_manager_confirm = False
                st.session_state.manager_candidate = ""

    # ----------- Top button bar -----------
    st.markdown("#### Main Actions")
    cols = st.columns([1, 1, 1, 0.3, 1])
    with cols[0]:
        if st.button("⏩ Advance", use_container_width=True, key=f"{vc_id}_advance"):
            if st.session_state[current_user_key] == vc_data["current_manager"]:
                if vc_data["queue"]:
                    first = vc_data["queue"].pop(0)
                    vc_data["queue"].append(first)
                    # Clear role assignments and song on advance
                    vc_data["selected_song"] = ""
                    vc_data["role_assignments"] = {}
                    history_key = f"{vc_id}_role_history"
                    st.session_state[history_key] = []
                    save_state(vc_id, vc_data)
                    if vc_id == "vc1":
                        st.session_state.vc1_data = vc_data
                    else:
                        st.session_state.vc2_data = vc_data
                    st.rerun()
            else:
                st.warning("You are not managing the queue.")
    with cols[1]:
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
                st.warning("You are not managing the queue.")
    with cols[2]:
        if st.button("🔄 Refresh", use_container_width=True, key=f"{vc_id}_refresh"):
            st.rerun()

    # Template selector - after main actions
    st.markdown("#### Select Template")
    available_templates = get_available_templates()
    selected_template = st.selectbox(
        "Select Template",
        available_templates,
        index=available_templates.index(vc_data["current_template"]) if vc_data["current_template"] in available_templates else 0,
        key=f"{vc_id}_template_select"
    )
    
    if selected_template != vc_data["current_template"]:
        vc_data["current_template"] = selected_template
        save_state(vc_id, vc_data)
        if vc_id == "vc1":
            st.session_state.vc1_data = vc_data
        else:
            st.session_state.vc2_data = vc_data
        st.rerun()

    # ----------- Input to join -----------
    def join_on_enter():
        name = st.session_state.get(f"{vc_id}_name_input", "").strip()
        if name and name not in vc_data["queue"] and name not in vc_data["calypso"]:
            vc_data["queue"].append(name)
            st.session_state[f"{vc_id}_name_input"] = ""
            save_state(vc_id, vc_data)
            if vc_id == "vc1":
                st.session_state.vc1_data = vc_data
            else:
                st.session_state.vc2_data = vc_data
            st.rerun()

    join_cols = st.columns([4, 1])
    with join_cols[0]:
        st.text_input(
            "",
            key=f"{vc_id}_name_input",
            on_change=join_on_enter,
            label_visibility="collapsed",
            placeholder="Add People"
        )
    with join_cols[1]:
        st.button("🎤 Join", on_click=join_on_enter, use_container_width=True, key=f"{vc_id}_join_btn")

    # ----------- Quick Actions -----------
    st.markdown("#### Quick Actions")
    qa = st.columns(4)

    def render_names(names, action_key):
        cols = st.columns(2, gap="small")
        for i, person in enumerate(names):
            col = cols[i % 2]
            with col:
                st.markdown('<div class="name-btn">', unsafe_allow_html=True)
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

        # ========== QUEUE MANAGER ==========
        st.markdown("---")
        st.markdown("### Queue Manager")

        # Build reverse map: person → list of roles assigned to them
        role_assignments = vc_data.get("role_assignments", {})
        person_to_roles = {}
        for role, person in role_assignments.items():
            person_to_roles.setdefault(person, []).append(role)

        def fmt_name(name):
            """Format name with ping indicator and assigned roles."""
            base = f"{name} 📣" if name in vc_data["pinged"] else name
            roles_for = person_to_roles.get(name, [])
            if roles_for:
                base += " [" + ", ".join(roles_for) + "]"
            return base

        def fmt_name_plain(name):
            """Format name for output text (no ping icon, just roles)."""
            ping = " 📣" if name in vc_data["pinged"] else ""
            roles_for = person_to_roles.get(name, [])
            role_tag = " [" + ", ".join(roles_for) + "]" if roles_for else ""
            return f"{name}{ping}{role_tag}"

        # Reorder column shows names with their assigned roles inline
        left, right = st.columns([1, 2])
        with left:
            st.markdown("#### 🔀 Reorder")
            if st.session_state[current_user_key] == vc_data["current_manager"]:
                # --- CHANGE THIS LINE TO REMOVE ROLES FROM REORDER LIST ---
                display_items = [f"{p} 📣" if p in vc_data["pinged"] else p for p in vc_data["queue"]]

                # Force sortable to refresh whenever queue length/content changes
                sortable_key = f"sortable_{vc_id}_{len(vc_data['queue'])}_{hash(tuple(vc_data['queue']))}_{st.session_state.rev}"

                reordered_display = sortables.sort_items(
                    display_items,
                    direction="vertical",
                    key=sortable_key
                )
                # --- CHANGE THIS LINE TO MAP THE CLEAN DISPLAY BACK TO REAL NAMES ---
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

            output = f"{current_template['title']}\n"
            output += f"{current_template['url']}\n"
            output += f"Template by: {vc_data['current_template']}\n"
            output += f"Managed by: {vc_data['current_manager'] if vc_data['current_manager'] else '-'}\n"
            if active_song:
                output += f"🎵 {active_song}\n"
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

        # ========== SONG & ROLE ASSIGNMENT ==========
        st.markdown("---")
        st.markdown("### 🎵 Song & Role Assignment")

        history_key = f"{vc_id}_role_history"
        is_manager = st.session_state[current_user_key] == vc_data["current_manager"]

        # Searchable song selector
        song_list = list(EPIC_SONGS.keys())
        search_query = st.text_input(
            "🔍 Search song",
            key=f"{vc_id}_song_search",
            placeholder="Type to filter songs...",
            disabled=not is_manager
        )
        filtered_songs = [s for s in song_list if search_query.lower() in s.lower()] if search_query else song_list
        filtered_songs_with_none = ["— Select a song —"] + filtered_songs

        current_song = vc_data.get("selected_song", "")
        default_idx = (filtered_songs_with_none.index(current_song)
                       if current_song in filtered_songs_with_none else 0)

        chosen_song = st.selectbox(
            "Song",
            filtered_songs_with_none,
            index=default_idx,
            key=f"{vc_id}_song_select",
            disabled=not is_manager,
            label_visibility="collapsed"
        )

        if is_manager and chosen_song != "— Select a song —" and chosen_song != current_song:
            st.session_state[history_key].append({
                "selected_song": vc_data.get("selected_song", ""),
                "role_assignments": dict(vc_data.get("role_assignments", {}))
            })
            vc_data["selected_song"] = chosen_song
            vc_data["role_assignments"] = {}
            save_state(vc_id, vc_data)
            if vc_id == "vc1":
                st.session_state.vc1_data = vc_data
            else:
                st.session_state.vc2_data = vc_data
            st.rerun()

        active_song = vc_data.get("selected_song", "")

        if active_song and active_song in EPIC_SONGS:
            roles = EPIC_SONGS[active_song]
            assignments = dict(vc_data.get("role_assignments", {}))
            all_people = vc_data["queue"] + vc_data["calypso"]

            st.markdown(f"**Assigning roles for:** *{active_song}*")

            # Role assignment — each role has a selectbox, icon varies by role type
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
            new_assignments = dict(assignments)
            role_cols = st.columns(min(len(roles), 3))
            for i, role in enumerate(roles):
                col = role_cols[i % min(len(roles), 3)]
                with col:
                    assigned_person = assignments.get(role, "— Unassigned —")
                    options = ["— Unassigned —"] + all_people
                    cur_idx = options.index(assigned_person) if assigned_person in options else 0
                    picked = st.selectbox(
                        f"{role_icon(role)} {role}",
                        options,
                        index=cur_idx,
                        # --- CHANGE: Append the rev counter to the key ---
                        key=f"{vc_id}_role_{role}_{active_song}_{st.session_state.rev}",
                        disabled=not is_manager
                    )
                    if picked != assigned_person:
                        changed = True
                    if picked != "— Unassigned —":
                        new_assignments[role] = picked
                    elif role in new_assignments:
                        del new_assignments[role]

            if is_manager and changed:
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

            # Undo + Clear buttons
            if is_manager:
                clear_col, _ = st.columns([1, 3])
                with clear_col:
                    if st.button("🗑️ Clear Roles", use_container_width=True,
                                 key=f"{vc_id}_role_clear"):
                        # Save current state to history before wiping
                        st.session_state[history_key].append({
                            "selected_song": active_song,
                            "role_assignments": dict(vc_data.get("role_assignments", {}))
                        })
                        
                        # 1. Clean out the backend dictionary completely
                        vc_data["role_assignments"] = {}
                        
                        # 2. Update a revision flag to force Streamlit to rebuild the dropdowns
                        # We'll use the existing st.session_state.rev counter
                        st.session_state.rev += 1
                        
                        # Save and force a clean rerun
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
                st.info("Search and select a song above to assign roles.")
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
    
    # Template selector
    available_templates = get_available_templates()
    selected_template = st.selectbox(
        "Select Template",
        available_templates,
        index=0
    )
    
    # Load current template for editing
    template = load_template(selected_template)
    
    st.markdown("---")
    st.subheader("Edit Template Fields")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Title", value=template.get("title", ""), key="tmpl_title")
        st.text_input("URL", value=template.get("url", ""), key="tmpl_url")
        st.text_input("Currently Singing Text", value=template.get("currently_singing", ""), key="tmpl_currently_singing")
        st.text_input("Currently Singing Symbol", value=template.get("current_symbol", ""), key="tmpl_current_symbol")
        st.text_input("Next Up Text", value=template.get("next_up", ""), key="tmpl_next_up")
        st.text_input("Next Up Symbol", value=template.get("next_symbol", ""), key="tmpl_next_symbol")
    
    with col2:
        st.text_input("On Queue Text", value=template.get("on_queue", ""), key="tmpl_on_queue")
        st.text_input("Queue Symbol", value=template.get("queue_symbol", ""), key="tmpl_queue_symbol")
        st.text_input("Away with Calypso Text", value=template.get("away_calypso", ""), key="tmpl_away_calypso")
        st.text_input("Calypso Symbol", value=template.get("calypso_symbol", ""), key="tmpl_calypso_symbol")
        st.text_area("Reactions Info", value=template.get("reactions", ""), key="tmpl_reactions", height=80)
        st.text_input("Wheel Link", value=template.get("wheel_link", ""), key="tmpl_wheel_link")
    
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
    
    preview_output = f"{preview_template['title']}\n"
    preview_output += f"{preview_template['url']}\n"
    preview_output += f"Template by: {selected_template}\n"
    preview_output += "Managed by: [Manager Name]\n"
    preview_output += "-# ------------------\n"
    preview_output += f"{preview_template['currently_singing']}\n{preview_template['current_symbol']} [Person 1]\n"
    preview_output += "-# ------------------\n"
    preview_output += f"{preview_template['next_up']}\n{preview_template['next_symbol']} [Person 2]\n"
    preview_output += "-# ------------------\n" + preview_template['on_queue'] + "\n"
    preview_output += f"{preview_template['queue_symbol']} [Person 3]\n"
    preview_output += "-# ------------------\n" + preview_template['away_calypso'] + "\n"
    preview_output += f"{preview_template['calypso_symbol']} [Person 4]\n"
    preview_output += "-# ------------------\nReact to join the legend:\n" + preview_template['reactions'] + "\n"
    preview_output += "-# ------------------\n"
    preview_output += f"{preview_template['wheel_link']}\n"
    
    st.code(preview_output, language="text")
    
    st.markdown("---")
    st.subheader("💾 Save Template")
    
    save_col1, save_col2 = st.columns([3, 1])
    
    with save_col1:
        new_template_name = st.text_input(
            "Template Name (must be unique)",
            placeholder="e.g., My Custom Queue",
            key="new_template_name"
        )
    
    with save_col2:
        if st.button("💾 Save Template", use_container_width=True):
            if new_template_name:
                if new_template_name == "Default EPIC":
                    st.error("Cannot overwrite the Default EPIC template.")
                else:
                    save_template(new_template_name, preview_template)
                    st.success(f"✅ Template '{new_template_name}' saved successfully!")
                    st.rerun()
            else:
                st.error("Please enter a template name.")
    
    st.markdown("---")
    st.subheader("📚 Available Templates")
    
    cols = st.columns(min(len(available_templates), 3))
    for idx, tmpl_name in enumerate(available_templates):
        with cols[idx % 3]:
            st.button(f"📌 {tmpl_name}", use_container_width=True, key=f"load_tmpl_{tmpl_name}", disabled=True)
    
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
                        st.success(f"✅ Template '{template_to_delete}' has been deleted!")
                        st.rerun()
                    else:
                        st.error(f"Could not delete template '{template_to_delete}'")
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
    </style>
""", unsafe_allow_html=True)
