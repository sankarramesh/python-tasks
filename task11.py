# cookie_world_app.py
import io
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

# -----------------------------
# App Config & Styling
# -----------------------------
st.set_page_config(page_title="Cookie World • Orders & Billing", page_icon="🍪", layout="wide")

CUSTOM_CSS = """
<style>
/* Background and global text */
.stApp {
  background: #FFF7E6; /* warm cream */
  color: #2c3e50;      /* dark readable text */
  padding-top: 1.5rem; /* space from Streamlit top bar */
}

/* Add more space below Streamlit toolbar */
.block-container {
  padding-top: 3rem !important;
}

/* Global text color */
h1, h2, h3, h4, h5, h6, p, span, div {
  color: #2c3e50 !important;
}

/* Title styling */
h1 span.title {
  background: linear-gradient(90deg, #7B1FA2, #F39C12);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Center header section */
.header-container {
  text-align: center;
  margin-bottom: 1.5rem;
}
.header-container h1 {
  margin-bottom: 0.4rem;
}
.header-container p {
  font-size: 1rem;
  color: #5a5a5a !important;
  margin-top: 0.2rem;
}

/* Cards */
.cookie-card, .summary-box {
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
  border: 1px solid #F6D68B;
}

/* Section wrappers */
.cookie-card { padding: 12px 14px; }
.summary-box { padding: 14px 16px; border-color: #D6C7F7; }

/* Menu header and rows */
.menu-header { font-weight: 700; font-size: 1.05rem; margin: 0 0 6px 0; color: #7B1FA2; }
.item-row {
  display: grid;
  grid-template-columns: 1fr 120px 140px;
  gap: 10px;
  align-items: center;
  background: #FFFDF9;
  border: 1px solid #F0E1B9;
  border-radius: 10px;
  padding: 8px 10px;
  margin: 6px 0;
}
.item-name { font-weight: 600; }
.item-price { font-weight: 700; color: #13795B; text-align: right; }

/* Unit pill */
.badge {
  background: #F39C12;
  color: #fff;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 0.72rem;
  margin-left: 8px;
}

/* Compact number inputs */
div[data-baseweb="input"] input {
  padding-top: 6px !important;
  padding-bottom: 6px !important;
}
div.stNumberInput > label { display: none; }
div.stNumberInput { margin: 0 !important; }

/* Buttons & HR */
hr.pretty { border: none; height: 2px; background: linear-gradient(90deg, #7B1FA244, #F39C1244); margin: 10px 0; }
.stButton>button {
  background: linear-gradient(90deg, #7B1FA2, #F39C12);
  color: #fff;
  border: 0;
  border-radius: 10px;
  padding: 8px 14px;
  font-weight: 700;
}
.stDownloadButton button {
  border-radius: 10px;
  padding: 8px 12px;
  font-weight: 600;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
RESTAURANT_NAME = "Cookie World"
VAT_RATE = 0.05  # 5% UAE VAT

MENU = [
    {"name": "Classic Choco chip",              "unit": "pcs", "price": 16},
    {"name": "Pistacho Cookie",                 "unit": "pcs", "price": 16},
    {"name": "Biscoff Cookie",                  "unit": "pcs", "price": 16},
    {"name": "Double choco Cookie",             "unit": "pcs", "price": 16},
    {"name": "Sugar free Chocochip cookie",     "unit": "pcs", "price": 18},
    {"name": "Millets Cookie (Gluten free)",    "unit": "pcs", "price": 18},
    {"name": "Coffee bean cookies",             "unit": "kg",  "price": 25},
    {"name": "Masala Cookies",                  "unit": "kg",  "price": 25},
    {"name": "Protein Crackers",                "unit": "kg",  "price": 30},
    {"name": "Brownies",                        "unit": "kg",  "price": 40},
]

# -----------------------------
# Helpers
# -----------------------------
def ensure_state():
    if "quantities" not in st.session_state:
        st.session_state.quantities = {item["name"]: 0 for item in MENU}
    if "buyer_name" not in st.session_state:
        st.session_state.buyer_name = ""
    if "invoice_counter" not in st.session_state:
        st.session_state.invoice_counter = 1001

def calc_totals(quantities: dict):
    rows = []
    for item in MENU:
        q = int(quantities.get(item["name"], 0) or 0)
        if q > 0:
            amount = q * item["price"]
            rows.append({
                "Item": item["name"],
                "Qty": q,
                "Unit": item["unit"],
                "Unit Price (AED)": item["price"],
                "Line Total (AED)": amount
            })
    df = pd.DataFrame(rows)
    subtotal = float(df["Line Total (AED)"].sum()) if not df.empty else 0.0
    vat = round(subtotal * VAT_RATE, 2)
    total = round(subtotal + vat, 2)
    return df, round(subtotal, 2), vat, total

def generate_csv(invoice_meta: dict, df: pd.DataFrame, subtotal: float, vat: float, total: float) -> bytes:
    meta_lines = [
        f"Restaurant,{invoice_meta['restaurant']}",
        f"Invoice No.,{invoice_meta['invoice_no']}",
        f"Date/Time,{invoice_meta['datetime']}",
        f"Customer,{invoice_meta['customer'] or 'Walk-in'}",
        "",
    ]
    items_csv = df.to_csv(index=False)
    totals_lines = [
        "",
        f"Subtotal (AED),{subtotal}",
        f"VAT 5% (AED),{vat}",
        f"Grand Total (AED),{total}",
    ]
    full = "\n".join(meta_lines) + items_csv + "\n".join(totals_lines)
    return full.encode("utf-8")

# -----------------------------
# UI
# -----------------------------
ensure_state()

# Centered header
st.markdown(
    f"""
    <div class="header-container">
        <h1>🍪 <span class="title">{RESTAURANT_NAME}</span></h1>
        <p>Sweet treats, happy hearts. Build your order below and generate your bill instantly.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    with st.expander("👤 Customer (optional)", expanded=False):
        st.session_state.buyer_name = st.text_input("Customer Name", value=st.session_state.buyer_name, placeholder="Walk-in")

    st.markdown("### 🧾 Create Your Order")
    st.markdown("<div class='cookie-card'>", unsafe_allow_html=True)
    st.markdown("<div class='menu-header'>Select quantities for each item</div>", unsafe_allow_html=True)

    form = st.form("order_form", clear_on_submit=False)
    for item in MENU:
        name_html = (
            f"<span class='item-name'>{item['name']}</span>"
            f"<span class='badge'>{item['unit']}</span>"
        )
        with form.container():
            st.markdown(
                f"<div class='item-row'>"
                f"  <div>{name_html}</div>"
                f"  <div class='item-price'>AED {item['price']}</div>",
                unsafe_allow_html=True
            )
            c1, c2, c3 = st.columns([1,1,1])
            with c3:
                st.session_state.quantities[item["name"]] = st.number_input(
                    "Qty",
                    min_value=0,
                    max_value=500,
                    value=int(st.session_state.quantities.get(item["name"], 0)),
                    step=1,
                    key=f"qty_{item['name']}",
                    label_visibility="collapsed",
                )
            st.markdown("</div>", unsafe_allow_html=True)

    form.form_submit_button("🛒 Add / Update Cart")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("### 💳 Bill Summary")
    df, subtotal, vat, total = calc_totals(st.session_state.quantities)

    st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
    if df.empty:
        st.info("No items selected yet. Pick your favorites on the left 🍫")
    else:
        st.dataframe(
            df.style.format({"Unit Price (AED)": "{:.2f}", "Line Total (AED)": "{:.2f}"}),
            use_container_width=True
        )
        st.markdown("<hr class='pretty' />", unsafe_allow_html=True)
        st.write(f"**Subtotal (AED):** {subtotal:,.2f}")
        st.write(f"**VAT (5%) (AED):** {vat:,.2f} _(as per UAE law)_")
        st.markdown(f"<div class='total-line'>Grand Total (AED): {total:,.2f}</div>", unsafe_allow_html=True)

        # Invoice meta
        tz = ZoneInfo("Asia/Dubai")
        now = datetime.now(tz)
        invoice_no = f"CW-{now.strftime('%Y%m%d')}-{st.session_state.invoice_counter}"
        invoice_meta = {
            "restaurant": RESTAURANT_NAME,
            "invoice_no": invoice_no,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "customer": (st.session_state.buyer_name or "").strip(),
        }

        st.markdown("<hr class='pretty' />", unsafe_allow_html=True)
        st.caption(f"Invoice No.: **{invoice_no}**  |  Date/Time: **{invoice_meta['datetime']}**")

        csv_bytes = generate_csv(invoice_meta, df, subtotal, vat, total)
        st.download_button(
            "📄 Download CSV",
            data=csv_bytes,
            file_name=f"{invoice_no}.csv",
            mime="text/csv",
            key="dl_csv"
        )

        st.session_state.invoice_counter += 1

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<small style='color:#6c757d; display:block; text-align:center;'>Designed with ❤️ for Cookie World • VAT 5% • Prices in AED</small>", unsafe_allow_html=True)
