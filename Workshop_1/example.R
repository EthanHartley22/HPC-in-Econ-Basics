library(tidyverse)
library(data.table)
library(fixest)
print('Running')

# Set seed for reproducibility
set.seed(123)

# Generate synthetic data
n <- 1000
data <- data.table(
  x = rnorm(n),
  z = rnorm(n),
  e = rnorm(n)
)
data[, y := 2 * x + 3 * z + e]

# Run a regression using fixest
model <- feols(y ~ x + z, data = data)
summary(model)

# Plot results and save to path
plot_path <- "regression_plot.png"
ggplot(data, aes(x = x, y = y)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm", color = "blue") +
  theme_minimal() +
  ggtitle("Regression of y on x")
ggsave(plot_path, width = 6, height = 4)

cat("Plot saved to:", plot_path)
