import numpy as np
import matplotlib.pyplot as plt
import time
import csv


MIN_PRICE_COAL = 10     # €/Tonne
MAX_PRICE_COAL = 200    # €/Tonne
DELTA_PRICE_COAL = 10   # €/Tonne
OMEGA_COAL = 4

# 1 Tonne → 1 Megawattstunde
MIN_PRICE_ENERGY = 10   # €/Megawattstunde
MAX_PRICE_ENERGY = 300  # €/Megawattstunde
DELTA_PRICE_ENERGY = 10 # €/Megawattstunde
OMEGA_ENERGY = 1

# 10 Megatonnen = 10_000 Kilotonnen = 10_000_000 Tonnen
MAX_STORAGE_COAL = 9_000   # Kilotonnen # eigentlich 90_000
BUY_AMOUNT_COAL = 10        # Kilotonnen

COAL_FOR_ENERGY = 10        # Kilotonnen
ENERGY_PRODUCTION = 10_000  # Megawattstunden

price_transition_cache = {}

def get_prob_minus(price, min_price, max_price, omega) -> int:
    denominator = (max_price - price) ** omega
    if denominator == 0:
        return 1 # prob = 100% for -1
    numerator = (price - min_price) ** omega
    rho = numerator / denominator

    if rho <= 1:
        prob = rho / 2
    else:
        prob = 1 - 1/(2*rho)

    return prob


def get_next_prices_and_probs_cached(coal_price, energy_price):
    key = (coal_price, energy_price)
    if key not in price_transition_cache:
        price_transition_cache[key] = get_next_prices_and_probs(coal_price, energy_price)
    return price_transition_cache[key]


def get_next_prices_and_probs(coal_price, energy_price):
    prob_coal_minus = get_prob_minus(coal_price, MIN_PRICE_COAL, MAX_PRICE_COAL, OMEGA_COAL)
    prob_coal_plus = 1 - prob_coal_minus

    prob_energy_minus = get_prob_minus(energy_price, MIN_PRICE_ENERGY, MAX_PRICE_ENERGY, OMEGA_ENERGY)
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

def export_policy_to_csv(policy, filename="policy.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Kopfzeile
        writer.writerow(["Storage", "CoalPrice", "EnergyPrice", "Buy", "Produce"])
        for (storage, coal_price, energy_price), (buy, produce) in policy.items():
            writer.writerow([storage, coal_price, energy_price, int(buy), int(produce)])
    print(f"Policy erfolgreich exportiert nach: {filename}\n")



def main():
    start_time = time.time()
    GAMMA = 0.99         # Diskontierungsfaktor
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
    
    valid_states = set(states)



    actions = [(False, False), (True, False), (False, True), (True, True)] # (kaufen, produzieren)

    # Initialisiere Wertfunktion und Strategie
    V = {state: 0.0 for state in states}
    policy = {state: None for state in states}

    # Wertfunktion
    for iteration in range(MAX_ITERATIONS):
        delta = 0
        V_new = {}

        action_change_counter = 0

        for state in states:
            storage, coal_price, energy_price = state
            best_action_value = float('-inf')
            best_action = None

            for action in actions:
                buy, produce = action

                # prüfen, ob die Aktion ausgeführt werden kann
                if buy and storage + BUY_AMOUNT_COAL > MAX_STORAGE_COAL:
                    continue
                if produce and storage < COAL_FOR_ENERGY:
                    continue

                # neuen Lagerstand berechnen
                next_storage = storage
                if buy:
                    next_storage += BUY_AMOUNT_COAL
                if produce:
                    next_storage -= COAL_FOR_ENERGY

                # Kosten und Einnahmen berechnen
                reward = 0
                if buy:
                    reward -= BUY_AMOUNT_COAL * 1_000 * coal_price
                if produce:
                    reward += ENERGY_PRODUCTION * energy_price

                # nächste Zustände ermitteln
                expected_value = 0.0
                next_prices_and_probs = get_next_prices_and_probs_cached(coal_price, energy_price)
                for (next_coal_price, next_energy_price), prob in next_prices_and_probs:
                    next_state = (next_storage, next_coal_price, next_energy_price)
                    if next_state not in V:
                        continue  # oder: setze prob auf 0
                    expected_value += prob * (reward + GAMMA * V[next_state])


                # beste Aktion ermitteln
                if expected_value > best_action_value:
                    best_action_value = expected_value
                    if best_action != action:
                        action_change_counter += 1
                    best_action = action

            # Wertfunktion und Strategie aktualisieren
            V_new[state] = best_action_value
            policy[state] = best_action
            delta = max(delta, abs(V_new[state] - V[state]))

        V = V_new

        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        print(f"It: {iteration+1}, delta: {delta}, actions changed: {action_change_counter} total duration: {hours:02d}:{minutes:02d}:{seconds:02d}")

        # auf Konvergenz prüfen
        if delta < THRESHOLD:
            print(f"Konvergenz erreicht bei Iteration {iteration+1}")
            break
        if (iteration+1) % 100 == 0:
            export_policy_to_csv(policy, f"w_4_1_iteration_{iteration+1}.csv")

    #plot_policy(policy)
    #export_policy_to_csv(policy, f"base_iteration_{iteration+1}.csv")
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    print(f"Finished! Total duration: {hours:02d}:{minutes:02d}:{seconds:02d}")


if __name__ == '__main__':
    main()
