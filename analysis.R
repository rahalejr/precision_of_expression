novel1 <- read.csv('sonsandlovers.csv')
novel2 <- read.csv('therainbow.csv')
novel3 <- read.csv('womeninlove.csv')
novel4 <- read.csv('ladychatterly.csv')

lolita <- read.csv('lolita.csv')
pale <- read.csv('palefire.csv')
rabbit <- read.csv('rabbitrun.csv')

novel1 <- novel1 %>%
  filter(!is_outlier(!!sym('similarity')))
novel2 <- novel2 %>%
  filter(!is_outlier(!!sym('similarity')))
novel3 <- novel3 %>%
  filter(!is_outlier(!!sym('similarity')))
novel4 <- novel4 %>%
  filter(!is_outlier(!!sym('similarity')))

lolita <- lolita %>%
  filter(!is_outlier(!!sym('similarity')))
pale <- pale %>%
  filter(!is_outlier(!!sym('similarity')))
rabbit <- rabbit %>%
  filter(!is_outlier(!!sym('similarity')))

novel3$syn_frequency = NA

data <- rbind(novel1,novel2,novel3, novel4)



data <- rbind(lolita, pale, rabbit, novel3)

library(tidyverse)
library(RColorBrewer)
library(reshape2)
library(dplyr)
library(rstatix)

ggplot(data = data, aes(x = book, y = similarity)) +
  geom_violin(trim = FALSE) +
  stat_summary(fun.y = mean, geom = "point", shape = 21, size = 2, colour = 'darkblue') +
  geom_boxplot(width = 0.1)

hist(log(novel4$similarity), breaks = 20)

t.test(novel1$similarity, novel2$similarity)
t.test(novel2$similarity, novel3$similarity)
t.test(novel1$similarity, novel3$similarity)
t.test(novel4$similarity, novel1$similarity)
t.test(novel4$similarity, novel2$similarity)
t.test(novel4$similarity, novel3$similarity)

t.test(lolita$similarity, pale$similarity)
t.test(lolita$similarity, rabbit$similarity)
t.test(pale$similarity, rabbit$similarity)
