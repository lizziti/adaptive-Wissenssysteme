import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# CSV-Datei laden
df = pd.read_csv("iteration_1000.csv")

# Filter auf Storage < 1000
df = df[df["Storage"] < 3000]

# Farbzuweisung basierend auf (Buy, Produce)
def get_color(row):
    if row["Buy"] == 0 and row["Produce"] == 0:
        return "gray"
    elif row["Buy"] == 1 and row["Produce"] == 0:
        return "red"
    elif row["Buy"] == 0 and row["Produce"] == 1:
        return "green"
    else:
        return "blue"

df["Color"] = df.apply(get_color, axis=1)

# 3D-Plot erzeugen
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

ax.scatter(df["Storage"], df["CoalPrice"], df["EnergyPrice"], c=df["Color"], s=40)

ax.set_xlabel("Storage")
ax.set_ylabel("CoalPrice")
ax.set_zlabel("EnergyPrice")
ax.set_title("3D Plot (Buy/Produce farbcodiert)")

# Blickwinkel ändern (optional)
ax.view_init(elev=20, azim=45)  # Höhe und Azimutwinkel

plt.show()
