"""
Code for the primary elements of the library: the MassSpectrum and MassSpectrumLibrary objects.
"""

from collections import Counter

import numpy as np


class MassSpectrum():
    """
    Base class for mass spectra, intended to be one spectrum per object.
    Multiple spectra can be collected into a MassSpectrumLibrary object.
    """
    
    def __init__(self, fields, spectrum=np.array()):
        self.fields = fields
        self.spectrum = spectrum
    
    
    def list_fields(self):
        """
        Convenience function that lists the metadata fields for the spectrum.
        """
        return list(self.fields.keys())


class MassSpectrumLibrary():
    """
    Class designed to store multiple MassSpectrum objects and do some cursory
    checks on them as a group.
    """

    def __init__(self, spectrum_list = []):
        self.spectra = spectrum_list
    
    def add_spectrum(self, additional_spectrum):
        """
        Convenience function for appending spectra to a library.
        """
        self.spectra.append(additional_spectrum)
    
    def count_all_fields(self):
        """
        Returns a list of all unique fields in the data, as well as how many spectra
        each one appears in.
        """
        all_fields = [field for spectrum in self.spectra for field in spectrum.list_fields()]
        return Counter(all_fields)


class MassSpectrumFileProcessor():
    """
    Class containing common operations for mass spectrum file processors.
    """

    def _process_spectrum_lines(self, spectrum_lines, peak_delimiter=None, mz_field=0, intensity_field=1):
        """
        Translates a list of lines with one m/z-intensity pair each into a mass spectrum.
        
        Leaving the delimiter as None will split on arbitrary whitespace.
        """
        split_lines = [sl.split(peak_delimiter) for sl in spectrum_lines]
        return np.array([[l[mz_field], l[intensity_field]] for l in split_lines])