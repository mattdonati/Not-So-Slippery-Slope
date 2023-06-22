import pandas as pd
import os
from sklearn.compose import ColumnTransformer
from sklearn.utils import shuffle
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from datetime import timedelta
import glob
import numpy as np
from sklearn.linear_model import LinearRegression

def total_salt_per_polygon(data_input, min_solid):
    '''
    Fit machine learning model for Iowa Winter Salt Data. Label is total salt per polygon per storm date. Features are
    Lane miles by road type by polygon and SNODAS variables by polygon per storm date. Estimator is
    HistGradientBoostingRegressor
    :param data_input: String. Path to file containing Iowa Winter Salt Data set
    :param min_solid: Int. Minimum amount of solid precipitation per day per polygon
    :return: Pipeline.  Fitted pipeline object.
    '''
    salt_df = pd.read_csv(data_input)
    salt_df = salt_df[(salt_df['solid_precip'] >= min_solid)]
    X = salt_df
    y = salt_df['WITHIN_POLY_TOTALSALT']
    X_ran, y_ran = shuffle(X, y, random_state=42)
    feature_names = ['solid_precip', 'SWE', 'snow_depth', 'runoff', 'sub_pack', 'sp_temp', 'solid_precip_PREV',
                     'liquid_precip_PREV', 'SWE_PREV', 'snow_depth_PREV', 'runoff_PREV', 'sub_pack_PREV',
                     'sp_temp_PREV', 'WITHIN_POLY_LANE_KMS_1', 'WITHIN_POLY_LANE_KMS_3', 'WITHIN_POLY_LANE_KMS_4',
                     'WITHIN_POLY_LANE_KMS_5']
    col_trans = ColumnTransformer([('pass', 'passthrough', feature_names)], remainder='drop')
    pipeline = Pipeline([('col_trans', col_trans), ('hsg', HistGradientBoostingRegressor(loss='poisson',
                                                                                         max_leaf_nodes=140,
                                                                                         min_samples_leaf=15))])
    pipeline.fit(X_ran, y_ran)
    return pipeline

def build_quarterly_storm_dataset(fitted_salt_model, snodas_input, roads_overlay_input, quarter, min_solid_precip=2):
       snodas_params_df = pd.read_csv(snodas_input)
       snodas_params_df['DATE'] = snodas_params_df['date'].astype('datetime64[ns]')

       storm_df = snodas_params_df.copy()
       storm_df = storm_df.rename(columns={"DATE": "STORM_DATE"})

       storm_df['PREV_DATE'] = storm_df['STORM_DATE'] - timedelta(days=1)

       X = pd.merge(storm_df, snodas_params_df, how='left', left_on=['PREV_DATE', 'poly_index'],
                                right_on=['DATE', 'poly_index'], suffixes=("", "_PREV"))
       roads_df = pd.read_csv(roads_overlay_input)
       X = pd.merge(X, roads_df, how='left', left_on=['poly_index'], right_on=['poly_index'])
       #all polyindexes regardless of solid precipitation or salt levels
       polygons_df = pd.DataFrame({'poly_index': roads_df['poly_index'],
                     'quarter': [quarter] * roads_df['poly_index'].size})

       X = X[(X['solid_precip'] >= min_solid_precip)]
       predictions = pd.DataFrame({'poly_index': X['poly_index'], "salt": fitted_salt_model.predict(X)})
       predictions = predictions.groupby(by=['poly_index'], as_index=False, sort=False).aggregate('sum')

       return pd.merge(polygons_df, predictions, how='left', left_on=['poly_index'], right_on=['poly_index'])

def quarterly_solid_precip(input_list):
    quarterly_solid_precip_df = pd.DataFrame()

    for file in input_list:
        quarter = file[-10:-4]
        temp_df = pd.read_csv(file)
        temp_df['quarter'] = [quarter] * temp_df['poly_index'].size
        temp_df = temp_df.groupby(by=['quarter', 'poly_index'], as_index=False).aggregate({'solid_precip':'sum'})
        quarterly_solid_precip_df = pd.concat([quarterly_solid_precip_df, temp_df], axis=0, ignore_index=True)
    return quarterly_solid_precip_df

def quarterly_salt_predictions(fitted_salt_model, roads_overlay_input, snodas_directory):
    quarterly_salt_predictions_df = pd.DataFrame()
    all_files = glob.glob(os.path.join(snodas_directory, "*.csv"))
    for file in all_files:
        quarter = file[-10:-4]
        quarterly_salt_predictions_df = pd.concat([quarterly_salt_predictions_df, build_quarterly_storm_dataset(
            fitted_salt_model, snodas_input=file, roads_overlay_input=roads_overlay_input, quarter=quarter)], axis=0,
                                                  ignore_index=True)
    quarterly_salt_predictions_df = quarterly_salt_predictions_df.groupby(by=['quarter', 'poly_index'], as_index=False).aggregate('sum')
    return quarterly_salt_predictions_df

def sales_model(quarterly_salt_input, actual_sales_input, depot_dist_input):
    market_df = pd.read_csv(quarterly_salt_input)
    actual_df = pd.read_csv(actual_sales_input)
    depot_df = pd.read_csv(depot_dist_input)

    market_df = pd.merge(market_df, actual_df, how='left', left_on='quarter', right_on='quarter')
    market_df = pd.merge(market_df, depot_df, how='left', left_on='poly_index', right_on='poly_index')
    return market_df

def company_model(market_input):
    exp = -.5
    salt_df = market_input
    salt_df['min_depot_distance'] = salt_df['min_depot_distance']/1000
    salt_df['volume'] = salt_df['volume'] * 2000 * 1000
    salt_df['estimates'] = salt_df['salt']/salt_df['min_depot_distance']**exp
    salt_df = salt_df.groupby(by=['quarter'], as_index=False).aggregate({'min_depot_distance':'mean', 'volume':'mean', 'estimates': 'sum', 'salt':'sum'})
    X = np.array(salt_df['estimates']).reshape(-1, 1)
    y = salt_df['volume']
    model = LinearRegression()
    model.fit(X, y)
    return pd.DataFrame({'quarter':salt_df['quarter'],'actual': salt_df['volume'], 'predicted': model.predict(X)})
