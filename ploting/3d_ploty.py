import pandas as pd
import plotly.express as px

# CSV laden
df = pd.read_csv(R"..\iteration_1000.csv")

# Optionaler Filter
#df = df[df["Storage"] < 5000]
# df = df[df["CoalPrice"] == 70]
# df = df[df["EnergyPrice"] == 90]

# Farbcodierung über kombinierte Spalte
df["Action"] = df["Buy"].astype(str) + df["Produce"].astype(str)

color_map = {
    "00": "gray",
    "10": "red",
    "01": "green",
    "11": "blue"
}

# 3D Scatterplot erzeugen
fig = px.scatter_3d(
    df,
    x="Storage",
    y="CoalPrice",
    z="EnergyPrice",
    color="Action",
    color_discrete_map=color_map,
    title="Interaktiver 3D-Plot (Buy/Produce)",
    labels={"Action": "(Buy, Produce)"}
)

# Punktgröße setzen
fig.update_traces(marker=dict(size=6))

# Optional: HTML-Datei speichern
#fig.write_html("n_it_1000_plot.html")

# Plot anzeigen
fig.show()
