# Ticket prices and peak multipliers (demonstrates "Flexibility to changes")
TICKET_PRICES = {
    "Standard": {"adult": 10, "child": 5},
    "VIP": {"adult": 20, "child": 12},
    "Family Bundle": {"adult": 25, "child": 10}
}

PEAK_MULTIPLIERS = {
    "Off-Peak (Weekday)": 1.0,
    "Peak (Weekend/Holiday)": 1.25
}


def calculate_base_price(adult_count, child_count, tier, peak_type):
    """Calculates base price based on tier, quantities, and peak/off-peak rates."""
    prices = TICKET_PRICES.get(tier, {"adult": 10, "child": 5})
    multiplier = PEAK_MULTIPLIERS.get(peak_type, 1.0)
    adult_total = adult_count * prices["adult"] * multiplier
    child_total = child_count * prices["child"] * multiplier
    return {
        "adult_total": adult_total,
        "child_total": child_total,
        "base_total": adult_total + child_total
    }
