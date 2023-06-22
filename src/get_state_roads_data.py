import os
import sys
from definitions import ROOT_DIR, NAR_LINK, NAR_CRS
from roads import build_state_roads_df

def download_nar_roads_data(state, link, crs):
    '''
    Download North American Roads (NAR) data for a state in CMP's market
    :param state: String. full state name
    :param link: String. ArcGIS API endpoint for North American Roads data
    :param crs: String. Coordinate reference system of NAR data sets
    :return: None
    '''
    if state == "West_Virginia":
        state_query_value = "West Virginia"
    else:
        state_query_value = state
    build_state_roads_df(link, state_query_value, crs).to_csv(os.path.join(ROOT_DIR, f"data/raw/roads_data_{state}.csv"))

def get_cli_argument():
    # Check the number of arguments
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]}.py <argument> command line argument missing")
        sys.exit(1)

    # Access the command-line argument
    return sys.argv[1]

if __name__ == "__main__":
    state = get_cli_argument()
    download_nar_roads_data(state, NAR_LINK, NAR_CRS)