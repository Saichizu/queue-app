import streamlit as st
import streamlit_sortables as sortables
import json, os, io, base64
from PIL import Image, ImageDraw, ImageFont
from streamlit_autorefresh import st_autorefresh

SAVE_FILE = "queue.json"

# --- Load & Save State ---
def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state.queue = data.get("queue", [])
        st.session_state.calypso = data.get("calypso", [])
        st.session_state.pinged = set(data.get("pinged", []))
        st.session_state.current_manager = data.get("current_manager", "")
    else:
        st.session_state.queue = []
        st.session_state.calypso = []
        st.session_state.pinged = set()
        st.session_state.current_manager = ""

def save_state():
    data = {
        "queue": st.session_state.queue,
        "calypso": st.session_state.calypso,
        "pinged": list(st.session_state.pinged),
        "current_manager": st.session_state.current_manager
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# --- Always load state ---
load_state()

# --- Initialize session state flags ---
if "initialized" not in st.session_state:
    st.session_state.rev = 0
    st.session_state.initialized = True
    st.session_state.current_user = ""
    st.session_state.needs_rerun = False
    st.session_state.last_claimed_input = ""
    st.session_state.show_manager_confirm = False
    st.session_state.manager_candidate = ""
    for flag in ["show_leave", "show_hold", "show_return", "show_ping"]:
        st.session_state[flag] = False

# auto refresh for non-manager viewers
if st.session_state.current_user != st.session_state.current_manager:
    st_autorefresh(interval=3000)

def bump_and_rerun():
    save_state()
    st.session_state.rev += 1
    st.session_state.needs_rerun = True
    st.rerun()

# --- Helper actions for users ---
def leave_queue(name):
    changed = False
    if name in st.session_state.queue:
        st.session_state.queue.remove(name)
        changed = True
    if name in st.session_state.calypso:
        st.session_state.calypso.remove(name)
        changed = True
    if name in st.session_state.pinged:
        st.session_state.pinged.discard(name)
    if changed:
        save_state()
        st.success(f"Removed {name} from queue.")
        bump_and_rerun()

def place_on_hold(name):
    if name in st.session_state.queue:
        st.session_state.queue.remove(name)
        st.session_state.calypso.append(name)
        save_state()
        st.success(f"{name} placed on hold.")
        bump_and_rerun()
    else:
        st.warning("You must be in the queue to place on hold.")

def return_from_hold(name):
    if name in st.session_state.calypso:
        st.session_state.calypso.remove(name)
        st.session_state.queue.append(name)
        save_state()
        st.success(f"{name} returned to the queue.")
        bump_and_rerun()
    else:
        st.warning("You are not on hold.")

def toggle_ping(name):
    if name in st.session_state.pinged:
        st.session_state.pinged.discard(name)
        save_state()
        st.info(f"Unpinged {name}.")
    else:
        st.session_state.pinged.add(name)
        save_state()
        st.info(f"Pinged {name}.")
    st.session_state.rev += 1
    st.rerun()

# --- UI Start ---
st.title("⚔️EPIC Singing VC 1 Queue🎭")
st.markdown(
    "_Use this only for **Epic Singing VC 1** because changes are saved. "
    "For Epic Singing VC 2, use [this link](https://epic-queue-2.streamlit.app/)._"
)

if st.session_state.current_manager:
    st.info(f"💡 Currently managing the queue: **{st.session_state.current_manager}**")
else:
    st.info("💡 No one is currently managing the queue. Press 'Manage Queue' to take control.")

# ----------- Manager Claim -----------
claim_cols = st.columns([4, 1, 1])
with claim_cols[0]:
    manager_name = st.text_input(
        "Type your name",
        key="manager_input",
        label_visibility="collapsed",
        placeholder="Type your name"
    )

def really_claim_manager(name):
    st.session_state.current_user = name
    st.session_state.current_manager = name
    save_state()
    st.success("You are now managing the queue.")
    st.session_state.show_manager_confirm = False
    st.session_state.manager_candidate = ""
    st.session_state.needs_rerun = True

def handle_claim_request(name):
    current_manager = st.session_state.get("current_manager", "")
    if name:
        if current_manager and current_manager != name:
            st.session_state.show_manager_confirm = True
            st.session_state.manager_candidate = name
        else:
            really_claim_manager(name)

with claim_cols[1]:
    if st.button("🛠 Manage Queue", use_container_width=True):
        if manager_name:
            handle_claim_request(manager_name)
        else:
            st.warning("Type your name before claiming the queue.")

with claim_cols[2]:
    if st.session_state.current_user == st.session_state.current_manager and st.session_state.current_manager:
        if st.button("🔓 Release Manage Rights", use_container_width=True):
            st.session_state.current_manager = ""
            st.session_state.current_user = ""
            save_state()
            st.success("You have released manage rights.")
            st.rerun()

# Manager-confirm prompt
if st.session_state.show_manager_confirm:
    st.warning(f"⚠️ You will REPLACE **{st.session_state.current_manager}** as manager. Are you sure?")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes, replace", key="manager_yes_btn"):
            really_claim_manager(st.session_state.manager_candidate)
    with col_no:
        if st.button("No, cancel", key="manager_no_btn"):
            st.session_state.show_manager_confirm = False
            st.session_state.manager_candidate = ""

# Accept enter on manager input
if manager_name and manager_name != st.session_state.last_claimed_input:
    handle_claim_request(manager_name)
    st.session_state.last_claimed_input = manager_name

# ----------- Main Actions (manager) -----------
st.markdown("#### Main Actions")
cols = st.columns([1, 1, 1, 0.3, 1])
with cols[0]:
    if st.button("⏩ Advance", use_container_width=True):
        if st.session_state.current_user == st.session_state.current_manager:
            if st.session_state.queue:
                first = st.session_state.queue.pop(0)
                st.session_state.queue.append(first)
                bump_and_rerun()
        else:
            st.warning("You are not managing the queue. Press 'Manage Queue' to claim control.")
with cols[1]:
    if st.button("🧹 Clear All", use_container_width=True):
        if st.session_state.current_user == st.session_state.current_manager:
            st.session_state.queue.clear()
            st.session_state.calypso.clear()
            st.session_state.pinged.clear()
            bump_and_rerun()
        else:
            st.warning("You are not managing the queue. Press 'Manage Queue' to claim control.")
with cols[2]:
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state.rev += 1
        st.rerun()
with cols[3]:
    st.write("")  # spacer
with cols[4]:
    st.write("")  # spacer

# ----------- Join input -----------
def join_on_enter():
    name = st.session_state.get("name_input", "").strip()
    if name and name not in st.session_state.queue and name not in st.session_state.calypso:
        st.session_state.queue.append(name)
        st.session_state.name_input = ""
        save_state()
        st.session_state.rev += 1
        st.session_state.needs_rerun = True

join_cols = st.columns([4, 1])
with join_cols[0]:
    st.text_input("", key="name_input", on_change=join_on_enter, label_visibility="collapsed", placeholder="Add People")
with join_cols[1]:
    st.button("🎤 Join", on_click=join_on_enter, use_container_width=True)

# ----------- Current user controls (Leave / Hold / Return / Ping) -----------
st.markdown("#### Your Controls")
if st.session_state.current_user:
    cu = st.session_state.current_user
    ctl_cols = st.columns([1,1,1,1])
    with ctl_cols[0]:
        if st.button("🚪 Leave Queue", use_container_width=True):
            leave_queue(cu)
    with ctl_cols[1]:
        if st.button("⏳ Place Me On Hold", use_container_width=True):
            place_on_hold(cu)
    with ctl_cols[2]:
        if st.button("↩️ Return From Hold", use_container_width=True):
            return_from_hold(cu)
    with ctl_cols[3]:
        if st.button("📣 Toggle Ping", use_container_width=True):
            toggle_ping(cu)
else:
    st.info("Type your name in 'Manage Queue' to enable personal controls (these actions affect your name).")

# ----------- Queue Display -----------
if st.session_state.queue:
    st.markdown("### Queue Manager")
    left, right = st.columns([1, 2])

    with left:
        st.markdown("#### 🔀 Reorder")
        if st.session_state.current_user == st.session_state.current_manager:
            reordered = sortables.sort_items(
                st.session_state.queue,
                direction="vertical",
                key=f"sortable_{st.session_state.rev}"
            )
            if reordered != st.session_state.queue:
                st.session_state.queue = reordered
                save_state()
                st.session_state.rev += 1
                st.rerun()
        else:
            st.info("🔹 Only the manager can reorder the queue.")

    with right:
        def fmt_name(name):
            return f"{name} 📣" if name in st.session_state.pinged else name

        # --- TEXT BASED QUEUE (Single Column) ---
        output = "🏛️ 𝑬𝑷𝑰𝑪 𝑺𝒐𝒏𝒈 𝑸𝒖𝒆𝒖𝒆 1 🎭\n"
        output += "<https://epic-queue.streamlit.app/>\n"
        output += f"Managed by: {st.session_state.current_manager if st.session_state.current_manager else '-'}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"🎶 𝑪𝑼𝑹𝑹𝑬𝑵𝑻𝑳𝒀 𝑺𝑰𝑵𝑮𝑰𝑵𝑮\n✨👑🎤 {fmt_name(st.session_state.queue[0]) if len(st.session_state.queue)>=1 else '-'}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"⏭️ 𝑵𝑬𝑿𝑻 𝑼𝑷\n🌟 {fmt_name(st.session_state.queue[1]) if len(st.session_state.queue)>=2 else '-'}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n🛶 𝑶𝑵 𝑸𝑼𝑬𝑼𝑬\n"
        if len(st.session_state.queue) > 2:
            for person in st.session_state.queue[2:]:
                output += f"🎭 {fmt_name(person)}\n"
        else:
            output += "- None\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n🏝️ 𝑨𝒘𝒂𝒚 𝒘𝒊𝒕𝒉 𝑪𝒂𝒍𝒚𝒑𝒔𝒐\n"
        if st.session_state.calypso:
            for person in st.session_state.calypso:
                output += f"🌴 {fmt_name(person)}\n"
        else:
            output += "- None\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\nReact to join the legend:\n🎤 — Join the Queue\n🚪 — Leave the Queue\n📣 — Summon the Bard (Ping)\n⏳ — Place Me On Hold\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += "The Wheel of The Gods: <https://wheelofnames.com/mer-8nr>\n"

        st.code(output, language="text")

# ----------- ✨ Compact Queue Card (Beautiful Screenshot Card) -----------
if st.session_state.queue:
    with st.container():
        st.markdown("""
        <style>
        .queue-card {
            max-width: 520px;
            margin: 24px auto 40px;
            background: linear-gradient(135deg, #111017 0%, #2b1b3f 60%, #3a1b3a 100%);
            color: #ffffff;
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 8px 30px rgba(40,20,80,0.45), inset 0 1px 0 rgba(255,255,255,0.03);
            text-align: left;
            font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        .qc-head {
            display:flex; justify-content:space-between; align-items:center; gap:12px;
        }
        .qc-title { font-size:20px; font-weight:700; letter-spacing:0.6px; }
        .qc-managed { font-size:12px; opacity:0.8; }
        .qc-grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:12px; }
        .qc-box { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:10px; padding:10px; min-height:56px; display:flex; flex-direction:column; justify-content:center; }
        .label { font-size:11px; color:#d7cfff; opacity:0.95; font-weight:700; }
        .who { font-size:16px; font-weight:700; }
        .badges { display:flex; flex-wrap:wrap; gap:8px; margin-top:6px; }
        .badge { background: rgba(255,255,255,0.04); padding:6px 8px; border-radius:8px; font-size:13px; }
        .foot { font-size:11px; color:rgba(255,255,255,0.72); margin-top:10px; text-align:center; opacity:0.9; }
        @media (max-width:560px){
            .queue-card { max-width: 92%; padding:14px; }
            .who { font-size:14px; }
        }
        </style>
        """, unsafe_allow_html=True)

        def fmt_card_name(name): 
            return f"📣 {name}" if name in st.session_state.pinged else name

        now_name = fmt_card_name(st.session_state.queue[0]) if len(st.session_state.queue) >= 1 else "-"
        next_name = fmt_card_name(st.session_state.queue[1]) if len(st.session_state.queue) >= 2 else "-"

        queue_items_html = ""
        if len(st.session_state.queue) > 2:
            for n in st.session_state.queue[2:]:
                queue_items_html += f'<div class="badge">🎭 {fmt_card_name(n)}</div>'
        else:
            queue_items_html = '<div class="badge">—</div>'

        calypso_items_html = ""
        if st.session_state.calypso:
            for n in st.session_state.calypso:
                calypso_items_html += f'<div class="badge">🌴 {fmt_card_name(n)}</div>'
        else:
            calypso_items_html = '<div class="badge">—</div>'

        card_html = f"""
        <div class="queue-card">
            <div class="qc-head">
                <div>
                    <div class="qc-title">🎶 EPIC Song Queue</div>
                    <div class="qc-managed">Managed by {st.session_state.current_manager or '-'}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:12px; color:#f5e6ff; opacity:0.9;">Now</div>
                    <div class="who">{now_name}</div>
                    <div style="font-size:12px; color:#f5e6ff; opacity:0.9; margin-top:6px;">Next</div>
                    <div class="who" style="opacity:0.92;">{next_name}</div>
                </div>
            </div>

            <div class="qc-grid">
                <div class="qc-box">
                    <div class="label">🛶 On Queue</div>
                    <div class="badges">{queue_items_html}</div>
                </div>
                <div class="qc-box">
                    <div class="label">🏝️ Away with Calypso</div>
                    <div class="badges">{calypso_items_html}</div>
                </div>
            </div>

            <div class="foot">Share this card by screenshot — the text queue above remains for copy/paste.</div>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)


# Save & auto-rerun management
save_state()
if st.session_state.get("needs_rerun"):
    st.session_state.needs_rerun = False
    st.rerun()

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

