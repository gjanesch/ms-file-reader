"""
Functions for processing MSP mass spectrum files.  This is one of the more
common file extensions that I come across, though as far as I know this isn't a
well-standardized format.
"""

from collections import Counter
import warnings

from ms_file_reader.common_ms import MassSpectrum, MassSpectrumFileProcessor, MassSpectrumLibrary


class MSPFileProcessor(MassSpectrumFileProcessor):
    """
    This class is for taking the contents of a mass spectral .msp file and performing
    some basic extraction of the spectra inside.  This is currently assuming that the
    contents of the file in question have been read into memory already -- the files
    that I've been dealing with so far are all easy to read into memory, so this isn't
    an issue yet, but it may need a more streaming-like solution in the future.

    TODO: see if a field_delimiter is necessary.    
    """

    def __init__(self, intensity_field=1, keep_empty_fields=True, num_peaks_text="Num Peaks", peak_delimiter=None, mz_field=0, spectrum_delimiter="\n\n", max_intensity=None):
        super().__init__(intensity_field=intensity_field, mz_field=mz_field, peak_delimiter=peak_delimiter, max_intensity=max_intensity)
        self.num_peaks_text = num_peaks_text
        self.keep_empty_fields = keep_empty_fields
        self.spectrum_delimiter = spectrum_delimiter

    def process_file(self, file_text):
        spectrum_texts = [s.strip() for s in file_text.split(self.spectrum_delimiter) if s.strip()]
        
        spectrum_object_list = []
        
        for text in spectrum_texts:
            spectrum_start_line = 0
            num_peaks = 0
            fields = {}

            # First part: identify which lines are 
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for n, l in enumerate(lines):
                if l.startswith(self.num_peaks_text):
                    # Found the line prefacing the peak list
                    spectrum_start_line = n + 1
                    num_peaks = int(l.split(":")[1])
                    break
                elif ":" in l:
                    # Found a field
                    field_name, value = l.split(":", maxsplit=1)
                    if value.strip():
                        # field has a value
                        fields[field_name.strip()] = value.strip()
                    elif self.keep_empty_fields:
                        # field doesn't have a value, but its existence should be included
                        fields[field_name.strip()] = None
                    else:
                        # field doesn't have a value, and don't want the entry
                        pass
                else:
                    warnings.warn(f"Line with un-delimited content '{l}' found.")
            
            if num_peaks == 0:
                warnings.warn(f"No spectrum found in text for spectrum number {n+1}.")
                spectrum = np.empty((0,2))
            else:
                spectrum_lines = lines[spectrum_start_line:(spectrum_start_line + num_peaks + 1)]
                spectrum = self._process_spectrum_lines(spectrum_lines, self.peak_delimiter)
            
            spectrum_object = MassSpectrum(fields=fields, spectrum=spectrum)
            if self.max_intensity:
                spectrum_object.rescale_spectrum(self.max_intensity)

            spectrum_object_list.append(MassSpectrum(fields=fields, spectrum=spectrum))
    
        return MassSpectrumLibrary(spectrum_object_list)
            
    