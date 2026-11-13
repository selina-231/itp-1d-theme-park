import streamlit as st
from mylibrary import PEAK_MULTIPLIERS, TICKET_PRICES, calculate_base_price

st.title("Theme Park Ticketing App")

# Ticket selection inputs
adults = st.number_input("Number of Adults", min_value=0, value=1, step=1)
children = st.number_input("Number of Children", min_value=0, value=0, step=1)
tier = st.selectbox("Select Ticket Tier / Package", list(TICKET_PRICES.keys()))
peak_type = st.selectbox("Select Season / Timing", list(PEAK_MULTIPLIERS.keys()))

# Automatic price calculation
if st.button("Calculate Base Price"):
    breakdown = calculate_base_price(adults, children, tier, peak_type)
    st.write(f"**Adult Subtotal:** ${breakdown['adult_total']:.2f}")
    st.write(f"**Child Subtotal:** ${breakdown['child_total']:.2f}")
    st.success(f"**Total Base Price:** ${breakdown['base_total']:.2f}")
