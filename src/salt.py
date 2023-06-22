from salt_client import Salt_client
import pandas as pd
import geopandas as gpd
from datetime import timedelta
from pyproj import Geod

def build_salt_df(link):
    """ Create instance of Salt_client and use it to download and save salt data
    :return: DataFrame with complete Iowa DOT historic salt dataset. Includes geometry col in wkt format.
    """
    salt = Salt_client(link)
    salt.get_record_count()
    return salt.build_df()

def parse_dates(salt_input):
    '''Save storm dates that will be used to join with SNODAS data. Determine storm dates based on datetime of last
    pass. SNODAS and IOWA DOT use same time zone.
    :return: Dataframe with dates saved that correspond to SNODAS dates
    '''
    salt_df = pd.read_csv(salt_input)
    salt_df['LAST_PASS'] = pd.to_datetime(salt_df['LAST_PASS'], unit='ms')
    salt_df['STORM_DATE'] = salt_df['LAST_PASS'].apply(
        lambda x: (x.floor('D') + timedelta(days=1)) if (x.hour > 11) else x.floor('D'))
    salt_df['PREV_DATE'] = salt_df['STORM_DATE'] - timedelta(days=1)
    return salt_df

def unique_salt_dates(salt_input):
    ''' Return numpy array of the set of all storm dates and one day previous dates
    :param filename: Path of salt dataset that includes storm dates
    :return: Numpy array of set of storm + prior to storm dates
    '''
    salt_df = pd.read_csv(salt_input)
    return pd.concat([salt_df['STORM_DATE'], salt_df['PREV_DATE']], ignore_index=True).unique()

def build_iowa_winter(salt_input, grid_input):
    '''
    Overlay iowa salt data and iowa grid. create per polygon features.
    :param salt_input: String. Path to salt data set.
    :param grid_input: String. Path to grid file.
    :return: DataFrame
    '''
    geod = Geod(ellps="WGS84")
    salt_df = pd.read_csv(salt_input)
    salt_df['geometry'] = gpd.GeoSeries.from_wkt(salt_df['geometry'])
    salt_gdf = gpd.GeoDataFrame(salt_df, geometry='geometry')
    salt_df['ORIG_ID'] = salt_df.index.to_numpy(copy=True)
    salt_gdf['ORIG_SEGMENT'] = salt_gdf['geometry'].apply(lambda x: geod.geometry_length(x))
    salt_gdf['SOLID_PER_SEGMENT'] = salt_gdf['QUANTITY_SOLID'] / salt_gdf['ORIG_SEGMENT']
    salt_gdf['TOTAL_PER_SEGMENT'] = salt_gdf['TOTAL_SALT_QUANTITY'] / salt_gdf['ORIG_SEGMENT']

    grid_df = pd.read_csv(grid_input)
    grid_df['geometry'] = gpd.GeoSeries.from_wkt(grid_df['geometry'])
    grid_gdf = gpd.GeoDataFrame(grid_df, geometry='geometry')

    # keep_geom_type=True keeps only the lines from salt_df, not the polygons from grid
    overlay = gpd.overlay(salt_gdf, grid_gdf, how='intersection', keep_geom_type=True, make_valid=False)

    overlay['NEW_SEGMENT'] = overlay['geometry'].apply(lambda x: geod.geometry_length(x))
    return overlay.to_wkt()

def groupby_poly_iowawinter(salt_input):
    '''
    Group by polygon and sum up total salt that falls within each polygon by storm date
    :param salt_input: Dataframe. Iowa winter salt overlay. Each observation is original segment by polygon
    :return: Dataframe. Iowa salt features are grouped by Iowa Grid polygons
    '''
    salt_df = salt_input
    salt_df['WITHIN_POLY_TOTALSALT'] = (salt_df['NEW_SEGMENT']/salt_df['ORIG_SEGMENT']) * salt_df['TOTAL_SALT_QUANTITY']
    salt_df['WITHIN_POLY_SOLIDSALT'] = (salt_df['NEW_SEGMENT'] / salt_df['ORIG_SEGMENT']) * salt_df['QUANTITY_SOLID']
    aggregations = {'WITHIN_POLY_SOLIDSALT': 'sum', 'WITHIN_POLY_TOTALSALT': 'sum'}
    salt_df = salt_df.groupby(by=['STORM_DATE', 'PREV_DATE', 'poly_index'], as_index=False, sort=False)\
        .aggregate(aggregations)
    return salt_df

def join_it_iowawinter(salt_input, snodas_input, roads_input):
    '''
    Join Iowa datasets (salt, SNODAS, roads)
    :param salt_input: String. Path of file containing Iowa salt data
    :param snodas_input: String. Path of file containing Iowa SNODAS data
    :param roads_input: String. Path of file containing Iowa roads overlay data
    :return: Dataframe
    '''
    salt_df = pd.read_csv(salt_input, parse_dates=["STORM_DATE", "PREV_DATE"])
    salt_df = salt_df.assign(STORM_DATE=salt_df['STORM_DATE'].astype('datetime64[ns]'),PREV_DATE=salt_df['PREV_DATE']
                             .astype('datetime64[ns]'))

    snodas_params_df = pd.read_csv(snodas_input)
    snodas_params_df['DATE'] = snodas_params_df['date'].astype('datetime64[ns]')

    merged = pd.merge(salt_df, snodas_params_df, how='left', left_on=['STORM_DATE', 'poly_index'],
                      right_on=['DATE', 'poly_index'])
    merged = pd.merge(merged, snodas_params_df, how='left', left_on=['PREV_DATE', 'poly_index'],
                      right_on=['DATE', 'poly_index'], suffixes=("","_PREV"))

    roads_df = pd.read_csv(roads_input)
    merged = pd.merge(merged, roads_df, how='left', left_on=['poly_index'], right_on=['poly_index'])

    return merged
