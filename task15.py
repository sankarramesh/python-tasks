import streamlit as st
import random
import time
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Snake Game",
    page_icon="🐍",
    layout="centered"
)

# Game constants
GRID_SIZE = 20
CELL_SIZE = 20

# Initialize session state
def init_game():
    st.session_state.snake = [(10, 10)]  # Start in middle
    st.session_state.direction = (0, 1)  # Start moving right
    st.session_state.food = generate_food()
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.game_started = False
    st.session_state.last_move_time = time.time()

def generate_food():
    """Generate food at random position not occupied by snake"""
    while True:
        food = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
        if food not in st.session_state.snake:
            return food

def move_snake():
    """Move snake in current direction"""
    head = st.session_state.snake[0]
    new_head = (
        head[0] + st.session_state.direction[0],
        head[1] + st.session_state.direction[1]
    )
    
    # Check wall collision
    if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or 
        new_head[1] < 0 or new_head[1] >= GRID_SIZE):
        st.session_state.game_over = True
        return
    
    # Check self collision
    if new_head in st.session_state.snake:
        st.session_state.game_over = True
        return
    
    # Add new head
    st.session_state.snake.insert(0, new_head)
    
    # Check if food eaten
    if new_head == st.session_state.food:
        st.session_state.score += 1
        st.session_state.food = generate_food()
    else:
        # Remove tail if no food eaten
        st.session_state.snake.pop()

def change_direction(new_direction):
    """Change snake direction if valid"""
    current_dir = st.session_state.direction
    # Prevent reverse direction
    if (new_direction[0] != -current_dir[0] or new_direction[1] != -current_dir[1]):
        st.session_state.direction = new_direction

def create_game_board():
    """Create visual representation of the game board"""
    # Create empty grid
    grid = [['⬜' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Place snake
    for i, segment in enumerate(st.session_state.snake):
        row, col = segment
        if i == 0:  # Head
            grid[row][col] = '🟢'
        else:  # Body
            grid[row][col] = '🟩'
    
    # Place food
    food_row, food_col = st.session_state.food
    grid[food_row][food_col] = '🍎'
    
    return grid

def display_game_board(grid):
    """Display the game board using streamlit"""
    board_html = "<div style='font-size: 20px; line-height: 1; font-family: monospace;'>"
    for row in grid:
        board_html += "".join(row) + "<br>"
    board_html += "</div>"
    
    st.markdown(board_html, unsafe_allow_html=True)

# Initialize game state if not exists
if 'snake' not in st.session_state:
    init_game()

# Title and instructions
st.title("🐍 Snake Game")
st.markdown("### Use the buttons below to control the snake!")

# Game info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Score", st.session_state.score)
with col2:
    st.metric("Snake Length", len(st.session_state.snake))
with col3:
    if st.session_state.game_over:
        st.error("Game Over!")
    elif st.session_state.game_started:
        st.success("Playing...")
    else:
        st.info("Ready to Start!")

# Control buttons
st.markdown("### Controls")
control_cols = st.columns(5)

with control_cols[1]:
    if st.button("⬆️", key="up", help="Up"):
        change_direction((-1, 0))
        if not st.session_state.game_started:
            st.session_state.game_started = True

with control_cols[0]:
    if st.button("⬅️", key="left", help="Left"):
        change_direction((0, -1))
        if not st.session_state.game_started:
            st.session_state.game_started = True

with control_cols[2]:
    if st.button("➡️", key="right", help="Right"):
        change_direction((0, 1))
        if not st.session_state.game_started:
            st.session_state.game_started = True

with control_cols[1]:
    if st.button("⬇️", key="down", help="Down"):
        change_direction((1, 0))
        if not st.session_state.game_started:
            st.session_state.game_started = True

# Game control buttons
st.markdown("### Game Controls")
game_control_cols = st.columns(3)

with game_control_cols[0]:
    if st.button("🎮 Start/Resume", key="start"):
        st.session_state.game_started = True

with game_control_cols[1]:
    if st.button("⏸️ Pause", key="pause"):
        st.session_state.game_started = False

with game_control_cols[2]:
    if st.button("🔄 Restart", key="restart"):
        init_game()

# Game board container
board_container = st.container()

# Auto-move logic (only if game is started and not over)
current_time = time.time()
if (st.session_state.game_started and 
    not st.session_state.game_over and 
    current_time - st.session_state.last_move_time > 0.3):  # Move every 300ms
    
    move_snake()
    st.session_state.last_move_time = current_time

# Display game board
with board_container:
    st.markdown("### Game Board")
    grid = create_game_board()
    display_game_board(grid)

# Game over message
if st.session_state.game_over:
    st.error(f"🎮 Game Over! Final Score: {st.session_state.score}")
    st.balloons()

# Auto-refresh for continuous gameplay
if st.session_state.game_started and not st.session_state.game_over:
    time.sleep(0.1)
    st.rerun()

# Instructions
st.markdown("---")
st.markdown("""
### How to Play:
1. Click **Start/Resume** to begin the game
2. Use the arrow buttons to control the snake's direction
3. Eat the red apples (🍎) to grow and increase your score
4. Avoid hitting the walls or the snake's own body
5. Use **Pause** to pause the game and **Restart** to start over

### Legend:
- 🟢 Snake Head
- 🟩 Snake Body
- 🍎 Food
- ⬜ Empty Space

**Tip:** The snake moves automatically once started. You just need to change its direction!
""")

# Score tracking
if 'high_score' not in st.session_state:
    st.session_state.high_score = 0

if st.session_state.score > st.session_state.high_score:
    st.session_state.high_score = st.session_state.score

st.sidebar.markdown("### Game Statistics")
st.sidebar.metric("High Score", st.session_state.high_score)
st.sidebar.metric("Current Score", st.session_state.score)
st.sidebar.metric("Snake Length", len(st.session_state.snake))

# Keyboard instructions
st.sidebar.markdown("---")
st.sidebar.markdown("""
### Quick Tips:
- Snake moves automatically every 300ms
- Can't reverse direction directly
- Game ends on wall or self collision
- Each food increases score by 1
- Snake grows with each food eaten
""")