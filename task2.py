# app.py
from typing import Dict, List
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Expense Splitter", layout="wide")
EPS = 0.01  # rounding tolerance


# ---------- helpers ----------
def money(x: float) -> float:
    return float(f"{x:.2f}")


def init_state():
    if "people" not in st.session_state:
        st.session_state.people = []            # type: List[str]
    if "expenses" not in st.session_state:
        st.session_state.expenses = []          # type: List[Dict]
    if "currency" not in st.session_state:
        st.session_state.currency = "AED"


def compute_balances(people: List[str], expenses: List[Dict]) -> Dict[str, float]:
    """Net balance per person (positive => others owe them)."""
    balances = {p: 0.0 for p in people}
    for e in expenses:
        amount = float(e["amount"])
        paid_by = e["paid_by"]
        shares = e["shares"]  # dict: person -> owed amount
        balances[paid_by] += amount
        for p, owed in shares.items():
            balances[p] -= float(owed)
    return {p: money(v) for p, v in balances.items()}


def settle(balances: Dict[str, float]) -> List[Dict]:
    """Greedy debtor→creditor settlement."""
    debtors = [[p, -amt] for p, amt in balances.items() if amt < -EPS]
    creditors = [[p, amt] for p, amt in balances.items() if amt > EPS]
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    transfers, i, j = [], 0, 0
    while i < len(debtors) and j < len(creditors):
        d_name, d_amt = debtors[i]
        c_name, c_amt = creditors[j]
        pay = money(min(d_amt, c_amt))
        if pay > EPS:
            transfers.append({"from": d_name, "to": c_name, "amount": money(pay)})
            d_amt = money(d_amt - pay)
            c_amt = money(c_amt - pay)
            debtors[i][1] = d_amt
            creditors[j][1] = c_amt
        if d_amt <= EPS:
            i += 1
        if c_amt <= EPS:
            j += 1
    return transfers


def validate_shares(total: float, shares: Dict[str, float]) -> Dict[str, float]:
    """Scale/round shares to match total; last person absorbs rounding."""
    names = list(shares.keys())
    vals = [max(0.0, float(shares[n])) for n in names]
    s = sum(vals)
    if s == 0:
        each = total / len(vals) if vals else 0
        vals = [each] * len(vals)
        s = sum(vals)
    scale = total / s if s else 1.0
    vals = [money(v * scale) for v in vals]
    diff = money(total - sum(vals))
    if names:
        vals[-1] = money(vals[-1] + diff)
    return {n: v for n, v in zip(names, vals)}


# ---------- UI ----------
init_state()
st.title("💸 Expense Splitter (Tricount-style)")
st.caption("Add people → add expenses → see who owes whom. Fair & simple.")

with st.sidebar:
    st.header("⚙️ Setup")
    st.session_state.currency = st.selectbox(
        "Currency", ["AED", "USD", "EUR", "INR", "SAR", "GBP"], index=0
    )

    st.subheader("👥 People")
    with st.form("people_form", clear_on_submit=False):
        num = st.number_input(
            "Number of participants",
            min_value=1, max_value=20,
            value=max(2, len(st.session_state.people) or 2),
            step=1,
        )
        base = st.session_state.people or [f"User {i+1}" for i in range(int(num))]
        if len(base) < num:
            base += [f"User {i+1}" for i in range(len(base), int(num))]
        cols = st.columns(2)
        names = []
        for i in range(int(num)):
            col = cols[i % 2]
            names.append(col.text_input(f"Name {i+1}", value=base[i]))
        if st.form_submit_button("Save People"):
            clean = [n.strip() for n in names if n.strip()]
            seen, unique = set(), []
            for n in clean:
                key = n.lower()
                if key not in seen:
                    unique.append(n)
                    seen.add(key)
            st.session_state.people = unique
            st.success(f"Saved {len(unique)} participant(s).")

if not st.session_state.people:
    st.info("Add at least two people in the sidebar to begin.")
    st.stop()

# ---------- Add expense ----------
st.header("➕ Add an Expense")
with st.form("expense_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    desc = c1.text_input("Description", value="Expense")
    amount = c2.number_input(
        f"Amount ({st.session_state.currency})",
        min_value=0.0, value=0.0, step=0.01, format="%.2f"
    )
    paid_by = c3.selectbox("Paid by", st.session_state.people)

    split_mode = st.radio(
        "How to split?",
        ["Equally", "By Percent (%)", "By Shares", "By Exact Amount"],
        horizontal=True,
    )

    per_user_inputs = {}
    if split_mode == "Equally":
        st.caption("Each person will owe an equal share.")
    else:
        st.caption("Enter the split for each person:")
        cols = st.columns(3)
        for idx, p in enumerate(st.session_state.people):
            if split_mode == "By Percent (%)":
                per_user_inputs[p] = cols[idx % 3].number_input(
                    f"{p} (%)", min_value=0.0, value=0.0, step=0.1, format="%.1f", key=f"pct_{p}"
                )
            elif split_mode == "By Shares":
                per_user_inputs[p] = cols[idx % 3].number_input(
                    f"{p} (shares)", min_value=0.0, value=0.0, step=1.0, format="%.0f", key=f"share_{p}"
                )
            else:  # By Exact Amount
                per_user_inputs[p] = cols[idx % 3].number_input(
                    f"{p} ({st.session_state.currency})", min_value=0.0, value=0.0, step=0.01, format="%.2f", key=f"amt_{p}"
                )

    if st.form_submit_button("Add Expense"):
        if amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            if split_mode == "Equally":
                each = amount / len(st.session_state.people)
                shares_amounts = {p: money(each) for p in st.session_state.people}
                diff = money(amount - sum(shares_amounts.values()))
                last = st.session_state.people[-1]
                shares_amounts[last] = money(shares_amounts[last] + diff)
            elif split_mode == "By Percent (%)":
                raw = {p: float(per_user_inputs.get(p, 0.0)) for p in st.session_state.people}
                if sum(raw.values()) <= 0:
                    raw = {p: 100 / len(raw) for p in raw}
                total_pct = sum(raw.values())
                amt_map = {p: money(amount * (raw[p] / total_pct)) for p in raw}
                shares_amounts = validate_shares(amount, amt_map)
            elif split_mode == "By Shares":
                raw = {p: float(per_user_inputs.get(p, 0.0)) for p in st.session_state.people}
                if sum(raw.values()) <= 0:
                    raw = {p: 1.0 for p in raw}
                total_shares = sum(raw.values())
                amt_map = {p: money(amount * (raw[p] / total_shares)) for p in raw}
                shares_amounts = validate_shares(amount, amt_map)
            else:  # By Exact Amount
                raw = {p: float(per_user_inputs.get(p, 0.0)) for p in st.session_state.people}
                shares_amounts = validate_shares(amount, raw)

            if any(v < -EPS for v in shares_amounts.values()):
                st.error("Invalid split amounts.")
            elif money(sum(shares_amounts.values())) != money(amount):
                st.error("Split does not sum to total. Please check inputs.")
            else:
                st.session_state.expenses.append(
                    {
                        "desc": desc.strip() or "Expense",
                        "amount": money(amount),
                        "paid_by": paid_by,
                        "split_mode": split_mode,
                        "shares": shares_amounts,
                    }
                )
                st.success("Expense added!")

# ---------- expense table ----------
st.subheader("📒 Expense Log")
if not st.session_state.expenses:
    st.info("No expenses yet. Add your first one above.")
else:
    rows = []
    for e in st.session_state.expenses:
        rows.append(
            {
                "Description": e["desc"],
                f"Amount ({st.session_state.currency})": e["amount"],
                "Paid by": e["paid_by"],
                "Split": e["split_mode"],
                "Per-person": ", ".join([f"{k}: {money(v)}" for k, v in e["shares"].items()]),
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear All Expenses", type="secondary"):
            st.session_state.expenses = []
            st.rerun()
    with c2:
        if st.button("↩️ Undo Last Expense", type="secondary", disabled=(len(st.session_state.expenses) == 0)):
            st.session_state.expenses.pop()
            st.rerun()

# ---------- balances & settlement ----------
if st.session_state.expenses:
    st.header("🧮 Balances & Settlement")
    balances = compute_balances(st.session_state.people, st.session_state.expenses)

    bal_df = (
        pd.DataFrame(
            [{"Person": p, f"Net Balance ({st.session_state.currency})": money(v)} for p, v in balances.items()]
        )
        .sort_values(by=f"Net Balance ({st.session_state.currency})", ascending=False)
        .reset_index(drop=True)
    )
    st.subheader("Net Balances")
    st.dataframe(bal_df, use_container_width=True)

    transfers = settle(balances)
    st.subheader("Who pays whom")
    if not transfers:
        st.success("🎉 All settled! Nobody owes anything.")
    else:
        tdf = pd.DataFrame(transfers)
        tdf["amount"] = tdf["amount"].map(money)
        tdf.rename(columns={"from": "From", "to": "To", "amount": f"Amount ({st.session_state.currency})"}, inplace=True)
        st.dataframe(tdf, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "⬇️ Download Expenses (CSV)",
                data=pd.DataFrame(rows).to_csv(index=False).encode("utf-8"),
                file_name="expenses.csv",
                mime="text/csv",
            )
        with c2:
            st.download_button(
                "⬇️ Download Settlements (CSV)",
                data=tdf.to_csv(index=False).encode("utf-8"),
                file_name="settlements.csv",
                mime="text/csv",
            )

st.markdown("---")
st.caption(
    "Tip: Use **By Shares** for rent by room size; **By Percent** when someone covers a percentage; "
    "**By Exact Amount** for itemized receipts."
)
