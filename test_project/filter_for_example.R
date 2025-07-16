policy <- read.csv("../it_10_policy.csv")
values <- read.csv("../it_10_values.csv")

merged <- merge(policy, values, by = c("CoalPrice", "EnergyPrice", "Storage"))


filtered <- merged %>%
  filter(CoalPrice <= 10, 
         EnergyPrice <= 10,
         Storage <= 0)

library(dplyr)

filtered <- filtered %>%
  mutate(Action = case_when(
    Buy == 1 & Produce == 0 ~ "K",
    Buy == 0 & Produce == 1 ~ "V",
    Buy == 1 & Produce == 1 ~ "K & V",
    TRUE ~ "Idle"
  ))

library(ggplot2)

plot1 <- ggplot(filtered, aes(x = Storage, y = 1, fill = Wert)) +
  geom_tile(height = 1) +
  scale_x_continuous(labels = scales::label_number(accuracy = 1)) +
  scale_fill_gradient(low = "red", high = "green",
                      labels = scales::label_number(accuracy = 1)) +
  labs(title = "Wert über Storage",
       x = "Storage",
       y = "",
       fill = "Wert") +
  theme_minimal() +
  theme(axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid = element_blank())


plot2 <- ggplot(filtered, aes(x = Storage, y = 1, fill = Action)) +
  geom_tile(height = 1) +
  scale_fill_manual(values = c(
    "K" = "red",
    "V" = "green",
    "K & V" = "blue",
    "Idle" = "grey"
  )) +
  labs(title = "Aktion über Storage",
       x = "Storage",
       y = "",
       fill = "Aktion") +
  theme_minimal() +
  theme(axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid = element_blank())




library(patchwork)

plot1 + plot2 + plot_layout(ncol = 1)

