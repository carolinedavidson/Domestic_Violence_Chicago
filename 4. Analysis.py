#Section 4: Analysis

import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

#Defining functions

indep_var_list_adult_binge_drinking = ['INC_2017-2021', 
                                        'EDB_2017-2021', 
                                        'EDE_2017-2021', 
                                        'HCSBDP_2021-2022', 
                                        'HCSRIP_2021-2022', 
                                        'RBS_2017-2021', 
                                        'POV_2017-2021']

indep_var_list_wo_adult_binge_drinking = ['INC_2017-2021', 
                                        'EDB_2017-2021', 
                                        'EDE_2017-2021', 
                                        'HCSRIP_2021-2022', 
                                        'RBS_2017-2021', 
                                        'POV_2017-2021']


indep_var_list_adult_binge_trust = ['INC_2017-2021', 
                                        'EDB_2017-2021', 
                                        'EDE_2017-2021', 
                                        'HCSBDP_2021-2022', 
                                        'HCSRIP_2021-2022', 
                                        'RBS_2017-2021', 
                                        'POV_2017-2021',
                                        'TRUST']

indep_var_list_adult_binge_female_trust = ['INC_2017-2021',
                                        'EDB_2017-2021',
                                        'EDE_2017-2021',
                                        'HCSBDP_2021-2022',
                                        'HCSRIP_2021-2022',
                                        'RBS_2017-2021',
                                        'POV_2017-2021',
                                        'T_SEX_FEMALE']

def run_regression(reg_data_final, indepvar_key,indep_var_list):
    col_names = indepvar_key['index'].iloc[6:]#Reference: ChatGPT

    for col in col_names:
        reg_data_final[col] = pd.to_numeric(reg_data_final[col], errors='coerce')

    indep_var_list = [var.replace('-', '_') for var in indep_var_list]    
    reg_eq= 'DV_per_thousand ~ ' + ' + '.join(indep_var_list)
    model = smf.ols(reg_eq, data=reg_data_final)
    reg_result = model.fit()
    return print(reg_result.summary())



#Calling functions

regression_output_drinking = run_regression(reg_data_final, 
                                            indepvar_key, 
                                            indep_var_list_adult_binge_drinking)

regression_output_wo_drinking = run_regression(reg_data_final, 
                                               indepvar_key, 
                                               indep_var_list_wo_adult_binge_drinking)

regression_output_trust = run_regression(reg_data_final, 
                                         indepvar_key, 
                                         indep_var_list_adult_binge_trust)

regression_output_female_trust = run_regression(reg_data_final, 
                                                indepvar_key, 
                                                indep_var_list_adult_binge_female_trust)
