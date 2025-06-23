# Lies die CSV-Datei ein
policy <- read.csv("../iteration_100.csv")


# Schau dir die ersten Zeilen an
head(policy)

library(ggplot2)

# Nur für CoalPrice == 100
subset_policy <- subset(policy, CoalPrice == 50)
subset_policy <- subset(subset_policy, Storage < 1000)

# Visualisiere Buy/Produce als Farben
ggplot(subset_policy, aes(x = Storage, y = EnergyPrice)) +
  geom_tile(aes(fill = interaction(Buy, Produce))) +
  scale_fill_manual(values = c("0.0" = "gray", "1.0" = "red", "0.1" = "green", "1.1" = "blue")) +
  labs(title = "Policy bei Kohlepreis 100 €/t", fill = "Aktion") +
  theme_minimal()

