import argparse
import glob
import os
import dill
import pandas as pd
from definitions import ROOT_DIR
from salt_model import build_quarterly_storm_dataset

def save_quarterly_salt_predictions(fitted_salt_model_path, roads_overlay_input, snodas_directory,):
    '''
    Using fitted salt model and quarterly-regional datasets to make predictions of salt usage by polygon for each
    quarter
    :param fitted_salt_model_path:
    :param roads_overlay_input:
    :param snodas_directory:
    :param quarterly_predictions_path:
    :return:
    '''
    with open(os.path.join(ROOT_DIR, fitted_salt_model_path), 'rb') as f:
        fitted_salt_model = dill.load(f)

    quarterly_salt_predictions_df = pd.DataFrame()
    all_files = glob.glob(os.path.join(ROOT_DIR, snodas_directory, "snodas_params_regional_poly10_Q*.csv"))
    for file in all_files:
        quarter = file[-10:-4]
        quarterly_salt_predictions_df = pd.concat([quarterly_salt_predictions_df,
                build_quarterly_storm_dataset(fitted_salt_model, snodas_input=file,
                                              roads_overlay_input=os.path.join(ROOT_DIR, roads_overlay_input),
                                              quarter=quarter)],
                axis=0,
                ignore_index=True)
        quarterly_salt_predictions_df.groupby(by=['quarter', 'poly_index'], as_index=False).aggregate('sum')\
            .to_csv(os.path.join(ROOT_DIR, output_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Dataframes of regional SNODAS params by polygon for each\
                                                 quarter')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-s', '--saltmodelfile', help='Fitted salt model file path')
    parser.add_argument('-r', '--roadoverlayfile', help='Regional road overlay file path')
    parser.add_argument('-d', '--snodasdirectory', help='Relative directory of snodas regional files')
    args = parser.parse_args()
    output_file = args.output
    snodas_directory = args.snodasdirectory
    fitted_salt_model_path = args.saltmodelfile
    road_overlays_input = args.roadoverlayfile

    save_quarterly_salt_predictions(fitted_salt_model_path, road_overlays_input, snodas_directory)
