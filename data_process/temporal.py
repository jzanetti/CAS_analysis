from logging import getLogger

from dask import compute as dask_compute
from dask import delayed as dask_delayed
from dask.diagnostics import ProgressBar
from numpy import array, asarray, linspace
from numpy import sum as numpy_sum
from pandas.core.frame import DataFrame
from sklearn.linear_model import LinearRegression

from data_process import (ANALYSIS_FILEDS_KEY, CONSTRAIN_KEY, CRASH_YEAR_KEY,
                          QUERY_KEY, REGION_KEY, YEAR_KEY)
from data_process.utils import get_query_keys

logger = getLogger()



def extract_temporal_dataset(
    data: DataFrame, data_region: str, data_year: int, fields_to_query: dict
) -> int:
    """extract dataset based on required keys

    Args:
        df ([type]): dataset (in Dataframe) to be used
        fields_to_query (dict): fields to be queried

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

    return grouped_data[fields_to_query[QUERY_KEY][0]].sum()


def create_time_series(data: DataFrame, cfg: dict, num_workers=4) -> dict:
    """Create timeseries data

    Args:
        data (DataFrame): decoded data
        cfg (dict): configuration file
        num_workers (int, optional): multiprocessing processors. Defaults to 4.

    Returns:
        dict: the dict contains timeseries data
    """

    jobs = []

    for field_name in cfg[ANALYSIS_FILEDS_KEY]:

        proc_field = cfg[ANALYSIS_FILEDS_KEY][field_name]

        for proc_region in cfg[REGION_KEY]:

            fields_to_query = get_query_keys(proc_field)

            for proc_year in cfg[YEAR_KEY]:

                jobs.append(
                    dask_delayed(extract_temporal_dataset)(
                        data, proc_region, proc_year, fields_to_query
                    )
                )

    ProgressBar().register()

    logger.info("computing jobs with dask ...")

    outputs = dask_compute(*jobs, num_workers=num_workers)

    i = 0

    analysis_fields_data = {}

    for field_name in cfg[ANALYSIS_FILEDS_KEY]:

        proc_field = cfg[ANALYSIS_FILEDS_KEY][field_name]
        analysis_fields_data[field_name] = {}

        for proc_region in cfg[REGION_KEY]:

            fields_to_query = get_query_keys(proc_field)

            analysis_fields_data[field_name][proc_region] = []

            for proc_year in cfg[YEAR_KEY]:
                analysis_fields_data[field_name][proc_region].append(outputs[i])
                i += 1

    return analysis_fields_data


def obtain_temporal_trend(ts_data: array) -> dict:
    """obtain the temporal changes trend using a SVR model

    Args:
        ts_data (array): decoded 2d timeseries data

    Returns:
        dict: the temporal change created by both SVR and Linear
    """

    total_ts_data = numpy_sum(ts_data, axis=0)
    x_regres = linspace(0, total_ts_data.shape[0], 100000)[:, None]
    x = asarray(range(0, len(total_ts_data)))
    x = x.reshape((len(x), 1))

    # svr_model = SVR(kernel="rbf", gamma=3.0)
    regres_model = LinearRegression()
    regres_model.fit(x, total_ts_data)

    return {"x_regres": x_regres, "y_regres": regres_model.predict(x_regres), "x": x, "y": total_ts_data}
