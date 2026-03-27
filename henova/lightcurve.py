"""
henova/lightcurve.py
~~~~~~~~~~~~~~~~~~~~
Ingest, clean, and analyse photometric light curves of helium nova candidates
from public archives (AAVSO, OGLE, literature).

All data sources are fully public and freely downloadable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import warnings


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class LightCurve:
    """Photometric time series for a nova candidate.

    Parameters
    ----------
    name : str
        System identifier (e.g. 'V445 Pup').
    jd : np.ndarray
        Julian dates of observations.
    mag : np.ndarray
        Apparent magnitudes (smaller = brighter).
    mag_err : np.ndarray
        Photometric uncertainties.
    band : str
        Photometric passband ('V', 'I', 'pg', …).
    source : str
        Data provenance (e.g. 'AAVSO', 'OGLE-II').
    """
    name: str
    jd: np.ndarray
    mag: np.ndarray
    mag_err: np.ndarray
    band: str = "V"
    source: str = "unknown"

    # Derived properties (computed lazily)
    _peak_idx: Optional[int] = field(default=None, repr=False, compare=False)

    # ------------------------------------------------------------------
    # Core photometric quantities
    # ------------------------------------------------------------------

    @property
    def peak_idx(self) -> int:
        if self._peak_idx is None:
            self._peak_idx = int(np.nanargmin(self.mag))
        return self._peak_idx

    @property
    def peak_mag(self) -> float:
        return float(self.mag[self.peak_idx])

    @property
    def peak_jd(self) -> float:
        return float(self.jd[self.peak_idx])

    @property
    def days_from_peak(self) -> np.ndarray:
        """Days elapsed since peak brightness."""
        return self.jd - self.peak_jd

    def measure_decline(self, delta_mag: float = 2.0) -> float:
        """Return t_{delta_mag} [days]: time to decline *delta_mag* magnitudes.

        Parameters
        ----------
        delta_mag : float
            Magnitude drop to measure (default 2 → t₂; use 3 for t₃).

        Returns
        -------
        float
            Days since peak, or np.nan if the threshold is never reached.
        """
        target = self.peak_mag + delta_mag
        after_jd  = self.jd[self.peak_idx:]
        after_mag = self.mag[self.peak_idx:]

        crossings = np.where(after_mag >= target)[0]
        if len(crossings) == 0:
            warnings.warn(
                f"{self.name}: magnitude never declines {delta_mag} mag below peak "
                "within the observed baseline — t_{delta_mag} is unconstrained.",
                RuntimeWarning,
            )
            return np.nan

        idx = crossings[0]
        if idx == 0:
            return 0.0

        # Linear interpolation between the two bracketing points
        m0, m1 = after_mag[idx - 1], after_mag[idx]
        t0, t1 = after_jd[idx - 1], after_jd[idx]
        frac = (target - m0) / (m1 - m0)
        return float((t0 + frac * (t1 - t0)) - self.peak_jd)

    @property
    def t2(self) -> float:
        """Time to decline 2 magnitudes below peak [days]."""
        return self.measure_decline(2.0)

    @property
    def t3(self) -> float:
        """Time to decline 3 magnitudes below peak [days]."""
        return self.measure_decline(3.0)

    def speed_class(self) -> str:
        """Nova speed classification based on t₂ (Payne-Gaposchkin 1957)."""
        t = self.t2
        if np.isnan(t):
            return "unknown"
        if t < 10:
            return "very fast"
        if t < 25:
            return "fast"
        if t < 80:
            return "moderately fast"
        if t < 150:
            return "slow"
        return "very slow"


# ---------------------------------------------------------------------------
# Ingestion from public sources
# ---------------------------------------------------------------------------

def load_aavso_csv(path: str | Path, band: str = "V") -> LightCurve:
    """Load an AAVSO download CSV (Visual or CCD data).

    Download from https://www.aavso.org/data-download
    Select: Star name → Download → CSV format.

    Parameters
    ----------
    path : str or Path
        Local path to the downloaded CSV.
    band : str
        Passband to keep (e.g. 'V', 'I', 'B').

    Returns
    -------
    LightCurve
    """
    path = Path(path)
    df = pd.read_csv(
        path,
        comment="#",
        usecols=["JD", "Magnitude", "Uncertainty", "Band", "Star Name"],
        dtype={"JD": float, "Magnitude": float, "Uncertainty": float,
               "Band": str, "Star Name": str},
    )
    df.columns = df.columns.str.strip()

    # Filter band and drop fainter-than estimates (NaN magnitude)
    mask = (df["Band"].str.strip() == band) & df["Magnitude"].notna()
    df = df[mask].sort_values("JD").reset_index(drop=True)

    if df.empty:
        raise ValueError(
            f"No valid '{band}'-band data found in {path}. "
            "Check the band label or download a different passband."
        )

    name = df["Star Name"].iloc[0].strip()
    return LightCurve(
        name=name,
        jd=df["JD"].to_numpy(),
        mag=df["Magnitude"].to_numpy(),
        mag_err=df["Uncertainty"].fillna(0.05).to_numpy(),
        band=band,
        source="AAVSO",
    )


def load_ogle_dat(path: str | Path, name: str, band: str = "I") -> LightCurve:
    """Load an OGLE photometry file (.dat, space-separated HJD/mag/err).

    OGLE-II/III/IV data available at:
    http://ogle.astrouw.edu.pl/

    Parameters
    ----------
    path : str or Path
        Local path to the .dat file.
    name : str
        Human-readable system name.
    band : str
        Passband label for bookkeeping.
    """
    path = Path(path)
    df = pd.read_csv(
        path, sep=r"\s+", header=None,
        names=["hjd", "mag", "mag_err"],
        comment="#",
    )
    df = df.sort_values("hjd").reset_index(drop=True)

    return LightCurve(
        name=name,
        jd=df["hjd"].to_numpy(),
        mag=df["mag"].to_numpy(),
        mag_err=df["mag_err"].to_numpy(),
        band=band,
        source="OGLE",
    )


def load_literature_table(
    path: str | Path,
    name: str,
    jd_col: str = "JD",
    mag_col: str = "mag",
    err_col: str = "err",
    band: str = "V",
    source: str = "literature",
) -> LightCurve:
    """Load a digitised light curve from any CSV with named columns.

    Useful for Harvard plate archive data or published tables from
    journals (digitised with e.g. WebPlotDigitizer).
    """
    df = pd.read_csv(path).sort_values(jd_col).reset_index(drop=True)
    err = df[err_col].fillna(0.1).to_numpy() if err_col in df.columns else \
          np.full(len(df), 0.1)
    return LightCurve(
        name=name,
        jd=df[jd_col].to_numpy(),
        mag=df[mag_col].to_numpy(),
        mag_err=err,
        band=band,
        source=source,
    )


# ---------------------------------------------------------------------------
# Synthetic / schematic light curves for demonstration
# (replace with real data once downloaded)
# ---------------------------------------------------------------------------

def make_schematic_v445pup() -> LightCurve:
    """Schematic V-band light curve of V445 Pup (2000) based on published data.

    Reference: Ashok & Banerjee 2003, A&A 409, 1007;
               Woudt et al. 2009, ApJ 706, 738.
    """
    # JD offsets from approximate V-band peak (JD ~2451870)
    t = np.concatenate([
        np.linspace(-20, 0, 30),   # pre-peak rise
        np.linspace(0, 7, 20),     # fast decline t₂ ~ 7d
        np.linspace(7, 60, 50),    # continued decline
        np.linspace(60, 200, 80),  # dust formation + slow fading
    ])
    t = np.unique(t)

    mag = np.piecewise(
        t.astype(float),
        [t < 0,
         (t >= 0) & (t < 7),
         (t >= 7) & (t < 60),
         t >= 60],
        [
            lambda x: 13.0 - (13.0 - 8.6) * (x / 20.0 + 1.0),  # rise
            lambda x: 8.6 + x * 0.20,                             # t₂ phase
            lambda x: 8.6 + 7 * 0.20 + (x - 7) * 0.055,         # slow decline
            lambda x: 8.6 + 7 * 0.20 + 53 * 0.055               # dust fading
                     + (x - 60) * 0.025
                     + 2.0 * (1 - np.exp(-(x - 60) / 30)),       # dust bump
        ],
    )
    # add mild noise
    rng = np.random.default_rng(42)
    err = rng.uniform(0.03, 0.12, size=len(t))
    mag = mag + rng.normal(0, err)

    return LightCurve(
        name="V445 Pup",
        jd=2451870.0 + t,
        mag=np.clip(mag, 8.0, 16.5),
        mag_err=err,
        band="V",
        source="schematic (Ashok & Banerjee 2003; Woudt et al. 2009)",
    )


def make_schematic_nova_smc1994() -> LightCurve:
    """Schematic I-band light curve of Nova SMC 1994 (candidate He-nova).

    Reference: Shafter et al. 1997, ApJ 487, L45.
    """
    t = np.concatenate([
        np.linspace(-5, 0, 15),
        np.linspace(0, 80, 100),
    ])
    t = np.unique(t)

    mag = np.piecewise(
        t.astype(float),
        [t < 0, t >= 0],
        [
            lambda x: 16.5 - (16.5 - 10.8) * (x / 5.0 + 1.0),
            lambda x: 10.8 + x * 0.085,
        ],
    )
    rng = np.random.default_rng(7)
    err = rng.uniform(0.05, 0.15, size=len(t))
    mag = mag + rng.normal(0, err)

    return LightCurve(
        name="Nova SMC 1994",
        jd=2449400.0 + t,
        mag=np.clip(mag, 10.0, 18.0),
        mag_err=err,
        band="I",
        source="schematic (Shafter et al. 1997)",
    )


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def summary_table(light_curves: list[LightCurve]) -> pd.DataFrame:
    """Return a summary DataFrame with key parameters for all light curves.

    Parameters
    ----------
    light_curves : list[LightCurve]

    Returns
    -------
    pd.DataFrame
        Columns: name, band, source, peak_mag, t2, t3, speed_class.
    """
    rows = []
    for lc in light_curves:
        rows.append({
            "name": lc.name,
            "band": lc.band,
            "source": lc.source,
            "peak_mag": round(lc.peak_mag, 2),
            "t2_days": round(lc.t2, 1) if not np.isnan(lc.t2) else "—",
            "t3_days": round(lc.t3, 1) if not np.isnan(lc.t3) else "—",
            "speed_class": lc.speed_class(),
            "n_obs": len(lc.jd),
        })
    return pd.DataFrame(rows)
