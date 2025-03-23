#title           : collect_results.R
#description     : Collects and combines results
#author          :
#date            :
#version         : 
#usage           : Provide the path containing all your analysed positions
#notes           :
#R_version       : 3

 
#=Packages==============================================================================================================

library(dplyr)
library(tidyr)

#=Functions=============================================================================================================

read_results <- function(res_path){
  pos_name = basename(dirname(res_path))
  data = read.csv(res_path, sep = ',')
  data$position = pos_name
  return(data)
}

#=Data==================================================================================================================

results_path = 'Example/'

results = list.files(path = results_path, pattern = ".csv$", recursive = TRUE, full.names = TRUE)
results_list = lapply(results, read_results)
data = bind_rows(results_list)

# Separate label into different columns
data = data %>% separate(col = Label, into = c('IMG', 'ROI','INFO'), sep = ':')

# is colony fluorescent tagged
data$tag = startsWith(d2$ROI, 'p')

# is there a second layer
data$dlayer = endsWith(d2$ROI, 'd')

# set colony id
data = data %>% separate(col = ROI, into = c('colony', 't'), sep = 't')


