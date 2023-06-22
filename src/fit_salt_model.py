import argparse
import os
from definitions import ROOT_DIR
from salt_model import total_salt_per_polygon
import dill
from definitions import MIN_SOLID

def fit_salt_model(winter_iowa_salt_data_path, output_file, min_solid):
    '''
    Fit and save machine learning model estimating total salt per polygon using Iowa Winter Salt Data
    :return: None
    '''
    fitted_salt_model = total_salt_per_polygon(data_input=os.path.join(ROOT_DIR, winter_iowa_salt_data_path),
                                               min_solid=min_solid)
    with open(os.path.join(ROOT_DIR, output_file), 'wb') as f:
        dill.dump(fitted_salt_model, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fit Winter Iowa Salt model and save to file')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-i', '--input', help='Winter Iowa salt data file path')
    args = parser.parse_args()
    output_file = args.output
    input_file = args.input

    fit_salt_model(input_file, output_file, MIN_SOLID)