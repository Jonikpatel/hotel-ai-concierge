"""
app.py
------
LuxStay AI Concierge — Main Streamlit Application
Run with: streamlit run app.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st  # noqa: E402

from src.hotel_db import fresh_state, HOTEL  # noqa: E402
from src.voice_input import voice_input_component  # noqa: E402

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{HOTEL['name']} — AI Concierge",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: Luxury dark-gold hotel aesthetic ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Montserrat:wght@300;400;500;600&display=swap');  # noqa: E501

:root {
  --gold: #C9A84C;
  --gold-light: #E8D5A3;
  --gold-dim: #8a6f2e;
  --ink: #0a0a0e;
  --ink2: #12121a;
  --ink3: #1c1c2a;
  --ink4: #252535;
  --cream: #f5f0e8;
  --text: #e8e0d0;
  --text-dim: #9a9080;
  --success: #4a9e6b;
  --danger: #c04a4a;
  --info: #4a7ec0;
}

html, body, [class*="css"] {
  font-family: 'Montserrat', sans-serif;
  background-color: var(--ink) !important;
  color: var(--text) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1400px; }

/* Header */
.luxstay-header {
  text-align: center;
  padding: 2rem 0 1.5rem;
  border-bottom: 1px solid var(--gold-dim);
  margin-bottom: 2rem;
  position: relative;
}
.luxstay-header::before, .luxstay-header::after {
  content: '◆';
  color: var(--gold-dim);
  font-size: 10px;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}
.luxstay-header::before { left: 0; }
.luxstay-header::after { right: 0; }

.hotel-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.8rem;
  font-weight: 300;
  letter-spacing: 0.15em;
  color: var(--gold);
  text-transform: uppercase;
  line-height: 1;
}
.hotel-subtitle {
  font-size: 0.72rem;
  letter-spacing: 0.35em;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-top: 0.4rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--ink2) !important;
  border-right: 1px solid var(--ink4) !important;
}
section[data-testid="stSidebar"] .block-container {
  padding: 1.5rem 1rem;
}

/* Sidebar labels */
.sidebar-section {
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold-dim);
  margin: 1.5rem 0 0.6rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid var(--ink4);
}

/* Chat container */
.chat-container {
  background: var(--ink2);
  border: 1px solid var(--ink4);
  border-radius: 2px;
  padding: 1.5rem;
  height: 480px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  scrollbar-width: thin;
  scrollbar-color: var(--gold-dim) var(--ink2);
}

/* Chat bubbles */
.msg-user {
  align-self: flex-end;
  background: var(--ink4);
  border: 1px solid var(--gold-dim);
  border-radius: 2px 2px 0 2px;
  padding: 0.75rem 1rem;
  max-width: 70%;
  font-size: 0.9rem;
  color: var(--text);
  position: relative;
}
.msg-user::before {
  content: '🎙️';
  font-size: 10px;
  position: absolute;
  top: -10px;
  right: 8px;
  background: var(--ink2);
  padding: 0 4px;
}

.msg-aria {
  align-self: flex-start;
  background: var(--ink3);
  border-left: 3px solid var(--gold);
  padding: 0.75rem 1rem;
  max-width: 75%;
  font-size: 0.9rem;
  color: var(--text);
  border-radius: 0 2px 2px 0;
}
.msg-aria .aria-label {
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.4rem;
  font-family: 'Montserrat', sans-serif;
}

/* Action cards */
.action-card {
  margin: 0.5rem 0 0.5rem 1.5rem;
  padding: 1rem 1.2rem;
  border-radius: 2px;
  font-size: 0.82rem;
  max-width: 72%;
}
.action-card.checkin {
  background: linear-gradient(135deg, #0d2018 0%, #1a3328 100%);
  border: 1px solid #4a9e6b;
}
.action-card.checkout {
  background: linear-gradient(135deg, #200d0d 0%, #331a1a 100%);
  border: 1px solid #c04a4a;
}
.action-card.roomservice {
  background: linear-gradient(135deg, #1a160d 0%, #2e2510 100%);
  border: 1px solid var(--gold-dim);
}
.action-card.housekeeping {
  background: linear-gradient(135deg, #0d1520 0%, #1a2535 100%);
  border: 1px solid #4a7ec0;
}
.action-card.maintenance {
  background: linear-gradient(135deg, #20140d 0%, #352118 100%);
  border: 1px solid #c08a4a;
}

.action-title {
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  margin-bottom: 0.6rem;
  font-weight: 600;
}
.action-card.checkin .action-title { color: #4a9e6b; }
.action-card.checkout .action-title { color: #c04a4a; }
.action-card.roomservice .action-title { color: var(--gold); }
.action-card.housekeeping .action-title { color: #4a7ec0; }
.action-card.maintenance .action-title { color: #c08a4a; }

.action-row { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 0.3rem; }
.action-item { display: flex; flex-direction: column; gap: 2px; }
.action-label { font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em; }  # noqa: E501
.action-value { color: var(--text); font-weight: 500; }

/* Input area */
.input-area {
  margin-top: 1rem;
  padding: 1rem 1.2rem;
  background: var(--ink2);
  border: 1px solid var(--ink4);
  border-radius: 2px;
}

/* Streamlit input overrides */
.stTextInput > div > div > input {
  background-color: var(--ink3) !important;
  border: 1px solid var(--ink4) !important;
  border-radius: 2px !important;
  color: var(--text) !important;
  font-family: 'Montserrat', sans-serif !important;
  font-size: 0.9rem !important;
  padding: 0.6rem 0.9rem !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--gold-dim) !important;
  box-shadow: 0 0 0 1px var(--gold-dim) !important;
}

.stButton > button {
  background: linear-gradient(135deg, var(--gold-dim) 0%, var(--gold) 100%) !important;
  color: var(--ink) !important;
  border: none !important;
  border-radius: 2px !important;
  font-family: 'Montserrat', sans-serif !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.15em !important;
  text-transform: uppercase !important;
  padding: 0.55rem 1.2rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px rgba(201,168,76,0.3) !important;
}

/* Selectbox / dropdown */
.stSelectbox > div > div {
  background-color: var(--ink3) !important;
  border: 1px solid var(--ink4) !important;
  color: var(--text) !important;
  border-radius: 2px !important;
}

/* Metrics */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.metric-box {
  flex: 1;
  background: var(--ink2);
  border: 1px solid var(--ink4);
  padding: 1rem 1.2rem;
  border-radius: 2px;
  border-top: 2px solid var(--gold-dim);
}
.metric-val { font-family: 'Cormorant Garamond', serif; font-size: 2rem;
              font-weight: 300; color: var(--gold); line-height: 1; }
.metric-lbl { font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase;
              color: var(--text-dim); margin-top: 0.3rem; }

/* Status badges */
.badge {
  display: inline-block; font-size: 0.6rem; font-weight: 600;
  letter-spacing: 0.15em; text-transform: uppercase; padding: 2px 8px;
  border-radius: 1px;
}
.badge-green { background: #0d2018; color: #4a9e6b; border: 1px solid #4a9e6b; }
.badge-gold { background: #1a160d; color: var(--gold); border: 1px solid var(--gold-dim); }
.badge-red { background: #200d0d; color: #c04a4a; border: 1px solid #c04a4a; }
.badge-blue { background: #0d1520; color: #4a7ec0; border: 1px solid #4a7ec0; }

/* Welcome screen */
.welcome-banner {
  text-align: center; padding: 3rem 2rem;
  background: linear-gradient(180deg, var(--ink2) 0%, var(--ink) 100%);
  border: 1px solid var(--ink4); margin-bottom: 1.5rem;
}
.welcome-title {
  font-family: 'Cormorant Garamond', serif; font-size: 1.5rem;
  font-weight: 300; color: var(--gold-light); margin-bottom: 0.5rem;
}
.welcome-text { font-size: 0.82rem; color: var(--text-dim); line-height: 1.8; }

.suggestion-row { display: flex; flex-wrap: wrap; gap: 0.5rem;
                  margin-top: 1.5rem; justify-content: center; }
.suggestion-chip {
  background: var(--ink3); border: 1px solid var(--gold-dim);
  color: var(--gold-light); padding: 0.4rem 0.9rem;
  border-radius: 1px; font-size: 0.75rem; cursor: pointer;
  font-style: italic; transition: all 0.2s;
}
.suggestion-chip:hover { background: var(--ink4); border-color: var(--gold); }

/* Divider */
.gold-divider { border: none; border-top: 1px solid var(--ink4); margin: 1.5rem 0; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--ink2); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "hotel_state" not in st.session_state:
    st.session_state.hotel_state = fresh_state()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, text, action_result)
if "current_room" not in st.session_state:
    st.session_state.current_room = None
if "api_key_ok" not in st.session_state:
    st.session_state.api_key_ok = False
if "pending_voice" not in st.session_state:
    st.session_state.pending_voice = ""

state = st.session_state.hotel_state


# ── Helper: format action result as HTML card ──────────────────────────────────
def _render_action_card(result: dict) -> str:
    if not result or not result.get("success"):
        err = result.get("error", "Unknown error") if result else "No result"
        err_card = (
            '<div class="action-card maintenance">'
            '<div class="action-title">Notice</div>'
            f'{err}</div>'
        )
        return err_card

    action = result.get("action", "")

    if action == "CHECK_IN":
        amenities = ", ".join(result.get("amenities", [])[:3])
        requests = result.get("special_requests", "")
        return f"""
<div class="action-card checkin">
  <div class="action-title">✓ Check-In Confirmed</div>
  <div class="action-row">
    <div class="action-item">
      <span class="action-label">Guest</span>
      <span class="action-value">{result.get('guest_name')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Room</span>
      <span class="action-value">{result.get('room_number')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Type</span>
      <span class="action-value">{result.get('room_type')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Rate</span>
      <span class="action-value">${result.get('rate_usd')}/night</span>
    </div>
    <div class="action-item">
      <span class="action-label">Check-out</span>
      <span class="action-value">{result.get('check_out_date')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">WiFi</span>
      <span class="action-value">{result.get('wifi_password')}</span>
    </div>
  </div>
  {'<div style="margin-top:0.6rem;font-size:0.78rem;color:#9a9080;">✦ ' + requests + '</div>' if requests else ''}  # noqa: E501
  <div style="margin-top:0.6rem;font-size:0.72rem;color:#4a9e6b;">Amenities: {amenities}…</div>
</div>"""

    elif action == "CHECK_OUT":
        return f"""
<div class="action-card checkout">
  <div class="action-title">✓ Check-Out Complete</div>
  <div class="action-row">
    <div class="action-item">
      <span class="action-label">Guest</span>
      <span class="action-value">{result.get('guest_name')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Room</span>
      <span class="action-value">{result.get('room_number')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Nights</span>
      <span class="action-value">{result.get('nights')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Room Charges</span>
      <span class="action-value">${result.get('room_charges'):,.2f}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Room Service</span>
      <span class="action-value">${result.get('room_service_charges'):,.2f}</span>
    </div>
    <div class="action-item">
      <span class="action-label">Taxes (15%)</span>
      <span class="action-value">${result.get('taxes'):,.2f}</span>
    </div>
    <div class="action-item">
      <span class="action-label" style="color:#c04a4a;">Total</span>
      <span class="action-value" style="color:#e8a0a0;font-size:1.1rem;">${result.get('total_usd'):,.2f}</span>  # noqa: E501
    </div>
  </div>
</div>"""

    elif action == "ROOM_SERVICE":
        items_html = "".join(
            f'<div style="display:flex;justify-content:space-between;padding:2px 0;">'
            f'<span>{i["quantity"]}× {i["item"]}</span>'
            f'<span style="color:var(--gold)">${i["price"] * i["quantity"]:.2f}</span></div>'
            for i in result.get("items", [])
        )
        return f"""
<div class="action-card roomservice">
  <div class="action-title">✓ Order #{result.get('order_id')}</div>
  <div style="margin-bottom:0.5rem;">{items_html}</div>
  <div class="action-row">
    <div class="action-item">
      <span class="action-label">Total</span>
      <span class="action-value">${result.get('total_usd'):,.2f}</span>
    </div>
    <div class="action-item">
      <span class="action-label">ETA</span>
      <span class="action-value">{result.get('eta_minutes')} min</span>
    </div>
    <div class="action-item">
      <span class="action-label">Room</span>
      <span class="action-value">{result.get('room_number')}</span>
    </div>
  </div>
</div>"""

    elif action == "HOUSEKEEPING":
        return f"""
<div class="action-card housekeeping">
  <div class="action-title">✓ Housekeeping #{result.get('ticket_id')}</div>
  <div class="action-row">
    <div class="action-item">
      <span class="action-label">Request</span>
      <span class="action-value">{result.get('request')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">ETA</span>
      <span class="action-value">{result.get('eta')}</span>
    </div>
  </div>
</div>"""

    elif action == "MAINTENANCE":
        return f"""
<div class="action-card maintenance">
  <div class="action-title">✓ Maintenance #{result.get('ticket_id')}</div>
  <div class="action-row">
    <div class="action-item">
      <span class="action-label">Issue</span>
      <span class="action-value">{result.get('issue')}</span>
    </div>
    <div class="action-item">
      <span class="action-label">ETA</span>
      <span class="action-value">{result.get('eta')}</span>
    </div>
  </div>
</div>"""

    return ""


# ── Send message handler ───────────────────────────────────────────────────────
def handle_send(user_input: str):
    if not user_input.strip():
        return
    from src.concierge import chat
    # chat() never raises — errors come back as friendly text
    ai_text, action_result = chat(
        user_message=user_input,
        state=state,
        current_room=st.session_state.current_room,
    )
    st.session_state.chat_history.append(("user", user_input, None))
    st.session_state.chat_history.append(("aria", ai_text, action_result))


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 1.5rem;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;
                  color:#C9A84C;letter-spacing:0.12em;font-weight:300;">LUXSTAY</div>
      <div style="font-size:0.58rem;letter-spacing:0.3em;color:#8a6f2e;
                  text-transform:uppercase;margin-top:2px;">Grand Hotel</div>
    </div>
    """, unsafe_allow_html=True)

    # API Key
    st.markdown('<div class="sidebar-section">API Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your free key at console.groq.com",
        key="api_key_input",
    )
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
        st.markdown(
            '<span class="badge badge-green">● Connected</span>', unsafe_allow_html=True
        )
    else:
        env_key = os.environ.get("GROQ_API_KEY", "")
        if env_key:
            st.markdown(
                '<span class="badge badge-gold">● Key from env</span>', unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<span class="badge badge-red">○ No key set</span>', unsafe_allow_html=True
            )

    # Room context
    st.markdown('<div class="sidebar-section">Guest Room Context</div>', unsafe_allow_html=True)
    occupied_rooms = [
        f"Room {r}" for r, data in state["rooms"].items() if data["status"] == "occupied"
    ]
    room_options = ["— Select room —"] + occupied_rooms
    room_sel = st.selectbox("Current Room", room_options, label_visibility="collapsed")
    if room_sel != "— Select room —":
        st.session_state.current_room = room_sel.replace("Room ", "")
    else:
        st.session_state.current_room = None

    # Hotel stats
    st.markdown('<div class="sidebar-section">Hotel Status</div>', unsafe_allow_html=True)
    total_rooms = len(state["rooms"])
    occupied = sum(1 for r in state["rooms"].values() if r["status"] == "occupied")
    available = sum(1 for r in state["rooms"].values() if r["status"] == "available")
    rs_orders = len(state["room_service_orders"])
    hk_open = sum(1 for t in state["housekeeping_tickets"] if t["status"] == "open")
    mnt_open = sum(1 for t in state["maintenance_tickets"] if t["status"] == "open")

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.3rem;">
      <div style="background:#12121a;border:1px solid #252535;padding:0.7rem;border-radius:2px;">
        <div style="font-size:1.4rem;color:#C9A84C;font-family:'Cormorant Garamond',serif;
                    font-weight:300;">{occupied}</div>
        <div style="font-size:0.58rem;color:#8a6f2e;letter-spacing:0.1em;
                    text-transform:uppercase;">Occupied</div>
      </div>
      <div style="background:#12121a;border:1px solid #252535;padding:0.7rem;border-radius:2px;">
        <div style="font-size:1.4rem;color:#4a9e6b;font-family:'Cormorant Garamond',serif;
                    font-weight:300;">{available}</div>
        <div style="font-size:0.58rem;color:#8a6f2e;letter-spacing:0.1em;
                    text-transform:uppercase;">Available</div>
      </div>
      <div style="background:#12121a;border:1px solid #252535;padding:0.7rem;border-radius:2px;">
        <div style="font-size:1.4rem;color:#C9A84C;font-family:'Cormorant Garamond',serif;
                    font-weight:300;">{rs_orders}</div>
        <div style="font-size:0.58rem;color:#8a6f2e;letter-spacing:0.1em;
                    text-transform:uppercase;">RS Orders</div>
      </div>
      <div style="background:#12121a;border:1px solid #252535;padding:0.7rem;border-radius:2px;">
        <div style="font-size:1.4rem;color:#4a7ec0;font-family:'Cormorant Garamond',serif;
                    font-weight:300;">{hk_open + mnt_open}</div>
        <div style="font-size:0.58rem;color:#8a6f2e;letter-spacing:0.1em;
                    text-transform:uppercase;">Open Tickets</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Session</div>', unsafe_allow_html=True)
    if st.button("Reset Hotel State", use_container_width=True):
        st.session_state.hotel_state = fresh_state()
        st.session_state.chat_history = []
        st.session_state.current_room = None
        st.rerun()

    st.markdown(
        '<div style="margin-top:2rem;font-size:0.58rem;color:#4a4040;'
        'text-align:center;letter-spacing:0.05em;">'
        'Powered by Groq AI · LuxStay v1.0</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="luxstay-header">
  <div class="hotel-name">LuxStay Grand Hotel</div>
  <div class="hotel-subtitle">AI Concierge · Manhattan, New York</div>
</div>
""", unsafe_allow_html=True)

# ── Welcome / suggestion chips (only if no conversation yet) ──────────────────
if not st.session_state.chat_history:
    st.markdown("""
<div class="welcome-banner">
  <div class="welcome-title">Good evening. I am Aria, your personal concierge.</div>
  <div class="welcome-text">
    Speak or type any request — check-in, room service, local recommendations,<br>
    housekeeping, and more. How may I assist you today?
  </div>
  <div class="suggestion-row">
    <span class="suggestion-chip" onclick="void(0)">"Check in under Johnson"</span>
    <span class="suggestion-chip">"Check me out of room 303"</span>
    <span class="suggestion-chip">"Club sandwich to room 601"</span>
    <span class="suggestion-chip">"Extra towels please"</span>
    <span class="suggestion-chip">"TV isn't working"</span>
    <span class="suggestion-chip">"Restaurant recommendations?"</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
if st.session_state.chat_history:
    chat_html = '<div class="chat-container" id="chat-box">'
    for role, text, action_result in st.session_state.chat_history:
        if role == "user":
            chat_html += f'<div class="msg-user">{text}</div>'
        else:
            chat_html += f'''<div class="msg-aria">
  <div class="aria-label">✦ Aria · AI Concierge</div>
  {text}
</div>'''
            if action_result:
                chat_html += _render_action_card(action_result)
    chat_html += '</div>'
    chat_html += """<script>
var cb = document.getElementById('chat-box');
if (cb) cb.scrollTop = cb.scrollHeight;
</script>"""
    st.markdown(chat_html, unsafe_allow_html=True)

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown('<div class="input-area">', unsafe_allow_html=True)

col_voice, col_input, col_send = st.columns([0.13, 0.73, 0.14])

with col_voice:
    st.markdown(
        '<div style="font-size:0.62rem;color:#8a6f2e;letter-spacing:0.1em;'
        'text-transform:uppercase;margin-bottom:4px;">Voice</div>',
        unsafe_allow_html=True,
    )
    voice_input_component(key="voice_comp")

with col_input:
    user_text = st.text_input(
        "Message",
        placeholder="Type a request or use the microphone…",
        label_visibility="collapsed",
        key="text_input",
    )

with col_send:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    send_clicked = st.button("Send →", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Quick action buttons ───────────────────────────────────────────────────────
st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:0.6rem;color:#8a6f2e;letter-spacing:0.2em;'
    'text-transform:uppercase;margin-bottom:0.6rem;">Quick Requests</div>',
    unsafe_allow_html=True,
)

q_cols = st.columns(6)
quick_actions = [
    ("🏨 Check-In", "I'd like to check in please"),
    ("🚪 Check-Out", f"Check me out of room {st.session_state.current_room or '303'} please"),
    ("🍽️ Room Service", "I'd like to order room service"),
    ("🧹 Housekeeping", "I need extra towels and toiletries"),
    ("🔧 Maintenance", "There's an issue in my room I'd like to report"),
    ("🗺️ Concierge", "What restaurants do you recommend nearby?"),
]
for col, (label, prompt) in zip(q_cols, quick_actions):
    with col:
        if st.button(label, use_container_width=True, key=f"quick_{label}"):
            handle_send(prompt)
            st.rerun()

# ── Handle text submit ─────────────────────────────────────────────────────────
if send_clicked and user_text.strip():
    handle_send(user_text.strip())
    st.rerun()
elif user_text.strip() and st.session_state.get("_last_input") != user_text:
    st.session_state["_last_input"] = user_text
