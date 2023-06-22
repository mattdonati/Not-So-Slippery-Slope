from definitions import ROOT_DIR, IOWA_UPPER_LEFT, IOWA_BOTTOM_RIGHT, POLY_SIZE
from grid import Grid, Point
import argparse
import os

def save_iowa_grid(output_file, upper_left, bottom_right, poly_size):
    '''
    Create a grid over the state of Iowa and save as Dataframe in wkt format.
    :param output_file: String. Relative path to output file
    :param upper_left: Tuple. Upper left coordinates of desired coverage area.
    :param bottom_right: Tuple. Bottom right coordinates of desired coverage area.
    :return: None
    '''
    # create iowa grid with polygons of size 10 x 10 where each unit is the size of a reference (SNODAS) polygon
    iowa_grid = Grid(Point(*upper_left), Point(*bottom_right), poly_size)
    # create dataframe of iowa_grid geometries for purpose of GIS overlays
    iowa_grid_df = iowa_grid.grid_df()
    iowa_grid_df.to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create and save to output file, Iowa grid with polygons of size 10x10\
                                                 (in units of SNODAS polygons)')
    # output argument with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    args = parser.parse_args()
    output_file = args.output

    save_iowa_grid(output_file, IOWA_UPPER_LEFT, IOWA_BOTTOM_RIGHT, POLY_SIZE)


