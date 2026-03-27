# HeNova-DB

**Photometric and spectroscopic analysis of helium nova candidates**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Open data](https://img.shields.io/badge/data-open%20%26%20public-gold?style=flat-square)](METHODS.md)
[![Reproducible](https://img.shields.io/badge/results-fully%20reproducible-teal?style=flat-square)](#reproduce)

---

A fully reproducible analysis pipeline for helium nova candidates, built as a transparent companion to hydrodynamic simulations of helium-rich thermonuclear runaways on white dwarfs.

Helium novae differ fundamentally from classical hydrogen novae: their ejecta lack hydrogen, are dominated by helium and carbon (products of the triple-α and αp processes), show unusually high expansion velocities (≳ 6,000 km s⁻¹ for V445 Pup), and in some cases exhibit supersoft X-ray emission. With only **one confirmed event** (V445 Puppis, 2000) and a handful of poorly-studied candidates, every observational constraint is valuable.

This project compiles public photometric and spectroscopic data for all known candidates, measures key observational diagnostics (t₂, t₃, peak luminosity, ejecta velocity, H/He equivalent width ratios), and provides a framework for comparing with thermonuclear runaway model outputs.

---

## Candidate systems

| System | Type | Peak mag | t₂ (d) | Data source |
|---|---|---|---|---|
| V445 Pup | Confirmed He-nova | V ≈ 8.6 | ~7 | AAVSO |
| V605 Aql | He-shell flash (1919) | pg ≈ 10.9 | — | Harvard CfA plates |
| V4334 Sgr (Sakurai's Object) | Born-again AGB | V ≈ 11.1 | — | AAVSO / OGLE |
| Nova SMC 1994 | Candidate He-nova | I ≈ 10.8 | ~4 | OGLE-II/III |
| [HP99] 159 | Candidate | — | — | Hoard et al. 1999 |
| V450 Cyg | Candidate | — | — | literature |

---

## Repository structure

```
HeNova-DB/
├── README.md                  # this file
├── METHODS.md                 # data provenance & pipeline documentation
├── pyproject.toml             # installable Python package
├── reproduce.py               # one-command full pipeline
│
├── henova/                    # core analysis package
│   ├── __init__.py
│   ├── lightcurve.py          # AAVSO/OGLE ingestion; t₂, t₃ measurement
│   ├── spectral.py            # ejecta velocity; H-deficiency diagnostics
│   ├── models.py              # interface to published SHIVA/MESA grids (v0.3)
│   └── plot.py                # publication-quality matplotlib figures
│
├── data/
│   ├── raw/                   # AAVSO/OGLE downloads (not committed — see METHODS)
│   └── processed/             # cleaned light curves (.csv)
│
├── notebooks/
│   ├── 01_lightcurve_analysis.ipynb
│   ├── 02_ejecta_velocities.ipynb
│   └── 03_nucleosynthesis_yields.ipynb
│
└── results/                   # auto-generated figures and tables
    ├── fig1_lightcurves.pdf
    ├── fig2_velocities.pdf
    ├── fig3_h_deficiency.pdf
    ├── lightcurve_summary.csv
    └── key_numbers.csv
```

---

## Reproduce everything <a name="reproduce"></a>

```bash
git clone https://github.com/your-handle/HeNova-DB
cd HeNova-DB
pip install -e .[dev]    # numpy, astropy, matplotlib, pandas, scipy
python reproduce.py      # downloads data → pipeline → figures
```

All photometric data is downloaded automatically from [AAVSO](https://www.aavso.org/data-download) and [OGLE](http://ogle.astrouw.edu.pl/). No institutional access required.

---

## Key physical motivation

Classical novae ignite at the base of a hydrogen-rich accreted shell when the pressure and temperature reach the conditions for the pp-chain and CNO cycle. Helium novae ignite a *helium-rich* layer instead, requiring substantially higher temperatures (T ≳ 10⁸ K) and column densities (~10⁻⁴ M☉) for the triple-α process to run away.

Consequences:
- No hydrogen in ejecta (diagnostic: Hα undetected in spectra)
- Dominance of He I lines and C II / C III emission
- Higher peak temperatures → higher expansion velocities
- Different nucleosynthetic yields: ¹²C, ¹⁶O, ²²Ne rather than CNO products
- Potentially contributes to Galactic carbon enrichment

This pipeline quantifies the observational signatures that discriminate He-novae from (i) classical novae, (ii) born-again AGB events (late He-shell flashes), and (iii) very fast H-novae, allowing comparison against thermonuclear runaway simulations.

---

## Science goals (by release)

- **v0.1** — Light curve compilation; t₂/t₃ measurement; speed classification ✓
- **v0.2** — Spectral ejecta velocity compilation; EW(He I)/EW(Hα) diagnostic diagram
- **v0.3** — Interface to published SHIVA/MESA simulation grids; ignition conditions
- **v1.0** — Nucleosynthetic yield comparison; Galactic ¹²C contribution estimate; paper companion

---

## Citation

If you use this pipeline, please cite this repository (Zenodo DOI on v1.0) and the underlying data sources listed in [METHODS.md](METHODS.md).

---

## License

MIT — see [LICENSE](LICENSE).
