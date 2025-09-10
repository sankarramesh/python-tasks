import streamlit as st

# Title
st.title("Simple Calculator App")

# Input fields
st.header("Enter your numbers")
numbers = st.text_input("Enter numbers separated by commas (e.g. 10, 20, 30):")

# Operator selection
operation = st.selectbox("Select operation", ["Addition", "Subtraction", "Multiplication", "Division"])

# Calculate when button is clicked
if st.button("Calculate"):
    try:
        # Convert input string to list of floats
        values = [float(x.strip()) for x in numbers.split(",")]

        if not values:
            st.error("Please enter at least one number.")
        else:
            result = None
            if operation == "Addition":
                result = sum(values)
            elif operation == "Subtraction":
                result = values[0]
                for num in values[1:]:
                    result -= num
            elif operation == "Multiplication":
                result = 1
                for num in values:
                    result *= num
            elif operation == "Division":
                result = values[0]
                try:
                    for num in values[1:]:
                        result /= num
                except ZeroDivisionError:
                    st.error("Error: Division by zero is not allowed.")
                    result = None

            if result is not None:
                st.success(f"The result of {operation.lower()} is: {result}")

    except ValueError:
        st.error("Please enter valid numbers separated by commas.")
