import streamlit as st
from mylibrary import (
    PEAK_MULTIPLIERS,
    TICKET_PRICES,
    ADD_ONS,
    calculate_base_price,
    calculate_add_ons,
    calculate_discounts,
    recommend_best_deal,
)

st.title("Theme Park Ticketing App")

# PERSON 3: Show package prices before customers select their tickets
st.subheader("Ticket Prices")

price_rows = []

for package, prices in TICKET_PRICES.items():
    row = {"Package": package}

    # Calculate adult and child prices for each timing
    for timing, multiplier in PEAK_MULTIPLIERS.items():
        row[f"{timing} - Adult"] = f"${prices['adult'] * multiplier:.2f}"
        row[f"{timing} - Child"] = f"${prices['child'] * multiplier:.2f}"

    price_rows.append(row)

st.table(price_rows)
st.caption("Prices are per person, before add-ons and discounts.")

# Ticket selection inputs
adults = st.number_input("Number of Adults", min_value=0, value=1, step=1)
children = st.number_input("Number of Children", min_value=0, value=0, step=1)
tier = st.selectbox("Select Ticket Tier / Package", list(TICKET_PRICES.keys()))
peak_type = st.selectbox("Select Season / Timing", list(PEAK_MULTIPLIERS.keys()))

st.subheader("Optional Perks & Add-ons")
selected_addons = st.multiselect(
    "Select Add-ons",
    list(ADD_ONS.keys()),
    format_func=lambda x: f"{x} (${ADD_ONS[x]['price']} {'per person' if ADD_ONS[x]['per_person'] else 'flat'})"
)
st.subheader("Promotions")
promo_code = st.text_input("Enter Promo Code (Optional)", value="")

# PERSON 3: Track the selections used to calculate the order
current_selection = (
    adults,
    children,
    tier,
    peak_type,
    tuple(selected_addons),
    promo_code,
)

# Clear the old calculation when selections change.
# The customer must calculate the updated total before confirming.
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

        # PERSON 3: Create the itemized bill using the calculated prices
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

        # Add each selected add-on and its quantity to the bill
        for name, cost in addon_data["breakdown"].items():
            quantity = total_visitors if ADD_ONS[name]["per_person"] else 1

            order_rows.append({
                "Item": f"{name} × {quantity}",
                "Amount": f"${cost:.2f}",
            })

        # Format the combined discount as a deduction
        discount_amount = discount_data["discount_amount"]
        discount_display = (
            f"-${discount_amount:.2f}" if discount_amount else "$0.00"
        )

        # Add the subtotal, discount, and final total
        order_rows.extend([
            {"Item": "Subtotal", "Amount": f"${subtotal:.2f}"},
            {"Item": "Discounts", "Amount": discount_display},
            {"Item": "Total", "Amount": f"${final_total:.2f}"},
        ])

        # Save the calculation so it stays available when Streamlit reruns
        st.session_state["calculated_selection"] = current_selection
        st.session_state["calculated_order"] = {
            "package": tier,
            "timing": peak_type,
            "rows": order_rows,
            "total": final_total,
            "applied_perks": discount_data["applied_perks"],
            "recommendation": recommendation,
        }

# PERSON 3: Retrieve and display the calculated order
order = st.session_state.get("calculated_order")

if order:
    st.subheader("Order Summary")

    st.write(f"**Package:** {order['package']}")
    st.write(f"**Timing:** {order['timing']}")
    st.table(order["rows"])

    # Show the discount messages returned by the pricing function
    for message in order["applied_perks"]:
        st.caption(message)

    # Show the recommendation returned by Person 2's function
    st.info(order["recommendation"])

    st.subheader("Checkout")

    # Simulate payment confirmation
    if st.button("Confirm Payment", type="primary"):

        # Increase the booking number for each confirmed order
        booking_number = st.session_state.get("booking_number", 0) + 1
        st.session_state["booking_number"] = booking_number

        # Save the confirmed order for the receipt.
        # Booking IDs use the format BOOK-0001, BOOK-0002, and so on.
        st.session_state["receipt"] = {
            "booking_id": f"BOOK-{booking_number:04d}",
            "package": order["package"],
            "timing": order["timing"],
            "rows": order["rows"],
            "total": order["total"],
        }

# PERSON 3: Retrieve the latest confirmed receipt
receipt = st.session_state.get("receipt")

if receipt:
    st.divider()
    st.subheader("Latest Receipt")

    booking_id = receipt["booking_id"]

    # Display the confirmation and saved booking details
    st.success(f"Demo payment confirmed · ${receipt['total']:.2f}")
    st.write(f"**Booking ID:** {booking_id}")
    st.write(f"**Package:** {receipt['package']}")
    st.write(f"**Timing:** {receipt['timing']}")
    st.table(receipt["rows"])

    # Prepare the receipt content for a text file
    receipt_lines = [
        "Theme Park Ticketing App",
        "Demo Payment Receipt",
        f"Booking ID: {booking_id}",
        f"Package: {receipt['package']}",
        f"Timing: {receipt['timing']}",
        "",
    ]

    # Include each item and total from the confirmed bill
    for row in receipt["rows"]:
        receipt_lines.append(f"{row['Item']}: {row['Amount']}")

    # Allow the customer to download the receipt
    st.download_button(
        "Download Receipt",
        data="\n".join(receipt_lines),
        file_name=f"receipt_{booking_id}.txt",
        mime="text/plain",
    )