#' This Script Takes the NYT Cumulative Case data File and Outputs Oregon's 
#' Weekly new cases and new deaths by County

case_diff <- function(vec){
  if(is.numeric(vec)){
    return( max(vec)-min(vec))
  }
  else{
    return(vec[[1]])
  }
}

case_data <- read_csv("/data/covid-19-data/us-counties.csv")
case_data <- filter(case_data, date >=  as.Date('2021-01-01') & state=='Oregon') # Select Study Year

case_data$calendar_week <-as.numeric(format(as.Date(case_data$date), "%W"))

weekly_case_data=aggregate(case_data, list(case_data$calendar_week,case_data$county),case_diff)
weekly_case_data$calendar_week<-weekly_case_data$Group.1 


weekly_case_data= subset(weekly_case_data, select = -c(Group.1,Group.2,date) )
write_csv(weekly_case_data,"Oregon_Weekly_Case_Data.csv")


          
          