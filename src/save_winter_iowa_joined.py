from definitions import ROOT_DIR
from salt import join_it_iowawinter
import argparse
import os

def save_winter_iowa_joined(salt_file, snodas_file, roads_file, output_file):
    '''Combine Iowa Datasets (salt, roads, snodas)'''
    # join salt-overlay with road overlay and snodas data
    join_it_iowawinter(salt_input=os.path.join(ROOT_DIR, salt_file),
                            snodas_input=os.path.join(ROOT_DIR, snodas_file),
                            roads_input=os.path.join(ROOT_DIR, roads_file)).to_csv(os.path.join(ROOT_DIR, output_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Join Winter Iowa Features')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-sa', '--saltfile', help='Salt file')
    parser.add_argument('-sn', '--snodasfile', help='Snodas file')
    parser.add_argument('-r', '--roadsfile', help='Roads file')

    args = parser.parse_args()
    output_file = args.output
    salt_file = args.saltfile
    snodas_file = args.snodasfile
    roads_file = args.roadsfile

    save_winter_iowa_joined(salt_file, snodas_file, roads_file, output_file)
