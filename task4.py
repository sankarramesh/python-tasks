import streamlit as st

# App Title
st.title("BMI Calculator 🧮")

# Get user inputs
height_cm = st.text_input("Enter your height (in cm):")
weight_kg = st.text_input("Enter your weight (in kg):")

if height_cm and weight_kg:
    try:
        # Convert inputs to float
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)

        # Convert height to meters
        height_m = height_cm / 100

        # BMI calculation
        bmi = weight_kg / (height_m ** 2)

        # Determine BMI category
        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 25:
            category = "Normal weight"
        elif 25 <= bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"

        # Show results
        st.success(f"Your BMI is **{bmi:.2f}**")
        st.info(f"Category: **{category}**")

    except ValueError:
        st.error("Please enter valid numbers for height and weight.")
