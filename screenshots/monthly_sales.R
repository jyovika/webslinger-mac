# Monthly sales summary
library(dplyr)
library(ggplot2)

sales <- read.csv("data/retail.csv", stringsAsFactors = FALSE)

summarise_month <- function(df, min_total = 100) {
  if (nrow(df) == 0) return(NULL)
  df |>
    group_by(month) |>
    summarise(total = sum(amount), orders = n()) |>
    filter(total > min_total)
}

monthly <- summarise_month(sales, min_total = 250)

# Plot the trend
ggplot(monthly, aes(month, total)) +
  geom_line(colour = "#E3242B", linewidth = 1.2) +
  labs(title = "Sales by month", x = NULL, y = "Total ($)") +
  theme_minimal()

quantile(sales$amount, c(.5, .9, .99), na.rm = TRUE)
