from definitions import ROOT_DIR, REGIONAL_UPPER_LEFT, REGIONAL_BOTTOM_RIGHT, POLY_SIZE
from grid import Grid, Point
import argparse
import os

def save_regional_grid(output_file, upper_left, bottom_right, poly_size):
    '''
    Create and save grid of polygons over entire market area for purpose of geospatially aligning data on
    winter conditions, roads, and distance from depots. The coordinates of regional grid align with the SNODAS grid
    :param output_file: String. Relative path to output file
    :param upper_left: Tuple. Upper left coordinates of desired coverage area.
    :param bottom_right: Tuple. Bottom right coordinates of desired coverage area.
    :return: None
    '''
    # create regional grid with polygons of size 10 x 10 where each unit is the size of a reference (SNODAS) polygon
    regional_grid = Grid(Point(*upper_left), Point(*bottom_right), poly_size)
    # create dataframe of regional grid geometries for purpose of GIS overlays
    regional_grid_df = regional_grid.grid_df()
    regional_grid_df.to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create and save to output file, regional grid with polygons of size\
                                                 10x10 (in units of SNODAS polygons)')
    # output argument with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    args = parser.parse_args()
    output_file = args.output

    save_regional_grid(output_file, REGIONAL_UPPER_LEFT, REGIONAL_BOTTOM_RIGHT, POLY_SIZE)


