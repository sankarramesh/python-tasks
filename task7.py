import streamlit as st
import pandas as pd
from datetime import date, datetime
from pathlib import Path

st.set_page_config(page_title="Gym Workout Logger 🏋️", page_icon="🏋️", layout="wide")

DATA_FILE = Path("workouts.csv")

# ---------- Utilities ----------
def load_data() -> pd.DataFrame:
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        # Ensure dtypes
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.date
        expected = ["date", "exercise", "sets", "reps", "weight_kg", "volume"]
        for col in expected:
            if col not in df.columns:
                df[col] = pd.Series(dtype="object")
        # clean types
        df["sets"] = pd.to_numeric(df["sets"], errors="coerce").fillna(0).astype(int)
        df["reps"] = pd.to_numeric(df["reps"], errors="coerce").fillna(0).astype(int)
        df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(0.0)
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
        return df[["date", "exercise", "sets", "reps", "weight_kg", "volume"]]
    else:
        return pd.DataFrame(columns=["date", "exercise", "sets", "reps", "weight_kg", "volume"])

def save_data(df: pd.DataFrame):
    df_to_save = df.copy()
    df_to_save["date"] = pd.to_datetime(df_to_save["date"]).dt.strftime("%Y-%m-%d")
    df_to_save.to_csv(DATA_FILE, index=False)

def ensure_state():
    if "df" not in st.session_state:
        st.session_state.df = load_data()

ensure_state()

# ---------- Sidebar: Add Entry ----------
with st.sidebar:
    st.header("➕ Log Workout")
    log_date = st.date_input("Date", value=date.today())
    # Suggest last used exercises
    existing_exercises = sorted(st.session_state.df["exercise"].dropna().unique().tolist())
    exercise_mode = st.radio("Exercise input", ["Pick from list", "Type new"], horizontal=True)
    if exercise_mode == "Pick from list" and existing_exercises:
        exercise = st.selectbox("Exercise", existing_exercises, index=0)
    else:
        exercise = st.text_input("Exercise", placeholder="e.g., Bench Press")

    colA, colB, colC = st.columns(3)
    with colA:
        sets = st.number_input("Sets", min_value=1, max_value=50, value=3, step=1)
    with colB:
        reps = st.number_input("Reps (per set)", min_value=1, max_value=100, value=10, step=1)
    with colC:
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=1000.0, value=40.0, step=2.5)

    add_btn = st.button("Add to Log", use_container_width=True, type="primary")

    if add_btn:
        if not exercise.strip():
            st.warning("Please enter an exercise name.")
        else:
            volume = sets * reps * float(weight)
            new_row = {
                "date": log_date,
                "exercise": exercise.strip(),
                "sets": int(sets),
                "reps": int(reps),
                "weight_kg": float(weight),
                "volume": float(volume),
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"Logged: {exercise} — {sets}×{reps} @ {weight}kg (Volume: {int(volume)})")

# ---------- Main: History & Analytics ----------
st.title("Gym Workout Logger 🏋️")
st.caption("Log exercises (sets, reps, weight), view history, and track weekly progress.")

# Filters
with st.expander("🔎 Filters", expanded=False):
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        unique_ex = ["All"] + sorted(st.session_state.df["exercise"].dropna().unique().tolist())
        selected_ex = st.selectbox("Exercise", unique_ex, index=0)
    with col2:
        min_date = st.session_state.df["date"].min() if not st.session_state.df.empty else None
        max_date = st.session_state.df["date"].max() if not st.session_state.df.empty else None
        date_range = st.date_input(
            "Date range",
            value=(min_date or date.today(), max_date or date.today()),
        )
    with col3:
        st.markdown("Use filters to narrow your view. Weekly chart updates automatically.")

# Apply filters
df = st.session_state.df.copy()
if not df.empty:
    # Normalize date_range value
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d, end_d = (df["date"].min(), df["date"].max())

    mask = (pd.to_datetime(df["date"]) >= pd.to_datetime(start_d)) & (pd.to_datetime(df["date"]) <= pd.to_datetime(end_d))
    if selected_ex != "All":
        mask = mask & (df["exercise"] == selected_ex)
    df_filtered = df.loc[mask].sort_values("date", ascending=False)
else:
    df_filtered = df

# ---------- Editable History Table ----------
st.subheader("📒 Workout History")
if df_filtered.empty:
    st.info("No entries yet. Add your first workout from the sidebar!")
else:
    edited = st.data_editor(
        df_filtered.reset_index(drop=True),
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "date": st.column_config.DateColumn("date", format="YYYY-MM-DD"),
            "exercise": st.column_config.TextColumn("exercise"),
            "sets": st.column_config.NumberColumn("sets", min_value=0, step=1),
            "reps": st.column_config.NumberColumn("reps", min_value=0, step=1),
            "weight_kg": st.column_config.NumberColumn("weight_kg", min_value=0.0, step=0.5, help="Weight in kilograms"),
            "volume": st.column_config.NumberColumn("volume", min_value=0.0, step=1.0, help="sets × reps × weight"),
        },
        key="history_editor",
    )

    # Recompute volume if any inputs changed
    edited["volume"] = (edited["sets"].astype(int) * edited["reps"].astype(int) * edited["weight_kg"].astype(float))

    col_save, col_dl, col_clear = st.columns([1,1,1])
    with col_save:
        if st.button("💾 Save Changes", use_container_width=True):
            # Merge edits back into full df (respect filters)
            # We replace the filtered slice with edited rows by matching on original indices after sorting
            # Easiest safe route: recompute full df using unfiltered + edited based on current mask
            full = st.session_state.df.copy()
            full_mask = (pd.to_datetime(full["date"]) >= pd.to_datetime(start_d)) & (pd.to_datetime(full["date"]) <= pd.to_datetime(end_d))
            if selected_ex != "All":
                full_mask = full_mask & (full["exercise"] == selected_ex)
            # Replace rows under full_mask with edited (align columns)
            full_subset = edited[["date","exercise","sets","reps","weight_kg","volume"]].copy()
            full.loc[full_mask, ["date","exercise","sets","reps","weight_kg","volume"]] = full_subset.values
            st.session_state.df = full
            save_data(st.session_state.df)
            st.success("Saved!")
    with col_dl:
        st.download_button(
            "⬇️ Download CSV",
            data=st.session_state.df.to_csv(index=False),
            file_name="workouts.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_clear:
        if st.button("🗑️ Clear All (danger)", type="secondary", use_container_width=True):
            st.session_state.df = pd.DataFrame(columns=["date", "exercise", "sets", "reps", "weight_kg", "volume"])
            save_data(st.session_state.df)
            st.warning("All logs cleared.")

# ---------- Weekly Progress (Training Volume) ----------
st.subheader("📈 Weekly Progress (Total Volume)")
if st.session_state.df.empty:
    st.info("No data yet to plot. Log some workouts!")
else:
    df_plot = st.session_state.df.copy()
    df_plot["date"] = pd.to_datetime(df_plot["date"])
    df_plot["week"] = df_plot["date"] - pd.to_timedelta(df_plot["date"].dt.weekday, unit="D")  # start of week (Mon)

    # Option to group by exercise or overall
    grp_mode = st.radio("Group by", ["Overall", "By Exercise"], horizontal=True)
    if grp_mode == "Overall":
        weekly = df_plot.groupby("week", as_index=False)["volume"].sum().rename(columns={"volume": "total_volume"})
        st.line_chart(weekly.set_index("week")["total_volume"])
    else:
        weekly = df_plot.groupby(["week", "exercise"], as_index=False)["volume"].sum()
        # Pivot for multi-line chart
        pivoted = weekly.pivot(index="week", columns="exercise", values="volume").fillna(0)
        st.line_chart(pivoted)

# ---------- Tips ----------
with st.expander("💡 Tips"):
    st.markdown(
        """
- **Volume** = sets × reps × weight. Higher weekly volume typically indicates progress for hypertrophy.
- Use filters to inspect specific exercises and see how volume trends over time.
- Download your CSV for backup or analysis elsewhere.
"""
    )
