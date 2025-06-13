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
    
    def __init__(self, fields, spectrum=np.empty((0,2))):
        self.fields = fields
        self.spectrum = spectrum
    
    
    def list_fields(self):
        """
        Convenience function that lists the metadata fields for the spectrum.
        """
        return list(self.fields.keys())
    
    def rescale_spectrum(self, new_max):
        current_max = self.spectrum[:,1].max()
        self.spectrum[:,1] = self.spectrum[:,1] * new_max / current_max


class MassSpectrumLibrary():
    """
    Class designed to store multiple MassSpectrum objects and do some cursory
    checks on them as a group.
    """

    def __init__(self, spectrum_list = [], max_intensity=None):
        self.spectra = spectrum_list
        self.max_intensity = max_intensity
    
    def add_spectrum(self, additional_spectrum):
        """
        Convenience function for appending spectra to a library.
        """
        if self.max_intensity:
            additional_spectrum.rescale_spectrum(self.max_intensity)
        self.spectra.append(additional_spectrum)
    
    def count_all_fields(self):
        """
        Returns a list of all unique fields in the data, as well as how many spectra
        each one appears in.
        """
        all_fields = [field for spectrum in self.spectra for field in spectrum.list_fields()]
        return Counter(all_fields)
    
    def count_field_values(self, field_name):
        """
        Returns a list of all values found in the specified field.  Spectra without the field will have None as their value.
        """
        values = [s.fields.get(field_name, None) for s in self.spectra]
        return Counter(values)


class MassSpectrumFileProcessor():
    """
    Class containing common operations for mass spectrum file processors.
        
    Leaving the delimiter as None will split on arbitrary whitespace.
    """

    def __init__(self, peak_delimiter=None, mz_field=0, intensity_field=1):
        self.mz_field = mz_field
        self.intensity_field = intensity_field
        self.peak_delimiter = peak_delimiter

    def _process_spectrum_lines(self, spectrum_lines, peak_delimiter=None):
        """
        Translates a list of lines with one m/z-intensity pair each into a mass spectrum.
        """
        split_lines = [sl.split(self.peak_delimiter) for sl in spectrum_lines]
        min_number_of_fields = 1 + max(self.mz_field, self.intensity_field)
        if any([len(vals) < min_number_of_fields for vals in split_lines]):
            raise ValueError(f"At least one line of the spectrum has too few values; expecting at least {min_number_of_fields} in each line.")
        return np.array([[float(l[self.mz_field]), float(l[self.intensity_field])] for l in split_lines])