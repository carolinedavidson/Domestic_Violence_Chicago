## Final Project: Domestic Violence in Chicago
### Group Members: Caroline Davidson and Tanaya Raj (github ids: carolinedavidson and tanayaraj)

### Research Question
We study the trend in Domestic Violence in the city 
of Chicago. We use cross-sectional data to explore the statistical relationship between reported 
Domestic Violence cases in the year 2021 and various socioeconomic indicators 
recorded over a period of 2017-2021. It is important to highlight that these 
factors, if found significant, could help in explaining both reporting rates and 
domestic violence incidence.

### Data
We use 3 main sources for pulling our data for this research project: 

Crime Data: This data source contains the data for the dependent variable i.e. 
reported domestic violence cases in the City of Chicago. This data reflects 
reported crimes, their location, and whether they are domestic in their nature. We aggregated the reported crimes data according to the community area as the 
independent variable data was available at the community area level. 
We consider the crime data for the year 2021 to match the time range of the 
independent variable data drawn from Chicago Health Atlas data.
After obtaining the reported domestic violence crime data at the community area
level, we create population adjusted values by incorporating the population of 
the community area. 

Chicago Health Atlas Data: We used this source for identifying the independent 
variables for our regressions: 

 * Median household income, 2017-2021
 * High school graduation rate (% of residents), 2017-2021
 * College graduation rate (% of residents), 2017-2021
 * Adult binge drinking rate (% of adults), 2021-2022
 * Prescription opiate misuse rate (% of adults), 2021-2022
 * Reliable internet access rate (% of adults), 2021-2022
 * Severely rent-burdened (% of renter-occupied housing units), 2017-2021
 * Poverty rate (% of residents), 2017-2021

The rationale for identifying these variables is influenced by articles we read
for assessing crime policies as a part of the Crime Prevention class. We found 
articles that support claims of alcohol consumption positively influencing
incidents of crime and similarly for high school and college graduation. Additionally, 
poverty may make it harder for people to leave situations that eventually develop
into domestic violence.

We exclude the opiate misuse rate variable as it is only available for 
 10 community areas so would limit our
sample size. The adult binge drinking variable also had a 
value missing for one community area, but given its relevance, we 
ran regressions with and without the variable.

Police sentiment data:
We include police sentiment data from monthly surveys about police sentiment 
in each police district. This is survey data that measures how residents of 
different parts of the city feel towards the Chicago Police Department as well 
as how safe they feel in their neighborhoods.

### Coding Involved

__Script 1a. Data Wrangling - police sentiment data.py (carolinedavidson)__
This script aggregates survey data from monthly surveys about police sentiment
in each police district. The data are filtered for 2021, aggregated to an 
average at the police district level, and then converted from the police 
district to the community area level for compatibility with our other community 
area-level variables. The script outputs a csv file with one row per community 
area and the average value in 2021 of relevant variables.

__Script 1b. Data Wrangling.py (tanayaraj)__
This script creates functions for retrieving data from City of Chicago's crime
portal using an API and creates function for loading the csv files downloaded 
from Chicago Health Atlas website and the Illinois.gov website. After creation
of the dataframes, we modify the datasets to have a common level of representation. 
Since the Chicago Health Atlas data is only available at the community level, 
we aggregate the crime data at the community level by counting the number of 
domestic violence cases reported in a certain community area. The dependent 
variable is transformed from a count to a rate to facilitate a meaningful regression 
model as the independent variables are also measured as rates.

__Script 2a. Static Plots.py  (carolinedavidson)__
The first part of this script creates a dual y-axis graph of reported DV crimes in Chicago and 
national domestic violence hotline calls from Chicago for January 2015 through 
the end of June 2020 (shown below). The DV hotline data comes from text processing done in 
script 3. The idea is to compare whether calls to the hotline and DV crimes 
reported to CPD trend in the same directions over time to understand whether 
the two are driven by the same factors. 

<img src="https://github.com/carolinedavidson/Domestic_Violence_Chicago/blob/e0d45b82f4369899d7f7ee10b10a7b4c71366b8e/images/dv_indicators.png">

The second part generates maps of police sentiment in Chicago at the original
(police district) and transformed (community area) levels. These graphs help 
visually inspect the quality of this spatial re-aggregation. One example is shown below:

<img src="https://github.com/carolinedavidson/Domestic_Violence_Chicago/blob/e0d45b82f4369899d7f7ee10b10a7b4c71366b8e/images/police_sentiment_maps/Women's%20Trust%20in%20Chicago%20PD%20map%20-%202021.png">


__Script 3. Text processing - dv hotline pdf parsing.py  (carolinedavidson)__
This script parses PDFs from the Domestic Violence Hotline to extract variables 
about the volume of calls the hotline received from Illinois from 2015 through 
the first half of 2020. It uses this information together with the percentage 
of calls from Chicago to construct a variable for the number of calls the 
hotline received from Chicago per 6-month period from January 2015 through 
June 2020. This data is then used in script 2a.

__Script 4. Analysis.py (tanayaraj)__
This script contains the function for running the regression. It also contains
variables containing the list of independent variables chosen for different 
models. This script uses statsmodels library for creating the run_regression
function.

__App.py (carolinedavidson and tanayaraj)__
In the Shiny script, we use the data created for the regression to create 
visualizations of the domestic violence rate versus a choice of one of the 
independent variables. Side by side choropleth maps allow users to compare 
the geographic distribution of domestic violence and the chosen independent variable. A scatterplot
shows the correlation between the two variables and their correlation 
coefficient. We also include an accordion panel with information about domestic
 violence support resources.

Below is a screenshot of our Shiny app and one of its drop-down menus:
<img src="https://github.com/carolinedavidson/Domestic_Violence_Chicago/blob/e0d45b82f4369899d7f7ee10b10a7b4c71366b8e/images/Shiny%20Default%20View.png">

<img src="https://github.com/carolinedavidson/Domestic_Violence_Chicago/blob/e0d45b82f4369899d7f7ee10b10a7b4c71366b8e/images/Shiny%20menu%20view.png">



### Weaknesses or Limitations

Since the dependent variable denotes *reported* domestic violence crimes, it 
is challenging to attribute effects of the independent variables to reporting 
of the incident or the occurrence. We also consider a cross-sectional dataset with just one year which limits our 
capacity to study time trends of reported domestic violence. A panel regression 
may provide better insights into these relationships.



### Results

We run four different regressions for studying the factors that correlate with 
Domestic Violence. All regressions including the following 6 independent variables:

*Standard Variables* = [Median household income, High school graduation rate (% of residents), College graduation rate 
(% of residents), Reliable internet access rate (% of adults), Severely rent-burdened (% of renter-occupied 
housing units), Poverty rate (% of residents)]

1. Domestic Violence Rate per thousand residents ~ Standard Variables + Adult binge drinking rate (% of adults)

This model has an adjusted R-squared value of 81.9%. All the independent 
variables are significant at 5% level of significance. The most precise
estimates are for College and High School graduation rate, poverty rate and 
access to internet. The coefficient with the most magnitude is poverty rate.

2. Domestic Violence Rate per thousand residents ~ Standard Variables 

This model has an adjusted R-squared value of 81.4%. All the independent 
variables are significant at 5% level of significance. We notice that including 
the adult binge drinking variable slightly improves the predictive power despite
reducing the sample size by one observation.

3. Domestic Violence Rate per thousand residents ~ Standard Variables + 
Adult binge drinking rate (% of adults) + Police Trust for 
men and women

4. Domestic Violence Rate per thousand residents ~ Standard Variables + 
Adult binge drinking rate (% of adults) + Police Trust for 
women only

After including the police trust variables, we find that both the trust variables 
increase the predictive power of the model. However, the variable denoting 
women's trust increases the predictive power more than trust of both males and 
females. Both the variables are significant at 5% level of significance.

In addition to building a regression model, we analyse the univariate relationship 
between reported domestic violence counts and the independent variables:

1. Average level of trust in the police
The downward sloping curve between the rate of reported domestic 
violence cases and average level of trust in the police seems to 
suggest that either areas with high level of trust have low incidence or low reporting of 
domestic violence.

2. Adult Binge Drinking Rate
The pearson correlation coefficient between adult binge drinking rate and 
reported domestic violence rate is -0.2 which goes against our initial intuition. 
However, the regression coefficient is positive.

3. College Graduation Rate
We observe that the education variables i.e. College Graduation Rate and High 
School Graduation rate are negatively correlated with domestic violence. 
Though the negative relationship is clearer for College Graduation as 
compared to high school graduation.

4. Median Household Income
Median Household Income is negatively related with domestic violence. Visually, 
the negative relationship seems clear.

5. Poverty Rate
Poverty Rate is positively correlated with domestic violence and has a Pearson's 
correlation coefficient of 0.84. 

6. Reliable internet access rate
This variable has a negative relationship with domestic violence. However, 
visually, the negative relationship is not very clear.

7. Severely Rent Burdened Rate
Rent Burden shows a positive correlation with domestic violence.


### Potential for future research

This research could be developed further by identifying more independent 
variables that can explain the trend in domestic violence reporting. Moreover, 
this study could be made more granular by including community area effects and 
understanding how the community areas vary in demographics. This framework 
could also be used for studying the trend between different types of crimes
and domestic violence. This framework could also be leveraged for triangulating 
various studies published on crime prevention in the US.
Overall, this study could have policy implications for prevention of domestic 
violence. Understanding the variables that correlate with domestic violence may
help in directing public funds towards the mitigation of those socioeconomic 
variables that potentially influence domestic violence. 



The Chicago crime data files (that we have in our “Data/yearly reported crimes 
data” folder) are very large so rather than push to GitHub they can be accessed
in this Google Drive folder: 
https://drive.google.com/drive/folders/1aQ3o5Pld0crpo6O2JlWrBVAebiff1J-o?usp=sharing








