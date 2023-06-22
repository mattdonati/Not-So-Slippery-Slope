import numpy as np

def to_padded_num(d):
    zero_padded = {1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06", 7: "07", 8: "08", 9: "09"}
    str_zero_padded = {"1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06", "7": "07", "8": "08", "9": "09"}
    return zero_padded.get(d) or str_zero_padded.get(d) or str(d)

def to_month_tag(m):
    abbrev_dict = {"Jan": "01_Jan", "Feb": "02_Feb", "Mar": "03_Mar", "Apr": "04_Apr", "May": "05_May", "Jun": "06_Jun",
                   "Jul": "07_Jul", "Aug": "08_Aug", "Sep": "09_Sep", "Oct": "10_Oct", "Nov": "11_Nov", "Dec": "12_Dec"}
    num_dict = {1: "01_Jan", 2: "02_Feb", 3: "03_Mar", 4: "04_Apr", 5: "05_May", 6: "06_Jun",
                7: "07_Jul", 8: "08_Aug", 9: "09_Sep", 10: "10_Oct", 11: "11_Nov", 12: "12_Dec"}
    string_dict = {"1": "01_Jan", "2": "02_Feb", "3": "03_Mar", "4": "04_Apr", "5": "05_May", "6": "06_Jun",
                "7": "07_Jul", "8": "08_Aug", "9": "09_Sep", "10": "10_Oct", "11": "11_Nov", "12": "12_Dec"}
    pad_string_dict = {"01": "01_Jan", "02": "02_Feb", "03": "03_Mar", "04": "04_Apr", "05": "05_May", "06": "06_Jun",
                "07": "07_Jul", "08": "08_Aug", "09": "09_Sep", "10": "10_Oct", "11": "11_Nov", "12": "12_Dec"}
    return abbrev_dict.get(m) or num_dict.get(m) or string_dict.get(m) or pad_string_dict.get(m)

def dat_to_numpy(fname):
    '''takes the name of an individual day data file and returns a numpy of values'''
    # values are in big endian format
    #tested with fname = "20221001"
    return np.fromfile(fname, dtype=np.dtype('>h')).astype(np.int32)