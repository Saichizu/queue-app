import streamlit as st
import streamlit_sortables as sortables

# Initialize session state
if "queue" not in st.session_state:
    st.session_state.queue = []
if "calypso" not in st.session_state:
    st.session_state.calypso = []

st.title("⚔️🏛️ Saichizu's Odyssean Song Queue 🎭")

# --- Input field ---
name = st.text_input("Enter your name:")

# --- Top button bar ---
cols = st.columns(6)
with cols[0]:
    if st.button("➕ Join") and name:
        if name not in st.session_state.queue and name not in st.session_state.calypso:
            st.session_state.queue.append(name)
with cols[1]:
    if st.button("➖ Leave") and name:
        if name in st.session_state.queue:
            st.session_state.queue.remove(name)
        if name in st.session_state.calypso:
            st.session_state.calypso.remove(name)
with cols[2]:
    if st.button("⏩ Advance"):
        if st.session_state.queue:
            first = st.session_state.queue.pop(0)
            st.session_state.queue.append(first)
with cols[3]:
    if st.button("⏳ Hold") and name in st.session_state.queue:
        st.session_state.queue.remove(name)
        st.session_state.calypso.append(name)
with cols[4]:
    if st.button("🏝️ Return") and name in st.session_state.calypso:
        st.session_state.calypso.remove(name)
        st.session_state.queue.append(name)
with cols[5]:
    if st.button("📋 Copy Output"):
        st.success("Copied! (select text below and copy manually if needed)")

# --- Drag & Drop Reordering (always active) ---
if st.session_state.queue:
    st.markdown("### 🔀 Drag to Reorder Queue")

    n = len(st.session_state.queue)

    if n <= 5:
        # Single list
        reordered = sortables.sort_items(
            [f"{i+1}. {p}" for i, p in enumerate(st.session_state.queue)],
            direction="vertical",
            key="sortable_single"
        )
        new_queue = [item.split(". ", 1)[1] for item in reordered]

    elif n <= 10:
        # Split into 2 columns
        half = (n + 1) // 2
        left_items = [f"{i+1}. {p}" for i, p in enumerate(st.session_state.queue[:half])]
        right_items = [f"{i+half+1}. {p}" for i, p in enumerate(st.session_state.queue[half:])]

        col1, col2 = st.columns(2)
        with col1:
            reordered_left = sortables.sort_items(left_items, direction="vertical", key="sortable_left")
        with col2:
            reordered_right = sortables.sort_items(right_items, direction="vertical", key="sortable_right")

        new_queue = [item.split(". ", 1)[1] for item in reordered_left + reordered_right]

    else:
        # Split into 3 columns
        third = (n + 2) // 3
        col1_items = [f"{i+1}. {p}" for i, p in enumerate(st.session_state.queue[:third])]
        col2_items = [f"{i+third+1}. {p}" for i, p in enumerate(st.session_state.queue[third:2*third])]
        col3_items = [f"{i+2*third+1}. {p}" for i, p in enumerate(st.session_state.queue[2*third:])]

        col1, col2, col3 = st.columns(3)
        with col1:
            reordered_1 = sortables.sort_items(col1_items, direction="vertical", key="sortable_col1")
        with col2:
            reordered_2 = sortables.sort_items(col2_items, direction="vertical", key="sortable_col2")
        with col3:
            reordered_3 = sortables.sort_items(col3_items, direction="vertical", key="sortable_col3")

        new_queue = [item.split(". ", 1)[1] for item in reordered_1 + reordered_2 + reordered_3]

    # Always update if different
    if new_queue != st.session_state.queue:
        st.session_state.queue = new_queue

# --- Build Queue Output ---
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

# --- Display final output ---
st.text(output)
