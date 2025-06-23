"""
Tests specifically for the MSP file reader.
"""

import pytest

from ms_file_reader.msp import MSPFileProcessor


@pytest.fixture
def good_test_file():
    with open("tests/test_files/msp/test1.msp", "r") as f:
        return f.read()

def test_read_good_file(good_test_file):
    reader = MSPFileProcessor(keep_empty_fields=True, num_peaks_text="Num_Peaks")
    library = reader.process_file(good_test_file)
    assert len(library.spectra) == 3

def test_filter_null_fields(good_test_file):
    reader1 = MSPFileProcessor(keep_empty_fields=True, num_peaks_text="Num_Peaks")
    library1 = reader1.process_file(good_test_file)
    field_counts1 = library1.count_all_fields()
    assert field_counts1["InChIKey"] == 3

    reader2 = MSPFileProcessor(keep_empty_fields=False, num_peaks_text="Num_Peaks")
    library2 = reader2.process_file(good_test_file)
    field_counts2 = library2.count_all_fields()
    assert field_counts2["InChIKey"] == 2

def test_count_field_values(good_test_file):
    reader = MSPFileProcessor(keep_empty_fields=True, num_peaks_text="Num_Peaks")
    library = reader.process_file(good_test_file)
    ion_modes = library.count_field_values("Ion Mode")
    assert set(ion_modes.keys()) == {"Positive", "Unknown"}