This is a small library intended to read some different types of mass spectrometry files.  The focus is on open, text-based file formats for already-processed spectra.  The current target is to be able to handle MSP, JCAMP-DX, and MassBank EU-styled files.

I wrote this because of a project that had to grab collections of mass spectra from a variety of sources.  A number of these sources had some significiant inconsistencies within their libraries, though -- sometimes due to fields that don't appear in all spectra, sometimes becuase the field does always appear but it has some sort of null value in the field, and so on.  Some exploration of the data was usually necessary, and much of it was repetetive.

This is currently a work in progress.