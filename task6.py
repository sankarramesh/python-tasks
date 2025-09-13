# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import time

st.set_page_config(page_title="Water Intake Tracker", page_icon="💧", layout="centered")

# ---------- THEME / STYLES ----------
st.markdown("""
    <style>
      .big-num {font-size: 42px; font-weight: 800; line-height: 1; margin-top: 8px;}
      .muted {color: #6c757d;}
      .card { border-radius: 16px; padding: 18px 18px 12px 18px; border: 1px solid rgba(0,0,0,0.08); background: rgba(255,255,255,0.6); }
      .accent {color:#3B82F6;}
      .btn-row button {margin-right: .5rem;}
      .goal-line {border-top: 2px dashed #999; margin: 8px 0 0;}
    </style>
""", unsafe_allow_html=True)

# ---------- INITIAL STATE ----------
if "log" not in st.session_state:
    st.session_state.log = {}
if "last_animate_from" not in st.session_state:
    st.session_state.last_animate_from = 0

# ---------- CONSTANTS ----------
DEFAULT_GOAL_ML = 4000  # 4 liters

# ---------- SIDEBAR ----------
st.sidebar.title("💧 Hydration Settings")
goal_ml = st.sidebar.number_input("Daily goal (ml)", min_value=500, max_value=10000, step=100, value=DEFAULT_GOAL_ML)
st.sidebar.caption("Tip: 4,000 ml = 4 liters")

if st.sidebar.button("Reset today's intake"):
    st.session_state.log[date.today().isoformat()] = 0
    st.session_state.last_animate_from = 0
    st.sidebar.success("Today’s intake reset.")

# ---------- HEADER ----------
st.title("💧 Water Intake Tracker")
st.caption("Track your daily water and see your weekly hydration at a glance.")

# ---------- INPUT CARD ----------
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1,1])
    with c1:
        entry_date = st.date_input("Date", value=date.today())
    with c2:
        add_ml = st.number_input("Add water (ml)", min_value=50, step=50, value=250)

    st.markdown('<div class="btn-row">', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    quicks = {b1:200, b2:250, b3:300, b4:500}
    labels = {200:"+200 ml", 250:"+250 ml", 300:"+300 ml", 500:"+500 ml"}

    clicked_quick = None
    for btn, amt in quicks.items():
        with btn:
            if st.button(labels[amt], use_container_width=True):
                clicked_quick = amt

    add_clicked = st.button("Add intake", type="primary")

    today_key = entry_date.isoformat()
    current_ml = st.session_state.log.get(today_key, 0)
    new_ml = current_ml

    added_amt = None
    if clicked_quick:
        added_amt = clicked_quick
        new_ml = current_ml + clicked_quick
    elif add_clicked:
        added_amt = add_ml
        new_ml = current_ml + add_ml

    if added_amt:
        st.session_state.log[today_key] = new_ml
        st.toast(f"Added {added_amt} ml for {entry_date.strftime('%b %d')}", icon="💧")
        st.session_state.last_animate_from = current_ml

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TODAY SUMMARY ----------
today_key = date.today().isoformat()
today_total = st.session_state.log.get(today_key, 0)
pct = min(today_total / goal_ml, 1.0)
remaining = max(goal_ml - today_total, 0)
liters_today = today_total / 1000

st.subheader("Today")
box1, box2, box3 = st.columns(3)
with box1:
    st.markdown("Intake", help="Total water logged today.")
    st.markdown(f'<div class="big-num accent">{liters_today:.2f} L</div>', unsafe_allow_html=True)
with box2:
    st.markdown("Goal")
    st.markdown(f'<div class="big-num">{goal_ml/1000:.2f} L</div>', unsafe_allow_html=True)
with box3:
    st.markdown("Remaining")
    st.markdown(f'<div class="big-num">{remaining/1000:.2f} L</div>', unsafe_allow_html=True)

# Animated progress bar
progress_placeholder = st.empty()
animate_from = st.session_state.last_animate_from if st.session_state.last_animate_from <= today_total else today_total
animate_to = today_total
animate_steps = max(int(abs(animate_to - animate_from) / 100), 1)

if animate_to > animate_from:
    for step in range(animate_steps + 1):
        val = animate_from + (animate_to - animate_from) * (step / animate_steps)
        progress = min(val / goal_ml, 1.0)
        progress_placeholder.progress(progress, text=f"Daily progress: {int(progress*100)}%")
        time.sleep(0.01)
    st.session_state.last_animate_from = today_total
else:
    progress_placeholder.progress(pct, text=f"Daily progress: {int(pct*100)}%")

if today_total >= goal_ml:
    st.success("Goal reached — great job staying hydrated! 🎉")
    st.balloons()

# ---------- WEEKLY CHART ----------
st.subheader("This Week")

def last_7_days():
    return [date.today() - timedelta(days=i) for i in range(6, -1, -1)]

week_days = last_7_days()
records = []
for d in week_days:
    key = d.isoformat()
    ml = st.session_state.log.get(key, 0)
    records.append({"date": d, "ml": ml, "liters": ml/1000})

df = pd.DataFrame(records)

# ✅ Convert to datetime so .dt works (this fixes your error)
df["date"] = pd.to_datetime(df["date"])

# Streaks (days where goal met)
streak = 0
for d in reversed(week_days):
    if st.session_state.log.get(d.isoformat(), 0) >= goal_ml:
        streak += 1
    else:
        break

# Interactive Plotly bar + goal line
fig = go.Figure()
fig.add_bar(
    x=df["date"].dt.strftime("%a %d"),
    y=df["liters"],
    name="Intake (L)",
    hovertemplate="%{x}<br>%{y:.2f} L<extra></extra>"
)
fig.add_trace(go.Scatter(
    x=df["date"].dt.strftime("%a %d"),
    y=[goal_ml/1000]*len(df),
    mode="lines",
    name="Daily Goal",
    line=dict(dash="dash", width=2),
    hovertemplate="Goal: %{y:.2f} L<extra></extra>"
))
fig.update_layout(
    yaxis_title="Liters",
    xaxis_title="Day",
    bargap=0.2,
    hovermode="x unified",
    height=380,
    margin=dict(l=10, r=10, t=10, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# ---------- EXTRA INSIGHTS ----------
met_days = int((df["ml"] >= goal_ml).sum())
avg_liters = float(df["liters"].mean()) if len(df) else 0.0

i1, i2, i3 = st.columns(3)
with i1:
    st.metric("Days Met Goal", f"{met_days}/7")
with i2:
    st.metric("Avg / Day (L)", f"{avg_liters:.2f}")
with i3:
    st.metric("Current Streak", f"{streak} days")

st.markdown("---")
with st.expander("📦 Data & Backup"):
    df_export = pd.DataFrame(
        [{"date": k, "ml": v} for k, v in sorted(st.session_state.log.items())]
    )
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button("Download log as CSV", csv, "water_log.csv", "text/csv")

    up = st.file_uploader("Restore/upload log (CSV with columns: date, ml)", type=["csv"])
    if up is not None:
        try:
            imported = pd.read_csv(up)
            imported["date"] = pd.to_datetime(imported["date"]).dt.date
            merged = {}
            for _, row in imported.iterrows():
                k = row["date"].isoformat()
                merged[k] = merged.get(k, 0) + int(row["ml"])
            st.session_state.log.update(merged)
            st.success("Log imported successfully.")
        except Exception as e:
            st.error(f"Import failed: {e}")

st.caption("Stay consistent. Small sips add up! 💙")
