# app.py
import streamlit as st

st.set_page_config(page_title="Currency Converter 💱", page_icon="💱", layout="centered")

st.title("Currency Converter 💱")
st.caption("Static rates • No external APIs")

# --- Static rates (units per 1 USD) ---
RATES_PER_USD = {
    "USD": 1.00,     # US Dollar
    "EUR": 0.92,     # Euro
    "AED": 3.6725,   # UAE Dirham
    "INR": 83.00,    # Indian Rupee
    "CAD": 1.35,     # Canadian Dollar
    "GBP": 0.78,     # British Pound
}

SYMBOL = {
    "USD": "$",
    "EUR": "€",
    "AED": "AED ",
    "INR": "₹",
    "CAD": "C$",
    "GBP": "£",
}

CODES = list(RATES_PER_USD.keys())

def convert(amount: float, from_code: str, to_code: str) -> float:
    """Convert amount from one currency to another using USD as base."""
    if from_code == to_code:
        return amount
    usd = amount / RATES_PER_USD[from_code]     # step 1: to USD
    return usd * RATES_PER_USD[to_code]         # step 2: to target

def fmt(amount: float, code: str) -> str:
    # Show 2 decimals for most, but avoid scientific notation for big numbers
    return f"{SYMBOL.get(code, '')}{amount:,.2f}"

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    from_code = st.selectbox("From", CODES, index=CODES.index("USD"))
with col2:
    to_code = st.selectbox("To", CODES, index=CODES.index("AED"))

amount = st.number_input("Amount", min_value=0.0, value=100.0, step=1.0)

swap = st.button("🔁 Swap")
if swap:
    from_code, to_code = to_code, from_code

# --- Conversion ---
result = convert(amount, from_code, to_code)

st.subheader("Result")
st.metric(
    label=f"{fmt(amount, from_code)} {from_code} equals",
    value=f"{fmt(result, to_code)} {to_code}"
)

with st.expander("View static rates used (per 1 USD)"):
    st.write(
        {k: round(v, 6) for k, v in RATES_PER_USD.items()}
    )
st.caption("Disclaimer: For demo purposes only. Update rates in RATES_PER_USD as needed.")

