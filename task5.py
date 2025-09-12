import streamlit as st

st.set_page_config(page_title="All-in-One Unit Converter", page_icon="🔄", layout="centered")
st.title("🔄 All-in-One Unit Converter")

st.caption(
    "Switch the conversion type below. Results update instantly. "
    "Note: Currency rates here are static examples; adjust with a custom rate if needed."
)

conv_type = st.selectbox(
    "Choose conversion type",
    ["Currency", "Temperature", "Length", "Weight"],
    index=0
)

st.divider()

# ---------- Helpers ----------
def convert_via_factor(value, from_unit, to_unit, unit_to_base_factor):
    """Generic factor-based conversion (linear units): normalize to base, then to target."""
    if from_unit not in unit_to_base_factor or to_unit not in unit_to_base_factor:
        return None
    base_value = value * unit_to_base_factor[from_unit]
    return base_value / unit_to_base_factor[to_unit]

def convert_currency(amount, from_code, to_code, usd_per_unit, custom_rate=None):
    """
    Currency conversion using USD as a bridge unless a custom_rate (per 1 FROM in TO) is provided.
    usd_per_unit: dict of USD value per 1 unit of currency (i.e., USD = amount * usd_per_unit[currency])
    """
    if custom_rate is not None:
        return amount * custom_rate

    if from_code not in usd_per_unit or to_code not in usd_per_unit:
        return None

    # amount_in_usd = amount * USD per FROM
    amount_in_usd = amount * usd_per_unit[from_code]
    # amount_in_to = USD / (USD per TO)
    return amount_in_usd / usd_per_unit[to_code]

def fmt_num(x):
    try:
        # nice formatting for large/small numbers
        if abs(x) >= 1e6 or (abs(x) > 0 and abs(x) < 1e-3):
            return f"{x:.6g}"
        return f"{x:,.6f}".rstrip('0').rstrip('.')
    except Exception:
        return str(x)

# ---------- Currency ----------
if conv_type == "Currency":
    st.subheader("💱 Currency")

    # Example static USD-per-unit mapping (approximate; AED is pegged ~3.6725 AED per USD).
    # USD per 1 unit:
    usd_per_unit = {
        "USD": 1.0,
        "AED": 1.0 / 3.6725,  # ≈ 0.272294 USD per AED
        "INR": 1.0 / 83.0,    # ≈ 0.012048 USD per INR (example)
        # Add more if you wish, following the same pattern.
    }

    # Few-shot defaults: AED -> INR
    cur_from = st.selectbox("From currency", ["AED", "USD", "INR"], index=0, key="cur_from")
    cur_to   = st.selectbox("To currency",   ["INR", "AED", "USD"], index=0, key="cur_to")

    col_amount, col_rate = st.columns([2, 1])
    with col_amount:
        amount = st.number_input("Amount", min_value=0.0, value=100.0, step=1.0, key="cur_amt")
    with col_rate:
        use_custom = st.checkbox("Use custom rate", value=False, help="If on, enter the rate below.")
        custom_rate = None
        if use_custom:
            custom_rate = st.number_input(
                f"Rate (1 {cur_from} = ? {cur_to})",
                min_value=0.0, value=3.0 if (cur_from, cur_to) == ("USD", "AED") else 22.0,
                step=0.0001, format="%.6f"
            )

    result = convert_currency(amount, cur_from, cur_to, usd_per_unit, custom_rate=custom_rate)
    if result is None:
        st.error("Unsupported currency combination.")
    else:
        st.success(f"**{fmt_num(amount)} {cur_from} = {fmt_num(result)} {cur_to}**")

    with st.expander("Quick examples"):
        st.markdown("- AED → INR (default)")
        st.markdown("- USD → AED (toggle From=USD, To=AED)")

# ---------- Temperature ----------
elif conv_type == "Temperature":
    st.subheader("🌡️ Temperature")

    # Few-shot: Celsius -> Fahrenheit
    t_from = st.selectbox("From", ["Celsius (°C)", "Fahrenheit (°F)"], index=0, key="t_from")
    t_to   = st.selectbox("To",   ["Fahrenheit (°F)", "Celsius (°C)"], index=0, key="t_to")

    temp_value = st.number_input("Temperature value", value=25.0, step=0.1, format="%.2f")

    def temp_convert(value, f_unit, t_unit):
        if f_unit.startswith("Celsius") and t_unit.startswith("Fahrenheit"):
            return value * 9.0/5.0 + 32.0
        elif f_unit.startswith("Fahrenheit") and t_unit.startswith("Celsius"):
            return (value - 32.0) * 5.0/9.0
        else:
            return value  # same unit

    t_result = temp_convert(temp_value, t_from, t_to)
    st.success(f"**{fmt_num(temp_value)} {t_from.split()[0]} = {fmt_num(t_result)} {t_to.split()[0]}**")

    with st.expander("Formula"):
        st.code("°F = (°C × 9/5) + 32\n°C = (°F − 32) × 5/9")

# ---------- Length ----------
elif conv_type == "Length":
    st.subheader("📏 Length (and Area*)")

    st.caption(
        "Length units: m, cm, mm, ft • Area units: sqm, sqft\n"
        "*Note: You can only convert length↔length or area↔area. Mixed conversions are invalid."
    )

    length_units = ["m", "cm", "mm", "ft"]
    area_units   = ["sqm", "sqft"]
    all_units    = length_units + area_units

    # Few-shot default: meter -> centimeter
    l_from = st.selectbox("From unit", all_units, index=all_units.index("m"))
    l_to   = st.selectbox("To unit",   all_units, index=all_units.index("cm"))

    value = st.number_input("Value", min_value=0.0, value=1.0, step=0.1)

    # Factors to base units
    length_to_m = {"m": 1.0, "cm": 0.01, "mm": 0.001, "ft": 0.3048}
    area_to_sqm = {"sqm": 1.0, "sqft": 0.09290304}

    def is_length(u): return u in length_units
    def is_area(u):   return u in area_units

    if (is_length(l_from) and is_length(l_to)):
        out = convert_via_factor(value, l_from, l_to, length_to_m)
        st.success(f"**{fmt_num(value)} {l_from} = {fmt_num(out)} {l_to}**")
    elif (is_area(l_from) and is_area(l_to)):
        out = convert_via_factor(value, l_from, l_to, area_to_sqm)
        st.success(f"**{fmt_num(value)} {l_from} = {fmt_num(out)} {l_to}**")
    else:
        st.error("Invalid conversion: cannot convert between length and area units.")

    with st.expander("Tips & extras"):
        st.markdown("- Lengths: m, cm, mm, ft")
        st.markdown("- Areas: sqm, sqft")
        st.markdown("- Example: **m → cm** (default)")

# ---------- Weight ----------
elif conv_type == "Weight":
    st.subheader("⚖️ Weight / Mass")

    # Few-shot defaults (common): kilogram -> gram
    w_from = st.selectbox("From unit", ["kg", "g", "mg", "lb"], index=0)
    w_to   = st.selectbox("To unit",   ["g", "kg", "mg", "lb"], index=1)

    w_value = st.number_input("Value", min_value=0.0, value=1.0, step=0.1)

    # Base is kilogram
    to_kg = {
        "kg": 1.0,
        "g": 0.001,
        "mg": 1e-6,
        "lb": 0.45359237,
    }

    w_result = convert_via_factor(w_value, w_from, w_to, to_kg)
    if w_result is None:
        st.error("Unsupported unit.")
    else:
        st.success(f"**{fmt_num(w_value)} {w_from} = {fmt_num(w_result)} {w_to}**")
