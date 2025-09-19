import streamlit as st
import pandas as pd

st.title("🎟️ Event Registration System")

# Initialize session state for registrations
if "registrations" not in st.session_state:
    st.session_state.registrations = []

# Registration form
with st.form("registration_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    event_choice = st.selectbox("Event Choice", ["Workshop A", "Workshop B", "Networking Dinner"])
    submitted = st.form_submit_button("Register")

    if submitted:
        if name and email:
            st.session_state.registrations.append({"Name": name, "Email": email, "Event": event_choice})
            st.success(f"✅ {name} registered for {event_choice}")
        else:
            st.error("⚠️ Please fill all fields")

# Show live count
st.subheader("📊 Live Registration Count")
st.metric("Total Registrations", len(st.session_state.registrations))

# Show current registrations
if st.session_state.registrations:
    df = pd.DataFrame(st.session_state.registrations)
    st.dataframe(df, use_container_width=True)

    # Export option
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Registrations CSV",
        data=csv,
        file_name="registrations.csv",
        mime="text/csv"
    )
