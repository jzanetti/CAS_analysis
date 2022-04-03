from logging import Formatter, StreamHandler, getLogger

from genericpath import exists
from pandas import read_csv
from yaml import safe_load

from data_process import (CONSTRAIN_KEY, CRASH_YEAR_KEY, LOGGER_LEVEL,
                          QUERY_KEY, REGION_KEY)


def setup_logging():
    """set up logging system for tasks

    Returns:
        object: a logging object
    """
    formatter = Formatter("%(asctime)s - %(name)s.%(lineno)d - %(levelname)s - %(message)s")
    ch = StreamHandler()
    ch.setLevel(LOGGER_LEVEL)
    ch.setFormatter(formatter)
    logger = getLogger()
    logger.setLevel(LOGGER_LEVEL)
    logger.addHandler(ch)

    return logger


def read_dataset(data_path: str):
    """Read dataset from NZTA

    Args:
        data_path (str): the dataset to be read
    """
    if not exists(data_path):
        raise Exception(f"not able to locate the data from {data_path}")

    if data_path.endswith("csv"):
        df = read_csv(data_path)
    else:
        raise Exception("currently only CSV format is supported ...")

    return df


def read_config(config_path: str):
    """Read config file for temporal analysis

    Args:
        config_path_str (str): the configuration file to be used
    """
    if not exists(config_path):
        raise Exception(f"not able to locate the config file from {config_path}")

    with open(config_path, "r") as fin:
        cfg = safe_load(fin)

    return cfg


def get_query_keys(proc_field) -> dict:
    """Return the keys to be queried

    Args:
        key_field (str): field to be queried, e.g., crashes

    Returns:
        dict: the fields to be queried
    """
    query_key = list(proc_field.keys())[0]

    query_keys = [query_key, CRASH_YEAR_KEY, REGION_KEY]

    if proc_field[query_key] is None:
        return {QUERY_KEY: query_keys, CONSTRAIN_KEY: []}

    query_constrains = []
    for constrain_key in proc_field[query_key]:

        query_keys.append(constrain_key)
        query_constrains.append({constrain_key: proc_field[query_key][constrain_key]})

    return {QUERY_KEY: query_keys, CONSTRAIN_KEY: query_constrains}
