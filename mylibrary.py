# Pricing dictionary (demonstrates "Flexibility to changes")
TICKET_PRICES = {
    "Standard": {"adult": 10, "child": 5},
    "VIP": {"adult": 20, "child": 12}
}


def calculate_base_price(adult_count, child_count, tier):
    """Calculates the base price based on ticket tier and quantities."""
    prices = TICKET_PRICES.get(tier, {"adult": 10, "child": 5})
    adult_total = adult_count * prices["adult"]
    child_total = child_count * prices["child"]
    return {
        "adult_total": adult_total,
        "child_total": child_total,
        "base_total": adult_total + child_total
    }
