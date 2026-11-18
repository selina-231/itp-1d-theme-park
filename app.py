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

# PERSON 3: Show package prices before customers select their tickets
st.subheader("Ticket Prices")

# Create a list to store each package's prices
price_rows = []

for package, prices in TICKET_PRICES.items():
    row = {"Package": package}

    # Apply each timing multiplier to the adult and child prices
    for timing, multiplier in PEAK_MULTIPLIERS.items():
        row[f"{timing} - Adult"] = f"${prices['adult'] * multiplier:.2f}"
        row[f"{timing} - Child"] = f"${prices['child'] * multiplier:.2f}"

    price_rows.append(row)

# Display the price comparison table
st.table(price_rows)
st.caption("Prices are per person, before add-ons and discounts.")

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

# PERSON 3: Record the current selections to detect changes to the order
current_selection = (
    adults,
    children,
    tier,
    peak_type,
    tuple(selected_addons),
    promo_code,
)

# Clear the previous calculation if any selection has changed.
# This makes the customer recalculate the total before checking out.
if st.session_state.get("calculated_selection") != current_selection:
    st.session_state.pop("calculated_order", None)

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

        # PERSON 3: Build the itemized bill using the calculated prices
        order_rows = [
            {
                "Item": f"Adult tickets × {adults}",
                "Amount": f"${base_breakdown['adult_total']:.2f}",
            },
            {
                "Item": f"Child tickets × {children}",
                "Amount": f"${base_breakdown['child_total']:.2f}",
            },
        ]

        # Add a separate row for each selected add-on.
        # Per-person add-ons use the total number of visitors.
        for name, cost in addon_data["breakdown"].items():
            quantity = total_visitors if ADD_ONS[name]["per_person"] else 1

            order_rows.append({
                "Item": f"{name} × {quantity}",
                "Amount": f"${cost:.2f}",
            })

        # Format the discount as a deduction when a discount applies
        discount_amount = discount_data["discount_amount"]
        discount_display = (
            f"-${discount_amount:.2f}" if discount_amount else "$0.00"
        )

        # Add the subtotal, combined discount, and final amount to the bill
        order_rows.extend([
            {"Item": "Subtotal", "Amount": f"${subtotal:.2f}"},
            {"Item": "Discounts", "Amount": discount_display},
            {"Item": "Total", "Amount": f"${final_total:.2f}"},
        ])

        # Save the calculated order in session state.
        # Streamlit reruns the script when a user interacts with a widget,
        # so this keeps the summary available during checkout.
        st.session_state["calculated_selection"] = current_selection
        st.session_state["calculated_order"] = {
            "package": tier,
            "timing": peak_type,
            "rows": order_rows,
            "total": final_total,
            "applied_perks": discount_data["applied_perks"],
            "recommendation": recommendation,
        }

# PERSON 3: Retrieve the saved calculation for display
order = st.session_state.get("calculated_order")

# Show the summary and checkout after a valid order has been calculated
if order:
    st.subheader("Order Summary")

    st.write(f"**Package:** {order['package']}")
    st.write(f"**Timing:** {order['timing']}")
    st.table(order["rows"])

    # Display the discount messages returned by the pricing function
    for message in order["applied_perks"]:
        st.caption(message)

    # Display the recommendation calculated by Person 2's function
    st.info(order["recommendation"])

    st.subheader("Checkout")

    # Let the cashier record the customer's payment method
    payment_method = st.selectbox(
        "Payment Method",
        ["Cash", "Card", "PayNow"],
    )

    # Simulate payment confirmation when the button is clicked
    if st.button("Confirm Payment", type="primary"):

        # Increase the booking counter for each confirmed order
        booking_number = st.session_state.get("booking_number", 0) + 1
        st.session_state["booking_number"] = booking_number

        # Save the confirmed details for the receipt.
        # Format the booking number as BOOK-0001, BOOK-0002, and so on.
        st.session_state["receipt"] = {
            "booking_id": f"BOOK-{booking_number:04d}",
            "package": order["package"],
            "timing": order["timing"],
            "payment_method": payment_method,
            "rows": order["rows"],
            "total": order["total"],
        }

# PERSON 3: Retrieve the latest confirmed receipt
receipt = st.session_state.get("receipt")

# Keep the latest receipt visible while the customer edits a new order
if receipt:
    st.divider()
    st.subheader("Latest Receipt")

    booking_id = receipt["booking_id"]

    # Display confirmation and the saved booking details
    st.success(f"Demo payment confirmed · ${receipt['total']:.2f}")
    st.write(f"**Booking ID:** {booking_id}")
    st.write(f"**Package:** {receipt['package']}")
    st.write(f"**Timing:** {receipt['timing']}")
    st.write(f"**Payment method:** {receipt['payment_method']}")
    st.table(receipt["rows"])

    # Prepare the receipt content as a list of text lines
    receipt_lines = [
        "Theme Park Ticketing App",
        "Demo Payment Receipt",
        f"Booking ID: {booking_id}",
        f"Package: {receipt['package']}",
        f"Timing: {receipt['timing']}",
        f"Payment method: {receipt['payment_method']}",
        "",
    ]

    # Include every item and total from the confirmed bill
    for row in receipt["rows"]:
        receipt_lines.append(f"{row['Item']}: {row['Amount']}")

    # Join the lines and allow the receipt to be downloaded as a text file
    st.download_button(
        "Download Receipt",
        data="\n".join(receipt_lines),
        file_name=f"receipt_{booking_id}.txt",
        mime="text/plain",
    )