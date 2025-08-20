import streamlit as st
import streamlit_sortables as sortables

# ---------------- Helpers ----------------
def ensure_state():
    if "queue" not in st.session_state: st.session_state.queue = []
    if "calypso" not in st.session_state: st.session_state.calypso = []
    if "rev" not in st.session_state: st.session_state.rev = 0  # forces sortable to remount

def bump_and_rerun():
    st.session_state.rev += 1
    st.rerun()

def numbered(items, start_index):
    # Return ["1. Alice", "2. Bob", ...] starting at start_index
    return [f"{i+start_index}. {p}" for i, p in enumerate(items)]

def strip_numbers(labeled_items):
    # Convert ["1. Alice", "2. Bob"] -> ["Alice", "Bob"]
    return [s.split(". ", 1)[1] if ". " in s else s for s in labeled_items]

# --------------- App ---------------------
ensure_state()

st.title("⚔️🏛️ Saichizu's Odyssean Song Queue 🎭")

# ---- Top input + controls ----
name = st.text_input("Enter your name:")

top = st.columns(7)
with top[0]:
    if st.button("➕ Join", use_container_width=True) and name:
        if name not in st.session_state.queue and name not in st.session_state.calypso:
            st.session_state.queue.append(name)
            bump_and_rerun()
with top[1]:
    if st.button("⏩ Advance", use_container_width=True):
        if st.session_state.queue:
            first = st.session_state.queue.pop(0)
            st.session_state.queue.append(first)
            bump_and_rerun()
with top[2]:
    if st.button("📋 Copy Output", use_container_width=True):
        st.session_state._show_copy_notice = True  # info only; copy via manual select

# Quick action bars (clickable names — now rows instead of columns)
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


# ---- Drag & Drop Reordering (always active, always refreshed) ----
if st.session_state.queue:
    st.markdown("### 🔀 Drag to Reorder Queue")

    n = len(st.session_state.queue)
    # Decide columns (1/2/3) and build labeled lists
    if n <= 5:
        col_count = 1
        labeled = numbered(st.session_state.queue, 1)
        # Unique key includes revision + layout so component remounts when data/layout changes
        sortable_key = f"sortable_single_{st.session_state.rev}"
        reordered = sortables.sort_items(labeled, direction="vertical", key=sortable_key)
        new_q = strip_numbers(reordered)

    elif n <= 10:
        col_count = 2
        half = (n + 1) // 2
        left_items = numbered(st.session_state.queue[:half], 1)
        right_items = numbered(st.session_state.queue[half:], half + 1)

        c1, c2 = st.columns(2)
        with c1:
            left_key = f"sortable_left_{st.session_state.rev}"
            r_left = sortables.sort_items(left_items, direction="vertical", key=left_key)
        with c2:
            right_key = f"sortable_right_{st.session_state.rev}"
            r_right = sortables.sort_items(right_items, direction="vertical", key=right_key)

        new_q = strip_numbers(r_left + r_right)

    else:
        col_count = 3
        third = (n + 2) // 3
        c1_items = numbered(st.session_state.queue[:third], 1)
        c2_items = numbered(st.session_state.queue[third:2*third], third + 1)
        c3_items = numbered(st.session_state.queue[2*third:], 2*third + 1)

        c1, c2, c3 = st.columns(3)
        with c1:
            k1 = f"sortable_c1_{st.session_state.rev}"
            r1 = sortables.sort_items(c1_items, direction="vertical", key=k1)
        with c2:
            k2 = f"sortable_c2_{st.session_state.rev}"
            r2 = sortables.sort_items(c2_items, direction="vertical", key=k2)
        with c3:
            k3 = f"sortable_c3_{st.session_state.rev}"
            r3 = sortables.sort_items(c3_items, direction="vertical", key=k3)

        new_q = strip_numbers(r1 + r2 + r3)

    # Apply reordering if changed
    if new_q != st.session_state.queue:
        st.session_state.queue = new_q
        bump_and_rerun()

# ---- Build final output (single display) ----
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

st.text(output)

# Built-in copy button (Streamlit shows it automatically in st.code)
st.code(output, language="text")

# Small notice after pressing "Copy Output"
if st.session_state.get("_show_copy_notice"):
    st.info("Select the output above and press Ctrl/Cmd+C to copy.")
    st.session_state._show_copy_notice = False


