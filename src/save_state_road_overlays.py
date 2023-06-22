import argparse
import os
from roads import nar_overlay
from definitions import ROOT_DIR, STATE_BREVS

def save_state_road_overlays(state, grid_file, road_file, outputfile, state_brevs):
    '''
    Create road-overlays of regional grid and NAR roads data for each state. These will be combined into one regional
    overlay
    :param state: String. Full state name
    :param grid_file: String. Relative path to file containing DataFrame of regional grid .csv file
    :param road_file: String. Relative path to file containing Dataframe of state's road data. .csv file
    :param outputfile: String. Relative path to save overlay. .csv file
    :param state_brevs: Dictionary. keys = full state name, values = two-letter state abbreviation
    :return: None
    '''
    nar_overlay(state_brevs.get(state), nar_input=os.path.join(ROOT_DIR, road_file),
                grid_input=grid_file).to_csv(os.path.join(ROOT_DIR, outputfile), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create, and save to output file, overlay of regional grid with a\
                                                 state's road data")
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-s', '--state', help='State name')
    parser.add_argument('-g', '--gridfile', help='Grid file')
    parser.add_argument('-r', '--roadsfile', help='Roads file')
    args = parser.parse_args()
    output_file = args.output
    state = args.state
    grid_file = args.gridfile
    road_file = args.roadsfile

    save_state_road_overlays(state, grid_file, road_file, output_file, STATE_BREVS)

