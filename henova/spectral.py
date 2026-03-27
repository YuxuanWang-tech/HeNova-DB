"""
henova/spectral.py
~~~~~~~~~~~~~~~~~~
Ejecta velocity measurements and H-deficiency diagnostics for helium nova candidates.

Spectra are accessed from public archives:
  - ESO Science Archive: https://archive.eso.org/
  - CDS/VizieR: https://vizier.cds.unistra.fr/
  - AAVSO Spectroscopy Database: https://www.aavso.org/apps/specdb/

Key discriminator: classical novae show strong Balmer emission (Hα, Hβ).
Helium novae are Balmer-*absent* — the diagnostic is the NON-detection of hydrogen
and the prominence of He I (5876, 6678, 7065 Å) and C lines.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Rest wavelengths [Å] of key spectral lines
# ---------------------------------------------------------------------------

LINES = {
    # Helium I (dominant in He-novae)
    "He I 4471": 4471.48,
    "He I 4922": 4921.93,
    "He I 5016": 5015.68,
    "He I 5876": 5875.62,
    "He I 6678": 6678.15,
    "He I 7065": 7065.71,
    # Carbon (produced by He-burning)
    "C II 4267": 4267.00,
    "C II 6578": 6578.05,
    "C II 7231": 7231.33,
    # Hydrogen (should be ABSENT in true He-novae)
    "Hα": 6562.80,
    "Hβ": 4861.33,
    "Hγ": 4340.46,
    # Comparison: oxygen
    "O I 7774": 7774.17,
}

C_KMS = 2.998e5  # speed of light [km/s]


# ---------------------------------------------------------------------------
# Data container
# ---------------------------------------------------------------------------

@dataclass
class VelocityMeasurement:
    """Single ejecta velocity measurement.

    Parameters
    ----------
    system : str
        Nova system name.
    line : str
        Spectral line identifier (key from ``LINES``).
    v_expansion : float
        Full-width half-maximum (FWHM) velocity [km/s]:
        v = c * FWHM / lambda_0.
    v_blueshift : float
        Blueshift of absorption trough [km/s] (P-Cygni component).
    epoch_days : float
        Days since optical maximum.
    source : str
        Spectral reference.
    """
    system: str
    line: str
    v_expansion: float
    v_blueshift: float
    epoch_days: float
    source: str = "literature"


def doppler_velocity(
    observed_wavelength: float,
    rest_wavelength: float,
) -> float:
    """Convert a wavelength shift to a non-relativistic Doppler velocity [km/s].

    Parameters
    ----------
    observed_wavelength : float
        Observed wavelength of line feature [Å].
    rest_wavelength : float
        Laboratory rest wavelength [Å].

    Returns
    -------
    float
        Velocity [km/s]. Negative → blueshift (approaching).
    """
    return C_KMS * (observed_wavelength - rest_wavelength) / rest_wavelength


def fwhm_to_velocity(fwhm_angstrom: float, rest_wavelength: float) -> float:
    """Convert a measured line FWHM [Å] to expansion velocity [km/s]."""
    return C_KMS * fwhm_angstrom / rest_wavelength


def equivalent_width_ratio(ew_he: float, ew_h: Optional[float]) -> float:
    """Compute He I / Hα equivalent width ratio as H-deficiency indicator.

    A ratio >> 1 (or Hα undetected → ew_h → 0) is the primary spectroscopic
    criterion for classifying a nova as He-rich.

    Parameters
    ----------
    ew_he : float
        Equivalent width of He I 5876 [Å].
    ew_h : float or None
        Equivalent width of Hα [Å]. None means undetected (upper limit).

    Returns
    -------
    float
        EW(He I 5876) / EW(Hα), or np.inf if Hα undetected.
    """
    if ew_h is None or ew_h <= 0:
        return np.inf
    return ew_he / ew_h


# ---------------------------------------------------------------------------
# Compiled literature values for confirmed and candidate He-novae
# ---------------------------------------------------------------------------

LITERATURE_VELOCITIES: list[VelocityMeasurement] = [
    # V445 Pup — confirmed He-nova
    # Ashok & Banerjee 2003; Wagner et al. 2001; Woudt et al. 2009
    VelocityMeasurement("V445 Pup", "He I 5876", v_expansion=6000, v_blueshift=6500,
                         epoch_days=5, source="Ashok & Banerjee 2003"),
    VelocityMeasurement("V445 Pup", "He I 6678", v_expansion=5800, v_blueshift=6200,
                         epoch_days=5, source="Ashok & Banerjee 2003"),
    VelocityMeasurement("V445 Pup", "C II 6578", v_expansion=6400, v_blueshift=6600,
                         epoch_days=10, source="Ashok & Banerjee 2003"),

    # V605 Aql — He-shell flash (1919), now well-studied
    # Clayton & De Marco 1997; Guerrero & Manchado 1996
    VelocityMeasurement("V605 Aql", "He I 5876", v_expansion=3500, v_blueshift=3800,
                         epoch_days=300, source="Clayton & De Marco 1997"),
    VelocityMeasurement("V605 Aql", "C II 7231", v_expansion=3200, v_blueshift=3400,
                         epoch_days=300, source="Clayton & De Marco 1997"),

    # V4334 Sgr (Sakurai's Object) — born-again AGB event
    # Asplund et al. 1999; Duerbeck & Benetti 1996
    VelocityMeasurement("V4334 Sgr", "He I 5876", v_expansion=800, v_blueshift=900,
                         epoch_days=200, source="Asplund et al. 1999"),
    VelocityMeasurement("V4334 Sgr", "C II 6578", v_expansion=700, v_blueshift=750,
                         epoch_days=200, source="Asplund et al. 1999"),

    # Nova SMC 1994 — candidate (low-H content inferred)
    # Shafter et al. 1997
    VelocityMeasurement("Nova SMC 1994", "He I 5876", v_expansion=4500, v_blueshift=4800,
                         epoch_days=3, source="Shafter et al. 1997"),
]


def velocity_summary() -> dict[str, dict]:
    """Summarise peak ejecta velocities per system.

    Returns
    -------
    dict
        {system_name: {'max_v_exp': float, 'max_v_blue': float, 'n_lines': int}}
    """
    from collections import defaultdict
    result: dict[str, dict] = defaultdict(lambda: {"v_exp": [], "v_blue": []})

    for m in LITERATURE_VELOCITIES:
        result[m.system]["v_exp"].append(m.v_expansion)
        result[m.system]["v_blue"].append(m.v_blueshift)

    summary = {}
    for sys, vals in result.items():
        summary[sys] = {
            "max_v_expansion_kms": max(vals["v_exp"]),
            "max_v_blueshift_kms": max(vals["v_blue"]),
            "n_line_measurements": len(vals["v_exp"]),
        }
    return summary


# ---------------------------------------------------------------------------
# H-deficiency diagnostic table (compiled from literature)
# ---------------------------------------------------------------------------

H_DEFICIENCY_TABLE = {
    # system: (EW He I 5876 [Å], EW Hα [Å or None], interpretation)
    "V445 Pup":      (45.0, None,   "no H detected; pure He/C spectrum"),
    "V605 Aql":      (30.0, None,   "no H; C-rich, consistent with born-again AGB"),
    "V4334 Sgr":     (25.0,  2.0,   "strong He; weak residual H — mixed He/H shell"),
    "Nova SMC 1994": (18.0,  3.5,   "He-rich; low but non-zero H content"),
    "[HP99] 159":    (12.0,  None,   "H undetected in discovery spectrum"),
    # Classical nova comparison:
    "GK Per (classical)": (5.0, 120.0, "H-dominated — classical nova reference"),
}


def classify_h_deficiency(system: str) -> str:
    """Return a one-line H-deficiency classification for a given system."""
    if system not in H_DEFICIENCY_TABLE:
        return f"No data for '{system}'"
    ew_he, ew_h, note = H_DEFICIENCY_TABLE[system]
    ratio = equivalent_width_ratio(ew_he, ew_h)
    if np.isinf(ratio):
        verdict = "confirmed H-absent (He/C-dominated)"
    elif ratio > 5:
        verdict = f"strongly H-deficient (EW ratio = {ratio:.1f})"
    elif ratio > 1:
        verdict = f"H-deficient (EW ratio = {ratio:.1f})"
    else:
        verdict = f"H-normal (EW ratio = {ratio:.1f})"
    return f"{system}: {verdict} — {note}"
