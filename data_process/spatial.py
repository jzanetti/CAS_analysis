from logging import getLogger

from dask import compute as dask_compute
from dask import delayed as dask_delayed
from dask.diagnostics import ProgressBar
from pandas.core.frame import DataFrame

from data_process import (ANALYSIS_FILEDS_KEY, CENSUS_YEAR_KEY, CONSTRAIN_KEY,
                          CRASH_YEAR_KEY, MEASURE_KEY, POPULATION_MEASURE,
                          QUERY_KEY, REGION_KEY, VALUE_KEY, YEAR_KEY)
from data_process.utils import get_query_keys

logger = getLogger()

def create_spatial(data: DataFrame, population: DataFrame, cfg: dict, num_workers=4) -> dict:
    """Create timeseries data

    Args:
        data (DataFrame): decoded data
        cfg (dict): configuration file
        num_workers (int, optional): multiprocessing processors. Defaults to 4.

    Returns:
        dict: the dict contains timeseries data
    """

    analysis_fields_data = {}

    for field_name in cfg[ANALYSIS_FILEDS_KEY]:

        proc_field = cfg[ANALYSIS_FILEDS_KEY][field_name]
        proc_field_name = list(proc_field.keys())[0]
        
        analysis_fields_data[field_name] = {}
        fields_to_query = get_query_keys(proc_field)

        analysis_fields_data[field_name][proc_field_name] = {}

        for proc_region in cfg[REGION_KEY]:

            analysis_fields_data[field_name][proc_field_name][proc_region] = {}

            for proc_year in cfg[YEAR_KEY]:
                
                analysis_fields_data[field_name][proc_field_name][proc_region][proc_year] = extract_spatial_dataset(
                        data, population, proc_region, proc_year, fields_to_query
                    )

    return analysis_fields_data


def extract_spatial_dataset(
    data: DataFrame, population: DataFrame or None, data_region: str, data_year: int, fields_to_query: dict,
) -> int:
    """extract dataset based on required keys

    Args:
        df (DataFrame): cas dataset (in Dataframe) to be used
        population (DataFrame): population dataset (in Dataframe) to be used
        data_field (str): fields to be queried, e.g., suv

    Returns:
        dict: the dict contains the required dataset
    """

    grouped_data = data[fields_to_query[QUERY_KEY]]

    grouped_data = grouped_data.loc[grouped_data[CRASH_YEAR_KEY] == data_year].loc[
        grouped_data[REGION_KEY] == data_region + " " + REGION_KEY.capitalize()
    ]

    for proc_constrain in fields_to_query[CONSTRAIN_KEY]:
        constrain_name = list(proc_constrain.keys())[0]
        grouped_data = grouped_data.loc[
            grouped_data[constrain_name] == proc_constrain[constrain_name]
        ]
    
    if population is not None:
        grouped_population = population[[REGION_KEY.capitalize(), VALUE_KEY.capitalize(), MEASURE_KEY.capitalize(), CENSUS_YEAR_KEY]]
        grouped_population = grouped_population.loc[grouped_population[MEASURE_KEY.capitalize()] == POPULATION_MEASURE].loc[
            grouped_population[CENSUS_YEAR_KEY] == str(data_year)].loc[grouped_population[REGION_KEY.capitalize()] == data_region]
        
        population_value = grouped_population[VALUE_KEY.capitalize()][grouped_population[VALUE_KEY.capitalize()].index[0]]
    else:
        population_value = 1.0

    return grouped_data[fields_to_query[QUERY_KEY][0]].sum()/population_value
        
