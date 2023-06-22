from ftplib import FTP
import numpy as np
import pandas as pd
import os
import time
import logging
import tarfile
from definitions import ROOT_DIR, EMAIL_ADDRESS
import dill
from utility import to_padded_num, to_month_tag

snodas_client_logger = logging.getLogger('snodas_client')
snodas_client_logger.setLevel(logging.DEBUG) #set cut off for logging to lowest severity
snodas_client_handler = logging.FileHandler('../snodas_client.log')
snodas_client_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
snodas_client_handler.setFormatter(snodas_client_formatter)
snodas_client_logger.addHandler(snodas_client_handler)

def snodas_download_day(year, day, month, dest_dir):
    '''
    Create directory and download SNODAS files corresponding to one day.
    :param year: four digit year
    :param month: capitalized three letter month abbreviation or integer month
    :param day: non-zero padded integer for day of month
    :param dest_dir: String. relative path of directory for cacheing SNODAS tar files
    :return: None
    '''
    month_name = to_month_tag(month)
    month_num = month_name[:2]

    # padded num
    day_num = to_padded_num(day)

    # 1. Set the directory you would like to download the files to
    absolute_destdir = os.path.join(ROOT_DIR, dest_dir)

    file_name = f"SNODAS_unmasked_{year}{month_num}{day_num}.tar"

    # check to see if already have the file
    # file format example SNODAS_unmasked_20190201.tar
    if os.path.exists(os.path.join(absolute_destdir, file_name)):
        snodas_client_logger.info(f"file {file_name} already saved")
        return
    if not os.path.exits(absolute_destdir):
        os.makedirs(absolute_destdir)
    # 2. Set the path to the FTP directory that contains the data you wish to download.
    directory = f'/DATASETS/NOAA/G02158/unmasked/{year}/{month_name}'
    # 3. Set the password which will be your email address
    password = EMAIL_ADDRESS

    # if not os.path.exists(destdir):
    # os.mkdir does not let you make a sub directory
    # os.makedirs(destdir)
    ############################################
    ### Don't need to change this code below ###
    ############################################
    # FTP server
    ftpdir = 'sidads.colorado.edu'

    # Connect and log in to the FTP
    ftp = FTP(ftpdir)
    ftp.login('anonymous', password)

    # Change to the directory where the files are on the FTP
    ftp.cwd(directory)
    ftp.dir()

    # Get a list of the files in the FTP directory
    files = ftp.nlst()
    files = files[2:]

    # Change to the destination directory on own computer where you want to save the files
    os.chdir(absolute_destdir)

    # Download all the files within the FTP directory
    if file_name in files:
        ftp.retrbinary('RETR ' + file_name, open(file_name, 'wb').write)
    else:
        snodas_client_logger.error(file_name + " may not be on snodas server")

    # Close the FTP connection
    ftp.quit()

def snodas_download_quarter(start, end, dest_dir):
    '''
    Download SNODAS files for every day in a date range.
    :param start: Datetime. Start date.
    :param end: Datetime. End date.
    :return: None
    '''
    dates = pd.date_range(start=start, end=end)
    for date in dates:
        snodas_download_day(date.year, date.day, date.month, dest_dir)
        time.sleep(10)

def snodas_unpack_tar_quarter(start, end, tar_dir, unpacked_dir):
    '''
     Unpack SNODAS tar files for every date within time period.
    :param start: Datetime. Start date
    :param end: Datetime. End date
    :return: None
    '''
    dates = pd.date_range(start=start, end=end)
    for date in dates:
        save_tar(date.year, date.day, date.month, tar_dir, unpacked_dir)

def save_tar(year, day, month, tar_dir, unpacked_dir):
    '''Unpack individual SNODAS tar file
    :param year: (int) four digit year
    :param month: (str) three-letter abbreviation of month
    :param day: (int) non-zero-padded day of month
    :return:
    '''

    month_tag = to_month_tag(month)
    month_num = month_tag[:2]
    # padded num
    day_num = to_padded_num(day)
    # check to see if date already unzipped
    if os.path.exists(os.path.join(ROOT_DIR, unpacked_dir, f"{year}{month_num}{day_num}")):
        return
    file_name = f"SNODAS_unmasked_{year}{month_num}{day_num}.tar"
    origin_dir = os.path.join(ROOT_DIR, tar_dir)
    file = os.path.join(origin_dir, file_name)
    if os.path.exists(file):
        save_dir = os.path.join(ROOT_DIR, unpacked_dir, f"{year}{month_num}{day_num}")
        if not os.path.exists(save_dir):
            # os.mkdir does not let you make a sub directory
            os.makedirs(save_dir)
        else:
            snodas_client_logger.info(f"upacking of {file_name} already exists")
            return
        with tarfile.open(file, 'r') as tf:
            for member in tf.getmembers():
                if member.name.endswith('.dat.gz'):
                    try:
                        tf.extract(member, save_dir)
                    except Exception as e:
                        snodas_client_logger.info(f"unpacking {member} from {file_name} caused {str(e)}")
        # remove tar file once extracted
        os.remove(file)
    else:
        snodas_client_logger.error(f"unpacking {file_name} failed, file may not exist")

def snodas_download(date_file, dest_dir):
    '''
    Download SNODAS files for every day contained in list of dates.
    :param date_file: String. Path to file containing list of dates in .pkd format
    :return: None
    '''
    with open(date_file, 'rb') as f:
        date_list = np.array(dill.load(f))

    for d in date_list:
        date = pd.to_datetime(d)
        snodas_download_day(date.year, date.day, date.month, dest_dir)
        time.sleep(10)

def snodas_unpack_all(date_file, tar_dir, unpacked_dir):
    '''
    Unpack SNODAS tar files for every date within list of dates.
    :param date_file: String. Path to file containing list of dates in .pkd format
    :param tar_dir: String. Relative path of directory containing SNODAS tar files
    :param unpacked_dir: String. Relative path to directory for unpacked SNODAS files
    :return: None
    '''
    with open(os.path.join(ROOT_DIR,date_file), 'rb') as f:
        date_list = np.array(dill.load(f))
    for d in date_list:
        date = pd.to_datetime(d)
        save_tar(date.year, date.day, date.month, tar_dir, unpacked_dir)
