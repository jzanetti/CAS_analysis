from logging import getLogger
from os import makedirs
from os.path import exists, join
from shutil import copyfile
from urllib.error import URLError
from urllib.request import urlretrieve

from data_process import CAS_KEY, DATA_API_SRC

logger = getLogger()


def download_cas_dataset(
    workdir: str, input_fmt: str, overwrite_api_src: str or None = None, max_tries: int = 3
) -> str or None:
    """Check and download CAS dataset from NZTA open data server

    Args:
        workdir (str): working directory
        input_fmt (str): the input data format, e.g., csv
        overwrite_api_src (str or None, optional): if it is defined, the API data source will be read from here
        max_tries (int, optional): If we need to download the data from internet, how many times maximum we want to try. Defaults to 3.

    Returns:
        str or None: the downloaded dataset path, or None if the download fails
    """

    if not exists(workdir):
        makedirs(workdir)

    data_source = DATA_API_SRC[input_fmt] if overwrite_api_src is None else overwrite_api_src
    data_destination = join(workdir, f"{CAS_KEY}.{input_fmt}")

    # if the data_source is downloaded, there is no need to download it again
    if not data_source.startswith("https"):
        if not exists(data_destination):
            copyfile(data_source, data_destination)
        logger.info("The requested file exists ...")
        return data_destination

    # if the data_source is not available locally, we download it from NZTA open-data server
    tried_times = 0
    while tried_times <= max_tries:
        try:
            urlretrieve(data_source, data_destination)
            return data_destination
        except URLError:
            tried_times += 1
            pass

    logger.error(
        f"Failed to download file from {data_source} after {max_tries} tries, check the data_source URL ..."
    )
    return None
