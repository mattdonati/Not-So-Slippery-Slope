from definitions import ROOT_DIR, REGIONAL_UPPER_LEFT, REGIONAL_BOTTOM_RIGHT, POLY_SIZE
from grid import Grid, Point
import argparse
import os

def save_depot_distances(depot_file, grid_file, output_file, upper_left, bottom_right, poly_size):
    '''
    Given a regional grid, calculate and save distances of centroid of each grid polygon from the closest CMP depot
    :param output_file: String. Relative path to output file
    :param upper_left: Tuple. Upper left coordinates of desired coverage area.
    :param bottom_right: Tuple. Bottom right coordinates of desired coverage area.
    :param poly_size: Int. Size of grid polygon dimensions in SNODAS units
    :return: None
    '''
    #create regional grid with polygons of size poly_size x poly_size where each unit is the size of a reference
    #(SNODAS) polygon
    regional_grid = Grid(Point(*upper_left), Point(*bottom_right), poly_size)
    regional_grid.depot_distances_df(os.path.join(ROOT_DIR, depot_file), os.path.join(ROOT_DIR, grid_file))\
        .to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Save distances of centroid of each grid polygon from the closest CMP\
                                                 depot')
    # output argument with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-d', '--depotfile', help='Depot file')
    parser.add_argument('-g', '--gridfile', help='Grid file')
    args = parser.parse_args()
    output_file = args.output
    depot_file = args.depotfile
    grid_file = args.gridfile

    save_depot_distances(depot_file, grid_file, output_file, REGIONAL_UPPER_LEFT, REGIONAL_BOTTOM_RIGHT, POLY_SIZE)


