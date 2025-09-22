# app.py
import random
import streamlit as st
from datetime import datetime

# -----------------------------
# Retro 90s THEME (CSS)
# -----------------------------
st.set_page_config(page_title="Rock • Paper • Scissors — 90s Edition", page_icon="🕹️", layout="centered")
retro_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

html, body, [class*="css"]  {
  font-family: 'Press Start 2P', monospace !important;
}

body {
  background: radial-gradient(ellipse at center, #1b1b2f 0%, #0f1020 60%, #000 100%);
  color: #e6f3ff;
}

/* CRT scanlines */
body:before {
  content: "";
  pointer-events: none;
  position: fixed;
  top:0; left:0; right:0; bottom:0;
  background: repeating-linear-gradient(
    to bottom,
    rgba(255,255,255,0.04),
    rgba(255,255,255,0.04) 2px,
    rgba(0,0,0,0.06) 3px,
    rgba(0,0,0,0.06) 4px
  );
  mix-blend-mode: overlay;
}

/* Flicker glow title */
.title-glow {
  text-shadow:
    0 0 6px #59f,
    0 0 12px #59f,
    0 0 24px #6cf,
    0 0 48px #9ff;
  animation: flicker 2.6s infinite steps(2, end);
}

@keyframes flicker {
  0%, 19%, 21%, 23%, 80%, 100% { opacity: 1; }
  20%, 22% { opacity: .7; }
}

/* Card styling */
.arcade-card {
  border: 4px solid #59f;
  border-radius: 20px;
  padding: 18px 16px;
  background: linear-gradient(180deg, rgba(25,35,70,0.9), rgba(10,15,35,0.9));
  box-shadow: 0 0 0 4px rgba(0, 255, 255, 0.08), 0 10px 30px rgba(0,0,0,0.6);
}

/* Pixel buttons */
button[title="Rock"], button[title="Paper"], button[title="Scissors"] {
  font-family: 'Press Start 2P', monospace !important;
}

.pixel-btn {
  border: 3px solid #ff3;
  border-radius: 12px;
  padding: 14px 12px;
  background: linear-gradient(180deg, #303a60, #141a35);
  color: #fff;
  text-transform: uppercase;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 6px 0 #8a6, 0 8px 16px rgba(0,0,0,0.4);
}
.pixel-btn:hover { filter: brightness(1.15); }
.pixel-btn:active { transform: translateY(2px); box-shadow: 0 4px 0 #8a6; }

.badge {
  display:inline-block;
  padding: 8px 12px;
  border: 2px solid #9ff;
  border-radius: 10px;
  background: rgba(20,40,80,0.8);
  color: #9ff;
  font-size: 12px;
}

.result-win { color: #5dff8a; text-shadow: 0 0 8px rgba(93,255,138,.6); }
.result-lose { color: #ff657a; text-shadow: 0 0 8px rgba(255,101,122,.6); }
.result-draw { color: #ffd166; text-shadow: 0 0 8px rgba(255,209,102,.6); }

hr { border: none; height: 2px; background: linear-gradient(90deg, transparent, #59f, transparent); }
</style>
"""
st.markdown(retro_css, unsafe_allow_html=True)

# -----------------------------
# Initialize session state
# -----------------------------
if "user_score" not in st.session_state:
    st.session_state.user_score = 0
if "cpu_score" not in st.session_state:
    st.session_state.cpu_score = 0
if "draws" not in st.session_state:
    st.session_state.draws = 0
if "rounds" not in st.session_state:
    st.session_state.rounds = 0
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {time, user, cpu, result}

CHOICES = {
    "Rock": {"emoji": "🪨", "wins_against": "Scissors"},
    "Paper": {"emoji": "📜", "wins_against": "Rock"},
    "Scissors": {"emoji": "✂️", "wins_against": "Paper"},
}
CHOICE_LIST = list(CHOICES.keys())

def play_round(user_choice: str):
    cpu_choice = random.choice(CHOICE_LIST)
    if user_choice == cpu_choice:
        result = "Draw"
        st.session_state.draws += 1
        result_style = "result-draw"
        result_msg = "DRAW — try again!"
    elif CHOICES[user_choice]["wins_against"] == cpu_choice:
        result = "Win"
        st.session_state.user_score += 1
        result_style = "result-win"
        result_msg = "YOU WIN! 🎉"
    else:
        result = "Lose"
        st.session_state.cpu_score += 1
        result_style = "result-lose"
        result_msg = "YOU LOSE! 💥"

    st.session_state.rounds += 1
    st.session_state.history.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "user": f'{CHOICES[user_choice]["emoji"]} {user_choice}',
        "cpu": f'{CHOICES[cpu_choice]["emoji"]} {cpu_choice}',
        "outcome": result,
    })
    return result_msg, result_style, user_choice, cpu_choice

def reset_game(hard=False):
    st.session_state.user_score = 0
    st.session_state.cpu_score = 0
    st.session_state.draws = 0
    st.session_state.rounds = 0
    if hard:
        st.session_state.history = []

# -----------------------------
# UI
# -----------------------------
st.markdown('<h1 class="title-glow" style="text-align:center;">🕹️ ROCK • PAPER • SCISSORS</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;">Insert coin ➜ <span class="badge">1P START</span></p>', unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

col1, col2 = st.columns([1,1], gap="large")

with col1:
    st.markdown('<div class="arcade-card">', unsafe_allow_html=True)
    st.subheader("Scoreboard")
    s1, s2, s3 = st.columns(3)
    s1.metric("YOU", st.session_state.user_score)
    s2.metric("CPU", st.session_state.cpu_score)
    s3.metric("DRAWS", st.session_state.draws)
    st.caption(f"Rounds played: {st.session_state.rounds}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="arcade-card">', unsafe_allow_html=True)
    st.subheader("Pick your move")
    b1, b2, b3 = st.columns(3)
    clicked = None
    with b1:
        if st.button("🪨  ROCK", use_container_width=True):
            clicked = "Rock"
    with b2:
        if st.button("📜  PAPER", use_container_width=True):
            clicked = "Paper"
    with b3:
        if st.button("✂️  SCISSORS", use_container_width=True):
            clicked = "Scissors"

    if clicked:
        msg, style, u, c = play_round(clicked)
        st.markdown(f'<p class="{style}" style="font-size:18px;margin-top:12px;">{msg}</p>', unsafe_allow_html=True)
        st.write(f"**You** chose: {CHOICES[u]['emoji']} {u}  |  **CPU** chose: {CHOICES[c]['emoji']} {c}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="arcade-card">', unsafe_allow_html=True)
    st.subheader("Reset")
    r1, r2 = st.columns(2)
    with r1:
        if st.button("🔄 Reset Scores", use_container_width=True):
            reset_game(hard=False)
            st.success("Scores reset!")
    with r2:
        if st.button("🗑️ Full Reset", use_container_width=True):
            reset_game(hard=True)
            st.success("Scores & history cleared!")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="arcade-card">', unsafe_allow_html=True)
    st.subheader("Recent Rounds")
    if len(st.session_state.history) == 0:
        st.info("No rounds yet. Press a move to begin! 🕹️")
    else:
        # Render a lightweight table without pandas (keeps app dependency-free)
        for i, row in enumerate(st.session_state.history[:12], start=1):
            badge_color = "result-win" if row["outcome"] == "Win" else ("result-lose" if row["outcome"] == "Lose" else "result-draw")
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                    border:2px solid rgba(153,204,255,.35); border-radius:12px; padding:10px 12px; margin-bottom:8px;">
                    <span style="opacity:.7;">{row['time']}</span>
                    <span>{row['user']}  <span style="opacity:.6;">vs</span>  {row['cpu']}</span>
                    <strong class="{badge_color}">{row['outcome']}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;opacity:.8;">Tip: Rock beats Scissors • Scissors beat Paper • Paper beats Rock</p>',
    unsafe_allow_html=True
)
