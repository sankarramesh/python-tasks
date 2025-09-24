# stopwatch_app.py (fixed text color)
import time
import math
import streamlit as st

st.set_page_config(page_title="Stopwatch ⏱️", page_icon="⏱️", layout="centered")

# ---------- THEME / STYLES ----------
st.markdown("""
<style>
/* Page background */
.main {
  padding-top: 1rem;
  padding-bottom: 2rem;
  background: linear-gradient(135deg, #fceabb 0%, #f8b500 40%, #ff6a88 100%) fixed;
}

/* Title styling */
h1, h2, h3 {
  color: #ffffff !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.6);
}

/* Timer display */
.timer-box {
  width: 100%;
  text-align: center;
  padding: 24px 18px;
  border-radius: 20px;
  background: rgba(0,0,0,0.6);
  box-shadow: 0 10px 25px rgba(0,0,0,0.25);
  border: 2px solid rgba(255,255,255,0.2);
}

.time {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: clamp(44px, 8vw, 72px);
  line-height: 1.1;
  letter-spacing: 1px;
  color: #ffffff !important;      /* ✅ Force white */
  margin: 0;
  text-shadow: 0 0 12px rgba(0,255,255,0.7);  /* ✅ Glow effect */
}

/* Pulsing effect when running */
.running .time {
  animation: glow 1.2s ease-in-out infinite;
}
@keyframes glow {
  0%   { text-shadow: 0 0 8px rgba(0,255,255,0.7); }
  50%  { text-shadow: 0 0 24px rgba(0,255,255,1); }
  100% { text-shadow: 0 0 8px rgba(0,255,255,0.7); }
}

/* Buttons */
.stButton>button {
  border: none;
  border-radius: 14px;
  padding: 14px 18px;
  font-weight: 700;
  letter-spacing: 0.2px;
  box-shadow: 0 8px 18px rgba(0,0,0,0.12);
  transition: transform 0.05s ease, filter 0.15s ease;
}
.stButton>button:active { transform: translateY(1px); }

/* Color variants by order (Start, Stop, Reset) */
div[data-testid="column"]:nth-child(1) .stButton>button {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}
div[data-testid="column"]:nth-child(2) .stButton>button {
  background: linear-gradient(135deg, #ef4444, #b91c1c);
  color: white;
}
div[data-testid="column"]:nth-child(3) .stButton>button {
  background: linear-gradient(135deg, #64748b, #334155);
  color: white;
}

/* Small info pill */
.pill {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.2);
  color: #ffffff;
  font-size: 12px;
  margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# ---------- STATE ----------
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = 0.0
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0

# ---------- HELPERS ----------
def fmt_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    ms = int((seconds - math.floor(seconds)) * 1000)
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
    else:
        return f"{m:02d}:{s:02d}.{ms:03d}"

def current_elapsed() -> float:
    if st.session_state.running:
        return st.session_state.elapsed + (time.time() - st.session_state.start_time)
    return st.session_state.elapsed

# ---------- UI ----------
st.title("⏱️ Colorful Stopwatch")

# Timer box
is_running = st.session_state.running
timer_class = "timer-box running" if is_running else "timer-box"
with st.container():
    st.markdown(f'<div class="{timer_class}">', unsafe_allow_html=True)
    st.markdown(f'<p class="time">{fmt_time(current_elapsed())}</p>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="pill">Status: {"Running" if is_running else "Stopped"}</span>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# Controls
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("▶️ Start", use_container_width=True):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.start_time = time.time()
with c2:
    if st.button("⏸️ Stop", use_container_width=True):
        if st.session_state.running:
            st.session_state.elapsed += time.time() - st.session_state.start_time
            st.session_state.running = False
with c3:
    if st.button("🔁 Reset", use_container_width=True):
        st.session_state.running = False
        st.session_state.elapsed = 0.0
        st.session_state.start_time = 0.0

st.caption("Tip: Click **Start** to begin, **Stop** to pause, **Reset** to clear. The display pulses while running.")

# ---------- LIVE UPDATE LOOP ----------
if st.session_state.running:
    time.sleep(0.1)
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()
