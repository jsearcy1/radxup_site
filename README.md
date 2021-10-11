# About

# Installation

# Usage
1. Download Data for your county

```rdx_get_data [-h] [--year year] S C V```

where S is a state for example Oregon, C is a county for example Lane, V is a cenus variable from the list provided 
here: https://api.census.gov/data/2015/acs/acs5/variables.html
for example

`rdx_getdata.py Oregon Lane B01003_001E --year 2019`

Please be patient this step may take awhile

2. Run Optimization
Two new options the number of sites to optimize and the number of cores to use when calculating the distance matrix
  './rdx_optimize.py Oregon Lane B01003_001E 5 --cores=12'

3. Visualize 
