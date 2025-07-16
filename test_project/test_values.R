# Lies die CSV-Datei ein
values <- read.csv("../it_100_values.csv")

library(ggplot2)
library(dplyr)

# Filtere relevante Daten
values_filtered <- values %>%
  filter(CoalPrice %% 10 == 0, CoalPrice >= 10, CoalPrice <= 200, Storage < 3000)

# Erzeuge das Plot
ggplot(values_filtered, aes(x = Storage, y = EnergyPrice)) +
  geom_tile(aes(fill = Wert)) +
  scale_fill_viridis_c(option = "plasma") +  # Alternativ: scale_fill_gradient(low = "white", high = "blue")
  facet_wrap(~ CoalPrice, ncol = 5) +
  labs(title = "Policy für verschiedene Kohlepreise", fill = "Wert") +
  theme_minimal()
