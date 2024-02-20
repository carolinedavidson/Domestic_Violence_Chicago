# carolinedavidson
# tanayaraj
# Python II Final Project - Fall 2023

from shiny import App, render, ui
import os
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import geopandas
import numpy as np

# Note: comment out the other's base path below when working on file
BASE_PATH = r'/Users/Caroline/Dropbox/*Harris/Classes/Q4/Python II/Final Project/final-project-caraya'
#BASE_PATH=r'C:\Users\tanay\OneDrive\Documents\GitHub\final-project-caraya'

# PREPARE DATA FOR GRAPHS/MAPS
def unzip_load_shapefile(file_name, folder_name, shapefile_name):
    # consulted for working with zip file: https://docs.python.org/3/library/zipfile.html
    zip_file_path = os.path.join(BASE_PATH, "Data","shapefiles", file_name)
    folder_path = os.path.join(BASE_PATH, "Data", "shapefiles", folder_name)
    
    with zipfile.ZipFile(zip_file_path, mode='r') as zip:
        zip.extractall(folder_path)
    
    df = geopandas.read_file(os.path.join(folder_path, shapefile_name))
    return df

community_areas = unzip_load_shapefile("Boundaries - Community Areas (current).zip", 
                                       "community area boundaries", 
                                       "geo_export_75cc0f3f-cd68-496a-bbb6-489e8c562a16.shp")

community_areas["area_numbe"] = community_areas["area_numbe"].astype(int)
data = pd.read_csv(os.path.join(BASE_PATH, "Data", "reg_data.csv"))
data = data.drop(columns=["_merge", "_merge_indicator"])
data["DV_per_thousand"] = data["DV_rate"] * 1000

mappable_data = pd.merge(community_areas,
                         data,
                         left_on="area_numbe",
                         right_on="GEOID",
                         how="outer",
                         indicator=True)

# this dictionary contains the selection of variables we'll allow users to select from in Shiny (a subset)
variable_choices_dict = {"Median Household Income (2017-2021)": "INC_2017_2021",
                         "High School Graduation Rate (2017-2021)": "EDB_2017_2021",
                         "College Graduation Rate (2017-2021)": "EDE_2017_2021",
                         "Adult Binge Drinking Rate (2021-2022)": "HCSBDP_2021_2022",
                         "Reliable Internet Access Rate (% of adults, 2021-2022)": "HCSRIP_2021_2022",
                         "Average Level of Trust in Police (0 to 100)": "TRUST",
                         "Severely Rent Burdened Rate (% renter-occupied housing units, 2017-2021)": "RBS_2017_2021",
                         "Poverty Rate": "POV_2017_2021"}

# we'll allow people to look at both rates and total counts of DV since the two maps are quite different
dv_choices_dict = {"Domestic Violence Rate (per 1000 residents)": "DV_per_thousand",
                   "Domestic Violence Count": "Domestic"}

# DEFINE FUNCTIONS TO CALL WITHIN SHINY
def create_comm_area_choropleth(df, variable):
    fig, ax = plt.subplots(figsize=(15, 15))
    df.plot(ax=ax, column=variable, edgecolor="black", legend=True)
    ax.axis("off")
    return ax

def create_scatter_plot(dep_var, indep_var, dep_descr, indep_descr):
    fig, ax = plt.subplots()
    ax.scatter(mappable_data[dep_var], mappable_data[indep_var], label='Data Points', color='purple', marker='o')
    ax.set_xlabel(f'{dep_descr}')
    ax.set_ylabel(f'{indep_descr}')
    # consulted for removing spines: https://stackoverflow.com/questions/925024/how-can-i-remove-the-top-and-right-axis
    ax.spines[['right', 'top']].set_visible(False)
    return ax

# PRE-DEFINE ROWS/COLUMNS/SELECTORS FOR SHINY APP
title_row = (ui.column(12,
                       ui.hr(),
                       ui.h1("Domestic Violence in Chicago"),
                       ui.h3("Caroline Davidson & Tanaya Raj"),
                       ui.h5("PPHA 30538 - Fall 2023"),
                       ui.hr(),
                       align="center",
                       style="color:white; background-color:purple")) 
# consulted for styling: https://shiny.posit.co/r/getstarted/shiny-basics/lesson2/
# consulted for color options: https://www.w3.org/wiki/CSS/Properties/color/keywords

maps_intro_row = ui.column(10, 
                           ui.hr(style="color:white"),
                           ui.em(ui.h4("Use the drop-down menus below to compare the geographic \
                                        distribution of domestic violence incidents reported to the \
                                        police and other variables by community area and the correlation \
                                        between these two variables in the graph below.")),
                           ui.hr(style="color:white"),
                           offset=1,
                           style="color:purple"
                           )

variable_selector = ui.column(5,
                              ui.input_select(id="variable",
                                              label="Select comparison variable",
                                              choices=[key for key in variable_choices_dict]),
                               align="center")

dv_selector = ui.column(6,
                        ui.input_select(id="dv_variable",
                                        label="Select Domestic Violence measure",
                                        choices=[key for key in dv_choices_dict]),
                                        align="center")

national_hotline_info = ui.column(6,
                                  ui.h5("National Domestic Violence Hotline"),
                                 ui.a("https://www.thehotline.org/",
                                      href="https://www.thehotline.org/",
                                      style="padding-left: 20px"),
                                 ui.div(
                                     "Call: 1.800.799.SAFE (7233)",
                                    style="padding-left: 20px"),
                                ui.div(
                                    "TTY 1.800.787.3224",
                                    style="padding-left: 20px"),
                                ui.div(
                                    "Text “START” to 88788",
                                    style="padding-left: 20px"),
                                    align="center")

illinois_hotline_info = ui.column(6,
                                  ui.h5("Illinois Coalition Against Domestic Violence"),
                                  ui.a("https://www.ilcadv.org/",
                                       href="https://www.ilcadv.org/",
                                       style="padding-left: 20px"),
                                    ui.div(
                                        "Call: (877) 863-6338",
                                        style="padding-left: 20px"
                                    ),
                                    ui.div(
                                        "TTY: (877) 863-6339",
                                        style="padding-left: 20px"
                                    ),
                                    align="center")

footer = ui.row(ui.hr(style="color:purple"), 
                ui.accordion_panel("If you or someone you know is experiencing or at risk of domestic violence, there is help. Click here to collapse/expand resources.",
                                    ui.hr(),
                                    ui.row(national_hotline_info,
                                           illinois_hotline_info)),
                ui.hr(style="color:purple"), 
                style="color:white; background-color:purple"
                ) 


# DEFINE SHINY APP
app_ui = ui.page_fluid(
    ui.panel_title(title="", window_title="Domestic Violence in Chicago"),
    title_row,
    maps_intro_row,
    ui.row(dv_selector, variable_selector),
    ui.row(ui.column(6, ui.output_plot(id="dv_map"), align="center"),
           ui.column(5, ui.output_plot(id="var_map"), align="center")), 
    ui.row(ui.column(6, ui.h5(ui.output_text(id="dv_map_annotation"), align="center")),
           ui.column(5, ui.h5(ui.output_text(id="var_map_annotation"), align="center"))),
    ui.hr(style="color:white"),
    ui.row(ui.column(6, ui.output_plot(id="scatter_map"), align="center", vertical_align="bottom", offset=3)), 
    ui.hr(style="color:white"),
    ui.row(ui.column(6, ui.h5(ui.output_text(id="scatter_map_annotation"), align="center"), offset=3)),
    ui.hr(style="color:white"),
    ui.row(footer),
    ui.hr()
                        )


def server(input, output, session):
    @render.plot
    def dv_map():
        df = mappable_data 
        variable = input.dv_variable()
        map = create_comm_area_choropleth(df, dv_choices_dict[variable])

    
    @render.plot
    def var_map():
        df = mappable_data 
        variable = input.variable()
        map = create_comm_area_choropleth(df, variable_choices_dict[variable])
    
    @render.plot
    def scatter_map():
        df=mappable_data
        dvar_name = input.dv_variable()
        ivar_name = input.variable()
        map = create_scatter_plot(dv_choices_dict[dvar_name], variable_choices_dict[ivar_name],
                                  dvar_name, ivar_name)
     
    @render.text
    def scatter_map_annotation():
        dv_var_name = input.dv_variable()
        var_name = input.variable()
        dv_var = dv_choices_dict[dv_var_name]
        var = variable_choices_dict[var_name]
        # correlation: https://pandas.pydata.org/docs/reference/api/pandas.Series.corr.html#pandas.Series.corr
        correlation = mappable_data[dv_var].corr(mappable_data[var], method="pearson")
        correlation = round(correlation, 2)
        annotation = "Correlation between " + input.dv_variable() + " and " + input.variable() + ": "  + correlation.astype(str)
        return annotation
    
    @render.text
    def dv_map_annotation():
        var_name = input.dv_variable()
        annotation = input.dv_variable() + " by Chicago Community Area"
        return annotation

    @render.text
    def var_map_annotation():
        var_name = input.variable()
        annotation = input.variable() + " by Chicago Community Area"
        return annotation

app = App(app_ui, server)