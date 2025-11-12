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

if st.session_state.current_user != st.session_state.current_manager:
    st_autorefresh(interval=3000)

def bump_and_rerun():
    save_state()
    st.session_state.rev += 1
    st.session_state.needs_rerun = True
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

if manager_name and manager_name != st.session_state.last_claimed_input:
    handle_claim_request(manager_name)
    st.session_state.last_claimed_input = manager_name

# ----------- Main Actions -----------
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

# ----------- Input to join -----------
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

        # --- Snapshot Queue as PNG + Copy ---
        if st.button("📸 Snapshot Queue (PNG)", use_container_width=True):
            text = output
            lines = text.splitlines()

            # Font
            try:
                font = ImageFont.truetype("DejaVuSansMono.ttf", 18)
            except:
                font = ImageFont.load_default()

            max_width = max(font.getlength(line) for line in lines)
            line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
            padding = 20
            img_height = line_height * len(lines) + padding * 2
            img_width = int(max_width) + padding * 2

            img = Image.new("RGB", (img_width, img_height), color=(18, 18, 18))
            draw = ImageDraw.Draw(img)
            y = padding
            for line in lines:
                draw.text((padding, y), line, font=font, fill=(255, 255, 255))
                y += line_height

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            st.image(buf, caption="Queue Snapshot", use_container_width=True)
            st.download_button(
                "💾 Download PNG",
                data=buf,
                file_name="queue_snapshot.png",
                mime="image/png",
            )

            # Auto-copy to clipboard (client side JS)
            img_base64 = base64.b64encode(buf.getvalue()).decode()
            js = f"""
            <script>
            async function copyImage() {{
                const response = await fetch("data:image/png;base64,{img_base64}");
                const blob = await response.blob();
                try {{
                    await navigator.clipboard.write([new ClipboardItem({{'image/png': blob}})]);
                    alert("✅ Image copied to clipboard! You can paste it in WhatsApp or Discord.");
                }} catch (err) {{
                    alert("⚠️ Copy to clipboard not supported in this browser.");
                }}
            }}
            copyImage();
            </script>
            """
            st.components.v1.html(js, height=0)

save_state()
if st.session_state.get("needs_rerun"):
    st.session_state.needs_rerun = False
    st.rerun()

# --- Custom Styling ---
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

# --- Credit ---
st.markdown('<div style="text-align:center; font-size:11px; color:gray; margin-top:18px;">credit: Saichizu</div>', unsafe_allow_html=True)
