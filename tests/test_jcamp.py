"""
Tests for the JCAMP-DX file reader.
"""

import pytest

from ms_file_reader.jcamp import JCAMPFileProcessor


@pytest.fixture(name="good_test_file")
def good_test_file_fixture():
    with open("tests/test_files/jcamp/test1.jdx", "r", encoding="utf-8") as f:
        return f.read()

def test_read_good_file(good_test_file):
    reader = JCAMPFileProcessor(peak_delimiter=",")
    library = reader.process_file(good_test_file)
    assert len(library.spectra) == 4

def test_filter_null_fields(good_test_file):
    reader1 = JCAMPFileProcessor(peak_delimiter=",")
    library1 = reader1.process_file(good_test_file)
    field_counts1 = library1.count_all_fields()
    assert field_counts1["ORIGIN"] == 4

    reader2 = JCAMPFileProcessor(peak_delimiter=",", keep_empty_fields=False)
    library2 = reader2.process_file(good_test_file)
    field_counts2 = library2.count_all_fields()
    assert field_counts2["ORIGIN"] == 3

def test_filter_field_prefixes(good_test_file):
    reader1 = JCAMPFileProcessor(peak_delimiter=",", keep_symbol_prefixes=True)
    library1 = reader1.process_file(good_test_file)
    field_counts1 = library1.count_all_fields()
    assert field_counts1[".IONIZATION MODE"] == 2

    reader2 = JCAMPFileProcessor(peak_delimiter=",", keep_symbol_prefixes=False)
    library2 = reader2.process_file(good_test_file)
    field_counts2 = library2.count_all_fields()
    assert field_counts2["IONIZATION MODE"] == 2

def test_count_field_values(good_test_file):
    reader = JCAMPFileProcessor(peak_delimiter=",")
    library = reader.process_file(good_test_file)
    ion_modes = library.count_field_values("ORIGIN")
    assert set(ion_modes.keys()) == {"Generated", "Made it up", None}