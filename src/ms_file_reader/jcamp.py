"""
Functions for processing for JCAMP-DX files.  These files come in a variety of
file extenstions, including .hpj and .jdx, but they all have essentially the
same structure.

I'm basing this code off of the contents of the paper "JCAMP-DX" for Mass Spectrometry" by Lampen, et al (1994).
"""

import warnings

from ms_file_reader.common_ms import MassSpectrum, MassSpectrumFileProcessor, MassSpectrumLibrary


class JCAMPFileProcessor(MassSpectrumFileProcessor):
    """
    Class used to process a JCAMP-DX style file and output a library of spectra.

    keep_symbol_prefixes is for whether to include '.' or '$' prefixes on field names (the specification that I used mentions them )
    """

    def __init__(self, peak_delimiter=None, max_intensity=None, keep_empty_fields=True, keep_symbol_prefixes=True, interpeak_delimiter=";", spectrum_delimiter=None):
        super().__init__(intensity_field=1, mz_field=0, peak_delimiter=peak_delimiter, max_intensity=max_intensity)
        self.keep_symbol_prefixes = keep_symbol_prefixes
        self.keep_empty_fields = keep_empty_fields
        self.interpeak_delimiter = interpeak_delimiter
        self.spectrum_delimiter = spectrum_delimiter
    

    def process_file(self, file_text):
        spectrum_texts = self._split_spectra(file_text)
        spectrum_object_list = []

        for text in spectrum_texts:
            spectrum_start_line = 0
            num_peaks = 0
            fields = {}

            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for n, l in enumerate(lines):
                if l.startswith("##XYDATA"):
                    # Found the line prefacing the peak list
                    spectrum_start_line = n + 1
                    break
                elif l.startswith("##NPOINTS"):
                    num_peaks = int(l.split("=")[1])
                elif l.startswith("$$") or l.startswith("##="):
                    # lines starting with '$$' or '##=' are comments, so skip them
                    continue
                elif l.startswith("##"):
                    trimmed_line = l.lstrip("##")
                    if (trimmed_line[0] in ".$") and not self.keep_symbol_prefixes:
                        trimmed_line = trimmed_line[1:]
                    field_name, value = trimmed_line.split("=", maxsplit=1)
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
                    warnings.warn(f"Line with non-standard content found: '{l}'")

            if num_peaks == 0:
                warnings.warn(f"No spectrum found in text for spectrum number {n+1}.")
                spectrum = np.empty((0,2))
            elif self.interpeak_delimiter in lines[spectrum_start_line]:
                all_peaks = []
                for l in lines[spectrum_start_line:]:
                    if self.interpeak_delimiter in l and l.strip()[0] in "0123456789":
                        line_peaks = l.split(self.interpeak_delimiter)
                        all_peaks.extend(line_peaks)
                    else:
                        break
                spectrum = self._process_spectrum_lines(all_peaks, self.peak_delimiter)
            else:
                spectrum_lines = lines[spectrum_start_line:(spectrum_start_line + num_peaks)]
                spectrum = self._process_spectrum_lines(spectrum_lines, self.peak_delimiter)

            spectrum_object = MassSpectrum(fields=fields, spectrum=spectrum)
            if self.max_intensity:
                spectrum_object.rescale_spectrum(self.max_intensity)

            spectrum_object_list.append(MassSpectrum(fields=fields, spectrum=spectrum))
    
        return MassSpectrumLibrary(spectrum_object_list)
            


    def _split_spectra(self, file_text):
        """
        Spectra in a JCAMP-DX file typically start with a line starting with '##TITLE', and sometimes end with '##END=' (though not always).  Entries may not have empty lines between them, either, so use the '##TITLE' fields as reference points to split the specra.
        """
        if self.spectrum_delimiter is not None:
            return file_text.split(self.spectrum_delimiter)
        else:
            # go from ##TITLE to ##TITLE
            title_indices = []
            title_index = file_text.find("##TITLE")

            # if first ##TITLE index is -1, then this isn't following the JCAMP format (enough)
            if title_index == -1:
                raise ValueError("Unable to process file text -- ##TITLE field is not present in document, which is necessary if there is no spectrum delimiter set.")

            while title_index != -1:
                title_indices.append(title_index)
                title_index = file_text.find("##TITLE", title_index+1)
            
            title_indices.append(len(file_text))
            
            return [file_text[a:b].strip() for a, b in zip(title_indices[:-1], title_indices[1:])]
