import argparse
from salt_model import sales_model, company_model
import os
from definitions import ROOT_DIR

def company_sales(predictions_file, actual_sales_file, distances_file, output_file):
    '''Using salt predictions by polygon for each quarter, estimate company sales using economics gravity formula to
    weight by distance to closest CMP depot'''
    sales_df = sales_model(os.path.join(ROOT_DIR, predictions_file), os.path.join(ROOT_DIR, actual_sales_file),
                           os.path.join(ROOT_DIR, distances_file))
    sales_df.to_csv('final_sales_df.csv', index=False)
    company_model(sales_df).to_csv(os.path.join(ROOT_DIR, output_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Derive company estimates from market estimates')
    # CLI arguments with short and long flags
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-p', '--predictions', help='Predictions file')
    parser.add_argument('-a', '--actualsales', help='Actual sales file')
    parser.add_argument('-d', '--distances', help='Depot distance file')
    args = parser.parse_args()
    output_file = args.output
    predictions_file = args.predictions
    actual_sales_file = args.actualsales
    distances_file = args.distances

    company_sales(predictions_file, actual_sales_file, distances_file, output_file)