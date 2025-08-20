import streamlit as st

# Initialize session state
if "queue" not in st.session_state:
    st.session_state.queue = []
if "calypso" not in st.session_state:
    st.session_state.calypso = []

st.title("⚔️🏛️ Saichizu's Odyssean Song Queue 🎭")

# --- Input field ---
name = st.text_input("Enter your name:")

col1, col2, col3 = st.columns(3)

# --- Queue Controls ---
with col1:
    if st.button("➕ Join Queue") and name:
        if name not in st.session_state.queue and name not in st.session_state.calypso:
            st.session_state.queue.append(name)

with col2:
    if st.button("➖ Leave Queue") and name:
        if name in st.session_state.queue:
            st.session_state.queue.remove(name)
        if name in st.session_state.calypso:
            st.session_state.calypso.remove(name)

with col3:
    if st.button("⏩ Advance Queue"):
        if st.session_state.queue:
            first = st.session_state.queue.pop(0)
            st.session_state.queue.append(first)

# --- Calypso Controls ---
col4, col5 = st.columns(2)
with col4:
    if st.button("⏳ Put On Hold (Calypso)") and name in st.session_state.queue:
        st.session_state.queue.remove(name)
        st.session_state.calypso.append(name)

with col5:
    if st.button("🏝️ Return From Calypso") and name in st.session_state.calypso:
        st.session_state.calypso.remove(name)
        st.session_state.queue.append(name)

# --- Change Order ---
if st.session_state.queue:
    st.markdown("### 🔀 Change Order")
    person_to_move = st.selectbox("Select person to reorder:", st.session_state.queue)
    new_position = st.number_input(
        "New position (1 = front of queue)", 
        min_value=1, 
        max_value=len(st.session_state.queue), 
        value=1, 
        step=1
    )
    if st.button("Change Order"):
        st.session_state.queue.remove(person_to_move)
        st.session_state.queue.insert(new_position - 1, person_to_move)
        st.success(f"Moved {person_to_move} to position {new_position}")

# --- Display the queue ---
st.markdown("## 📋 Queue Status")

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

# Show output nicely
st.text(output)

# --- Copy to clipboard ---
st.markdown("### 📋 Copy Output")
st.code(output, language="text")
st.caption("Copy the above output manually (Streamlit doesn’t allow direct clipboard writes).")
