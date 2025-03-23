#title           : process_results.R
#description     : Clusters cells into groups\colonies and calculates the distance of each cell to the edge of a colony
#author          : Tobias Wechsler
#date            : 2021/03/01
#version         : 
#usage           : 
#notes           :
#R_version       :
#=======================================================================================================================

library(ggplot2)
library(tidyr)
library(dplyr)
library(plyr)
library(alphahull)




# Calculate the distance of a point to a linesegment
getDist2Line <- function(x0, y0, x1, y1, x2, y2){
  distance = rep(NA, length(x0))
  
  v = as.vector(c(x1,y1))
  w = as.vector(c(x2,y2))
  l2 = (y2-y1)**2 + (x2-x1)**2
  
  for (i in 1:length(distance)){
    p = as.vector(c(x0[i],y0[i]))
    
    t = max(0, min(1, ((p-v)%*%(w-v))/l2))
    pp = v + t * (w - v)
    distance[i] = sqrt( (pp[1]-p[1])^2 + (pp[2]-p[2])^2)
    
  }
  return(distance)
}


# Determines cells on the edge of the colony and returns the distance to the edge of every cell
getDist <-function(x,y){
  temp = data.frame(x=x,y=y)
  
  temp$dist.to.edge = 0
  
 
  
  hull = tryCatch(ahull(temp, alpha=30), error=function(e) list())
  if (length(hull)==0){
    
    temp$dist.to.edge = 0
    return(temp$dist.to.edge)
  }
  if (sum(hull$ashape.obj$alpha.extremes) == length(x)){
    temp$dist.to.edge = 0
    return(temp$dist.to.edge)
  } else {
    
    temp[hull$ashape.obj$alpha.extremes,]$edge = TRUE
    edg = data.frame(hull$ashape.obj$edges)
    old.dists = getDist2Line(temp$x, temp$y,
                             edg[1,'x1'], edg[1,'y1'],
                             edg[1,'x2'], edg[1,'y2'])
    
    for (l in 1:nrow(edg)){
      dists = getDist2Line(temp$x, temp$y,
                           edg[l,'x1'], edg[l,'y1'],
                           edg[l,'x2'], edg[l,'y2'])
      smlr = dists < old.dists
      old.dists[smlr & !is.na(smlr)] = dists[smlr & !is.na(smlr)]

    }
    
    return(old.dists)
    
  }
}

filename = 'example/Results.csv'
 
data<-read.csv(filename, header=T, stringsAsFactors=TRUE);names(data)

# Create and remove some columns
data <- data %>% separate(Label, into=c('image','roi'), sep=':')
data$image <- NULL
data$X.1 <- NULL
data$XM <- NULL
data$YM <- NULL

# Pivot wider to have one line per ROI
data.1 = pivot_wider(data, names_from = Channel, values_from = c(Mean,Min,Max,IntDen,RawIntDen), names_sep = ".")

# Show cell position from beginning, middle and end
t.snap = c(min(data.1$Time), floor(max(data.1$Time)/2), max(data.1$Time))
ggplot(dplyr::filter(data.1, Time %in% t.snap), aes(x=X, y=Y)) + geom_point(alpha=0.5) + facet_grid(~Time)

# Specify the number of colonies to be clustered
n.cluster = 1

# Calculate euclidean distance between cells 
dist.Matrix = dist(cbind(data.1$X,data.1$Y), method = "euclidean")

# Cluster according to distance an group in k groups
cluster = hclust(dist.Matrix, method="ward.D")
data.1$Group = cutree(cluster, k=n.cluster)

# Show results of clustering
ggplot(filter(data.1, Time %in% t.snap), aes(x=X, y=Y, color=as.factor(Group))) + geom_point() + facet_grid(~Time)

# Calculate the distance to the edge
data.2 = plyr::ddply(data.1, .(Time, Group), mutate, dist.to.edge=getDist(X,Y))
data.2$edge = FALSE
data.2[which(data.2$dist.to.edge==0), 'edge'] = TRUE


ggplot(dplyr::filter(data.2, Time %in% t.snap)) +
  geom_point(aes(x=X, y=Y, color=dist.to.edge, shape = edge)) + facet_grid(~Time)


write.csv(data.2, paste(dirname(filename), basename(filename), sep = '_'))
