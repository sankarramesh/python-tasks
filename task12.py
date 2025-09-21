import random
import streamlit as st

# -----------------------------
# Helpers & Game Logic
# -----------------------------
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6)              # diagonals
]

def init_state():
    if "board" not in st.session_state:
        st.session_state.board = ["" for _ in range(9)]
    if "current_player" not in st.session_state:
        st.session_state.current_player = "X"
    if "winner" not in st.session_state:
        st.session_state.winner = None
    if "winning_cells" not in st.session_state:
        st.session_state.winning_cells = []
    if "mode" not in st.session_state:
        st.session_state.mode = "Two Players"
    if "game_over" not in st.session_state:
        st.session_state.game_over = False


def reset_game():
    st.session_state.board = ["" for _ in range(9)]
    st.session_state.current_player = "X"
    st.session_state.winner = None
    st.session_state.winning_cells = []
    st.session_state.game_over = False


def check_winner(board):
    """Return (winner_symbol, winning_cells) or (None, [])."""
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], [a, b, c]
    if all(cell != "" for cell in board):
        return "Draw", []
    return None, []


def available_moves(board):
    return [i for i, v in enumerate(board) if v == ""]


def make_move(index):
    if st.session_state.game_over:
        return

    # If the cell is empty, place current player's symbol
    if st.session_state.board[index] == "":
        st.session_state.board[index] = st.session_state.current_player
        winner, cells = check_winner(st.session_state.board)
        if winner:
            st.session_state.winner = winner
            st.session_state.winning_cells = cells
            st.session_state.game_over = True
            return
        # Switch player
        st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"

        # If vs Computer and it's computer's turn now
        if st.session_state.mode == "Vs Computer" and st.session_state.current_player == "O":
            computer_move()


def computer_move():
    # Random move from available cells
    empties = available_moves(st.session_state.board)
    if not empties:
        return
    choice = random.choice(empties)
    st.session_state.board[choice] = "O"

    winner, cells = check_winner(st.session_state.board)
    if winner:
        st.session_state.winner = winner
        st.session_state.winning_cells = cells
        st.session_state.game_over = True
    else:
        st.session_state.current_player = "X"


# -----------------------------
# UI Rendering
# -----------------------------
st.set_page_config(page_title="Tic‑Tac‑Toe ❌⭕", page_icon="🎮", layout="centered")
init_state()

st.title("Tic‑Tac‑Toe ❌⭕")

# Mode selector and Reset
left, right = st.columns([2, 1])
with left:
    mode = st.selectbox(
        "Mode",
        ["Two Players", "Vs Computer"],
        index=0 if st.session_state.mode == "Two Players" else 1,
        help="Play locally with a friend or vs a simple computer making random moves."
    )
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        reset_game()  # restart game when switching modes

with right:
    st.button("🔄 Reset", use_container_width=True, on_click=reset_game)

# Status banner
status = st.empty()
if st.session_state.winner == "Draw":
    status.info("It's a draw! 🤝")
elif st.session_state.winner in ("X", "O"):
    status.success(f"{st.session_state.winner} wins! 🏆")
else:
    turn_text = (
        "Your turn (X)" if st.session_state.mode == "Vs Computer" and st.session_state.current_player == "X"
        else f"{st.session_state.current_player}'s turn"
    )
    status.write(f"**{turn_text}**")

# Subtle styling to make the grid tidy and buttons roomy
st.markdown(
    """
    <style>
        /* Increase button height & font size */
        .stButton>button { 
            height: 70px; 
            font-size: 1.6rem; 
            font-weight: 700; 
        }
        /* Center the emoji labels visually */
        .stButton>button p { margin: 0 auto; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3x3 Grid of buttons
for r in range(3):
    cols = st.columns(3, gap="small")
    for c in range(3):
        idx = r * 3 + c
        cell = st.session_state.board[idx]

        # Highlight winning cells with green square emoji prefix
        display_label = cell if cell else "\u2003"  # em-space for empty boxes
        if st.session_state.winner in ("X", "O") and idx in st.session_state.winning_cells:
            display_label = f"🟩 {display_label}"

        disabled_now = st.session_state.game_over or (cell != "")

        if cols[c].button(display_label, key=f"cell_{idx}", use_container_width=True, disabled=disabled_now):
            make_move(idx)

# Legend + note
with st.expander("How it works / Notes", expanded=False):
    st.markdown(
        "- **Two Players**: X and O take turns on the same device.\n"
        "- **Vs Computer**: You are **X**; the computer plays **O** with random moves.\n"
        "- Winning line gets a green marker (🟩).\n"
        "- Use **Reset** to start a fresh game."
    )
