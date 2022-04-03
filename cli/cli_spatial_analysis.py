import argparse

from data_process import (ANALYSIS_FILEDS_KEY, LATLON_KEY, POPULATION_KEY,
                          REGION_KEY, WORKDIR)
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
        description="Producing spatial data analysis for the CAS dataset",
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


def spatial_analysis(
    workdir: str,
    data_src: str,
    config_file: list,
):
    """Producing spatial analysis (changes) based on the CAS dataset

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

    logger.info("read lat and lon info ...")
    latlon = read_dataset(cfg[f"{LATLON_KEY}_data"])

    population_data = None
    if cfg[f"use_{POPULATION_KEY}_data"] is not None:
        logger.info("using population data ...")
        population_data = read_dataset(cfg[f"use_{POPULATION_KEY}_data"])


    logger.info(f"{ANALYSIS_FILEDS_KEY} analysis")

    logger.info("spatial analysis ...")

    spatial_data = create_spatial(data, population_data, cfg)

    logger.info("temporal visualization ...")
    plot_spatial(workdir, spatial_data, latlon, cfg["vis_scatter_factor"], cfg[f"use_{POPULATION_KEY}_data"])


    logger.info(f"job done (data are created at {workdir})...")


def main():
    args = setup_parser()

    spatial_analysis(args.workdir, args.data_src, args.config_file)


if __name__ == "__main__":
    main()
