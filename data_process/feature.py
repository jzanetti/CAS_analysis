
from logging import getLogger
from os.path import join

from matplotlib.pyplot import close, savefig
from numpy import array, asarray, isnan, nan, ones, where
from pandas.core.frame import DataFrame
from shap import Explainer, KernelExplainer, summary_plot
from shap.plots import force as shap_force_plot
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor, plot_importance

from data_process import (FEATURE_IMPORTANCE_FILENAME, FEATURE_SHAP_FILENAME,
                          FEATURES_KEY, MISSING_DATA, STR2DIGIT_MAPPING)

logger = getLogger()

def obtain_importance(work_dir: str, proc_field: str, model, feature_dataset: dict):
    """Obtain the importance for different features

    Args:
        work_dir (str): working directory
        proc_field (str): field to be studied
        model ([type]): training model
        xy (dict): xy dataset
        feature_dataset (dict): processed feature dataset
    """
    logger.info("processing importance ...")

    model.get_booster().feature_names = feature_dataset[proc_field]["features"]
    plot_importance(model.get_booster())
    savefig(join(work_dir, FEATURE_IMPORTANCE_FILENAME.format(field_name=proc_field)), bbox_inches="tight")


def obtain_shap_values(work_dir: str, proc_field: str, model, xy: dict, features_name: list, crash_index = [1,3,5]):
    """Obtain SHAP values

    Args:
        work_dir (str): [description]
        proc_field (str): [description]
        model ([type]): [description]
        xy (dict): [description]
        features_name (list): [description]
        crash_index (list, optional): [description]. Defaults to [1,3,5].
    """
    proc_type = "training"

    all_index = []
    for i in range(len(xy[proc_type]["y"])):
        proc_weather = xy[proc_type]["x"][i][-1]
        proc_crash = xy[proc_type]["y"][i]

        if i == 113609:
            x = 3

        if proc_crash > 1.0 and (proc_weather == 2.0 or proc_weather == 3.0):
            all_index.append(i)

    explainer = Explainer(model)

    len_index = len(all_index)

    logger.info(f"total data to be plotted: {len_index}")

    for i in all_index:

        shap_values = explainer(asarray([xy[proc_type]["x"][i]]))

        shap_force_plot(shap_values[0], show=False, matplotlib=True, feature_names=features_name)

        savefig(join(work_dir, FEATURE_SHAP_FILENAME.format(field_name=proc_field + f"_{i}")), bbox_inches="tight")

        close()


def get_weight(xy: dict) -> array:
    """Get training weights

    Args:
        xy (dict): xy dataset

    Returns:
        array: weights for training
    """
    y_data = xy["training"]["y"]
    weight = ones(y_data.shape)
    weight[y_data > 0.0] = 3.0
    return weight


def create_feature_analysis(work_dir: str, data: DataFrame, cfg: dict) -> dict:

    feature_dataset = extract_feature_dataset(data, cfg)

    for proc_field in cfg[FEATURES_KEY]:

        logger.info(f"feature analysis {proc_field}")

        xy = split_training_test_data(feature_dataset[proc_field]["x"], feature_dataset[proc_field]["y"])

        model = XGBRegressor(max_depth=75, eta=0.1, subsample=0.5, objective="reg:squarederror", verbose=1)

        model.fit(
            xy["training"]["x"],
            xy["training"]["y"],
            sample_weight=get_weight(xy)
        )


        # obtain_importance(work_dir, proc_field, model, feature_dataset)

        obtain_shap_values(work_dir, proc_field, model, xy, feature_dataset[proc_field]["features"])


def extract_feature_dataset(
    data: DataFrame, cfg: dict,
) -> int:
    """extract dataset based on required keys

    Args:
        df (DataFrame): cas dataset (in Dataframe) to be used
        cfg (DataFrame): feature analysis configuration
        data_field (str): fields to be queried, e.g., suv

    Returns:
        dict: the dict contains the required dataset
    """

    output = {}

    for proc_field in cfg[FEATURES_KEY]:

        features_to_apply = [proc_field]

        proc_cfg = cfg[FEATURES_KEY][proc_field]

        for proc_constrain in proc_cfg:

            features_to_apply.append(proc_constrain)
        
        data_qc_controlled = data_qc(data[features_to_apply], features_to_apply)
        data_qc_controlled = data_qc_controlled.to_numpy()

        y_qc_controlled = data_qc_controlled[:, 0]
        # y_qc_controlled[y_qc_controlled >= 1.0] = 1.0

        output[proc_field] = {"y": y_qc_controlled, "x": data_qc_controlled[:,1:], "features": features_to_apply[1:]}

    return output

def data_qc(data_to_be_processed: DataFrame, features_to_check: list) -> DataFrame:
    """Data quality control

    Args:
        data_to_be_processed (DataFrame): raw data to be processed
        features_to_check (list): features to be chcked

    Returns:
        DataFrame: quality controlled dataset
    """
    # remove all nan values
    data_to_be_processed = data_to_be_processed.dropna()
    for proc_feature in features_to_check:
        # convert str to values
        if proc_feature in STR2DIGIT_MAPPING:
            data_to_be_processed = data_to_be_processed.replace(STR2DIGIT_MAPPING[proc_feature])
    
        # remove missing values
        for proc_missing_value in MISSING_DATA[proc_feature]:
            data_to_be_processed = data_to_be_processed[data_to_be_processed[proc_feature] != proc_missing_value]
    
    return data_to_be_processed
    

def split_training_test_data(x_total: array, y_total: array, random_state: int = 1, test_size: float = 0.1) -> dict:
    """Split dataset used for training and test

    Args:
        x_total (array): total x
        y_total (array): total y
        random_state (int, optional): random state used for splitting. Defaults to 1.
        test_size (float, optional): ratio for test dataset. Defaults to 0.2.

    Returns:
        dict: [description]
    """

    output = {"training": {}, "test": {}}
    (
        output["training"]["x"],
        output["test"]["x"],
        output["training"]["y"],
        output["test"]["y"],
    ) = train_test_split(
        x_total,
        y_total,
        test_size=test_size,
        random_state=random_state,
    )

    return output
