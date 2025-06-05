import random

MIN_PRICE_COAL = 10
MAX_PRICE_COAL = 200
DELTA_PRICE_COAL = 10
OMEGA_COAL = 2

MIN_PRICE_ENERGY = 10
MAX_PRICE_ENERGY = 300
DELTA_PRICE_ENERGY = 10
OMEGA_ENERGY = 1



def get_ypsilon(price, min, max, omega):
    denominator = (max - min) ** omega
    if denominator == 0:
        return -1
    numerator = (price - min) ** omega
    rho = numerator / denominator

    if rho <= 1:
        prob = rho / 2
    else:
        prob = 1 - 1/(2*rho)

    return random.choices([-1, 1], weights=[prob, 1 - prob], k=1)[0]

print(get_ypsilon(120, MIN_PRICE_COAL, MAX_PRICE_COAL, OMEGA_COAL))
