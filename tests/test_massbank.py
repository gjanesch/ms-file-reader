"""
Tests specifically for the MassBank EU file reader.
"""

import pytest

from ms_file_reader.massbank import MassBankFileProcessor


@pytest.fixture
def good_test_file1():
    with open("tests/test_files/massbank/MSBNK-UvA_IBED-UI000101.txt", "r") as f:
        return f.read()


def test_read_good_file(good_test_file1):
    reader = MassBankFileProcessor()
    spectrum = reader.process_file(good_test_file1)
    assert len(spectrum.spectrum) == 17
    assert "CHROMATOGRAPHY - FLOW_RATE" in list(spectrum.fields.keys())
    assert len(spectrum.fields["NAME"]) == 1
