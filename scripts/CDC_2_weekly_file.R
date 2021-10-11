#' This Script Takes the CDC Cumulative Case data File and Outputs Oregon's 
#' Weekly vaccine rates using the maximum value of daily data for each week


vaccine_data <- read_csv("COVID-19_Vaccinations_in_the_United_States_County.csv")

vaccine_data <- filter(vaccine_data, as.Date(Date,"%m/%d/%Y") >=  as.Date('01/01/2021',"%m/%d/%Y") & Recip_State=='OR') # Select Study Year

vaccine_data$calendar_week <-as.numeric(format(as.Date(vaccine_data$Date,"%m/%d/%Y"), "%W"))



weekly_vaccine_data <- aggregate(vaccine_data,list(vaccine_data$calendar_week,vaccine_data$Recip_County),max)

weekly_vaccine_data= subset(weekly_vaccine_data, select = -c(Group.1,Group.2,Date) )
write_csv(weekly_vaccine_data,"Oregon_Weekly_Vaccine_Data.csv")
