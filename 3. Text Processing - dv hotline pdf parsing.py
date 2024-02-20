# carolinedavidson
# Final Project - Python II
# Fall 2023

"""
This script parses PDFs from the Domestic Violence Hotline to extract variables about the
volume of calls the hotline received from Illinois from 2015 through the first half of 2020.
It uses this information together with the percentage of calls from Chicago to construct
a variable for the number of calls the hotline received from Chicago per 6-month period 
from January 2015 through June 2020.
"""

import os
import pandas as pd
from pypdf import PdfReader
import re


BASE_PATH = r"/Users/Caroline/Dropbox/*Harris/Classes/Q4/Python II/Final Project/final-project-caraya"

Hotline_report_files = [
    #(year, existing pdf file name, name for parsed text file)
    (2015, "2015_NDVH_Illinois.pdf", "2015_Hotline_Report.txt"),
    (2016, "2016_NDVH_Illinois.pdf", "2016_Hotline_Report.txt"),
    (2017, "2017_NDVH_Illinois.pdf", "2017_Hotline_Report.txt"),
    (2018, "NDVH_2018_Illinois.pdf", "2018_Hotline_Report.txt"),
    (2019, "The-Hotline-IL-Report_2019.pdf", "2019_Hotline_Report.txt")
    ]

Hotline_report_halfyear_files = [
    #(year, existing pdf file name, name for parsed text file)
    (2015, "Jan-June2015_NDVH_Illinois.pdf", "2015_Hotline_Report_halfyear.txt"),
    (2016, "Jan-Jun2016_NDVH_Illinois.pdf", "2016_Hotline_Report_halfyear.txt"),
    (2017, "Illinois.pdf", "2017_Hotline_Report_halfyear.txt"),
    (2018, "Half NDVH_2018_Illinois.pdf", "2018_Hotline_Report_halfyear.txt"),
    (2019, "NDVH_2019_Half Report_Illinois.pdf", "2019_Hotline_Report_halfyear.txt"),
    (2020, "2020-Hotline-MY-Reports_IL.pdf", "2020_Hotline_Report_halfyear.txt")
    ]

def save_DVpdf_to_text_file(pdf_folder, pdf_fname, text_fname):
    pdf = PdfReader(os.path.join(BASE_PATH,
                                 "Data",
                                 "DV hotline data",
                                 "DV Hotline PDFs",
                                 pdf_folder,
                                 pdf_fname))
    pdf_pages = [page.extract_text() for page in pdf.pages]
    # above list comprehension adapted from for loop in Lecture 4
    pdf_full_text = "\n".join(pdf_pages)
    
    with open(os.path.join(BASE_PATH, 
                           "Data", 
                           "DV hotline data", 
                           "DV Hotline PDFs", 
                           pdf_folder, 
                           "Text Files", 
                           text_fname),
              "w", encoding="utf-8") as ofile:
        ofile.write(pdf_full_text)

    
def extract_stats_hotline_reports(year, text_file, pdf_folder):
    
    text_file_path = os.path.join(BASE_PATH, 
                                  "Data",
                                  "DV hotline data",
                                  "DV Hotline PDFs", 
                                  pdf_folder, 
                                  "Text Files", 
                                  text_file)

    with open(text_file_path, "r") as file:
        content = file.read()
    
    chicago_percent_pattern = r"(?i)Chicago\s*([\d.]+)%" # used regex101.com to build expression
    chicago_percent_phrase = re.search(chicago_percent_pattern, content)
    chicago_percent = chicago_percent_phrase.group(1)
    
    illinois_calls_pattern = r"([\d,]+)\s*contacts\*?\s*from\s*Illinois"
    illinois_calls_phrase = re.search(illinois_calls_pattern, content)
    illinois_calls = illinois_calls_phrase.group(1).replace(",", "")

    line = [str(year), chicago_percent, illinois_calls]
    
    return line


def save_csv_for_report_type(file_list, pdf_folder, annual_or_halfyear):
    # next 7 lines adapted from Prof Levy's Lecture 5 slides
    lines = [extract_stats_hotline_reports(year, txt, pdf_folder) for year, pdf, txt in file_list]
    lines = [",".join(line) for line in lines]
    header = "year,chicago_percent,illinois_calls"
    lines.insert(0, header)
    doc = "\n".join(lines)
    
    csv_name = "hotline_reports_data_" + annual_or_halfyear + ".csv"
    
    csv_path = os.path.join(BASE_PATH, 
                            "Data",
                            "DV hotline data", 
                            csv_name)
    
    with open(csv_path, "w") as ofile:
              ofile.write(doc)
    
    ndvh_data = pd.read_csv(csv_path)
    ndvh_data["chicago_calls"] = (ndvh_data["chicago_percent"]/100) * ndvh_data["illinois_calls"]

    ndvh_data.to_csv(csv_path, index=False)



# apply functions to annual reports
for year, pdf, txt in Hotline_report_files:
    save_DVpdf_to_text_file("Hotline Reports", pdf, txt)

save_csv_for_report_type(Hotline_report_files, "Hotline Reports", "annual")

# apply functions to halfyear reports
for year, pdf, txt in Hotline_report_halfyear_files:
    save_DVpdf_to_text_file("Hotline Reports - Half Year", pdf, txt)

save_csv_for_report_type(Hotline_report_halfyear_files, "Hotline Reports - Half Year", "halfyear")

# now load both files to construct dataframe for 6-month periods
dv_calls_annual = pd.read_csv(os.path.join(BASE_PATH, 
                                           "Data",
                                           "DV hotline data", 
                                           "hotline_reports_data_annual.csv"))
dv_calls_annual = dv_calls_annual.drop(columns=["chicago_percent", "illinois_calls"], axis=1)
dv_calls_annual = dv_calls_annual.rename(columns={"chicago_calls": "annual"})

dv_calls_halfyear = pd.read_csv(os.path.join(BASE_PATH, 
                                             "Data",
                                             "DV hotline data", 
                                             "hotline_reports_data_halfyear.csv"))
dv_calls_halfyear = dv_calls_halfyear.drop(columns=["chicago_percent", "illinois_calls"], axis=1)
dv_calls_halfyear = dv_calls_halfyear.rename(columns={"chicago_calls": "Semester 1"})


dv_calls_all = dv_calls_annual.merge(dv_calls_halfyear,
                                     on="year",
                                     how="outer",
                                     indicator=True)
dv_calls_all = dv_calls_all.drop(columns=["_merge"], axis=1)
dv_calls_all["Semester 2"] = dv_calls_all["annual"] - dv_calls_all["Semester 1"]
dv_calls_all[["annual", "Semester 1", "Semester 2"]] = dv_calls_all[["annual", "Semester 1", "Semester 2"]].round()

dv_calls_long = dv_calls_all.melt(id_vars="year",
                                  value_vars=None,
                                  var_name="period",
                                  value_name="DV_hotline_calls_from_Chicago")

dv_calls_long = dv_calls_long.sort_values(by=["year", "period"]).reset_index(drop=True).dropna()

dv_calls_long.to_csv(os.path.join(BASE_PATH, 
                                  "Data", "DV hotline data",                                  
                                  "DV_calls_by_semester.csv"), 
                     index=False)

