import streamlit as st

# App title
st.title("Simple Greeting App")

# Input fields
name = st.text_input("Enter your name:")
age = st.slider("Select your age:", 1, 100, 25)

# Submit button
if st.button("Submit"):
    st.success(f"Hello, {name}! You are {age} years old.")
    