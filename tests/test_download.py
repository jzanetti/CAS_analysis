import unittest
from os.path import join

from data_process import CAS_KEY
from data_process.download import download_cas_dataset
from numpy.testing import assert_equal


class TestDownload(unittest.TestCase):
    def test_download_cas_dataset(self):
        workdir = "/tmp/test"
        input_fmt = "csv"

        overwrite_api_src = "https://test"
        output = download_cas_dataset(workdir, input_fmt, overwrite_api_src=overwrite_api_src)
        assert_equal(output, None)

        overwrite_api_src = "tests/test_download.py"
        output = download_cas_dataset(workdir, input_fmt, overwrite_api_src=overwrite_api_src)
        assert_equal(output, join(workdir, f"{CAS_KEY}.{input_fmt}"))


if __name__ == "__main__":
    unittest.main()
