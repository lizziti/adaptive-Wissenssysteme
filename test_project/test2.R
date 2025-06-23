# ===============================
# Policy Animation aus policy.csv
# ===============================

# Pakete laden (bei Bedarf vorher mit install.packages(...) installieren)
library(ggplot2)
library(gganimate)
library(gifski)
library(png)
library(dplyr)
library(readr)

# Arbeitsverzeichnis anpassen (falls nötig):
# setwd("Pfad/zum/Ordner/mit/policy.csv")

# CSV-Datei laden (eine Ebene höher)
policy <- read_csv("../iteration_100.csv")

# Aktion als Textlabel hinzufügen
policy <- policy %>%
  mutate(Action = case_when(
    Buy == 0 & Produce == 0 ~ "Nichts",
    Buy == 1 & Produce == 0 ~ "Kaufen",
    Buy == 0 & Produce == 1 ~ "Produzieren",
    Buy == 1 & Produce == 1 ~ "Beides"
  ))

subset_policy <- subset(policy, Storage < 1000)

# Farbzuweisung für Aktionen
action_colors <- c(
  "Nichts" = "gray",
  "Kaufen" = "red",
  "Produzieren" = "green",
  "Beides" = "blue"
)

# Animationsplot definieren
p <- ggplot(subset_policy, aes(x = Storage, y = EnergyPrice, fill = Action)) +
  geom_tile() +
  scale_fill_manual(values = action_colors) +
  labs(
    title = "Policy bei Kohlepreis: {closest_state} €/Tonne",
    x = "Lagerbestand (kt)",
    y = "Energiepreis (€/MWh)",
    fill = "Aktion"
  ) +
  theme_minimal(base_size = 14) +
  transition_states(CoalPrice, transition_length = 2, state_length = 1) +
  ease_aes("linear")

# Animation anzeigen (in RStudio Viewer)
animate(p, width = 800, height = 600, fps = 20, renderer = gifski_renderer())

# Animation als GIF speichern
#anim_save("policy_animation.gif", animation = last_animation())

