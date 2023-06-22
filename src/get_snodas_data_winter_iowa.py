from snodas_client import snodas_download, snodas_unpack_all
import argparse

def download_snodas_winter_iowa(input_file, tar_dir, unpacked_dir):
    '''
    Download and unpack SNODAS tar files for dates included in Iowa winter salt dataset
    :param input_file: String. relative path of unique iowa winter dates file in .pkd format
    :param dest_dir: String. relative path of directory for cacheing SNODAS tar files
    :return: None
    '''
    snodas_download(input_file, tar_dir)
    #unpack tar files into dat.gzip file and remove tar files
    snodas_unpack_all(input_file, tar_dir, unpacked_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Download and unpack SNODAS files for winter iowa salt data set save salt usage data from Iowa DOT')
    # output argument with short and long flags
    parser.add_argument('-i', '--input', help='Input file')
    parser.add_argument('-t', '--tardir', help='Destination directory for SNODAS tar files')
    parser.add_argument('-u', '--unpackeddir', help='Destination directory for unpacked SNODAS files')
    args = parser.parse_args()
    input_file = args.input
    tar_dir = args.tardir
    unpacked_dir = args.unpackeddir

    download_snodas_winter_iowa(input_file, tar_dir, unpacked_dir)

