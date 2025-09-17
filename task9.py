import streamlit as st

st.set_page_config(page_title="Digital Marketing Quiz", page_icon="🧠", layout="centered")

# ----------------------------
# QUIZ DATA
# ----------------------------
QUESTIONS = [
    {
        "q": "Which metric best indicates the efficiency of your ad spend in generating revenue?",
        "options": ["CTR", "CPC", "ROAS", "Impressions"],
        "answer": 2,  # ROAS
    },
    {
        "q": "In Google Ads, which match type shows for queries that include the meaning of your keyword?",
        "options": ["Broad match", "Phrase match", "Exact match", "Negative match"],
        "answer": 0,  # Broad
    },
    {
        "q": "UTM parameters are primarily used to:",
        "options": [
            "Improve page speed",
            "Track traffic sources and campaigns",
            "Enhance SEO keyword rankings",
            "Reduce bounce rate automatically",
        ],
        "answer": 1,
    },
    {
        "q": "In email marketing, which metric measures how many recipients clicked at least one link?",
        "options": ["Open Rate", "Click-Through Rate (CTR)", "Bounce Rate", "Unsubscribe Rate"],
        "answer": 1,
    },
    {
        "q": "Which KPI is most appropriate for the Consideration stage in a full-funnel strategy?",
        "options": ["Purchases", "Video ThruPlays", "Add to Cart / Lead", "Reach"],
        "answer": 2,
    },
    {
        "q": "On Meta Ads, which objective is best if your goal is online sales with the pixel set up?",
        "options": ["Awareness", "Traffic", "Engagement", "Sales (Conversions)"],
        "answer": 3,
    },
    {
        "q": "A/B testing should ideally change:",
        "options": [
            "Multiple elements at once",
            "Only one variable at a time",
            "Ad budget & audiences together",
            "Nothing; it’s random",
        ],
        "answer": 1,
    },
    {
        "q": "Which metric best reflects landing page quality and audience–message fit?",
        "options": ["Impressions", "CPC", "Bounce Rate", "Frequency"],
        "answer": 2,
    },
    {
        "q": "In GA4, which is TRUE about Events?",
        "options": [
            "Events are only pageviews",
            "Events can include parameters like value and content_type",
            "Events require Google Ads",
            "Events are deprecated",
        ],
        "answer": 1,
    },
    {
        "q": "Which bidding strategy optimizes automatically for the lowest cost per desired action?",
        "options": ["Manual CPC", "Maximize Clicks", "Target CPA", "Target Impression Share"],
        "answer": 2,
    },
]

# ----------------------------
# STATE HELPERS
# ----------------------------
def init_state():
    if "current_q" not in st.session_state:
        st.session_state.current_q = 0
    if "answers" not in st.session_state:
        st.session_state.answers = [None] * len(QUESTIONS)  # store selected index or None
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "score" not in st.session_state:
        st.session_state.score = 0

def reset_quiz():
    st.session_state.current_q = 0
    st.session_state.answers = [None] * len(QUESTIONS)
    st.session_state.submitted = False
    st.session_state.score = 0

def compute_score():
    score = 0
    for i, ans in enumerate(st.session_state.answers):
        if ans is not None and ans == QUESTIONS[i]["answer"]:
            score += 1
    st.session_state.score = score
    return score

# ----------------------------
# UI
# ----------------------------
def header():
    st.title("🧠 Digital Marketing Quiz")
    st.caption("Multiple-choice. Keep score with session state. Good luck!")

def progress():
    q_idx = st.session_state.current_q
    total = len(QUESTIONS)
    st.progress((q_idx) / total if not st.session_state.submitted else 1.0)
    if not st.session_state.submitted:
        st.write(f"**Question {q_idx + 1} of {total}**")

def render_question(q_idx: int):
    q = QUESTIONS[q_idx]
    st.write(f"### {q['q']}")

    # Make radio return index directly (0..len-1). No .index() calls, no None crash.
    options_idx = list(range(len(q["options"])))
    selected_idx = st.radio(
        "Select one:",
        options_idx,
        index=st.session_state.answers[q_idx] if st.session_state.answers[q_idx] is not None else None,
        format_func=lambda i: q["options"][i],
        key=f"radio_{q_idx}",
        label_visibility="collapsed",
    )

    # Only save if a choice was actually made (index is an int). If index=None, do nothing.
    if selected_idx is not None:
        st.session_state.answers[q_idx] = selected_idx

def go_next():
    if st.session_state.answers[st.session_state.current_q] is None:
        st.warning("Please select an answer before continuing.")
        return
    if st.session_state.current_q < len(QUESTIONS) - 1:
        st.session_state.current_q += 1

def submit_quiz():
    if st.session_state.answers[st.session_state.current_q] is None:
        st.warning("Please select an answer before submitting.")
        return
    st.session_state.submitted = True
    compute_score()

def navigation():
    cols = st.columns(3)
    with cols[0]:
        st.button("⬅️ Previous", use_container_width=True,
                  disabled=st.session_state.current_q == 0,
                  on_click=lambda: setattr(st.session_state, "current_q", st.session_state.current_q - 1))
    with cols[1]:
        st.button("🔁 Restart", on_click=reset_quiz, use_container_width=True)
    with cols[2]:
        is_last = st.session_state.current_q == len(QUESTIONS) - 1
        if not is_last:
            st.button("Next ➡️", on_click=go_next, use_container_width=True)
        else:
            st.button("✅ Submit Quiz", on_click=submit_quiz, use_container_width=True)

def show_results():
    score = st.session_state.score
    total = len(QUESTIONS)
    st.success(f"🎉 You scored **{score} / {total}**")
    st.write("---")
    st.write("### Review")
    for i, q in enumerate(QUESTIONS):
        user_idx = st.session_state.answers[i]
        correct = q["answer"]
        is_correct = (user_idx == correct)
        status = "✅ Correct" if is_correct else "❌ Incorrect"
        st.write(f"**Q{i+1}. {q['q']}**")
        st.write(f"- Your answer: {q['options'][user_idx] if user_idx is not None else '—'}")
        st.write(f"- Correct answer: **{q['options'][correct]}**")
        st.caption(status)
        st.write("")
    st.button("🔁 Try Again", on_click=reset_quiz)

# ----------------------------
# APP
# ----------------------------
def main():
    init_state()
    header()
    progress()

    if st.session_state.submitted:
        show_results()
        return

    render_question(st.session_state.current_q)
    navigation()

if __name__ == "__main__":
    main()
