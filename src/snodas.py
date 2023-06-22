import numpy as np
import pandas as pd
import os
import logging
from definitions import ROOT_DIR
import dill
import gzip
from utility import to_padded_num, dat_to_numpy

def join_snodas_folder(date, file_pre_suf, x_slice, y_slice, flat_size):
    '''
    For a given date and SNODAS variable, slice dowloaded array according to coverage area
    :param date: Datetime
    :param file_pre_suf: String. Prefix and suffix of file corresponding to variable
    :param x_slice: Slice object. horizontal slice
    :param y_slice: Slice object. vertical slice
    :param flat_size: Int. size of flattened sliced matrix
    :return: Ndarray
    '''
    month_num = to_padded_num(date.month)
    year = date.year
    day = to_padded_num(date.day)

    snodas_folder = os.path.join(ROOT_DIR, "data/raw/snodas_params", f"{year}{month_num}{day}")

    snodas_file = os.path.join(snodas_folder,
                               f"zz_ssmv{file_pre_suf[0]}TNATS{year}{month_num}{day}{file_pre_suf[1]}.dat.gz")

    if not os.path.exits(os.path.join(ROOT_DIR, 'data/raw/binary_files')):
        os.makedirs(os.path.join(ROOT_DIR, 'data/raw/binary_files'))

    b_path = os.path.join(ROOT_DIR, 'data/raw/binary_files',
                          f"zz_ssmv{file_pre_suf[0]}TNATS{year}{month_num}{day}{file_pre_suf[1]}.dat")
    try:
        if not os.path.exists(b_path):
            with gzip.open(snodas_file, 'rb') as gf:
                binary_content = gf.read()
            with open(b_path, 'wb') as bf:
                bf.write(binary_content)
        flat_grid = dat_to_numpy(b_path)
        matrix_grid = flat_grid.reshape((4096, 8192))
        matrix_grid = matrix_grid[y_slice, x_slice]
        new_grid = matrix_grid.reshape(flat_size)

        #clear binary files after loading to numpy
        os.remove(b_path)

        return new_grid

    except Exception as e:
        logging.info(str(e))
        print("error", str(e))
        logging.info(
            f"problem reading binary file:  zz_ssmv{file_pre_suf[0]}TNATS{year}{month_num}{day}{file_pre_suf[1]}.dat")
        empty = np.empty(flat_size)
        empty.fill(np.nan)
        return empty

def snodas_iowa_with_poly_index(grid, date_file):
    '''
    Create Dataframe of SNODAS variables by day across every storm date in Winter Iowa Salt data set.
    :param grid: Grid object. Initialized with Iowa parameters.
    :param date_file: String. Absolute path to file containing list of dates. .pkd format
    :return: DataFrame.
    '''

    y_slice = slice(grid.y_start, grid.y_height + grid.y_start)
    x_slice = slice(grid.x_start, grid.x_width + grid.x_start)
    flat_size = grid.y_height * grid.x_width

    with open(date_file, 'rb') as f:
        dates = np.array(dill.load(f))

    params_dict = {"solid_precip": ("01025SlL01T0024T", "05DP001"),
                   "liquid_precip": ("01025SlL00T0024T", "05DP001"),
                   "SWE": ("11034tS__T0001T", "05HP001"),
                   "snow_depth": ("11036tS__T0001T", "05HP001"),
                   "runoff": ("11044bS__T0024T", "05DP000"),
                   "sub_pack": ("11050lL00T0024T", "05DP000"),
                   "sub_blow": ("11039lL00T0024T", "05DP000"),
                   "sp_temp": ("11038wS__A0024T", "05DP001")
                   }

    snodas_params_df = pd.DataFrame()
    for d in dates:
        date = pd.to_datetime(d)
        month_num = to_padded_num(date.month)
        year = date.year
        day = to_padded_num(date.day)
        snodas_date = np.array(np.datetime64(f'{year}-{month_num}-{day}T00:00'))
        snodas_date.repeat(flat_size, axis=0)
        temp_df = pd.DataFrame({"poly_index": grid.poly_index, "snodas": grid.reference_index, "date": snodas_date})

        for k, v in params_dict.items():
            temp_df[k] = join_snodas_folder(date, v, x_slice, y_slice, flat_size)
        snodas_params_df = pd.concat([snodas_params_df, temp_df], axis=0, ignore_index=True)
    return snodas_params_df

def snodas_regional_with_poly_index(grid, start_date, end_date):
    '''Create Dataframe of SNODAS variables, by day, for a FY calendar quarter. poly_index corresponds to poly_index of
    grid of polygons of size, poly_size
    :param uppleft: upper left coordinates of corresponding grid of polygons
    :param bottright: bottom right coordinates of corresponding grid of polygons
    :param poly_size: size of corresponding grid of polygons
    :param start_date: first day of FY quarter
    :param end_date: last day of FY quarter
    :return: Dataframe
    '''

    y_slice = slice(grid.y_start, grid.y_height + grid.y_start)
    x_slice = slice(grid.x_start, grid.x_width + grid.x_start)
    flat_size = grid.y_height * grid.x_width

    dates = pd.date_range(start=start_date, end=end_date)

    params_dict = {"solid_precip": ("01025SlL01T0024T", "05DP001"),
                    "liquid_precip": ("01025SlL00T0024T", "05DP001"),
                       "SWE": ("11034tS__T0001T", "05HP001"),
                       "snow_depth": ("11036tS__T0001T", "05HP001"),
                       "runoff": ("11044bS__T0024T", "05DP000"),
                       "sub_pack": ("11050lL00T0024T", "05DP000"),
                       "sub_blow": ("11039lL00T0024T", "05DP000"),
                       "sp_temp": ("11038wS__A0024T", "05DP001")
                       }

    snodas_params_df = pd.DataFrame()
    for date in dates:
        month_num = to_padded_num(date.month)
        year = date.year
        day = to_padded_num(date.day)
        snodas_date = np.array(np.datetime64(f'{year}-{month_num}-{day}T00:00'))
        snodas_date.repeat(flat_size, axis=0)
        temp_df = pd.DataFrame({"poly_index": grid.poly_index, "snodas": grid.reference_index, "date": snodas_date})

        for k, v in params_dict.items():
            temp_df[k] = join_snodas_folder(date, v, x_slice, y_slice, flat_size)
        print(temp_df.head())
        print(temp_df.dtypes)
        temp_df = agg_by_poly_index(temp_df)
        snodas_params_df = pd.concat([snodas_params_df, temp_df], axis=0, ignore_index=True)
    return snodas_params_df

def agg_by_poly_index(data_frame):
    '''
    Aggregate SNODAS variables by Grid polygons
    :param data_frame: DataFrame. SNODAS data set with SNODAS variables by SNODAS index
    :return: DataFrame
    '''
    snodas_params_df = data_frame
    snodas_params_df['date'] = snodas_params_df['date'].astype('datetime64[ns]')
    snodas_params_df = snodas_params_df.replace(-9999, np.nan)
    snodas_params_df = snodas_params_df.groupby(['date', 'poly_index'], as_index=False, sort=False).aggregate({
                    "solid_precip": "max",
                    "liquid_precip": "max",
                    "SWE": "max",
                    "snow_depth": "max",
                    "runoff": "max",
                    "sub_pack": "max",
                    "sub_blow": "min",
                    "sp_temp": "min"
     })

    return snodas_params_df

