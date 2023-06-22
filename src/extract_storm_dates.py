import os
from salt import unique_salt_dates
import argparse
from definitions import ROOT_DIR
import dill

def add_storm_dates(input_file, output_file):
    '''
    Extract set of unique dates, including storm dates and 1 day priors, to specify range of SNODAS variable downloads
    :param input_file: String. Relative path to file containing winter Iowa salt data with storm dates
    :param output_file: String. Relative path to output file in .pkd format
    :return: None
    '''
    all_dates = unique_salt_dates(salt_input=input_file)
    unique_dates_path = os.path.join(ROOT_DIR, output_file)
    with open(unique_dates_path, 'wb') as f:
        dill.dump(all_dates, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract set of unique dates from winter Iowa salt data and save .pkd')
    #input/output arguments with short and long flags
    parser.add_argument('-i', '--input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')
    args = parser.parse_args()
    output_file = args.output
    input_file = args.input

    add_storm_dates(input_file, output_file)
