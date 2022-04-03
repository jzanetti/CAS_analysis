import argparse
from datetime import datetime

from data_process import CSV_KEY, WORKDIR
from data_process.download import download_cas_dataset
from data_process.utils import setup_logging


def get_example_usage():
    example_text = """example:
        * cli_preproc [--workdir /tmp/cas_analysis_experiment]
                      [--input_fmt csv]
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Download and decode CAS dataset from opendata-nzta",
        epilog=get_example_usage(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--workdir",
        required=False,
        default=WORKDIR,
        type=str,
        help="Where the Pandas Dataframe will be located (default: /tmp/cas_analysis/{unique_id})",
    )

    parser.add_argument(
        "--input_fmt",
        required=False,
        type=str,
        default=CSV_KEY,
        choices={CSV_KEY},
        help="Input data format, by default the data (default: CSV) will be downloaded from internet. "
        "Please set environmental variable {data_fmt}_src for the source of data",
    )

    return parser.parse_args()


def preproc(
    workdir: str,
    input_fmt: str,
):
    """Download (if it is required) and export the CAS dataset to Dataframe

    Args:
        workdir (str): the working directory, e.g., where the output will be exported
        input_fmt (datetime): input data format (currently only CSV is supported)
    """
    logger = setup_logging()

    logger.info("check and download CAS dataset from NZTA")
    if download_cas_dataset(workdir, input_fmt) is None:
        return

    logger.info("job done ...")


def main():
    args = setup_parser()

    preproc(args.workdir, args.input_fmt)


if __name__ == "__main__":
    main()
