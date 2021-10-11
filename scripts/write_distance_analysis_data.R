library(lme4)
library(lmerTest)
library(haven)
library(readxl)
library(readr)
library(dplyr)
library(performance)
#Load Data
weekly_case_data <- read_csv("Oregon_Weekly_Counts.csv")
weekly_vaccine_data <- read_csv("Oregon_Weekly_Vaccine_Data.csv")
OR_Pop <- read_csv("OR_Pop.csv")
flp_site_data <- read_csv("~/radxup_clean/scripts/flp_data.csv")
all_event_data <- read_sav("RADX YEAR1.SITE.DATA.NoCancel.sav")

# Standardize Column Names
flp_site_data$uo_site_id <- flp_site_data$'UO Site ID'
weekly_case_data$County <- weekly_case_data$county
weekly_vaccine_data$County<-gsub(" County","",weekly_vaccine_data$Recip_County)

#Add Flag for Mexican Consulate Event
flp_site_data$mc_event <- startsWith(flp_site_data$uo_site_id,"MC")


# Combine Data
# Add population to Case Data
weekly_case_data <- merge(weekly_case_data,OR_Pop,'County') 
# Add GIS Data to Event Data Case Data
flp_event_data=merge(all_event_data,flp_site_data,'uo_site_id',all=FALSE)
# Add Case Data
#flp_event_data=merge(flp_event_data,weekly_case_data,by=c('calendar_week','County')) 
# Add Vaccine Data
#flp_event_data=merge(flp_event_data,weekly_vaccine_data,by=c('calendar_week','County')) 


#Add Some Transformed Variables
#flp_event_data$log_uvpop <- log(flp_event_data$Population_Assigned*(1-flp_event_data$Series_Complete_Pop_Pct/100))
flp_event_data$log_pop <- log(flp_event_data$Population_Assigned)
#flp_event_data$log_unemp <- log(flp_event_data$UNEMP_ZP)
flp_event_data$log_vc <- log(flp_event_data$vacpct/100.)
#flp_event_data$log_bg <- log(flp_event_data$LX_BG)
#flp_event_data$log_zp <- log(flp_event_data$LX_ZP)
flp_event_data$casespc <- flp_event_data$cases/flp_event_data$Population
flp_event_data$drive_10min <- flp_event_data$Average_Drivetime/60./10.
#flp_event_data$log_fampov <- flp_event_data$FAMPOV_ZP


#Some Basic Filters to remove sites with known problems LA3 had a unique outreach from J4 school district
#JA7 had events cancled on some dates
flp_event_data<-filter(flp_event_data, cancelled ==0)

flp_event_data<-filter(flp_event_data, uo_site_id != 'LA3')
#flp_event_data<-filter(flp_event_data, uo_site_id != 'JA7' & calendar_week != 25 & calendar_week != 33) #These events were canceled



###Add Event Type Variables
#Type 1 = Control Event
#Type 2 = Outreach Intervention Event
# Type 2 = Site add after intervention
# Type 3 = Site add after intervention
# Type 4 = Mexican Consulate Event


#Set MC Consulate ITT events to 0 since this intervention does not involve outreach 
flp_event_data[flp_event_data$mc_event,]$ITT <- 0

#New sites have ITT set to zero
flp_event_data$new_site<-is.na(flp_event_data$ITT)
flp_event_data[is.na(flp_event_data$ITT),]$ITT <- 0. 

flp_event_data$event_type1<-!flp_event_data$ITT & !flp_event_data$mc_event & !flp_event_data$new_site
flp_event_data$event_type2<-as.logical(flp_event_data$ITT)
flp_event_data$event_type3<-flp_event_data$new_site
flp_event_data$event_type4<-flp_event_data$mc_event



write_csv(flp_event_data,"Distance_Analysis_Data.csv")
