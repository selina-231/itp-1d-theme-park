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

ADD_ONS = {
    "Express": {"price": 15, "per_person": True},
    "Photo": {"price": 5, "per_person": True},
    "Meal Voucher": {"price": 10, "per_person": True},
    "Parking": {"price": 15, "per_person": False}
}

def calculate_add_ons(selected_addons, visitors):
    "Calculates total cost of add_ons."
    addon_total = 0
    breakdown = {}
    
    for x in selected_addons:
        if x in ADD_ONS:
            item = ADD_ONS[x]
            if item["per_person"]:
                cost = item["price"] * visitors 
            else:
                cost = item["price"]
            addon_total += cost
            breakdown[x] = cost
            
    return {
        "breakdown": breakdown,
        "addon_total": addon_total
    }

PROMO_CODES = {
    "PARK10": {"type": "percent", "value": 0.10, "min_spend": 30},
    "WELCOME5": {"type": "flat", "value": 5.0, "min_spend": 20},
    "FAMILY15": {"type": "percent", "value": 0.15, "min_spend": 50}
}

def calculate_discounts(subtotal, tier, peak_type, total_visitors, promo_code):
    "Applies tier perks, off-peak bonuses, and promo codes."
    discount_amount = 0.0
    applied_perks = []

    if tier == "Family Bundle" and total_visitors >= 4:
        family_disc = 5.0
        discount_amount += family_disc
        applied_perks.append(f"Family Bundle 4+ perk (-${family_disc:.2f})")

    if peak_type == "Off-Peak (Weekday)":
        peak_disc = 5.0
        discount_amount += peak_disc
        applied_perks.append(f"Off-Peak Bonus (-${peak_disc:.2f})")

    code = promo_code.strip().upper()
    if code in PROMO_CODES:
        promo = PROMO_CODES[code]
        if subtotal >= promo["min_spend"]:
            if promo["type"] == "percent":
                promo_disc = subtotal * promo["value"]
            else:
                promo_disc = promo["value"]
            discount_amount += promo_disc
            applied_perks.append(f"Promo '{code}' (-${promo_disc:.2f})")
        else:
            applied_perks.append(f"Promo '{code}' requires ${promo['min_spend']} min spend")

    discount_amount = min(discount_amount, subtotal)
    return {
        "discount_amount": discount_amount,
        "applied_perks": applied_perks
    }

def recommend_best_deal(adult_count, child_count, current_tier, peak_type, selected_addons, promo_code=""):
    "Simulates all tiers to find the cheapest option or best value upgrade."
    total_visitors = adult_count + child_count
    if total_visitors == 0:
        return "Add at least 1 visitor to see deal recommendations."

    tier_totals = {}

    for tier in TICKET_PRICES:
        base = calculate_base_price(adult_count, child_count, tier, peak_type)["base_total"]
        addons = calculate_add_ons(selected_addons, total_visitors)["addon_total"]
        subtotal = base + addons
        discount = calculate_discounts(subtotal, tier, peak_type, total_visitors, promo_code)["discount_amount"]
        tier_totals[tier] = round(subtotal - discount, 2)

    cheapest_tier = min(tier_totals, key=tier_totals.get)
    current_price = tier_totals[current_tier]
    cheapest_price = tier_totals[cheapest_tier]

    if cheapest_tier != current_tier and cheapest_price < current_price:
        savings = current_price - cheapest_price
        return f"💡 Best Deal: Switch to '{cheapest_tier}' (${cheapest_price:.2f}) to save ${savings:.2f}!"
    
    # Smart upsell check: if VIP is within $10 of their current choice
    if current_tier == "Standard" and (tier_totals["VIP"] - current_price) <= 10:
        diff = tier_totals["VIP"] - current_price
        return f"✨ Value Tip: Upgrade to 'VIP' for just ${diff:.2f} more!"

    return f"✅ You already have the best deal with '{current_tier}' (${current_price:.2f})!"