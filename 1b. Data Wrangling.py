"""
This script contains functions for creating datasets for the analysis.
The functions create the following datasets:
1. Reported domestic violence data using an API:
    https://data.cityofchicago.org/resource/dwme-t96c.csv?$limit=300000

2. Chicago Health Atlas Data used for identifying independent variables:
    https://chicagohealthatlas.org/

3. Community Area Population data: 
    https://datahub.cmap.illinois.gov/datasets/CMAPGIS::community-data-snapshots-raw-data-2014-2022/explore?layer=21
    
4. Community Area Data: This data is drawn from the Chicago Health Atlas and
contains the mapping of Community Area to the Community Area code. This data is 
used for facilitating a merge between the crime data (dependent variable) and 
the independent variable data 

5. Independent variable Key: this function extracts the independent variable key
from the downloaded Chicago Health altas data for identifying variables

    

"""


import os
import pandas as pd
import geopandas
import numpy as np

import statsmodels.api as sm
import statsmodels.formula.api as smf

#Defining Base paths for calling the datafiles

BASE_PATH=r'C:\Users\tanay\OneDrive\Documents\GitHub\final-project-caraya\Data'

path_community_area = os.path.join(BASE_PATH,'Chicago Health Atlas Data.csv')
path_police_sent = os.path.join(BASE_PATH,'police_sentiment_by_comm_area_1.csv')
path_population = os.path.join(BASE_PATH,'CA_Population.csv')


#Defining functions

def load_crime_data():
    csv_name = "2021_crime_data.csv"
    crime_url_2021 = "https://data.cityofchicago.org/resource/dwme-t96c.csv?$limit=300000"
    path_crime = os.path.join(BASE_PATH,csv_name)
    
    if os.path.exists(path_crime):
        print(f"Reading 2021 crime data from existing csv file.")
        df = pd.read_csv(path_crime)
    else:
        print(f"Downloading 2021 crime data via API.")
        df = pd.read_csv(crime_url_2021)
        df.to_csv(path_crime)
    
    #renaming column in crime data to facilitate merge
    df.rename(columns={'Community Area':'GEOID'},inplace=True)
    return df

def load_community_area_data():
    #importing data from chicago health atlas for the 
    community_area_data = pd.read_csv(path_community_area)
    #only keeping the community area and code in this dataset to facilitate mapping
    community_area_data = community_area_data[['Name','GEOID']]
    community_area_data = community_area_data.drop(community_area_data.index[0])
    return community_area_data  

def load_pop_data():
    pop_data = pd.read_csv(path_population)
    pop_20 = pop_data[['GEOID','GEOG','2020_POP']]
    return pop_20

def load_indep_var_data():
    #importing the chicago health atlas data
    path_indepvar = os.path.join(BASE_PATH, 'indep_var.csv')
    indepvar_data = pd.read_csv(path_indepvar)
    return indepvar_data

def create_indep_var_key(indepvar_data):
    #extracting the variable key from the dataframe to know independent variable names
    indepvar_key = indepvar_data.head(1).transpose().reset_index()
    indepvar_data = indepvar_data.drop(0)
    #the following code replaces the hyphens to avoid having hyphens read as arithmetic operation
    indepvar_key['index'] = indepvar_key['index'].apply(lambda x: x.replace('-', '_'))#Reference: ChatGPT
    return indepvar_key

def create_regression_data(crime_data, community_area_data, police_sentiment_by_comm_area,indepvar_data, pop_20,):
    crime_data_ca = pd.merge(crime_data, community_area_data, how='outer', on=['GEOID'])
    #aggregating the data based on community area
    crime_data_aggr = crime_data_ca.groupby(['Name'])['Domestic', 'Arrest'].sum().reset_index()
    #renaming columns to facilitate merge
    police_sentiment_by_comm_area.rename(columns={'comm_area_num':'GEOID'}, inplace=True)
    reg_data = pd.merge(crime_data_aggr,
                      indepvar_data,
                      how='outer',
                      on=['Name'])
    reg_data_ps = pd.merge(reg_data,
                         police_sentiment_by_comm_area, 
                         how='outer', 
                         on=['GEOID'], 
                         indicator=True)

    reg_data_final = pd.merge(reg_data_ps, 
                         pop_20, 
                         how='outer', 
                         on=['GEOID'], 
                         indicator='_merge_indicator')
    #creating a new column for the DV rate
    reg_data_final['DV_rate'] = reg_data_final['Domestic']/reg_data_final['2020_POP']
    reg_data_final['DV_per_thousand'] = reg_data_final['DV_rate']*1000
    reg_data_final.columns = reg_data_final.columns.str.replace('-', '_')
    return reg_data_final

#calling functions

crime_data = load_crime_data()

community_area_data = load_community_area_data()

pop_20 = load_pop_data()

indepvar_data = load_indep_var_data()

indepvar_key = create_indep_var_key(indepvar_data)


#loading police sentiment data from part 1a of Data Wrangling
police_sentiment_by_comm_area = pd.read_csv(path_police_sent)

reg_data_final = create_regression_data(crime_data,
                                      community_area_data,
                                      police_sentiment_by_comm_area,
                                      indepvar_data,pop_20)
