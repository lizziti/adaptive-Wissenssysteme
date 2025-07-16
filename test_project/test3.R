# Lies die CSV-Datei ein
policy <- read.csv("../it_1000_policy.csv")

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
  filter(EnergyPrice %% 10 == 0, EnergyPrice >= 10, EnergyPrice <= 300, Storage < 3000) %>%
  mutate(
    Aktion = case_when(
      Buy == 0 & Produce == 0 ~ "Nichts",
      Buy == 1 & Produce == 0 ~ "Kaufen",
      Buy == 0 & Produce == 1 ~ "Produzieren",
      Buy == 1 & Produce == 1 ~ "Beides"
    )
  )

# Erzeuge das Plot
ggplot(policy_filtered, aes(x = Storage, y = CoalPrice)) +
  geom_tile(aes(fill = Aktion)) +
  scale_fill_manual(values = action_colors) +
  facet_wrap(~ EnergyPrice, ncol = 5) +
  labs(title = "Policy für verschiedene Energiepreise", fill = "Aktion") +
  theme_minimal()






library(mgcv)

gam_model <- gam(Buy ~ s(CoalPrice) + s(Storage), 
                 data = policy_filtered, 
                 family = binomial)
newdata <- expand.grid(
  CoalPrice = seq(min(policy_filtered$CoalPrice), max(policy_filtered$CoalPrice), length.out = 200),
  Storage = seq(min(policy_filtered$Storage), max(policy_filtered$Storage), length.out = 200)
)

newdata$BuyProb <- predict(gam_model, newdata, type = "response")

ggplot(policy_filtered, aes(x = CoalPrice, y = Storage)) +
  geom_point(aes(color = factor(Buy)), alpha = 0.4) +
  geom_contour(data = newdata, aes(z = BuyProb), breaks = 0.5, color = "black", size = 1.2) +
  scale_color_manual(values = c("0" = "gray70", "1" = "red"), labels = c("Nein", "Ja")) +
  labs(
    title = "Nicht-lineare Entscheidungskante für Kaufen",
    x = "Kohlepreis",
    y = "Lagerbestand",
    color = "Kaufen"
  ) +
  theme_minimal()

