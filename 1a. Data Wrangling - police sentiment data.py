# carolinedavidson
# Python II Final Project - Fall 2023
"""
This script aggregates survey data from monthly surveys about police sentiment 
in each police district. The data are fitlered for 2021, aggregated to an average
at the police district level, and then converted from the police district to the
community area level for compatibility with our other community area-level variables.
The script outputs a csv file with one row per community area and the average value
in 2021 of relevant variables.

police sentiment data from:
    https://catalog.data.gov/dataset/police-sentiment-scores
police districts shapefiles from:
    https://gis.chicagopolice.org/datasets/ChicagoPD::police-district-boundary-view/explore
community area shapefiles from:
    https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6
"""
import pandas as pd
import os
import zipfile
import geopandas
from tobler.area_weighted import area_interpolate

BASE_PATH = r'/Users/Caroline/Dropbox/*Harris/Classes/Q4/Python II/Final Project/final-project-caraya'

# DEFINE FUNCTIONS

def unzip_load_shapefile(file_name, folder_name, shapefile_name):
    # consulted for working with zip file: https://docs.python.org/3/library/zipfile.html
    zip_file_path = os.path.join(BASE_PATH, "Data","shapefiles", file_name)
    folder_path = os.path.join(BASE_PATH, "Data", "shapefiles", folder_name)
    
    with zipfile.ZipFile(zip_file_path, mode='r') as zip:
        zip.extractall(folder_path)
    
    df = geopandas.read_file(os.path.join(folder_path, shapefile_name))
    return df


def load_agg_police_sentiment_data(year):
    ps_data = pd.read_csv(os.path.join(BASE_PATH, "Data", "police sentiment data", "Police_Sentiment_Scores.csv"))

    ps_columns_to_keep = ["DISTRICT",
                          "START_DATE", "END_DATE",
                          "SAFETY", "S_SEX_FEMALE", 
                          "TRUST", "T_SEX_FEMALE",
                          "T_LISTEN", "T_LISTEN_SEX_FEMALE",
                          "T_RESPECT", "T_RESPECT_SEX_FEMALE"]

    police_sentiment = ps_data[ps_columns_to_keep]
    """
    The different variables in police_sentiment are averages of answers to 
    the following questions on a scale from 0 to 100. Each variable is also 
    available disaggregated by sex. We focus on the female response variables.
    
    SAFETY: 'When it comes to the threat of crime, how safe do you feel 
    in your neighborhood?''
    
    T_LISTEN: 'How much do you agree with this statement? The police in my
    neighborhood listen to and take into account the concerns of local residents.'
        
    T_RESPECT: 'How much do you agree with this statement? The police in my
    neighborhood treat local residents with respect.'
    
    TRUST is an average of T_LISTEN and T_RESPECT. 
    """
    police_sentiment["start_year"] = police_sentiment["START_DATE"].str[-4:].astype(int)
    police_sentiment["end_year"] = police_sentiment["END_DATE"].str[-4:].astype(int)

    police_sentiment = police_sentiment[(police_sentiment["start_year"] == year) &
                                        (police_sentiment["end_year"] == year) &
                                        (police_sentiment["DISTRICT"].notna())]

    police_sentiment_district = police_sentiment.drop(columns=["START_DATE", 
                                                               "END_DATE", 
                                                               "start_year", 
                                                               "end_year"], axis=1).groupby("DISTRICT").mean().reset_index()

    police_districts["DISTRICT"] = police_districts["DISTRICT"].astype(int)

    police_data_district = police_districts.merge(police_sentiment_district, 
                                                  left_on="DISTRICT", 
                                                  right_on="DISTRICT", 
                                                  how="outer",
                                                  indicator=True)
   
    merge_audit = police_data_district["_merge"].value_counts() 
    print(merge_audit)

    police_data_district = police_data_district.drop(columns=["OBJECTID", "_merge"])
    
    # save version of this data to csv for use in static plots script
    police_data_district.drop(columns="geometry").to_csv(os.path.join(BASE_PATH, 
                                                                      "Data", 
                                                                      "police sentiment data",
                                                                      "police_sentiment_by_district.csv"), 
                                                         index=False)
    return police_data_district


def spatial_join(community_areas, police_data_district):
    
    community_areas = community_areas.to_crs(police_data_district.crs)
    community_areas = community_areas.drop(columns=["area", "area_numbe", 
                                                    "comarea", "comarea_id",
                                                    "perimeter", "shape_len"])
    community_areas = community_areas.rename({"area_num_1": "comm_area_num",
                                              "shape_area": "ca_shape_area"}, 
                                             axis=1)

    police_data_district = police_data_district.rename({"SHAPE__Are": "pd_shape_area",
                                                        "SHAPE__Len": "pd_shape_length"}, axis=1)

    # consulted this site for how to do a spatial join with weighted aggregation:
        # https://geographicdata.science/book/notebooks/12_feature_engineering.html
    police_sentiment_comm_area = area_interpolate(
        source_df=police_data_district.to_crs(epsg=3311),
        target_df=community_areas.to_crs(epsg=3311),
        intensive_variables=["SAFETY", "S_SEX_FEMALE",
                             "TRUST", "T_SEX_FEMALE",
                             "T_LISTEN", "T_LISTEN_SEX_FEMALE",
                             "T_RESPECT", "T_RESPECT_SEX_FEMALE"],
    )

    police_sentiment_comm_area = police_sentiment_comm_area.to_crs(police_data_district.crs)
    
    # merge back in columns with community area names and numbers that get dropped when interpolating
    comm_area_ids = community_areas[["comm_area_num", "community"]]

    police_sentiment_comm_area = pd.merge(comm_area_ids, 
                                          police_sentiment_comm_area,
                                          left_index=True,
                                          right_index=True)
    return police_sentiment_comm_area


# CALL FUNCTIONS

police_districts = unzip_load_shapefile("Police_District_Boundary_View-shp.zip", 
                                        "police district boundaries", 
                                        "Police_District_Boundary_View.shp")

community_areas = unzip_load_shapefile("Boundaries - Community Areas (current).zip", 
                                       "community area boundaries", 
                                       "geo_export_75cc0f3f-cd68-496a-bbb6-489e8c562a16.shp")

police_data_district = load_agg_police_sentiment_data(2021)

police_sentiment_comm_area = spatial_join(community_areas, police_data_district)

police_sentiment_comm_area.drop(columns="geometry").to_csv(os.path.join(BASE_PATH, 
                                                                        "Data", 
                                                                        "police sentiment data",
                                                                        "police_sentiment_by_comm_area.csv"), 
                                                           index=False)
