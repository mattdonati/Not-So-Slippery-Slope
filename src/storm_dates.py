import os
from salt import parse_dates
import argparse
from definitions import ROOT_DIR

def add_storm_dates(input_file, output_file):
    '''
    Determine storm dates and add to winter Iowa salt data'
    :param input_file: String. Relative path to file containing winter Iowa salt data
    :param output_file: String. Relative path to output file
    :return: None
    '''
    parse_dates(salt_input=os.path.join(ROOT_DIR, input_file)).to_csv(os.path.join(ROOT_DIR, output_file), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Determine storm dates from winter Iowa salt data and add to data')
    #input/output arguments with short and long flags
    parser.add_argument('-i', '--input', help='Input file')
    parser.add_argument('-o', '--output', help='Output file')
    args = parser.parse_args()
    output_file = args.output
    input_file = args.input

    add_storm_dates(input_file, output_file)