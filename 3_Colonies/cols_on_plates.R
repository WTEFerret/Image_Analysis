# Short script to have a look at the Results.csv

library(dplyr)
library(tidyr)
library(ggplot2)

data = read.csv('Example/240320_T6SS_Pilot_19h_Mcherry/Results.csv')

# Create two new columns from the Label by seperating the image name and position on the plate 
data <- data %>% tidyr::separate(col = Label, into = c('img', 'temp1', 'temp2', 'position' ), sep = ' ') %>% select(-temp1, -temp2)

# Separate plate position into row, column and plate number
data <- data %>% tidyr::separate(col = position, into = c('plate', 'row', 'col'), sep = '/')
data$col <- as.numeric(data$col)

# Plot the sum of all fluorescent signal (RawIntDen) 
ggplot(data, aes(x=col, y = log10(RawIntDen))) +
  geom_boxplot(aes(group=col)) +
  geom_jitter(aes(col=plate)) +
  theme_bw()

# Plot the data in the setup of the original plate
ggplot(data, aes(x=row, y=col)) +
  geom_point(aes(size=log10(RawIntDen))) +
  facet_wrap(vars(plate), ncol = 1) +
  theme_bw()

# Count number of colonies per plate
data %>% group_by(plate) %>% count()


