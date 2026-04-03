# HeNova-DB 🌌
**Astrophysics Database and Simulation Pipeline for Helium Novae on Extreme-Mass White Dwarfs**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![MESA](https://img.shields.io/badge/MESA-r23.05.1-red.svg)](https://docs.mesastar.org/)
[![Status](https://img.shields.io/badge/Status-Active_Research-success.svg)]()

## 📖 Overview
HeNova-DB is a computational pipeline designed to model **Thermonuclear Runaways (Helium Novae)** on extreme-mass white dwarfs (WDs) approaching the Chandrasekhar limit (1.40 M_sun). 

Simulating extreme-mass WDs presents unique computational challenges, specifically regarding implicit solver stability, compressional heating, and degenerate matter equations of state (EOS). 
This project tracks the transition from Carbon-Oxygen (CO) WDs to Oxygen-Neon (ONe) WDs to ensure physical accuracy when pushing the boundaries of stellar gravity.

## 🚀 Key Features
* **Automated MESA Pipelines:** Custom `inlist` configurations to navigate the "multi-stage rocket" of massive star evolution (ZAMS -> AGB -> Envelope Stripping -> WD Cooling).
* **Extreme Mass Generation:** Stable generation of 1.35 M_sun ONe White Dwarfs from 12.5 M_sun progenitors, avoiding the numerical collapse of the `relax_mass` module.
* **Cold Accretion Handling:** Precision control over accretion rates (e.g., 1e-6 M_sun/yr) and timestep limits (down to 1e-12 yrs) to manage extreme surface density gradients.
* **Reproducibility:** `reproduce.py` ensures that all hydrostatic and nucleosynthesis models can be locally rebuilt.

## 🛠️ Tech Stack
* **Simulation Engine:** MESA (Modules for Experiments in Stellar Astrophysics), SHIVA
* **Data Pipeline:** Python, pandas, h5py
* **Analysis & ML:** PyTorch (for downstream time-series signal extraction)

## ⚡ Quick Start
To reproduce the baseline 1.35 M_sun ONe White Dwarf progenitor:
```bash
# 1. Clean default testing models
rm standard_*.mod

# 2. Compile the star engine
./mk

# 3. Ignite the 12.5 M_sun main-sequence evolution
nohup ./rn > run.log 2>&1 &
