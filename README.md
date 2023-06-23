# Not So Slippery Slope
Compass Minerals (NYSE:  CMP) produces rock salt for roadway de-icing. CMP represents a potential long-term equity investment, but the large fluctuations in sales, the result of changes in winter weather, increase investment risk by masking potential changes to the underlying business. This project reduces that investment risk, by estimating changes in sales net of the influence of winter weather fluctuations. 

### Problem Statement

Compass Minerals (NYSE:  CMP) produces rock salt for roadway de-icing. The fundamentals of the 
business are attractive. CMP produces a necessity good with a competitive moat. Due to the very 
high weight-to-value ratio of de-icing salt (a metric ton of salt sells for approximately $70 in 
the snow belt region) CMP’s sales in an area are largely determined by distance from their salt 
mines. The company has a monopoly or oligopoly in all of its markets. The problem is that the 
company regularly experiences huge fluctuations in sales and cash flow on a year over year basis 
as the result of fluctuations in winter weather severity. As an illustration, their forward EBITDA 
guidance for 2023 is $175mm-275mm, a 40% relative range. The average relative range for company’s 
this size is 10% (source:  marketbeat.com). These fluctuations create investment risk because they 
make it very difficult to monitor for changes to the underlying business. Given that CMP has a 
cash-cow business there is a very real risk that management will deteriorate over time. This 
project solves this problem by providing estimates of company performance, via a web application, 
net of the effects of winter weather severity. Portfolio managers will be able to use the 
application to get an estimate of quarterly sales growth/decline that is over and above changes in 
winter weather severity. Having this product will lower the risk of the investment and allow 
managers to take larger positions, all else being equal.

### Methods Used
* Machine Learning
* Geospatial Analysis
* Data Visualization
* Predictive Modeling
* Regression Analysis: Histogram Gradient Boosting Regressor with poisson loss function

### Technologies
* Python
* Geopandas, Shapely, Pyproj
* Pandas
* Scikit-learn
* Matplotlib
* Streamlit

## Project Description
There are two main steps in the modeling process: 
1) prediction of geocoded quarterly market salt usage based on snow-related conditions and extent of roads
2) prediction of company quarterly sales based on predictions in step 1 weighted by distance from closest company depot. 

### Data sources: 
* SNODAS: Geocoded snow-related variables 
  * Snow Data Assimilation System (SNODAS) Data Products at NSIDC
  https://nsidc.org/data/g02158/versions/1
* BTS NAR: Geospatial Roads Data 
  * US DOT BTS North American Roads Data 
  https://data-usdot.opendata.arcgis.com/datasets/usdot::north-american-roads/about	
* SALT IOWA:  Geocoded salt data by winter storm event
  * Iowa DOT  Winter Storm Analysis Historic View 
  Salt usage: https://public-iowadot.opendata.arcgis.com/datasets/IowaDOT::winter-storm-analysis-historic-view/about
* Geocoded CMP Salt Depot Locations (estimated from published reports) 
* CMP quarterly road de-icing salt volumes (collected from company financial reports)      

### ML Model 1:  Predict quarterly market salt usage by geography
* Overview: 
  * Label: total salt usage (lbs.) per salting event, per geospatial polygon (10 km x 10 km) 
  * Features: 
    * SNODAS variables the day of and day prior to salting event per geospatial polygon. 
    * Extent and type of road lane kms per geospatial polygon
  * Estimator: Histogram Gradient Boosting Regressor with poisson loss function
* Data wrangling and munging: 
  * Geospatial overlays: geospatially align SNODAS, salt and road variables.
* Feature extraction/engineering:  
  * Optimize size of geospatial grids, aggregations of SNODAS variables (max, min, mean), time extent of SNODAS 
  variables, road extent aggregation, and subset of SNODAS and road variables based on correlation matrices    
* Cross-validation and hyperparameter tuning 
### ML Model 2: Predict quarterly company salt volumes 
* Overview: 
  * Label: quarterly salt sales 
  * Features: 
    * Market salt usage estimates per geospatial polygon (predictions using fitted Model 1)
    * Depot distances: distance from closest salt depot, per geospatial polygon
* Estimators: economic gravity model weighting sales by distance from depot; linear regression
* Data wrangling and munging: 
  * Geospatial overlays: geospatially align SNODAS, salt estimates, and road variables.
* Hyperparameter tuning:  distance weights 
### Application and visualizations
  * Streamlit application:  src/app.py
    * Example Bar plot:  comparison of estimated quarterly volume based on winter weather vs. actual sales volume <br />
    <img src=volumes.png style="width: 40%; height: auto;">
    * Example Salt color map: estimated salt volumes per geography for selected quarter and prior year quarter <br />
    <img src=salt.png style="width: 40%; height: auto;">
    * Example solid precipitation color map: solid precipitation per geography for selected quarter and prior year quarter <br />
     <img src=solid_precip.png style="width: 40%; height: auto;">
## Getting Started <br />
### For development: 
1. Clone this repo (for help see this [tutorial](https://help.github.com/articles/cloning-a-repository/)).
2. Raw data (not constructed with Makefile) kept here: ```data/raw/```
3. Create and activate ```venv```
4. Install dependencies <br />
```pip install -r requirements.txt```<br />
5. Makefile: 
   running ```make``` from root directory will output list of make targets in order <br />

### For application end use: <br />
1. Clone this repo (for help see this [tutorial](https://help.github.com/articles/cloning-a-repository/)). 
2. Processed data needed for application kept here:  
```data/processed/```
```models/```
4. Create and activate ```venv```
5. Install dependencies <br />
```pip install -r requirements.txt```<br />
6. Runn application from command line<br />
```streamlit run src/app.py```
