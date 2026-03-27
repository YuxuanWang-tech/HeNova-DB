# Data provenance and methods

## Photometric data

### AAVSO (American Association of Variable Star Observers)
- URL: https://www.aavso.org/data-download
- Free registration required; data freely downloadable as CSV
- Stars: V445 Pup, V4334 Sgr, V605 Aql
- Filter: V-band; fainter-than estimates excluded

### OGLE (Optical Gravitational Lensing Experiment)
- URL: http://ogle.astrouw.edu.pl/
- OGLE-II/III/IV public photometry archives
- Stars: V4334 Sgr, Nova SMC 1994
- Filter: I-band; standard OGLE .dat format

### Harvard plate archive (DASCH)
- URL: https://dasch.cfa.harvard.edu/
- V605 Aql historical photographic photometry
- Filter: pg (photographic blue)

## Spectroscopic data

### CDS/VizieR
- URL: https://vizier.cds.unistra.fr/
- Published equivalent widths and line identifications

### ESO Science Archive
- URL: https://archive.eso.org/
- VLT/UVES and FORS spectra for V445 Pup, V605 Aql

## Literature values compiled in spectral.py

| System | Primary reference |
|---|---|
| V445 Pup | Ashok & Banerjee 2003, A&A 409, 1007; Woudt et al. 2009, ApJ 706, 738 |
| V605 Aql | Clayton & De Marco 1997, AJ 114, 2679; Guerrero & Manchado 1996, ApJ 472, 711 |
| V4334 Sgr | Asplund et al. 1999, A&A 343, 507; Duerbeck & Benetti 1996, ApJ 468, L111 |
| Nova SMC 1994 | Shafter et al. 1997, ApJ 487, L45 |

## Pipeline steps

1. **Ingest**: Load AAVSO CSV or OGLE .dat into `LightCurve` objects.
2. **Clean**: Remove fainter-than estimates; sort by time; flag outliers (>5σ).
3. **Peak finding**: `numpy.nanargmin` on the magnitude array.
4. **t₂ / t₃ measurement**: Linear interpolation between bracketing points.
5. **Speed classification**: Payne-Gaposchkin (1957) scheme.
6. **Velocity compilation**: Literature values cross-matched to LITERATURE_VELOCITIES list.
7. **H-deficiency diagnostic**: EW(He I 5876) / EW(Hα) ratio diagram.
