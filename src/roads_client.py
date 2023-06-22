import pandas as pd
import geopandas as gpd
import requests
import time
from retrying import retry

class Roads_client(object):
    """The Roads_client class is used to interact with the ArcGIS API for purpose of downloading road data for a state
    in CMP's market"""
    def __init__(self, link, state, spatial_ref, **kwargs):
        '''
        Initiallize a Roads_client object
        :param link: String. ArcGIS API endpoint
        :param state: String. Capitalized full name of state
        :param spatial_ref: String. Coordinate reference system of NAR data set
        :param kwargs: optional URL query parameters
        '''
        self.link = link
        self.call_limit = 2000
        self.record_count = None
        self.state = state

        #URL query parameters
        self.params = {
            "where": "1=1",
            "outFields": "*",
            "resultOffset": "0",
            "outSR": spatial_ref,
            "resultRecordCount": str(self.call_limit),
            "returnCountOnly": "false",
            "f": "geojson"}
        self.add_params(**kwargs)
        self.total_record_count = None

    def add_params(self, **kwargs):
        """Add query parameters and corresponding values to the query string of a Salt_client object
        :param kwargs: Dictionary. Keys are the names of query parameters and values are values of query parameters.
        Keys are strings and values are strings or lists of strings.
        :return:  None
        :modify: self.params"""
        for k, v in kwargs.items():
            if isinstance(v, list):
                self.params.update({str(k): " AND ".join([str(x) for x in v])})
            else:
                self.params.update({str(k): str(v)})

    def get_record_count(self):
        """Ping the API for the record count, and save it in attribute
        :return:  None
        :modify: self.total_record_count"""
        #save current parameters to return to this state following call to API for record count
        temp_params = {**self.params}
        self.add_params(returnCountOnly="true", f="json")
        self.total_record_count = requests.get(self.link, params=self.params).json()["count"]
        self.params = {**temp_params}

    def build_df(self):
        """Make repeated calls to API to download all data for a particular state and concat into DataFrame
        :return: DataFrame with geometry in wkt format
        """
        offset = 0
        #first API call
        self.add_params(resultOffset=str(offset), resultRecordCount=self.call_limit)
        response_json = self.call_API()

        #load into GeoDataframe
        road_gdf = gpd.GeoDataFrame.from_features(response_json["features"])

        time.sleep(5)
        offset += self.call_limit
        while offset < self.total_record_count:
            self.add_params(resultOffset=str(offset), resultRecordCount=self.call_limit)
            response_json = self.call_API()
            road_gdf = pd.concat([road_gdf, gpd.GeoDataFrame.from_features(response_json["features"])],
                                 ignore_index=True)
            offset += self.call_limit
            time.sleep(5)
        return road_gdf.to_wkt()

    @retry(wait_fixed=5000, stop_max_attempt_number=2)
    def call_API(self):
        """Make single call tp API
        :return: response in json format
        :raise: requests.ConnectionError"""
        response = requests.get(self.link, params=self.params)
        if response.status_code != 200:
            raise requests.ConnectionError(f"Requests error, status code {response.status_code}, params {self.params}")
        else:
            return response.json()
