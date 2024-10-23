novel1 <- read.csv('sonsandlovers.csv')
novel2 <- read.csv('therainbow.csv')
novel3 <- read.csv('womeninlove.csv')

data <- rbind(novel1,novel2,novel3)

library(tidyverse)
library(RColorBrewer)
library(reshape2)
library(dplyr)
library(rstatix)

ggplot(data = data, aes(x = book, y = similarity)) +
  geom_violin(trim = FALSE) +
  stat_summary(fun.y = mean, geom = "point", shape = 21, size = 2, colour = 'darkblue') +
  geom_boxplot(width = 0.1)


t.test(novel1$similarity, novel2$similarity)
t.test(novel2$similarity, novel3$similarity)
t.test(novel1$similarity, novel3$similarity)
