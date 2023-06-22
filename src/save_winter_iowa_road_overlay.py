import argparse
from roads import winter_iowa_roads_overlay, winter_iowa_road_features
import os
from definitions import ROOT_DIR

def save_winter_iowa_road_overlay(road_file, grid_file, output_file):
    '''
    Create iowa road-overlay (overlay of grid and roads) that aligns with salt-overlay because the components of the
    regional overlay that are over Iowa won't align as well with the salt data.
    :param road_file: String. Relative path to Iowa roads .csv file
    :param grid_file: String. Relative path to Winter Iowa grid .csv file
    :param output_file: String. Relative path to output file
    :return: None
    '''
    ''''''
    overlay_df = winter_iowa_roads_overlay(roads_input=os.path.join(ROOT_DIR, road_file),
                                    grid_input=os.path.join(ROOT_DIR, grid_file))
    #create road features and groupby polygon index
    winter_iowa_road_features(roads_overlay_input=overlay_df).to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create, and save to output file, overlay of Iowa grid with roads\
                                                  data. Include road features by polygon.')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-r', '--roadfile', help='Road input file')
    parser.add_argument('-g', '--gridfile', help='Grid input file')
    args = parser.parse_args()
    output_file = args.output
    road_file = args.roadfile
    grid_file = args.gridfile

    save_winter_iowa_road_overlay(road_file, grid_file, output_file)