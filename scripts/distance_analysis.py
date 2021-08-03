import pickle
import csv
import matplotlib.pyplot as plt
import numpy as np
import pystan
from sklearn.linear_model import LinearRegression
import pandas as pd

site_data= pickle.load(open('distance_analysis.pk','rb'))

all_sites={}
for county in site_data:
     for s in site_data[county]:
          all_sites[s['uo_site_id']]=s
     

event_data={}
all_data=[]
with open('Phase2_clean.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if row['uo_site_id']!=event_data:
             event_data[row['uo_site_id']]=[]
         event_data[row['uo_site_id']].append(row)
         all_data.append(row)
sites=list(event_data.keys())



df=pd.DataFrame()
tested=[int(i['tested_latinx']) for i in all_data]

for var in ['calendar_week','MDINC_ZP','UNEMP_ZP','FAMPOV_ZP','MDAGE_ZP','itt','LX_BG','tested_latinx']:
     df[var]=[float(i[var]) for i in all_data]


df['Population']=[np.log(float(all_sites[i['uo_site_id']]['Served_Pop'])) for i in all_data]
df['DriveTime']=[float(all_sites[i['uo_site_id']]['Avg_Drive'])/60. for i in all_data]
df['Sites']=[sites.index(i['uo_site_id']) for i in all_data]
df['MDINC_ZP'] =(df['MDINC_ZP'] -np.mean(df['MDINC_ZP']))/np.std(df['MDINC_ZP'])
df['MDAGE_ZP'] =(df['MDAGE_ZP'] -np.mean(df['MDAGE_ZP']))/np.std(df['MDAGE_ZP'])
df['LX_BG'] =np.log(df['LX_BG'] +1)

df.to_csv('distance.csv')


ddict={}
for s in sites:
     for v in all_sites[s]:
          if v in ['routes']:continue
          if v not in ddict:
               ddict[v]=[]
          ddict[v].append(all_sites[s][v])
df_agg=pd.DataFrame.from_dict(ddict)


agg_tested=[]
for s in sites:
     agg_tested.append( sum([int(i['tested_latinx']) for i in all_data if i['uo_site_id']==s]) )
df_agg['tested_latinx']=agg_tested
df_agg.to_csv('distance_agg.csv')

#week=[float(i['calendar_week']) for i in all_data]
#mdinc=[float(i['MDINC_ZP']) for i in all_data]
#unemp=[float(i['UNEMP_ZP']) for i in all_data]
#fpov=[float(i['FAMPOV_ZP']) for i in all_data]
#mdage=[float(i['MDAGE_ZP']) for i in all_data]





#pop=[np.log(float(all_sites[i['uo_site_id']]['Served_Pop'])) for i in all_data]
#dt=[float(all_sites[i['uo_site_id']]['Avg_Drive'])/60. for i in all_data]


#dt=[ all_sites[s]['Avg_Drive'] for s in sites]
#pop=[ all_sites[s]['Served_Pop'] for s in sites]


#pop_bg=[ float(event_data[s][0]['LX_BG']) for s in sites]
#pop_zp=[ float(event_data[s][0]['LX_ZP']) for s in sites]
#itt=[ float(event_data[s][0]['itt']) for s in sites]

#x=np.concatenate([np.expand_dims(i,-1) for i in [pop,dt,week,itt,np.random.normal(size=len(pop))]],-1)
#y=np.array(tested)
#y=y/np.array(pop)


import statsmodels.api as sm
import statsmodels.formula.api as sm
from statsmodels.genmod.bayes_mixed_glm import PoissonBayesMixedGLM

l2_variables=['MDINC_ZP','UNEMP_ZP','FAMPOV_ZP','MDAGE_ZP','itt','LX_BG','Population','DriveTime']
l1_variables=['calendar_week']


prb=PoissonBayesMixedGLM(df['tested_latinx'],df[l2_variables],np.expand_dims(df[l1_variables],0),df['County'])


pr = smf.mixedlm("tested_latinx ~ DriveTime", df, family=sm.families.Poisson(),groups=df['County']).fit()
print(pr.summary())

from sklearn.linear_model import LinearRegression
lmodel = LinearRegression()
lmodel.fit(x, y)
r_sq = lmodel.score(x, y)
print('intercept:', lmodel.intercept_)
print('slope:', lmodel.coef_)
#x=np.concatenate([np.expand_dims(i,0) for i in [pop,dt,week,itt]],0)
dsfasdf

model = """
data {
  int<lower=0> N; 
  int y[N];
  vector[N] itt;
  vector[N] week;
  vector[N] pop;
  vector[N] drive_time;
} 
parameters {
  real beta[5];
  real avg_eff;
} 

transformed parameters {
  vector[N] mu;
  vector[N] mylogit;
  vector[N] eff; 
  for (i in 1:N){
    mylogit[i] = avg_eff+beta[1]*itt[i]+beta[2]*week[i]+beta[3]*drive_time[i];
    eff[i] = 1/(1-exp(-1*mylogit[i]));
    mu[i] = pop[i]*eff[i];
   }
}
model {
  avg_eff ~ uniform(-10,10);
  beta ~ uniform(-10,1);
  y ~ poisson(mu);
}"""

stan_data_dict = {'N': len(pop),
                  'pop':pop,
                  'drive_time':dt,
                  'week':week,
                  'itt': itt,
                  'y': tested}

stan_fit = pystan.stan(model_code=model, 
                         data=stan_data_dict, iter=1000, chains=2)










width = 0.30
x = np.arange(len(sites))  # the label locations
fig, ax = plt.subplots()
rects1 = ax.bar(x - width, pop_bg, width, label='LX BG')
rects2 = ax.bar(x , pop, width, label='LX SERVED')
rects3 = ax.bar(x + width, pop_zp, width, label='LX ZP')
ax.set_xticks(x)
ax.set_xticklabels(sites)
ax.legend()


fig.tight_layout()

plt.show()
