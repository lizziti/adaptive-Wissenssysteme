import random

MIN_PRICE_COAL = 10     # €/Tonne
MAX_PRICE_COAL = 200    # €/Tonne
DELTA_PRICE_COAL = 10   # €/Tonne
OMEGA_COAL = 2

# 1 Tonne → 1 Megawattstunde
MIN_PRICE_ENERGY = 10   # €/Megawattstunde
MAX_PRICE_ENERGY = 300  # €/Megawattstunde
DELTA_PRICE_ENERGY = 10 # €/Megawattstunde
OMEGA_ENERGY = 1

# 10 Megatonnen = 10_000 Kilotonnen = 10_000_000 Tonnen
MAX_STORAGE_COAL = 90_000   # Kilotonnen
BUY_AMOUNT_COAL = 10        # Kilotonnen

COAL_FOR_ENERGY = 10        # Kilotonnen
ENERGY_PRODUCTION = 10_000  # Megawattstunden

def get_ypsilon(price, min, max, omega) -> int:
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

    return prob

def get_next_prices_and_probs(coal_price, energy_price):
    prob_coal_minus = get_ypsilon(coal_price, MIN_PRICE_COAL, MAX_PRICE_COAL, OMEGA_COAL)
    prob_coal_plus = 1 - prob_coal_minus

    prob_energy_minus = get_ypsilon(energy_price, MIN_PRICE_ENERGY, MAX_PRICE_ENERGY, OMEGA_ENERGY)
    prob_energy_plus = 1 - prob_energy_minus

    next_prices = []

    # für plus und minus mit der jeweiligen Wahrscheinlichkeit ...
    for coal_delta, coal_prob in [(-DELTA_PRICE_COAL, prob_coal_minus), (+DELTA_PRICE_COAL, prob_coal_plus)]:
        # ... wird der nächste Kohlepreis berechnet
        next_coal_price = max(MIN_PRICE_COAL, min(MAX_PRICE_COAL, coal_price + coal_delta))

        # für plus und minus mit der jeweiligen Wahrscheinlichkeit ...
        for energy_delta, energy_prob in [(-DELTA_PRICE_ENERGY, prob_energy_minus), (+DELTA_PRICE_ENERGY, prob_energy_plus)]:
            # ... wird der nächste Energiepreis berechnet
            next_energy_price = max(MIN_PRICE_ENERGY, min(MAX_PRICE_ENERGY, energy_price + energy_delta))

            # kombinierte Wahrscheinlichkeit, dass sowohl der neue Kohle- als auch der Energiepreis eintreten
            combined_prob = coal_prob * energy_prob
            next_prices.append(((next_coal_price, next_energy_price), combined_prob))
    return next_prices

def get_next_state_and_reward(state, action) -> (int, int):
    storage, coal_price, energy_price = state
    buy, produce = action
    new_storage = storage
    reward = 0

    # Lagerstand Änderungen
    if buy:
        if new_storage + BUY_AMOUNT_COAL <= MAX_STORAGE_COAL:
            new_storage += BUY_AMOUNT_COAL
            reward-= BUY_AMOUNT_COAL * 1_000 * coal_price
        else:
            return None

    # TODO: Fragen: kann man Energie erzeugen, aus der Kohle, die zum gleichen Zeitpunkt gekauft wurde?
    # state = 0, action = (kaufen = True, produzieren= True)
    if produce:
        if new_storage >= COAL_FOR_ENERGY:
            new_storage -= COAL_FOR_ENERGY
            reward += ENERGY_PRODUCTION * energy_price
        else:
            return None

    # Preis Änderungen


    return new_storage, reward


def main():
    GAMMA = 0.4         # Diskontierungsfaktor
    THRESHOLD = 1e-3    # Konvergenz
    MAX_ITERATIONS = 1000
    storage_states = range(0, MAX_STORAGE_COAL + 1, BUY_AMOUNT_COAL)
    coal_price_states = range(MIN_PRICE_COAL, MAX_PRICE_COAL + 1, DELTA_PRICE_COAL)
    energy_price_states = range(MIN_PRICE_ENERGY, MAX_PRICE_ENERGY + 1, DELTA_PRICE_ENERGY)
    states = [
        (storage, coal_price, energy_price)
        for storage in storage_states
        for coal_price in coal_price_states
        for energy_price in energy_price_states
    ]
    actions = [(False, False), (True, False), (False, True), (True, True)] # (kaufen, produzieren)

    # Initialisiere Wertfunktion und Strategie
    V = {state: 0.0 for state in states}
    policy = {state: None for state in states}

    # Wertfunktion
    for iteration in range(MAX_ITERATIONS):
        delta = 0
        V_new = {}

        #for state in states:
         #TODO: hier weiter machen



if __name__ == '__main__':
    main()
