import argparse

from data_process import (ANALYSIS_FILEDS_KEY, LATLON_KEY, POPULATION_KEY,
                          REGION_KEY, WORKDIR)
from data_process.feature import (create_feature_analysis,
                                  extract_feature_dataset)
from data_process.spatial import create_spatial
from data_process.utils import read_config, read_dataset, setup_logging
from data_process.vis import plot_spatial


def get_example_usage():
    example_text = """example:
        * cli_temporal_analysis --data_src /tmp/cas_analysis_experiment
                                [--config_file /tmp/temporal_analysis_exp1.yaml]
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Producing feature data analysis for the CAS dataset",
        epilog=get_example_usage(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--workdir",
        required=False,
        default=WORKDIR,
        type=str,
        help="Where the data will be run (default: /tmp/cas_analysis/{unique_id})",
    )

    parser.add_argument(
        "--data_src",
        required=True,
        type=str,
        help="which dataset to be used, e.g., /tmp/tmp/cas_test/cas.csv",
    )

    parser.add_argument(
        "--config_file",
        required=True,
        type=str,
        help="the path for the configuration file [in YAML]",
    )

    return parser.parse_args()


def feature_analysis(
    workdir: str,
    data_src: str,
    config_file: list,
):
    """Producing feature analysis (changes) based on the CAS dataset

    Args:
        workdir (str): where to run the codes
        data_src (str): the dataset to be used
        data_keys (list): the keys to be used, e.g., crashDirectionDescription,bicycle
    """
    logger = setup_logging()

    logger.info("read raw dataset ...")

    data = read_dataset(data_src)

    logger.info("read configs ...")

    cfg = read_config(config_file)

    logger.info(f"{ANALYSIS_FILEDS_KEY} analysis")

    logger.info("feature analysis ...")

    create_feature_analysis(workdir, data, cfg)

    logger.info(f"job done (data are created at {workdir})...")


def main():
    args = setup_parser()

    feature_analysis(args.workdir, args.data_src, args.config_file)


if __name__ == "__main__":
    main()
