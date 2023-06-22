from definitions import ROOT_DIR, REGIONAL_UPPER_LEFT, REGIONAL_BOTTOM_RIGHT, POLY_SIZE
from snodas import snodas_regional_with_poly_index
import argparse
import os
from grid import Grid, Point

def save_regional_snodas(upper_left, bottom_right, poly_size, output_file):
    '''
    Create SNODAS data sets corresponding to regional grid area for each quarter in time frame.
    :param regional_grid: Grid. Grid corresponding to entire market area
    :return: None
    '''
    # create regional grid with polygons of size 10 x 10 where each unit is the size of a reference (SNODAS) polygon
    regional_grid = Grid(Point(*upper_left), Point(*bottom_right), poly_size)
    quarter = output_file[-10:-8]
    year = int(output_file[-8:-4])
    if quarter == 'Q1':
        snodas_regional_with_poly_index(regional_grid, f"12/31/{year - 1}", f"04/01/{year}") \
            .to_csv(os.path.join(ROOT_DIR, 'data/interim/' + f'snodas_params_regional_poly{poly_size}_Q1{year}.csv'))
    else:
        snodas_regional_with_poly_index(regional_grid, f"09/30/{year}", f"01/01/{year + 1}") \
            .to_csv(os.path.join(ROOT_DIR, 'data/interim/' + f'snodas_params_regional_poly{poly_size}_Q4{year}.csv'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Dataframes of regional SNODAS params by polygon for each\
                                                 quarter')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    args = parser.parse_args()
    output_file = args.output

    save_regional_snodas(REGIONAL_UPPER_LEFT, REGIONAL_BOTTOM_RIGHT, POLY_SIZE, output_file)




