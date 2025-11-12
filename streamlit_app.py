import streamlit as st
import streamlit_sortables as sortables
import json, os

SAVE_FILE = "queue.json"

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

# --- Always load state at the top ---
load_state()

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

from streamlit_autorefresh import st_autorefresh
if st.session_state.current_user != st.session_state.current_manager:
    st_autorefresh(interval=3000)

def bump_and_rerun():
    save_state()
    st.session_state.rev += 1
    st.session_state.needs_rerun = True
    st.rerun()

st.title("⚔️EPIC Singing VC 1 Queue🎭")
st.markdown(
    "_Use this only for **Epic Singing VC 1** because changes are saved. "
    "For Epic Singing VC 2, use [this link](https://epic-queue-2.streamlit.app/)._"
)

if st.session_state.current_manager:
    st.info(f"💡 Currently managing the queue: **{st.session_state.current_manager}**")
else:
    st.info("💡 No one is currently managing the queue. Press 'Manage Queue' to take control.")

# ----------- Manager Name Input & Claim Button -----------
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
            # Prompt for confirmation
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

# Prompt for manager replacement
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

# Enter key handling for manager name input
if manager_name and manager_name != st.session_state.last_claimed_input:
    handle_claim_request(manager_name)
    st.session_state.last_claimed_input = manager_name

# ----------- Top button bar -----------
st.markdown("#### Main Actions")
qa = st.columns(4)
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
    st.write("")  # extra spacer for layout

# ----------- Input to join (side by side, with placeholder) -----------
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
    st.text_input(
        "",
        key="name_input",
        on_change=join_on_enter,
        label_visibility="collapsed",
        placeholder="Add People"
    )
with join_cols[1]:
    st.button("🎤 Join", on_click=join_on_enter, use_container_width=True)

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

        # helper to print items in 2 columns
        def two_columns(items, prefix="🎭", width=20):
            lines = []
            for i in range(0, len(items), 2):
                left = f"{prefix} {fmt_name(items[i])}" if i < len(items) else ""
                right = f"{prefix} {fmt_name(items[i+1])}" if i+1 < len(items) else ""
                lines.append(f"{left:<{width}}{right}")
            return "\n".join(lines)

        output = "🏛️ 𝑬𝑷𝑰𝑪 𝑺𝒐𝒏𝒈 𝑸𝒖𝒆𝒖𝒆 1 🎭\n"
        output += "https://epic-queue.streamlit.app/\n"
        output += f"Managed by: {st.session_state.current_manager if st.session_state.current_manager else '-'}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"

        # singing and next up (side by side)
        singing = fmt_name(st.session_state.queue[0]) if len(st.session_state.queue) >= 1 else "-"
        next_up = fmt_name(st.session_state.queue[1]) if len(st.session_state.queue) >= 2 else "-"
        output += f"𝑺𝑰𝑵𝑮𝑰𝑵𝑮{' ' * 16}⏭️ 𝑵𝑬𝑿𝑻 𝑼𝑷\n"
        output += f"👑 {singing:<15}🌟 {next_up}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"

        # queue list (two per line)
        output += "🛶 𝑶𝑵 𝑸𝑼𝑬𝑼𝑬\n"
        if len(st.session_state.queue) > 2:
            on_queue = st.session_state.queue[2:]
            output += two_columns(on_queue) + "\n"
        else:
            output += "- None\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"

        # calypso list (two per line)
        output += "🏝️ 𝑨𝒘𝒂𝒚 𝒘𝒊𝒕𝒉 𝑪𝒂𝒍𝒚𝒑𝒔𝒐\n"
        if st.session_state.calypso:
            output += two_columns(st.session_state.calypso, prefix="🌴") + "\n"
        else:
            output += "- None\n"

        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += "React to join the legend:\n"
        output += "🎤 — Join the Queue\n🚪 — Leave the Queue\n📣 — Summon the Bard (Ping)\n⏳ — Place Me On Hold\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"

        st.code(output, language="text")



save_state()
if st.session_state.get("needs_rerun"):
    st.session_state.needs_rerun = False
    st.rerun()

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

# --- Credit at bottom ---
st.markdown('<div style="text-align:center; font-size:11px; color:gray; margin-top:18px;">credit: Saichizu</div>', unsafe_allow_html=True)













