from logging import INFO
from os import environ, makedirs
from os.path import exists, join
from uuid import uuid4

from numpy import nan

# --------------------------------
# KEYS USED IN THE CODES
# --------------------------------
GEOJSON_KEY = "geojson"
CSV_KEY = "csv"
CAS_KEY = "cas"
CRASH_YEAR_KEY = "crashYear"
REGION_KEY = "region"
VALUE_KEY = "value"
YEAR_KEY = "year"
MEASURE_KEY = "measure"
ANALYSIS_FILEDS_KEY = "analysis_fields"
QUERY_KEY = "query_key"
CONSTRAIN_KEY = "constrain_key"
POPULATION_KEY = "population"
CENSUS_YEAR_KEY = "Census year"
LATLON_KEY = "latlon"
RECORDS_KEY = "records"
LAT_KEY = "lat"
LON_KEY = "lon"
FEATURES_KEY = "features"

# --------------------------------
# ENVIRONMENT VARIALBLES
# --------------------------------
WORKDIR = environ.get("WORKDIR", join("/tmp/cas_analysis", str(uuid4())))
DATA_API_SRC = {
    GEOJSON_KEY: environ.get(
        f"{GEOJSON_KEY}_src",
        "https://opendata.arcgis.com/datasets/8d684f1841fa4dbea6afaefc8a1ba0fc_0.geojson",
    ),
    CSV_KEY: environ.get(
        f"{CSV_KEY}_src",
        "https://opendata.arcgis.com/api/v3/datasets/8d684f1841fa4dbea6afaefc8a1ba0fc_0/downloads/data?format=csv&spatialRefId=2193",
    ),
}
LOGGER_LEVEL = environ.get("LOGGER_LEVEL", INFO)

# --------------------------------
# CONSTANTS
# --------------------------------
TIMESERIES_FILENAME = "timeseries_{field_name}.png"
SPATIAL_FILENAME = "spatial_{field_name}.png"
FEATURE_IMPORTANCE_FILENAME = "feature_importance_{field_name}.png"
FEATURE_SHAP_FILENAME = "feature_shap_{field_name}.png"
POPULATION_MEASURE = "Census usually resident population count"
if not exists(WORKDIR):
    makedirs(WORKDIR)

MAP_CFG = {
    "resolution": "i",
    "llcrnrlon": 165.0,
    "urcrnrlon": 180.0,
    "llcrnrlat": -48.0,
    "urcrnrlat": -33.0
}

# --------------------------------
# FEATURE DIGITIZATION
# --------------------------------
STR2DIGIT_MAPPING = {
    "weatherA": {'Fine': 0, 'Light rain': 1, 'Mist or Fog': 2, 'Heavy rain': 3, 'Snow': 4,
       'Hail or Sleet': 5},
    "directionRoleDescription": {'North': 0, 'East': 1, 'South': 2, 'West': 3},
    "flatHill": {'Flat': 0, 'Hill Road': 1},
    "light": {"Dark": 0, 'Bright sun': 1, 'Overcast': 2, 'Twilight': 3},
    "roadSurface": {'Sealed': 0, 'Unsealed': 1, 'End of seal': 2},
    "urban": {"Urban": 0, "Open": 1},

    }

MISSING_DATA = {
    "weatherA": ["Null"],
    "directionRoleDescription": ["Null"],
    "flatHill": ["Null"],
    "light": ["Unknown"],
    "NumberOfLanes": [],
    "roadSurface": ["Null"],
    "speedLimit": [],
    "urban": [],
    "bicycle": [],
    "truck": [],
    "motorcycle": []
} # except nan
