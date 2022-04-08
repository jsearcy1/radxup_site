# About

# Installation
Due to some dependancies Anaconda is the easiset way to install this package

``` conda create -n myenv
    conda activate myenv
    conda install geopandas
    pip install git+ssh://git@github.com/jsearcy1/radxup_site.git
```


# Usage

To Run all steps of the process use the command

```create_proposals state county censusvar year n_sites```

* The following command will create proposals for 5 sites within Lane County in Oregon optimizing to reach the population definied by census var B01003_001E

```create_proposals Oregon Lane B01003_001E 2019 5```

# Individual Steps

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
