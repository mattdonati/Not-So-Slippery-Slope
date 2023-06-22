from definitions import ROOT_DIR
import argparse
import os
from salt import build_iowa_winter, groupby_poly_iowawinter

def save_overlay_winter_iowa(output_file, salt_file, grid_file):
    '''Create and save winter Iowa salt overlay. Overlay grid onto salt data; add salt-per-segment metrics that, along
    with the proportions of each segment that are intersected by each polygon, are used to determine the amount of a
    segment's salt that belongs in each polygo
    :param output_file: String. Relative path to outputfile
    :param salt_file: String. Relative path to .csv file containing Dataframe of winter Iowa salt data.
    :param grid_file: String. Relative path to .csv file containing Dataframe of Iowa grid
    :return: None
    :modifies: Outputfile. Saves overlay with salt data summarized per polygon per storm date in Dataframe. .csv format.
    '''
    #create initial overlay and calculate per segment per polygon salt metrics
    salt_df = build_iowa_winter(salt_input=os.path.join(ROOT_DIR, salt_file),
                                   grid_input=os.path.join(ROOT_DIR, grid_file))
    # group by polygon and sum up total salt that falls within each polygon by storm date
    groupby_poly_iowawinter(salt_input=salt_df) \
        .to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create, and save to output file, overlay of Iowa grid with winter\
                                                 Iowa salt data with salt usage aggregated by polygon.')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-s', '--saltfile', help='Salt input file')
    parser.add_argument('-g', '--gridfile', help='Grid input file')
    args = parser.parse_args()
    output_file = args.output
    salt_file = args.saltfile
    grid_file = args.gridfile

    save_overlay_winter_iowa(output_file, salt_file, grid_file)


