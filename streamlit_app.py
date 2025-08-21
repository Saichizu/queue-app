import streamlit as st
import streamlit_sortables as sortables
import json, os

# ---------------- Persistence ----------------
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

# --- FIX: Always load state at the top ---
load_state()

# Only set up session flags if not already done
if "initialized" not in st.session_state:
    st.session_state.rev = 0
    st.session_state.initialized = True
    st.session_state.current_user = ""
    st.session_state.needs_rerun = False
    st.session_state.last_claimed_input = ""
    for flag in ["show_leave", "show_hold", "show_return", "show_ping"]:
        st.session_state[flag] = False

def bump_and_rerun():
    save_state()
    st.session_state.rev += 1
    st.session_state.needs_rerun = True
    st.rerun()

# ---------------- UI ----------------
st.title("⚔️EPIC Singing VC 1 Queue🎭")

st.markdown(
    "_Use this only for **Epic Singing VC 1** because changes are saved. "
    "For Epic Singing VC 2, use [this link](https://epic-queue-2.streamlit.app/)._"
)

# Display current manager
if st.session_state.current_manager:
    st.info(f"💡 Currently managing the queue: **{st.session_state.current_manager}**")
else:
    st.info("💡 No one is currently managing the queue. Press 'Manage Queue' to take control.")

# ---------------- Manager Name Input & Claim Button (side by side) ----------------
claim_cols = st.columns([4, 1])
with claim_cols[0]:
    manager_name = st.text_input(
        "Type your name",
        key="manager_input",
        label_visibility="collapsed",
        placeholder="Type your name"
    )
def claim_manager(name):
    if name:
        if st.session_state.get("current_manager") and st.session_state.current_manager != name:
            st.warning(f"You are now replacing **{st.session_state.current_manager}** as manager.")
        else:
            st.success("You are now managing the queue.")
        st.session_state.current_user = name
        st.session_state.current_manager = name
        save_state()
        st.session_state.needs_rerun = True
with claim_cols[1]:
    if st.button("🛠 Claim Queue", use_container_width=True):
        if manager_name:
            claim_manager(manager_name)
        else:
            st.warning("Type your name before claiming the queue.")

# Enter key handling for manager name input
if manager_name and manager_name != st.session_state.last_claimed_input:
    claim_manager(manager_name)
    st.session_state.last_claimed_input = manager_name

# ---------------- Top button bar ----------------
cols = st.columns(4)  # Advance, Clear, Refresh, Spacer

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
        # Just rerun; state is always loaded from file at the top
        st.session_state.rev += 1
        st.rerun()

with cols[3]:
    st.write(" ")  # spacer

# ---------------- Input to join (side by side, with placeholder) ----------------
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

# ---- Quick Actions (Leave, Hold, Return, Ping) ----
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

if st.session_state.current_user == st.session_state.current_manager:
    with qa[0]:
        if st.button("➖ Leave", use_container_width=True):
            st.session_state.show_leave = not st.session_state.show_leave
            for flag in ["show_hold", "show_return", "show_ping"]:
                st.session_state[flag] = False
        if st.session_state.show_leave:
            person = render_names(st.session_state.queue, "Leave")
            if person:
                st.session_state.queue.remove(person)
                st.session_state.pinged.discard(person)
                bump_and_rerun()

    with qa[1]:
        if st.button("⏳ Hold", use_container_width=True):
            st.session_state.show_hold = not st.session_state.show_hold
            for flag in ["show_leave", "show_return", "show_ping"]:
                st.session_state[flag] = False
        if st.session_state.show_hold:
            person = render_names(st.session_state.queue, "Hold")
            if person:
                st.session_state.queue.remove(person)
                st.session_state.calypso.append(person)
                bump_and_rerun()

    with qa[2]:
        if st.button("🏝️ Return", use_container_width=True):
            st.session_state.show_return = not st.session_state.show_return
            for flag in ["show_leave", "show_hold", "show_ping"]:
                st.session_state[flag] = False
        if st.session_state.show_return:
            person = render_names(st.session_state.calypso, "↩️")
            if person:
                st.session_state.calypso.remove(person)
                st.session_state.queue.append(person)
                bump_and_rerun()

    with qa[3]:
        if st.button("📣 Ping/Unping", use_container_width=True):
            st.session_state.show_ping = not st.session_state.show_ping
            for flag in ["show_leave", "show_hold", "show_return"]:
                st.session_state[flag] = False
        if st.session_state.show_ping:
            names = st.session_state.queue + st.session_state.calypso
            person = render_names(names, "📣")
            if person:
                if person in st.session_state.pinged:
                    st.session_state.pinged.remove(person)
                else:
                    st.session_state.pinged.add(person)
                bump_and_rerun()
else:
    st.info("⚠️ You are not managing the queue. Press 'Manage Queue' to interact with it.")

# ---- Layout: Reorder + Output ----
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

        output = "🏛️ 𝑬𝑷𝑰𝑪 𝑺𝒐𝒏𝒈 𝑸𝒖𝒆𝒖𝒆 1 🎭\n"
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
        output += "━━━━━━━━━━━━━━━━━━━━━\nReact to join the legend:\n🎤 — Join the Queue\n🚪 — Leave the Queue\n📣 — Summon the Bard (Ping)\n⏳ — Place Me On Hold\n━━━━━━━━━━━━━━━━━━━━━\n"
        output += "by Saichizu :)"
        st.code(output, language="text")

# Save state only once per session run
save_state()

if st.session_state.get("needs_rerun"):
    st.session_state.needs_rerun = False
    st.rerun()

# --- Style ---
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
