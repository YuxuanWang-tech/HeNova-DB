"""
henova/plot.py
~~~~~~~~~~~~~~
Publication-quality figures for helium nova candidate analysis.

All figures are saved to results/ with 300 dpi by default.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from pathlib import Path
from typing import Optional

from henova.lightcurve import LightCurve
from henova.spectral import LITERATURE_VELOCITIES, H_DEFICIENCY_TABLE, equivalent_width_ratio

# Publication style
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
})

RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Colour scheme for each system
SYSTEM_COLORS = {
    "V445 Pup":      "#E8A020",
    "V605 Aql":      "#3B82F6",
    "V4334 Sgr":     "#14B8A6",
    "Nova SMC 1994": "#FF6B35",
    "[HP99] 159":    "#A855F7",
    "V450 Cyg":      "#EC4899",
}


def plot_light_curves(
    light_curves: list[LightCurve],
    outfile: Optional[str] = "fig1_lightcurves.pdf",
    show: bool = False,
) -> plt.Figure:
    """Multi-panel light curve comparison figure.

    One panel per system, x-axis aligned to days since peak, y-axis inverted
    (brighter at top) following photometric convention.
    """
    n = len(light_curves)
    ncols = min(2, n)
    nrows = (n + 1) // 2

    fig, axes = plt.subplots(nrows, ncols, figsize=(7 * ncols, 3.5 * nrows),
                              squeeze=False)
    fig.subplots_adjust(hspace=0.4, wspace=0.35)

    for i, lc in enumerate(light_curves):
        ax = axes[i // ncols][i % ncols]
        color = SYSTEM_COLORS.get(lc.name, "#888888")
        days = lc.days_from_peak

        ax.errorbar(days, lc.mag, yerr=lc.mag_err,
                    fmt="o", color=color, alpha=0.65, ms=2.5, lw=0,
                    elinewidth=0.6, capsize=1.5, label="observed")

        # Mark peak
        ax.axvline(0, ls="--", lw=0.7, color="gray", alpha=0.6)

        # Mark t₂
        t2 = lc.t2
        if not np.isnan(t2):
            ax.axvline(t2, ls=":", lw=1.0, color=color, alpha=0.8,
                       label=rf"$t_2={t2:.0f}$ d")

        ax.invert_yaxis()
        ax.set_xlabel("Days since peak")
        ax.set_ylabel(f"Magnitude ({lc.band})")
        ax.set_title(lc.name, fontweight="bold", pad=6)
        ax.legend(loc="lower right", framealpha=0.4)
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.grid(True, which="major", alpha=0.15, lw=0.5)

    # Hide unused panels
    for j in range(n, nrows * ncols):
        axes[j // ncols][j % ncols].set_visible(False)

    fig.suptitle("He-nova candidates: optical light curves", fontsize=12,
                 fontweight="bold", y=1.01)

    if outfile:
        fig.savefig(RESULTS_DIR / outfile, bbox_inches="tight")
        print(f"Saved {RESULTS_DIR / outfile}")
    if show:
        plt.show()
    return fig


def plot_velocity_comparison(
    outfile: Optional[str] = "fig2_velocities.pdf",
    show: bool = False,
) -> plt.Figure:
    """Horizontal bar chart of peak ejecta velocities [km/s] per system."""
    systems = {}
    for m in LITERATURE_VELOCITIES:
        if m.system not in systems:
            systems[m.system] = []
        systems[m.system].append(m.v_expansion)

    names  = list(systems.keys())
    v_max  = [max(v) for v in systems.values()]
    colors = [SYSTEM_COLORS.get(n, "#888888") for n in names]

    fig, ax = plt.subplots(figsize=(6.5, 0.7 * len(names) + 1.5))

    bars = ax.barh(names, v_max, color=colors, alpha=0.85, height=0.55,
                   edgecolor="white", linewidth=0.5)

    for bar, v in zip(bars, v_max):
        ax.text(v + 80, bar.get_y() + bar.get_height() / 2,
                f"{v:,.0f}", va="center", fontsize=8.5, color="black")

    # Reference: typical classical nova velocity
    ax.axvline(1500, ls="--", lw=0.9, color="dimgray", alpha=0.7,
               label="Typical classical nova (~1500 km/s)")

    ax.set_xlabel("Peak ejecta expansion velocity [km/s]")
    ax.set_xlim(0, max(v_max) * 1.25)
    ax.set_title("Ejecta velocities: He-nova candidates vs classical novae",
                 fontweight="bold", pad=8)
    ax.legend(framealpha=0.4, fontsize=8)
    ax.xaxis.set_minor_locator(MultipleLocator(500))
    ax.grid(True, axis="x", which="major", alpha=0.15, lw=0.5)
    ax.invert_yaxis()

    if outfile:
        fig.savefig(RESULTS_DIR / outfile, bbox_inches="tight")
        print(f"Saved {RESULTS_DIR / outfile}")
    if show:
        plt.show()
    return fig


def plot_h_deficiency(
    outfile: Optional[str] = "fig3_h_deficiency.pdf",
    show: bool = False,
) -> plt.Figure:
    """Scatter plot of EW(He I 5876) vs EW(Hα): the H-deficiency diagram."""
    fig, ax = plt.subplots(figsize=(6, 5))

    for system, (ew_he, ew_h, note) in H_DEFICIENCY_TABLE.items():
        color = SYSTEM_COLORS.get(system, "#AAAAAA")
        is_classical = "classical" in system.lower()

        if ew_h is None:
            # Plot as upper limit arrow on x-axis
            ax.annotate(
                "", xy=(0.3, ew_he), xytext=(5.0, ew_he),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
            )
            ax.scatter([5.0], [ew_he], color=color, s=60, zorder=5,
                       marker="<" if not is_classical else "D")
            ax.text(5.5, ew_he, system, va="center", fontsize=7.5, color=color)
        else:
            ax.scatter([ew_h], [ew_he], color=color, s=80, zorder=5,
                       marker="D" if is_classical else "o")
            ax.text(ew_h * 1.08, ew_he, system, va="center", fontsize=7.5,
                    color=color)

    # Diagonal: He I EW = Hα EW (parity line)
    x_ref = np.linspace(0, 130, 200)
    ax.plot(x_ref, x_ref, ls="--", lw=0.8, color="gray", alpha=0.5,
            label="EW(He I) = EW(Hα)")

    ax.set_xlabel(r"EW(H$\alpha$) [Å]  (→ undetected)")
    ax.set_ylabel(r"EW(He I $\lambda$5876) [Å]")
    ax.set_title("H-deficiency diagnostic: He I vs Hα equivalent widths",
                 fontweight="bold", pad=8)
    ax.set_xlim(-5, 135)
    ax.set_ylim(0, 55)
    ax.legend(framealpha=0.4, fontsize=8)
    ax.grid(True, alpha=0.12, lw=0.5)

    # Annotation: helium-nova region
    ax.fill_betweenx([0, 55], -5, 10, alpha=0.05, color="#E8A020")
    ax.text(5, 50, "He-nova\nregion", ha="center", fontsize=7.5,
            color="#E8A020", alpha=0.8, fontstyle="italic")

    if outfile:
        fig.savefig(RESULTS_DIR / outfile, bbox_inches="tight")
        print(f"Saved {RESULTS_DIR / outfile}")
    if show:
        plt.show()
    return fig
