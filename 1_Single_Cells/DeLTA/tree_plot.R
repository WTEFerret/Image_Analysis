#title           : plot_tree.R
#description     : 
#author          : Tobias Wechsler
#date            : 2024/04/16
#version         : 
#usage           : The data provided must from a single imaged position
#notes           :
#R_version       : 4.3.0
#=Packages==============================================================================================================

library(dplyr)
library(ggplot2)
library(ggtree)

#=Functions=============================================================================================================

# create a cid for each cell
set_cid <- function(id, daugthers){
  cdivs <- 0
  divs <- rep(0, length(daugthers))
  for (i in 1:length(daugthers)) {
    if (!is.na(daugthers[i])){
      cdivs = cdivs + 1
    }
    divs[i] <- cdivs
  }
  
  return(paste(id, divs, sep = '_'))
}

# Set the daughter id for the first daughter cell
set_did1 <- function(id, daugthers){
  did <- NA
  divs <- rep(NA, length(daugthers))
  for (i in length(daugthers):1) {
    
    divs[i] <- did
    
    if (!is.na(daugthers[i])){
      if (is.na(did)){
        did <- sum(!is.na(daugthers))
      } else {
        did <- did - 1
      }
    }
  }
  return(ifelse(is.na(divs), NA,paste(id, divs, sep = '_')))
}

# Set the daughter id for the second daughter cells
set_did2 <- function(id, daugthers){
  did <- NA
  dids <- rep(NA, length(daugthers))
  for (i in length(daugthers):1) {

    dids[i] <- did
    
    if (!is.na(daugthers[i])){
      did = daugthers[i]
    }
  }
  
  return(ifelse(is.na(dids), NA,paste(dids, 0, sep = '_')))
}

# Get all cell ids belonging to the same lineage
get_lin <- function(cid, df) {
  
  if (is.na(cid)) {
    return(NA)
  }
  did1 <- df[which(df$cid==cid), 'did1']$did1
  did2 <- df[which(df$cid==cid), 'did2']$did2
  no.did <- is.na(did2) & is.na(did2)
  if (no.did){
    return(cid)
  } else {
    return(c(cid, get_lin(did1, df), get_lin(did2, df)))
  }
}

# Recursive function to get the lineage tree in Newick format from daughter IDs
get_tree <- function(id, data){
  d1 <- as.character(data[which(data$cid==id), 'did1'][[1]])
  d2 <- as.character(data[which(data$cid==id), 'did2'][[1]])
  lfs <- data[which(data$cid==id), 'lifespan']
  
  if (is.na(d1) | is.na(d2)){
    return(paste(id,lfs, sep=':'))
  } else {
    
    return(paste(paste('(',get_tree(d1, data),',', get_tree(d2, data),')', sep = ''), paste(id,lfs, sep=':'), sep=''))
  }
}


#=Data==================================================================================================================

data <- read.csv('results.csv', sep = ',')

# Since the ID stays the same after divisions we have to add a cid
# that consist of two numbers, the id and the number of division
# e.g 0_1 for the cell with the id 0 after the first division 
# here we also create two new columns indicating the cid of the 
# two daughter cells (did1 and did2)
data <- data %>% group_by(id) %>% mutate(cid = set_cid(id, daughters),
                                      did2 = set_did2(id, daughters), 
                                      did1 = set_did1(id, daughters))

# Calculate the per cell mean expression, the first frame and the lifespan
data.mean <- data %>% group_by(cid, did1, did2) %>% summarise(cell.mean = mean(IntDen), 
                                                              first.frame = min(frames), 
                                                              lifespan = length(frames))


# Get all cid present in the first frame to define the lineages growing from them
root_cids <- data.mean %>% filter(first.frame==0) %>% dplyr::select(cid)

data.mean$lineage = NA

for (lid in root_cids$cid){
  lin_ids = get_lin(lid, data.mean)
  data.mean[which(data.mean$cid %in% lin_ids), "lineage"] <- lid
}



#=Plot==================================================================================================================

# Set the root cell ID of the tree
root_id <- '11_0'
root_cell <- data.mean %>% filter(cid==root_id)
root_len <- root_cell$lifespan[1]
data.lin <- data.mean %>% filter(lineage==root_id)

# make the tree from data
tree <- get_tree(root_id, data.lin)
tree <- paste(tree, ';', sep='')
Tree <- read.tree(text = tree)

# Combine the tree with the data
nodes <- data.frame(order = seq(1,length(c(Tree$tip.label, Tree$node.label))),
                    cid=c(Tree$tip.label, Tree$node.label))

nodes <- merge(nodes, data.lin, by='cid', all.x = T)
nodes <- nodes %>% arrange(order)


plot.tree.pvd <- ggtree(Tree, aes(color=nodes$cell.mean), root.position = root_len, size=0.5) +
  geom_rootedge(size=1, color='blue') +
  geom_nodepoint(size=1) +
  theme_tree2() +
  scale_color_gradientn(name='',colours=c("grey", "lightblue","blue")) +
  theme() +
  xlab("Time (h)");plot.tree.pvd
