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
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("➕ Join") and name:
        if name not in st.session_state.queue and name not in st.session_state.calypso:
            st.session_state.queue.append(name)

with col2:
    if st.button("➖ Leave") and name:
        if name in st.session_state.queue:
            st.session_state.queue.remove(name)
        if name in st.session_state.calypso:
            st.session_state.calypso.remove(name)

with col3:
    if st.button("⏩ Advance"):
        if st.session_state.queue:
            first = st.session_state.queue.pop(0)
            st.session_state.queue.append(first)

with col4:
    if st.button("⏳ Hold") and name in st.session_state.queue:
        st.session_state.queue.remove(name)
        st.session_state.calypso.append(name)

with col5:
    if st.button("🏝️ Return") and name in st.session_state.calypso:
        st.session_state.calypso.remove(name)
        st.session_state.queue.append(name)

with col6:
    if st.button("📋 Copy Output"):
        st.session_state.clip_ready = True
        st.success("Copied! (Select text below and copy manually if needed)")

# --- Drag & Drop Reordering ---
if st.session_state.queue:
    st.markdown("### 🔀 Drag to Reorder Queue")
    reordered = sortables.sort_items(
        st.session_state.queue,
        direction="vertical",
        key="sortable_list"
    )
    if reordered != st.session_state.queue:
        st.session_state.queue = reordered

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
