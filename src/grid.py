import pandas as pd
import numpy as np
import geopandas as gpd
import shapely.geometry as sgeom
import math
from collections import namedtuple
from pyproj import Geod

'''
SNODAS grid parameters: 
    unmasked upper left start point = (-130.5167, 58.2333); after Oct 2013
    unmasked grid size = 8192 x 4096
Regional grid coordinates:
    upper left: (-97.239209, 49.384358) - MN  
    bottom right (-77.719519, 34.982972) - TN latitude, WV longitude
Iowa state grid coordinates: 
    upper left: (-96.639704, 43.501196)
    bottom right: (-90.140061, 40.375501)
'''
Increment = namedtuple("Increment", ['degrees', 'direction'])
Point = namedtuple("Point", ['lon', 'lat'])

class Grid(object):
    '''
    Grid Class is used to create a geospatial grid over a desired coverage area. The grid coordinates align with a
    SNODAS grid, but the dimensions of every cell/polygon are poly_size times that of a SNODAS polygon
    '''
    def __init__(self, upper_left, bottom_right, poly_size, reference_upper_left=Point(-130.5167, 58.2333),
                 reference_x_size=8192, reference_lat_increment=Increment(1 / 3600 * 30, -1),
                 reference_lon_increment=Increment(1 / 3600 * 30, 1)):
        '''
        Initialize Grid object
        :param upper_left: Point. Upper left coordinates of coverage area
        :param bottom_right: Point. Bottom right coordinates of coverage area
        :param poly_size: Width and Height of each grid polygon in units of SNODAS polygons
        :param reference_upper_left: Point. Upper left coordinates of SNODAS coverage area
        :param reference_x_size: Int. Width, in polygons, of SNODAS grid
        :param reference_lat_increment: Increment. Latitudinal Increment of SNODAS grid from upper left corner
        :param reference_lon_increment: Increment. Longitudinal Increment of SNODAS grid from upper left corner
        '''
        self.upper_left = upper_left
        self.bottom_right = bottom_right
        self.poly_size = poly_size
        self.reference_upper_left = reference_upper_left
        self.reference_x_size = reference_x_size
        self.reference_lat_increment = reference_lat_increment
        self.reference_lon_increment = reference_lon_increment

        self.reference_index = None #index of SNODAS polygons
        self.poly_index = None #index of Grid polygons
        self.x_width = None #width of Grid in units of SNODAS polygons
        self.y_height = None #height of Grid in units of SNODAS polygons
        self.x_start = None #zero-referenced horizontal starting point of Grid within SNODAS grid
        self.x_end = None #zero-referenced horizontal ending point of Grid within SNODAS grid
        self.y_start = None #zero-referenced vertical starting point of Grid within SNODAS grid
        self.y_end = None #zero-referenced vertical ending point of Grid within SNODAS grid

        self._create_grid_params()

    def _xy_start(self, ref_start_coord, start_coord, increment):
        '''
        Translate a boundary of coverage area into a position in a y by x matrix
        :param ref_start_coord: Float. Latitude or longitude coordinate of upper left point in SNODAS grid, in degrees
        :param start_coord: Flaat. Latitude or longitude coordinate of upper left point in desired coverage area
        :param increment: Increment. Latitudinal or longitudinal increment of SNODAS grid starting in upper left
        corner
        :return: Int. Zero-references starting y, or x position of coverage area within a y by x SNODAS grid
        '''

        #truncate rather than round up to include the polygon that overlaps the start coordinate
        return int((abs(ref_start_coord) - abs(start_coord)) / increment.degrees)

    def _xy_end(self, ref_start_coord, end_coord, increment):
        '''
        Translate a boundary of coverage area into a position in a y by x matrix
        :param ref_start_coord: Float. Latitude or longitude coordinate of upper left point in SNODAS grid, in degrees
        :param end_coord: Flaat. Latitude or longitude coordinate of bottom right point in desired coverage area
        :param increment: Increment. Latitudinal or longitudinal increment of SNODAS grid starting in upper left
        corner
        :return: Int. Zero-references ending y, or x position of coverage area within a y by x SNODAS grid
        '''
        '''start by adding size of directional increment to reference start point in order determine how many polygons 
        to advance the farthest edge of the start polygon'''
        # round up to include the reference polygon that overlaps the end boundary of the coverage area
        return int(math.ceil((abs(ref_start_coord + increment.degrees * increment.direction)
                              - abs(end_coord)) / increment.degrees))

    def _adjust_dimension(self, initial_start, initial_end, poly_size):
        '''
        Adjust the starting and ending x or y positions so that the width or height is divisible by poly_size. Keep
        Grid roughly centered over desired coverage area
        :param initial_start: Int. zero-referenced starting position prior to adjustment
        :param initial_end: Int. zero-referenced ending position prior to adjustment
        :param poly_size: Int. size of Grid polygons in units of number of SNODAS polygons
        :return: new_start, new_end
        '''
        new_start = initial_start
        new_end = initial_end
        initial_size = initial_end - initial_start + 1
        new_size = initial_end - initial_start + 1
        while new_size % poly_size != 0:
            new_size += 1
        add_size = new_size - initial_size

        new_start -= (add_size // 2)
        new_end += (add_size // 2 + add_size % 2)
        return new_start, new_end

    def _create_grid_params(self):
        '''
        Translate from SNODAS parameters into Grid parameters over desired coverage area. Create indexes.
        :return: None
        :modifies: self.x_start, self.x_end, self.x_width, self.y_height, self.poly_index, self.reference_index
        '''
        lat_inc = self.reference_lat_increment
        lon_inc = self.reference_lon_increment

        #translate starting and ending coordinates to starting and ending x, y positions in a zero-based matrix
        #without considering width of new polygons, initially
        initial_x_start = self._xy_start(self.reference_upper_left.lon, self.upper_left.lon, lon_inc)
        initial_y_start = self._xy_start(self.reference_upper_left.lat, self.upper_left.lat, lat_inc)
        initial_x_end = self._xy_end(self.reference_upper_left.lon, self.bottom_right.lon, lon_inc)
        initial_y_end = self._xy_end(self.reference_upper_left.lat, self.bottom_right.lat, lat_inc)

        #adjust x, y starting and ending positions to ensure the dimensions are evenly divisible by polygon size and
        #and roughly centered over desired area
        self.x_start, self.x_end = self._adjust_dimension(initial_x_start, initial_x_end, self.poly_size)
        self.y_start, self.y_end = self._adjust_dimension(initial_y_start, initial_y_end, self.poly_size)

        self.x_width = self.x_end - self.x_start + 1
        self.y_height = self.y_end - self.y_start + 1

        self.poly_index = self._poly_index()
        self.reference_index = self._reference_index()

    def _reference_index(self):
        '''
        Flattended index of SNODAS polygons included in Grid. Index numbers correspond to index in SNODAS data files
        :return: ndarray.
        '''
        # this height will include the unnecessary rows in the beginning
        index_height = self.y_end + 1  # because zero indexed

        # creating a grid that is already cutting off the bottom rows.
        flat_index = np.arange(self.reference_x_size * index_height)  # zero indexed

        matrix_index = flat_index.reshape((index_height, self.reference_x_size))
        matrix_index = matrix_index[self.y_start:self.y_end + 1, self.x_start:self.x_end + 1]

        return matrix_index.reshape(matrix_index.size)

    def _poly_index(self):
        '''
        Flattended index of Grid polygons. Index is same length as reference index and is used to group SNODAS polygons
        into Grid polygons
        :return: ndarray.
        '''
        pmatrix_width = self.x_width // self.poly_size
        pmatrix_height = self.y_height // self.poly_size

        count = 1
        row = None
        poly_matrix = None
        for x_count in range(1, pmatrix_width + 1):
            for y_count in range(1, pmatrix_height + 1):
                if y_count == 1:
                    row = np.full((self.poly_size, self.poly_size), count, dtype='int')
                else:
                    row = np.concatenate((row, np.full((self.poly_size, self.poly_size), count, dtype='int')), axis=1)
                count += 1
            if x_count == 1:
                poly_matrix = row
            else:
                poly_matrix = np.concatenate((poly_matrix, row), axis=0)

        return poly_matrix.reshape(poly_matrix.size)

    def grid_df(self):
        '''
        Create DataFrame representation of Grid, including Grid geometry in wkt format, index of SNODAS polygons, and
        index of Grid polygons
        '''
        polygons = self._polygons()
        return pd.DataFrame({'geometry': polygons.to_wkt(), 'poly_index': pd.unique(self.poly_index)})

    def depot_distances_df(self, depot_locations_input, grid_df_input):
        '''
        Create dataframe of distances from centroid of each grid polygon to closest CMP depot
        :param depot_locations_input: String. Path of csv file containing coordinates of depot locations
        :param grid_df_input: String. Path of csv file containing geometry and index of grid
        :return: DataFrame. Columns = ['poly_index', 'min_depot_distance']
        '''
        depot_df = pd.read_csv(depot_locations_input)
        depot_gdf = gpd.GeoDataFrame(depot_df, geometry=gpd.points_from_xy(depot_df.longitude, depot_df.lattitude),
                                    crs="EPSG:4326")
        geod = Geod(ellps="WGS84")
        grid_df = pd.read_csv(grid_df_input)
        grid_df['geometry'] = gpd.GeoSeries.from_wkt(grid_df['geometry'])
        grid_gdf = gpd.GeoDataFrame(grid_df, geometry='geometry')
        grid_gdf['centroids'] = grid_gdf['geometry'].centroid

        grid_gdf['min_depot_distance'] = grid_gdf['centroids'].apply(lambda centroid: centroid)

        grid_gdf['min_depot_distance'] = grid_gdf['centroids']\
            .apply(lambda centroid: np.amin(geod.inv(lons1=np.array([centroid.x]*depot_gdf['geometry'].size),
                                                     lats1=np.array([centroid.y]*depot_gdf['geometry'].size),
                                                     lons2=depot_gdf['geometry'].x,
                                                     lats2=depot_gdf['geometry'].y, return_back_azimuth=False)[2]))

        return pd.DataFrame({'poly_index': grid_gdf['poly_index'],
                             'min_depot_distance': grid_gdf['min_depot_distance']})

    def _polygons(self):
        '''
        Create GeoSeries of Grid polygons
        :return: GeoSeries. Grid polygons
        '''
        lat_inc = self.reference_lat_increment
        lon_inc = self.reference_lon_increment

        boxes = None
        # upp left point of area that will be gridded (likely bigger than the mapped area)

        upp_left = Point(lon=self.reference_upper_left.lon + self.x_start * lon_inc.degrees * lon_inc.direction,
                         lat=self.reference_upper_left.lat + self.y_start * lat_inc.degrees * lat_inc.direction)

        max_lat = upp_left.lat
        min_lat = max_lat + lat_inc.degrees * lat_inc.direction * self.poly_size

        for y in range(self.y_height // self.poly_size):
            min_lon = upp_left.lon
            max_lon = min_lon + lon_inc.degrees * lon_inc.direction * self.poly_size
            for x in range(self.x_width // self.poly_size):
                if boxes is None:
                    boxes = gpd.GeoSeries(sgeom.box(min_lon, min_lat, max_lon, max_lat), name='geometry')
                else:
                    boxes = pd.concat([boxes, gpd.GeoSeries(sgeom.box(min_lon, min_lat, max_lon, max_lat),
                                                            name='geometry')], ignore_index=True)
                min_lon = max_lon
                max_lon = min_lon + lon_inc.degrees * lon_inc.direction * self.poly_size
            max_lat = min_lat
            min_lat = max_lat + lat_inc.degrees * lat_inc.direction * self.poly_size

        return boxes
