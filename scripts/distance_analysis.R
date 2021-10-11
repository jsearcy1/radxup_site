library(lme4)
library(lmerTest)
library(haven)
library(readxl)
library(readr)
library(dplyr)
library(performance)

#Load Data
flp_event_data=read_csv("Distance_Analysis_Data.csv")


fit_data<-data.frame(flp_event_data)
for (var in c("UNEMP_ZP","FAMPOV_ZP","MDINC_ZP","MDAGE_ZP",'casespc')){
  fit_data[var] <- scale(flp_event_data[var]);
  }



ml_latinx <-glmer(
    tested_latinx~drive_10min+UNEMP_ZP+FAMPOV_ZP+
            MDINC_ZP+MDAGE_ZP+(1|uo_site_id)+casespc+
            event_type2+event_type3+event_type4+log_vc+log_pop,
            fit_data,
            family= poisson,
            control=glmerControl(optCtrl = list(maxfun=2e7),optimizer='bobyqa')
#            verbose=3
    )


            
check_model(ml_latinx)
summary(ml_latinx)
sjPlot::tab_model(ml_latinx,pred.labels=c('(Intercept)','Average Drive Time','Unemployment Rate','Poverty Rate','Median Income','Median Age','New County Cases PC','Intervention Site','Non-CT/Non-MC Site','MC Site','Log Vaccine Rate','Log Local Population'))

