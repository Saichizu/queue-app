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

# ----------- Main Actions -----------
st.markdown("#### Main Actions")
cols = st.columns([1, 1, 1])
with cols[0]:
    if st.button("⏩ Advance", use_container_width=True):
        if st.session_state.current_user == st.session_state.current_manager:
            if st.session_state.queue:
                first = st.session_state.queue.pop(0)
                st.session_state.queue.append(first)
                bump_and_rerun()
        else:
            st.warning("You are not managing the queue.")
with cols[1]:
    if st.button("🧹 Clear All", use_container_width=True):
        if st.session_state.current_user == st.session_state.current_manager:
            st.session_state.queue.clear()
            st.session_state.calypso.clear()
            st.session_state.pinged.clear()
            bump_and_rerun()
with cols[2]:
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state.rev += 1
        st.rerun()

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

# ----------- Queue Display -----------
if st.session_state.queue:
    st.markdown("### Queue Manager")
    left, right = st.columns([1, 2])
    with left:
        st.markdown("#### 🔀 Reorder")
        if st.session_state.current_user == st.session_state.current_manager:
            reordered = sortables.sort_items(st.session_state.queue, direction="vertical", key=f"sortable_{st.session_state.rev}")
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
        output += f"𝑺𝑰𝑵𝑮𝑰𝑵𝑮                ⏭️ 𝑵𝑬𝑿𝑻 𝑼𝑷\n"
        singing = fmt_name(st.session_state.queue[0]) if len(st.session_state.queue)>=1 else '-'
        nxt = fmt_name(st.session_state.queue[1]) if len(st.session_state.queue)>=2 else '-'
        output += f"👑 {singing:<20} 🌟 {nxt}\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n🛶 𝑶𝑵 𝑸𝑼𝑬𝑼𝑬\n"
        for i in range(2, len(st.session_state.queue), 2):
            left = fmt_name(st.session_state.queue[i])
            right = fmt_name(st.session_state.queue[i+1]) if i+1 < len(st.session_state.queue) else ""
            output += f"🎭 {left:<12} 🎭 {right}\n"
        if len(st.session_state.queue) <= 2:
            output += "- None\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n🏝️ 𝑨𝒘𝒂𝒚 𝒘𝒊𝒕𝒉 𝑪𝒂𝒍𝒚𝒑𝒔𝒐\n"
        if st.session_state.calypso:
            for i in range(0, len(st.session_state.calypso), 2):
                left = fmt_name(st.session_state.calypso[i])
                right = fmt_name(st.session_state.calypso[i+1]) if i+1 < len(st.session_state.calypso) else ""
                output += f"🌴 {left:<12} 🌴 {right}\n"
        else:
            output += "- None\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\nReact to join the legend:\n🎤 — Join the Queue\n🚪 — Leave the Queue\n📣 — Summon the Bard (Ping)\n⏳ — Place Me On Hold\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += "The Wheel of The Gods: <https://wheelofnames.com/mer-8nr>\n"

        st.code(output, language="text")

# ----------- ✨ Compact Queue Card -----------
if st.session_state.queue:
    with st.container():
        st.markdown("""
        <style>
        .queue-card {
            background: linear-gradient(135deg, #1f1b3a, #3a1b3a);
            color: #fff;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 0 25px rgba(200,100,255,0.2);
            text-align: center;
            margin-top: 20px;
        }
        .queue-card h2 {
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .queue-card .section {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px;
        }
        .queue-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 6px;
            justify-items: center;
        }
        .badge {
            background: rgba(255,255,255,0.1);
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 0.9rem;
            backdrop-filter: blur(4px);
        }
        </style>
        """, unsafe_allow_html=True)

        def fmt_card_name(name): return f"📣 {name}" if name in st.session_state.pinged else name

        st.markdown(f"""
        <div class="queue-card">
            <h2>🎶 EPIC Song Queue 🎭</h2>
            <div class="section"><b>👑 Now Singing:</b><br>{fmt_card_name(st.session_state.queue[0]) if st.session_state.queue else '-'}</div>
            <div class="section"><b>🌟 Next Up:</b><br>{fmt_card_name(st.session_state.queue[1]) if len(st.session_state.queue)>=2 else '-'}</div>
            <div class="section">
                <b>🛶 On Queue:</b>
                <div class="queue-grid">
                    {''.join(f'<div class="badge">🎭 {fmt_card_name(n)}</div>' for n in st.session_state.queue[2:]) if len(st.session_state.queue)>2 else '<div class="badge">None</div>'}
                </div>
            </div>
            <div class="section">
                <b>🏝️ Away with Calypso:</b>
                <div class="queue-grid">
                    {''.join(f'<div class="badge">🌴 {fmt_card_name(n)}</div>' for n in st.session_state.calypso) if st.session_state.calypso else '<div class="badge">None</div>'}
                </div>
            </div>
            <div style="font-size:0.8rem; opacity:0.7; margin-top:8px;">Managed by {st.session_state.current_manager or '-'}</div>
        </div>
        """, unsafe_allow_html=True)
