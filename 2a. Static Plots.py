# carolinedavidson
# Python II - Final Project
# Fall 2023
"""
The first part of this script creates a graph of reported DV crimes in Chicago and 
national domestic violence hotline calls from Chicago for January 2015 through the 
end of June 2020. If "DV_calls_by_semester.csv" doesn't exist locally, then 
script 3 must be run before this script.

The second part of this script generates maps of police sentiment in Chicago. This
data was transformed from the police district level to the community area level
in script 1a. These graphs serve to visually inspect the quality of this spatial
re-aggregtion by displaying the data at the original and reaggregated levels.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import zipfile
import geopandas


BASE_PATH = r'/Users/Caroline/Dropbox/*Harris/Classes/Q4/Python II/Final Project/final-project-caraya'

"""
VISUALIZATION 1: Domestic Violence over Time
"""
# DEFINE FUNCTIONS ETC.

crime_data_info = [
    #(year, API link),
    (2015, "https://data.cityofchicago.org/resource/vwwp-7yr9.csv?$limit=300000"),
    (2016, "https://data.cityofchicago.org/resource/kf95-mnd6.csv?$limit=300000"),
    (2017, "https://data.cityofchicago.org/resource/d62x-nvdr.csv?$limit=300000"),
    (2018, "https://data.cityofchicago.org/resource/3i3m-jwuy.csv?$limit=300000"),
    (2019, "https://data.cityofchicago.org/resource/w98m-zvie.csv?$limit=300000"),
    (2020, "https://data.cityofchicago.org/resource/qzdf-xmn8.csv?$limit=300000")
    ]

def download_process_crime_data_csv(year, url):    
    csv_name = str(year) + "_crime_data.csv"
    csv_path = os.path.join(BASE_PATH, "Data", "yearly reported crimes data", csv_name)
    
    if os.path.exists(csv_path):
        print(f"Reading {year} crime data from existing csv file.")
        df = pd.read_csv(csv_path)
    else:
        print(f"Downloading {year} crime data via API.")
        df = pd.read_csv(url)
        df.to_csv(csv_path)
        
    # aggregate data to 6-month periods to match DV hotline data periods
    df["datetime"] = pd.to_datetime(df["Date"], 
                                    format="%m/%d/%Y %I:%M%S %p", 
                                    errors="coerce")
    df["month"] = df["Date"].str[:2].astype(int)
    df["period"] = df["month"].apply(lambda month: "Semester 1" if 1 <= month <= 6
                                                   else "Semester 2" if 7 <= month <= 12
                                                   else "Error")
    df_domestic = df[df["Domestic"] == True]
    df_semester = df_domestic[["Domestic", "period"]].groupby("period").count().reset_index()
    df_semester["year"] = year
    return df_semester


def create_dv_timeseries_graph():
    df = dv_semester
    # define colors for two different variables, consulted: 
    # https://matplotlib.org/stable/gallery/color/named_colors.html#base-colors
    cpd = "darkblue"
    ndvh = "indigo"
    # relied heavily on Prof Clapp's Python I Lecture 14 slides for this graph
    sns.set()
    sns.set_style("white")
    fig, ax = plt.subplots()
    
    ax.plot(df["date"], df["reported"], color=cpd, marker="o", linestyle="dotted",
            label="Domestic Violence Incidents Reported to Chicago Police Department")
    ax.plot(df["date"], df["NaN"], color=ndvh, marker="o", linestyle="dashed",
               label="Calls from Chicago to the National Domestic Violence Hotline")
    
    ax2 = ax.twinx()
    ax2.plot(df["date"], df["calls"], color=ndvh, marker="o", linestyle="dashed",
             label="Calls from Chicago to the National Domestic Violence Hotline")
    
    ax.set_ylabel("Reported DV Incidents", color=cpd, fontweight="bold")
    ax2.set_ylabel("Calls to National DV Hotline", color=ndvh, fontweight="bold")
    
    # consulted for getting the y-axes custom colors:
    # https://www.tutorialspoint.com/how-to-change-the-color-of-the-axis-ticks-and-labels-for-a-plot-in-matplotlib
    ax.tick_params(axis="y", colors=cpd)  
    ax2.tick_params(axis="y", colors=ndvh)  
    
    # consulted for removing specific spine:
    # https://stackoverflow.com/questions/925024/how-can-i-remove-the-top-and-right-axis
    ax.spines["top"].set_visible(False) 
    ax2.spines["top"].set_visible(False)
        
    plt.title("Domestic Violence in Chicago", fontweight="bold")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
    annotation = "Points represent the total volume \n of reports or calls for the first \n or second half of each year."
    plt.figtext(0.6, 0.25, annotation, ha="center", fontsize=8)

    fig.savefig(os.path.join(BASE_PATH, "images", "dv_indicators.png"),
                dpi=300, bbox_inches='tight', pad_inches=0.25)
    sns.reset_defaults()
    plt.show()


# APPLY FUNCTIONS

# download and prepare crime data from CPD
crime_dataframes = {}
# note: this step can take a few minutes if the data does not exist locally
for year, url in crime_data_info:
    df_name = "crimes_" + str(year)
    df = download_process_crime_data_csv(year, url) 
    crime_dataframes[df_name] = df
    # consulted this site for above method of putting dfs in a dictionary: 
    # https://stackoverflow.com/questions/35709402/create-a-dictionary-of-dataframes

data_2015_2020 = pd.concat(crime_dataframes.values())

# load in DV Hotline data prepared in script 3
dv_calls = pd.read_csv(os.path.join(BASE_PATH, "Data", "DV hotline data", "DV_calls_by_semester.csv"))
dv_calls_semester = dv_calls[dv_calls["period"] != "annual"]

# merge and prepare data for graph with additional needed columns
dv_semester = pd.merge(dv_calls_semester,
                       data_2015_2020,
                       how="inner")

dv_semester["month"] = dv_semester["period"].apply(lambda x: 1 if x == "Semester 1" else 7)
dv_semester["day"] = 1
dv_semester["date"] = pd.to_datetime(dv_semester[["year", "month", "day"]])
dv_semester = dv_semester.rename(columns={"DV_hotline_calls_from_Chicago": "calls",
                                          "Domestic": "reported"})
dv_semester["NaN"] = np.NaN
dv_semester.to_csv(os.path.join(BASE_PATH, "Data", "time_series_graph_data.csv"))


create_dv_timeseries_graph()


"""
VISUALIZATION 2: Police Sentiment Scores
"""
# DEFINE FUNCTIONS ETC.

def unzip_load_shapefile(file_name, folder_name, shapefile_name):
    # consulted for working with zip file: https://docs.python.org/3/library/zipfile.html
    zip_file_path = os.path.join(BASE_PATH, "Data","shapefiles", file_name)
    folder_path = os.path.join(BASE_PATH, "Data", "shapefiles", folder_name)
    
    with zipfile.ZipFile(zip_file_path, mode='r') as zip:
        zip.extractall(folder_path)
    
    df = geopandas.read_file(os.path.join(folder_path, shapefile_name))
    return df


# create maps of police sentiment variables at district level and interpolated to community area level
def gen_map_pairs(var_name, var_descr, year):
    # gridspec: https://matplotlib.org/3.1.0/tutorials/intermediate/gridspec.html
    fig, axs = plt.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.3]})
    ax1, ax2 = axs

    # police district level map on left (original data)
    police_sentiment_district.plot(ax=ax1, 
                                   column=var_name, 
                                   edgecolor="black", 
                                   legend=False)
    ax1.axis("off")
    fig.text(0.32, 0.125, 
             "Average Level \n By Police District \n on scale of 0 - 100", 
             fontsize=10, 
             ha="center")    
    
    # community area level map on right (interpolated data)
    police_sentiment_comm_area.plot(ax=ax2, 
                                    column=var_name, 
                                    edgecolor="black", 
                                    legend=True)
    ax2.axis("off")
    fig.text(0.69, 0.125,
             "Average Level \n By Community Area \n on scale of 0 - 100", 
             fontsize=10, 
             ha="center")

    fig.text(0.475, 0.8, var_descr, fontsize=15, fontweight="bold", ha="center")
    fig.text(0.425, 0.5, "Interpolated -->")
    data_source = "Police Sentiment Scores Data from: https://catalog.data.gov/dataset/police-sentiment-scores"
    fig.text(0.25, 0.09, data_source, fontsize=5, style="italic", color="navy", va="center")
    # consulted for background color in line below: https://www.geeksforgeeks.org/matplotlib-figure-figure-text-in-python/
    fig.text(0.15, 0.09, year, fontsize=10, fontweight="bold", color="navy", va="center",
             bbox={"boxstyle":"square", 
                   "facecolor": 'gold', 
                   "edgecolor":'navy', 
                   "pad": 0.25})
    
    file_name = f"{var_descr} map - {year}.png"
    fig.savefig(os.path.join(BASE_PATH, "images", "police_sentiment_maps", file_name),
                dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.show()


variables_to_map = [
    #(variable_name, #variable_description), #year,
    ("SAFETY", "Feeling of Safety in Neighborhood", 2021),
    ("S_SEX_FEMALE", "Women Feel Safe in Neighborhood", 2021),
    ("TRUST", "Trust in Chicago Police Department", 2021),
    ("T_SEX_FEMALE", "Women's Trust in Chicago PD", 2021),
    ("T_LISTEN", "Feel Police Listen to Residents", 2021),
    ("T_LISTEN_SEX_FEMALE", "Women Feel Police Listen to Residents", 2021),
    ("T_RESPECT", "Feel Police Respect Residents", 2021),
    ("T_RESPECT_SEX_FEMALE", "Women Feel Police Respect Residents", 2021)
    ]


# CALL FUNCTIONS

# load police sentiment data aggregated in script 1a to district for 2021 and merge with shapefile
police_district = pd.read_csv(os.path.join(BASE_PATH, "Data", "police sentiment data", "police_sentiment_by_district.csv"))
districts = unzip_load_shapefile("Police_District_Boundary_View-shp.zip", 
                                 "police district boundaries", 
                                 "Police_District_Boundary_View.shp")

districts["DISTRICT"] = districts["DISTRICT"].astype(int)
police_sentiment_district = districts.merge(police_district, 
                                            left_on="DISTRICT", 
                                            right_on="DISTRICT", 
                                            how="outer",
                                            indicator=True)


# load police sentiment data aggregated in script 1a to community area for 2021 and merge with shapefile
police_comm_area = pd.read_csv(os.path.join(BASE_PATH, "Data", "police sentiment data", "police_sentiment_by_comm_area.csv"))
community_areas = unzip_load_shapefile("Boundaries - Community Areas (current).zip", 
                                       "community area boundaries", 
                                       "geo_export_75cc0f3f-cd68-496a-bbb6-489e8c562a16.shp")

community_areas["area_numbe"] = community_areas["area_numbe"].astype(int)
police_sentiment_comm_area = community_areas.merge(police_comm_area,
                                                   left_on="area_numbe",
                                                   right_on="comm_area_num",
                                                   how="outer",
                                                   indicator=True)


for variable_name, variable_description, year in variables_to_map:
    gen_map_pairs(variable_name, variable_description, year)

"""
Graphs for each of the variables show that the interpolation 
(re-aggregating the data to a different geometry - from police district to community area)
was successful and the original patterns in the data seem to hold. While graphs
were created for each of the police sentiment variables, the variables of interest are
TRUST and T_SEX_FEMALE since we will use one of them in our regression, under the hypothesis
the individuals experiencing domestic violence may be more likely to report it to the police
if they have more trust in the police.
"""


