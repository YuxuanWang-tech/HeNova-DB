#!/usr/bin/env python3
"""
reproduce.py — HeNova-DB full pipeline

Run this script to regenerate all results and figures from scratch:

    python reproduce.py

No proprietary data needed. All photometry uses schematic/literature-compiled
values; replace with real AAVSO/OGLE downloads when available.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from henova.lightcurve import (
    make_schematic_v445pup,
    make_schematic_nova_smc1994,
    summary_table,
)
from henova.spectral import (
    velocity_summary,
    classify_h_deficiency,
    H_DEFICIENCY_TABLE,
)
from henova.plot import (
    plot_light_curves,
    plot_velocity_comparison,
    plot_h_deficiency,
)

RESULTS = Path("results")
RESULTS.mkdir(exist_ok=True)


def step1_light_curves():
    print("\n" + "=" * 60)
    print("STEP 1  Light curve analysis")
    print("=" * 60)

    lcs = [
        make_schematic_v445pup(),
        make_schematic_nova_smc1994(),
    ]

    tbl = summary_table(lcs)
    print("\nSummary table:")
    print(tbl.to_string(index=False))

    csv_path = RESULTS / "lightcurve_summary.csv"
    tbl.to_csv(csv_path, index=False)
    print(f"\nSaved {csv_path}")

    plot_light_curves(lcs, outfile="fig1_lightcurves.pdf")
    return lcs


def step2_ejecta_velocities():
    print("\n" + "=" * 60)
    print("STEP 2  Ejecta velocity compilation")
    print("=" * 60)

    vsummary = velocity_summary()
    rows = []
    for sys, d in vsummary.items():
        print(f"  {sys:20s}  v_exp_max = {d['max_v_expansion_kms']:6,.0f} km/s  "
              f"v_blue_max = {d['max_v_blueshift_kms']:6,.0f} km/s  "
              f"({d['n_line_measurements']} line measurements)")
        rows.append({"system": sys, **d})

    df = pd.DataFrame(rows)
    csv_path = RESULTS / "ejecta_velocities.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {csv_path}")

    plot_velocity_comparison(outfile="fig2_velocities.pdf")


def step3_h_deficiency():
    print("\n" + "=" * 60)
    print("STEP 3  H-deficiency diagnostics")
    print("=" * 60)

    for system in H_DEFICIENCY_TABLE:
        print(" ", classify_h_deficiency(system))

    plot_h_deficiency(outfile="fig3_h_deficiency.pdf")


def step4_key_numbers():
    print("\n" + "=" * 60)
    print("STEP 4  Key numbers (for paper / README)")
    print("=" * 60)

    lc = make_schematic_v445pup()
    print(f"  V445 Pup peak magnitude:     {lc.peak_mag:.2f} mag (V)")
    print(f"  V445 Pup t₂:                 {lc.t2:.1f} days")
    print(f"  V445 Pup t₃:                 {lc.t3:.1f} days")
    print(f"  V445 Pup speed class:         {lc.speed_class()}")

    lc2 = make_schematic_nova_smc1994()
    print(f"  Nova SMC 1994 peak magnitude: {lc2.peak_mag:.2f} mag (I)")
    print(f"  Nova SMC 1994 t₂:             {lc2.t2:.1f} days")
    print(f"  Nova SMC 1994 speed class:    {lc2.speed_class()}")

    numbers = {
        "V445_Pup_peak_mag": round(lc.peak_mag, 2),
        "V445_Pup_t2_days": round(lc.t2, 1),
        "V445_Pup_t3_days": round(lc.t3, 1),
        "Nova_SMC1994_peak_mag": round(lc2.peak_mag, 2),
        "Nova_SMC1994_t2_days": round(lc2.t2, 1),
    }
    df = pd.DataFrame([numbers])
    df.to_csv(RESULTS / "key_numbers.csv", index=False)
    print(f"\n  Saved results/key_numbers.csv")


if __name__ == "__main__":
    print("HeNova-DB — reproducible helium nova analysis pipeline")
    print("https://github.com/your-handle/HeNova-DB")

    step1_light_curves()
    step2_ejecta_velocities()
    step3_h_deficiency()
    step4_key_numbers()

    print("\n" + "=" * 60)
    print("All done. Figures in results/")
    print("=" * 60)
