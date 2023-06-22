from definitions import ROOT_DIR, IOWA_UPPER_LEFT, IOWA_BOTTOM_RIGHT, POLY_SIZE
from snodas import snodas_iowa_with_poly_index, agg_by_poly_index
import argparse
import os
from grid import Grid, Point

def save_winter_iowa_snodas(upper_left, bottom_right, poly_size, date_file, output_file):
   '''
   Create SNODAS data set for Iowa winter salt analysis
   :param upper_left: Tuple. Upper left coordinates of Iowa grid coverage area
   :param bottom_right: Tuple. Bottom right coordinates of Iowa grid coverage area
   :param poly_size: Int. Size each dimension of polygon in units of SNODAS polygons
   :param date_file: String. Relative path to file containing date range for Winter Iowa Salt data
   :param output_file: String. Relative path of outputfile
   :return: None
   '''

   '''create iowa grid parameters with polygons of size 10 x 10 where each unit is the size of a reference (SNODAS) 
    polygon'''
   iowa_grid = Grid(Point(*upper_left), Point(*bottom_right), poly_size)

   snodas_df = snodas_iowa_with_poly_index(iowa_grid, os.path.join(ROOT_DIR, date_file))
   agg_by_poly_index(snodas_df).to_csv(os.path.join(ROOT_DIR, output_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Dataframe of SNODAS params by polygon for Winter Iowa dataset')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-d', '--datefile', help='Date file')
    args = parser.parse_args()
    output_file = args.output
    date_file = args.datefile

    save_winter_iowa_snodas(IOWA_UPPER_LEFT, IOWA_BOTTOM_RIGHT, POLY_SIZE, date_file, output_file)




