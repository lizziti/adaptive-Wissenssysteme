# Lies die CSV-Datei ein
policy <- read.csv("../iteration_1000.csv")

library(ggplot2)
library(dplyr)

# Farbzuweisung für Aktionen
action_colors <- c(
  "Nichts" = "gray",
  "Kaufen" = "red",
  "Produzieren" = "green",
  "Beides" = "blue"
)

# Filtere relevante Daten
policy_filtered <- policy %>%
  filter(CoalPrice %% 10 == 0, CoalPrice >= 10, CoalPrice <= 200, Storage < 3000) %>%
  mutate(
    Aktion = case_when(
      Buy == 0 & Produce == 0 ~ "Nichts",
      Buy == 1 & Produce == 0 ~ "Kaufen",
      Buy == 0 & Produce == 1 ~ "Produzieren",
      Buy == 1 & Produce == 1 ~ "Beides"
    )
  )

# Erzeuge das Plot
ggplot(policy_filtered, aes(x = Storage, y = EnergyPrice)) +
  geom_tile(aes(fill = Aktion)) +
  scale_fill_manual(values = action_colors) +
  facet_wrap(~ CoalPrice, ncol = 5) +
  labs(title = "Policy für verschiedene Kohlepreise", fill = "Aktion") +
  theme_minimal()

