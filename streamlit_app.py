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
    else:
        st.session_state.queue = []
        st.session_state.calypso = []

def save_state():
    data = {
        "queue": st.session_state.queue,
        "calypso": st.session_state.calypso
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# ---------------- Init ----------------
if "initialized" not in st.session_state:
    load_state()
    st.session_state.rev = 0
    st.session_state.initialized = True

def bump_and_rerun():
    save_state()
    st.session_state.rev += 1
    st.rerun()

# ---------------- UI ----------------
st.title("⚔️🏛️ Saichizu's Odyssean Song Queue 🎭")

# Input box (Enter = Join)
def join_on_enter():
    name = st.session_state.name_input.strip()
    if name and name not in st.session_state.queue and name not in st.session_state.calypso:
        st.session_state.queue.append(name)
        st.session_state.name_input = ""  # clear input
        save_state()
        # bump rev so sortable remounts on next render
        st.session_state.rev += 1
        st.session_state.needs_rerun = True



st.text_input(
    "Enter your name:",
    key="name_input",
    on_change=join_on_enter
)

# --- Top button bar ---
cols = st.columns(3)
with cols[0]:
    if st.button("⏩ Advance", use_container_width=True):
        if st.session_state.queue:
            first = st.session_state.queue.pop(0)
            st.session_state.queue.append(first)
            bump_and_rerun()
with cols[1]:
    if st.button("🧹 Clear All", use_container_width=True):
        st.session_state.queue.clear()
        st.session_state.calypso.clear()
        bump_and_rerun()
with cols[2]:
    st.write(" ")  # spacer

# ---- Quick Actions (rows) ----
st.markdown("#### Quick Actions")
qa = st.columns(3)

with qa[0]:
    st.caption("➖ Leave (Queue)")
    if not st.session_state.queue:
        st.write("—")
    else:
        for i, person in enumerate(st.session_state.queue):
            if st.button(person, key=f"leave_{i}", use_container_width=True):
                st.session_state.queue.remove(person)
                bump_and_rerun()

with qa[1]:
    st.caption("⏳ Hold (to Calypso)")
    if not st.session_state.queue:
        st.write("—")
    else:
        for i, person in enumerate(st.session_state.queue):
            if st.button(person, key=f"hold_{i}", use_container_width=True):
                st.session_state.queue.remove(person)
                st.session_state.calypso.append(person)
                bump_and_rerun()

with qa[2]:
    st.caption("🏝️ Return (from Calypso)")
    if not st.session_state.calypso:
        st.write("—")
    else:
        for i, person in enumerate(st.session_state.calypso):
            if st.button(person, key=f"return_{i}", use_container_width=True):
                st.session_state.calypso.remove(person)
                st.session_state.queue.append(person)
                bump_and_rerun()

# ---- Drag & Drop Reordering ----
if st.session_state.queue:
    st.markdown("### 🔀 Drag to Reorder Queue")

    n = len(st.session_state.queue)

    def numbered(items, start): return [f"{i+start}. {p}" for i, p in enumerate(items)]
    def strip_numbers(labeled): return [s.split(". ", 1)[1] if ". " in s else s for s in labeled]

    if n <= 5:
        reordered = sortables.sort_items(
            numbered(st.session_state.queue, 1),
            direction="vertical",
            key=f"sortable_{st.session_state.rev}"
        )
        new_q = strip_numbers(reordered)
    elif n <= 10:
        half = (n + 1) // 2
        left_items = numbered(st.session_state.queue[:half], 1)
        right_items = numbered(st.session_state.queue[half:], half + 1)

        c1, c2 = st.columns(2)
        with c1:
            r_left = sortables.sort_items(left_items, direction="vertical", key=f"sortable_l_{st.session_state.rev}")
        with c2:
            r_right = sortables.sort_items(right_items, direction="vertical", key=f"sortable_r_{st.session_state.rev}")

        new_q = strip_numbers(r_left + r_right)
    else:
        third = (n + 2) // 3
        c1_items = numbered(st.session_state.queue[:third], 1)
        c2_items = numbered(st.session_state.queue[third:2*third], third + 1)
        c3_items = numbered(st.session_state.queue[2*third:], 2*third + 1)

        c1, c2, c3 = st.columns(3)
        with c1:
            r1 = sortables.sort_items(c1_items, direction="vertical", key=f"sortable1_{st.session_state.rev}")
        with c2:
            r2 = sortables.sort_items(c2_items, direction="vertical", key=f"sortable2_{st.session_state.rev}")
        with c3:
            r3 = sortables.sort_items(c3_items, direction="vertical", key=f"sortable3_{st.session_state.rev}")

        new_q = strip_numbers(r1 + r2 + r3)

    if new_q != st.session_state.queue:
        st.session_state.queue = new_q
        bump_and_rerun()

# ---- Build final output ----
output = "⚔️🏛️ 𝑺𝒂𝒊𝒄𝒉𝒊𝒛𝒖'𝒔  𝑺𝒐𝒏𝒈 𝑸𝒖𝒆𝒖𝒆 🎭\n\n"
output += ("━━━━━━━━━━━━━━━━━━━━━\n"
           "🎶 𝑪𝑼𝑹𝑹𝑬𝑵𝑻𝑳𝒀 𝑺𝑰𝑵𝑮𝑰𝑵𝑮\n"
           f"✨👑🎤 {st.session_state.queue[0] if len(st.session_state.queue) >= 1 else '-'}\n")
output += ("━━━━━━━━━━━━━━━━━━━━━\n"
           "⏭️ 𝑵𝑬𝑿𝑻 𝑼𝑷\n"
           f"🌟 {st.session_state.queue[1] if len(st.session_state.queue) >= 2 else '-'}\n")
output += "━━━━━━━━━━━━━━━━━━━━━\n"
output += "🛶 𝑶𝑵 𝑸𝑼𝑬𝑼𝑬\n"
if len(st.session_state.queue) > 2:
    for person in st.session_state.queue[2:]:
        output += f"🎭 {person}\n"
else:
    output += "- None\n"
output += "━━━━━━━━━━━━━━━━━━━━━\n"
output += "🏝️ 𝑨𝒘𝒂𝒚 𝒘𝒊𝒕𝒉 𝑪𝒂𝒍𝒚𝒑𝒔𝒐\n"
if st.session_state.calypso:
    for person in st.session_state.calypso:
        output += f"🌴 {person}\n"
else:
    output += "- None\n"
output += ("━━━━━━━━━━━━━━━━━━━━━\n"
           "React to join the legend:\n"
           "🎤 — Join the Queue\n"
           "🚪 — Leave the Queue\n"
           "📣 — Summon the Bard (Ping)\n"
           "⏳ — Place Me On Hold\n"
           "━━━━━━━━━━━━━━━━━━━━━")

# Main display + built-in copy button
st.text(output)
st.code(output, language="text")

# Always save state at end of render
save_state()

# Force rerun after input enter (fixes reorder not refreshing)
if st.session_state.get("needs_rerun"):
    st.session_state.needs_rerun = False
    st.rerun()





