import streamlit as st
from mylibrary import (
    PEAK_MULTIPLIERS, 
    TICKET_PRICES, 
    ADD_ONS, 
    calculate_base_price, 
    calculate_add_ons, 
    calculate_discounts, 
    recommend_best_deal)

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

st.subheader("Optional Perks & Add-ons")
selected_addons = st.multiselect(
    "Select Add-ons", 
    list(ADD_ONS.keys()),
    format_func=lambda x: f"{x} (${ADD_ONS[x]['price']} {'per person' if ADD_ONS[x]['per_person'] else 'flat'})"
)
st.subheader("Promotions")
promo_code = st.text_input("Enter Promo Code (Optional)", value="")

# 4. Calculation & Display
if st.button("Calculate Total & Best Deal"):
    total_visitors = adults + children
    
    if total_visitors == 0:
        st.warning("Please add at least 1 visitor to calculate pricing.")
    else:
        # Calculate components
        base_breakdown = calculate_base_price(adults, children, tier, peak_type)
        addon_data = calculate_add_ons(selected_addons, total_visitors)
        
        subtotal = base_breakdown["base_total"] + addon_data["addon_total"]
        
        discount_data = calculate_discounts(subtotal, tier, peak_type, total_visitors, promo_code)
        final_total = max(0.0, subtotal - discount_data["discount_amount"])
        
        recommendation = recommend_best_deal(adults, children, tier, peak_type, selected_addons, promo_code)