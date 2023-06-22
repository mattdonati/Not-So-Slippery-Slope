import argparse
from salt_model import quarterly_solid_precip
import os
from definitions import ROOT_DIR
import glob

def solid_precipitation(glob_pattern, output_file):
    '''Summarize quarterly snodas solid preciptiation for purpose of demonstration of changes in snodas params year over
    year'''
    all_files = glob.glob(os.path.join(ROOT_DIR, glob_pattern))
    quarterly_solid_precip(all_files).to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Summarize quarterly snodas solid preciptiation for purpose of '
                                                 'visualizing changes in snodas params year over year')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-g', '--globpattern', help='Glob file pattern for input')
    args = parser.parse_args()
    output_file = args.output
    glob_pattern = args.globpattern

    solid_precipitation(glob_pattern, output_file)