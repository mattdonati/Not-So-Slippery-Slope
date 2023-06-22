from snodas_client import snodas_download_quarter, snodas_unpack_tar_quarter
from definitions import ROOT_DIR, START_YEAR, END_YEAR
import argparse

def download_snodas_regional(tar_dir, unpacked_dir, start_year, end_year):
    '''
    Download and unpack SNODAS tar files for dates entire coverage period over regional area
    :param tar_dir: String. relative path of directory for cacheing SNODAS tar files
    :param unpacked_dir: String. relative path of directory for unpacked binary SNODAS files
    :return: None
    '''

    '''
    Download and prepare SNODAS data corresponding to regional grid area for every quarter in time frame
    '''
    for year in range(end_year, start_year - 1, -1):
        # Q1
        snodas_download_quarter(f"12/31/{year - 1}", f"04/01/{year}", dest_dir=tar_dir)
        snodas_unpack_tar_quarter(f"12/31/{year - 1}", f"04/01/{year}", tar_dir=tar_dir, unpacked_dir=unpacked_dir)
        # Q4
        snodas_download_quarter(f"09/30/{year}", f"01/01/{year + 1}", dest_dir=tar_dir)
        snodas_unpack_tar_quarter(f"09/30/{year}", f"01/01/{year + 1}", tar_dir=tar_dir, unpacked_dir=unpacked_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Download and unpack SNODAS files for regional area over entire coverage period')
    # output argument with short and long flags
    parser.add_argument('-t', '--tardir', help='Destination directory for SNODAS tar files')
    parser.add_argument('-u', '--unpackeddir', help='Destination directory for unpacked SNODAS files')
    args = parser.parse_args()
    tar_dir = args.tardir
    unpacked_dir = args.unpackeddir

    download_snodas_regional(tar_dir, unpacked_dir, start_year=START_YEAR, end_year=END_YEAR)

