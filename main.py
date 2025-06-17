import plotly.io as pio
pio.renderers.default = 'browser'
import plotly.graph_objects as go

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

def get_ypsilon(price, min_price, max_price, omega) -> int:
    denominator = (max_price - price) ** omega
    if denominator == 0:
        return -1
    numerator = (price - min_price) ** omega
    rho = numerator / denominator

    if rho <= 1:
        prob = rho / 2
    else:
        prob = 1 - 1/(2*rho)

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

def plot_policy_3d(policy):
    x, y, z, colors, texts = [], [], [], [], []

    # Farben je Aktion
    action_colors = {
        (False, False): 'gray',    # nichts tun
        (True, False): 'blue',     # kaufen
        (False, True): 'green',    # produzieren
        (True, True): 'orange'     # kaufen & produzieren
    }

    for (storage, coal_price, energy_price), action in policy.items():
        x.append(coal_price)
        y.append(energy_price)
        z.append(storage)
        colors.append(action_colors.get(action, 'black'))
        if action == (False, False):
            texts.append('Nichts')
        elif action == (True, False):
            texts.append('Kaufen')
        elif action == (False, True):
            texts.append('Produzieren')
        elif action == (True, True):
            texts.append('Kaufen & Produzieren')
        else:
            texts.append('Unbekannt')

    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(size=4, color=colors),
        text=texts,
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Kohlepreis [€/Tonne]',
            yaxis_title='Energiepreis [€/MWh]',
            zaxis_title='Lagerstand [kt]',
        ),
        title='3D-Policy-Visualisierung',
        margin=dict(l=0, r=0, b=0, t=40)
    )

    fig.show()

def main():
    GAMMA = 0.4         # Diskontierungsfaktor
    THRESHOLD = 1e-3    # Konvergenz
    MAX_ITERATIONS = 10
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

                # nächsten Zustände ermitteln
                expected_value = 0.0
                next_prices_and_probs = get_next_prices_and_probs(coal_price, energy_price)
                for (next_coal_price, next_energy_price), prob in next_prices_and_probs:
                    next_state = (next_storage, next_coal_price, next_energy_price)
                    expected_value += prob * (reward + GAMMA * V[next_state])

                # beste Aktion ermitteln
                if expected_value > best_action_value:
                    best_action_value = expected_value
                    best_action = action

            # Wertfunktion und Strategie aktualisieren
            V_new[state] = best_action_value
            policy[state] = best_action
            delta = max(delta, abs(V_new[state] - V[state]))

        V = V_new
        print(f"Iteration {iteration+1}, max Delta: {delta}")

        # auf Konvergenz prüfen
        if delta < THRESHOLD:
            print(f"Konvergenz erreicht bei Iteration {iteration+1}")
            break

    plot_policy_3d(policy)


if __name__ == '__main__':
    main()
