import argparse
import os
from roads import nar_combine_overlays, regional_nar_overlay_road_features
from definitions import ROOT_DIR, STATE_BREVS
import glob

def save_regional_road_overlay(overlays_directory, output_file):
    '''
    Combine all state overlays into regional overlay. Calculate road features.
    :param overlays_directory: String. Relative path to file directory containing state overlays
    :param output_file: String. Relative path to output file
    :return: None
    '''

    all_files = glob.glob(os.path.join(ROOT_DIR, overlays_directory, "regional_poly_10_road_overlay_*.csv"))
    print(all_files)
    combined_overlay = nar_combine_overlays(all_files)
    regional_nar_overlay_road_features(regional_overlay_input=combined_overlay)\
        .to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine state road overlays and add road features state's road data")
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-d', '--directory', help='State overlays directory')
    args = parser.parse_args()
    output_file = args.output
    overlays_directory = args.directory
    print(overlays_directory)
    save_regional_road_overlay(overlays_directory, output_file)

