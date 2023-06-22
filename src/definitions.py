import os

EMAIL_ADDRESS = ""
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
STATES = [
        "Illinois",
        "Indiana",
        "Iowa",
        "Kentucky",
        "Michigan",
        "Minnesota",
        "Missouri",
        "Ohio",
        "Pennsylvania",
        "Tennessee",
        "West Virginia",
        "Wisconsin"
        ]
STATE_BREVS = {
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kentucky": "KY",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Missouri": "MO",
        "Ohio": "OH",
        "Pennsylvania": "PA",
        "Tennessee": "TN",
        "West_Virginia": "WV",
        "West Virginia": "WV",
        "Wisconsin": "WI"
}
#Link for North American Roads(NAR) API
NAR_LINK = "https://geo.dot.gov/mapping/rest/services/NTAD/North_American_Roads/MapServer/0/query"
#North American Roads coordinate reference system
NAR_CRS = "4326"
#Link for Iowa DOT historical winter operations API
SALT_LINK = "https://services.arcgis.com/8lRhdTsQyJpO52F1/arcgis/rest/services/Winter_Storm_Analysis_" \
            "Historic_View/FeatureServer/0/query"
IOWA_UPPER_LEFT = (-96.639704, 43.501196)
IOWA_BOTTOM_RIGHT = (-90.140061, 40.375501)
REGIONAL_UPPER_LEFT = (-97.239209, 49.384358)
REGIONAL_BOTTOM_RIGHT = (-77.719519, 34.982972)
POLY_SIZE = 10
END_YEAR = 2022
START_YEAR = 2014
MIN_SOLID = 2

