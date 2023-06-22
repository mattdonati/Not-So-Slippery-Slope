import pandas as pd
import geopandas as gpd
from pyproj import Geod
from roads_client import Roads_client

def build_state_roads_df(link, state, crs):
    '''
    Create DataFrame, with geometry in wkt format, of state North American Roads data set
    :param link: String. ArcGIS API endpoint
    :param state: String. Capitalized full name of state
    :param crs: String. Coordinate reference system of NAR data set
    :return: DataFrame
    '''
    state_roads_client = Roads_client(link, state, crs)
    state_roads_client.add_params(where=["COUNTRY=2", f"JURISNAME='{state}'"])
    state_roads_client.get_record_count()
    return state_roads_client.build_df()

def nar_overlay(state_abbrev, nar_input, grid_input):
    '''
    Create overlay of polygons that correspond to SNODAS grid (each polygon is a 10 x 10 SNODAS grid) with
    road data for a state in CMP's market
    :param state_abbrev: String. Two-letter state abbreviation
    :param nar_input: String. Path of file containing state NAR road data
    :param grid_input: String. Path of file containing regional grid
    :return: DataFrame. Geometries are returned in wkt format
    '''

    """ Create overlay of polygons that correspond to SNODAS grid (each polygon is a 10 x 10 SNODAS grid) with
    road data for every state in CMP's market
    :return: None
    modify: os.path.join(ROOT_DIR, "NAR", "OVERLAYS",f'regional_poly10_NAR_{states.get(state)}.csv')
    """
    geod = Geod(ellps="WGS84")

    road_gdf = pd.read_csv(nar_input)
    road_gdf['geometry'] = gpd.GeoSeries.from_wkt(road_gdf['geometry'])
    road_gdf = gpd.GeoDataFrame(road_gdf, geometry='geometry')

    #calculate length of each road and in km prior to overlay and intersections with polygon grid
    road_gdf['ORIG_KMS'] = road_gdf['geometry'].apply(lambda x: geod.geometry_length(x))/1000
    # calculate lanes * length of each road and in km prior to overlay and intersections with polynomial grid
    road_gdf['ORIG_LANE_KMS'] = road_gdf['ORIG_KMS'] * road_gdf['LANES']
    road_gdf['STATE'] = pd.Series([state_abbrev]*len(road_gdf))
    print(road_gdf.head())
    grid_gdf = pd.read_csv(grid_input)
    grid_gdf['geometry'] = gpd.GeoSeries.from_wkt(grid_gdf['geometry'])
    grid_gdf = gpd.GeoDataFrame(grid_gdf, geometry='geometry')
    print(grid_gdf.head())
    # create overaly of roads and polygons
    # keep_geom_type=True keeps only the roads geometry for each road, not the polygons
    overlay = gpd.overlay(road_gdf, grid_gdf, how='intersection', keep_geom_type=True, make_valid=False)
    print(overlay.head())
    # save the length, and lanes * length of each road section that will be summed when grouping by polygon
    overlay['WITHIN_POLY_KMS'] = overlay['geometry'].apply(lambda x: geod.geometry_length(x))/1000
    overlay['WITHIN_POLY_LANE_KMS'] = overlay['WITHIN_POLY_KMS'] * overlay['LANES']


    return overlay.to_wkt()

def nar_combine_overlays(all_files):
    ''' Combine all roads overlay files. Combine prior to grouping by polygon because there are polygons that straddle
    state boundaries
    :param: all_files:  List. List of overlay files
    :return: DataFrame
    '''
    return pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

def regional_nar_overlay_road_features(regional_overlay_input):
    '''
    Add features to regional roads overlay. Create length and length * lanes features for each class of road. Groupby
    polygon.
    :param regional_overlay_input: Dataframe containing regional overlay
    :return: DataFrame.  Regional overlay with road features, with geometry in wkt format
    '''
    road_df = regional_overlay_input

    max_class = road_df['CLASS'].max()

    for n in range(1, max_class + 1):
        road_df[f'WITHIN_POLY_KMS_{n}'] = road_df[f'WITHIN_POLY_KMS'] * (road_df['CLASS'] == n)
        road_df[f'WITHIN_POLY_LANE_KMS_{n}'] = road_df[f'WITHIN_POLY_LANE_KMS'] * (road_df['CLASS'] == n)

    road_cols = [col for col in road_df.columns if "WITHIN_POLY" in col]
    #sum within polygon for all length and lane * length features
    aggregations = {col: "sum" for col in road_cols}

    #avoid aggregating over state at first in order to keep track of polygons that straddle state lines
    road_df = road_df.groupby(by=['poly_index', 'STATE'], as_index=False, sort=False).aggregate(aggregations)

    #add aggregate function for STATE that creates a list of state abbreviations for polygons that straddle state lines
    aggregations["STATE"] = " ".join

    road_df = road_df.groupby(by=['poly_index'], as_index=False, sort=False).aggregate(aggregations)

    return road_df

def winter_iowa_roads_overlay(roads_input, grid_input):
    """ Create overlay of polygons that correspond to SNODAS grid (each polygon is a 10 x 10 SNODAS grid) with
    road data for Iowa
    :return: Dataframe with geometry in wkt format
   """
    geod = Geod(ellps="WGS84")

    road_gdf = pd.read_csv(roads_input)

    road_gdf['geometry'] = gpd.GeoSeries.from_wkt(road_gdf['geometry'])
    road_gdf = gpd.GeoDataFrame(road_gdf, geometry='geometry')
    # calculate length of each road in km prior to overlay and intersections with polygon grid
    road_gdf['ORIG_KMS'] = road_gdf['geometry'].apply(lambda x: geod.geometry_length(x))/1000
    # calculate lanes * length of each road in km prior to overlay and intersections with polynomial grid
    road_gdf['ORIG_LANE_KMS'] = road_gdf['ORIG_KMS'] * road_gdf['LANES']
    road_gdf['STATE'] = pd.Series(["IA"]*len(road_gdf))

    grid_gdf = pd.read_csv(grid_input)
    grid_gdf['geometry'] = gpd.GeoSeries.from_wkt(grid_gdf['geometry'])
    grid_gdf = gpd.GeoDataFrame(grid_gdf, geometry='geometry')

    # create overaly of roads and polygons
    # keep_geom_type=True keeps only the roads geometry for each road, not the polygons
    overlay = gpd.overlay(road_gdf, grid_gdf, how='intersection', keep_geom_type=True, make_valid=False)

    # save the length, and lanes * length of each road section that will be summed when grouping by polygon
    overlay['WITHIN_POLY_KMS'] = overlay['geometry'].apply(lambda x: geod.geometry_length(x))/1000
    overlay['WITHIN_POLY_LANE_KMS'] = overlay['WITHIN_POLY_KMS'] * overlay['LANES']

    return overlay.to_wkt()

def winter_iowa_road_features(roads_overlay_input):
    '''
    Create length and length * lanes features for each class of road. Groupby polygon.
    :param roads_overlay_input: Dataframe. Overlay of grid and roads with within polygon length and lane x length
    :return: Dataframe with geometry in wkt format. Includes road features by road class, summarized within polygon
    '''

    road_df = roads_overlay_input

    for n in range(1, 6):
        road_df[f'WITHIN_POLY_KMS_{n}'] = road_df[f'WITHIN_POLY_KMS'] * (road_df['CLASS'] == n)
        road_df[f'WITHIN_POLY_LANE_KMS_{n}'] = road_df[f'WITHIN_POLY_LANE_KMS'] * (road_df['CLASS'] == n)

    columns = [col for col in road_df.columns if "WITHIN_POLY" in col]
    aggregations = {col: "sum" for col in columns}
    road_df = road_df.groupby(by=['poly_index'], as_index=False, sort=False).aggregate(aggregations)
    return road_df