import random

MIN_PRICE_COAL = 10
MAX_PRICE_COAL = 200
DELTA_PRICE_COAL = 10
OMEGA_COAL = 2

MIN_PRICE_ENERGY = 10
MAX_PRICE_ENERGY = 300
DELTA_PRICE_ENERGY = 10
OMEGA_ENERGY = 1

# 10 Megatonnen = 10_000 Kilotonnen = 10_000_000 Tonnen
MAX_STORAGE_COAL = 90_000   # Kilotonnen
BUY_AMOUNT_COAL = 10        # Kilotonnen

COAL_FOR_ENERGY = 10        # Kilotonnen
ENERGY_PRODUCTION = 10_000  # Megawattstunden

def get_ypsilon(price, min, max, omega):
    denominator = (max - min) ** omega
    if denominator == 0:
        return -1
    numerator = (price - min) ** omega
    rho = numerator / denominator
    print(rho)

    if rho <= 1:
        prob = rho / 2
    else:
        prob = 1 - 1/(2*rho)
    print(prob)

    return random.choices([-1, 1], weights=[prob, 1 - prob], k=1)[0]

def get_next_price(price, coal):
    if coal:
        min_price = MIN_PRICE_COAL
        max_price = MAX_PRICE_COAL
        delta = DELTA_PRICE_COAL
        ypsilon = get_ypsilon(price, min_price, max_price, OMEGA_COAL)
    else:
        min_price = MIN_PRICE_ENERGY
        max_price = MAX_PRICE_ENERGY
        delta = DELTA_PRICE_ENERGY
        ypsilon = get_ypsilon(price, min_price, max_price, OMEGA_ENERGY)
    return max(min_price, min(max_price, price + ypsilon * delta))

print(get_next_price(100, False))
