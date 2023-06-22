import os
from definitions import ROOT_DIR, SALT_LINK
from salt import build_salt_df
import argparse

def download_winter_iowa_data(link, filename):
    '''
    Download winter Iowa salt data and save to file
    :param link: String. Iowa DOT Winter Operations API endpoint
    :param filename: String. relative path from root directory to file
    :return: None
    '''
    build_salt_df(link).to_csv(os.path.join(ROOT_DIR, filename), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and save salt usage data from Iowa DOT')
    # output argument with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    args = parser.parse_args()
    output_file = args.output

    download_winter_iowa_data(SALT_LINK, output_file)

