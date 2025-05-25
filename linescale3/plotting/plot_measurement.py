import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import pandas as pd
from typing import Optional

def _setup_axes(ax: Axes, xlabel: str = "Zeit $t$ [s]", ylabel: Optional[str] = None) -> None:
    """
    Gemeinsame Achsen-Formatierung für alle Plots.
    """
    ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=12))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=12))

def plot_force_vs_time(
    df: pd.DataFrame,
    sensor_id: str,
    measurement_id: int,
    max_index: Optional[int] = None,
    max_force: Optional[float] = None,
    release: Optional[float] = None
) -> plt.Figure:
    """
    Plots force vs time und optional Marker für max + release.
    """
    sns.set(style="whitegrid")
    fig, ax = plt.subplots()

    # Linienplot der Kraft
    sns.lineplot(
        data=df, x='sec_since_start', y='force',
        ax=ax, label=r"$F$ [kN]", linewidth=2
    )

    # Release-Linie
    if release is not None:
        ax.axhline(
            release, linestyle='--', color='green',
            label=r"$F_{\mathrm{release}}$ [kN]"
        )

    # Marker für max
    if max_index is not None and max_force is not None:
        t = df.loc[max_index, 'sec_since_start']
        ax.scatter(
            t, max_force, marker='v', color='red',
            s=100, label=r"$F_{\mathrm{max}}$ [kN]"
        )

    ax.set_title(f"Kraftverlauf – Sensor {sensor_id}, Messung {measurement_id}")
    _setup_axes(ax, ylabel=r"Kraft $F$ [kN]")
    ax.legend(loc='upper right')
    fig.tight_layout()
    return fig

def plot_force_integral(
    df: pd.DataFrame,
    sensor_id: str,
    measurement_id: int,
    integral: float,
    integral_unit: str
) -> plt.Figure:
    """
    Plots raw und centered force plus positive integral area.
    """
    sns.set(style="whitegrid")
    fig, ax = plt.subplots()

    times = df['sec_since_start']
    raw   = df['force']
    cent  = df['force_cent']

    ax.plot(times, raw,  label='Rohdaten', linewidth=1)
    ax.plot(times, cent, label='Zentriert', linewidth=1)

    ax.fill_between(
        times, cent, 0,
        where=cent >= 0, interpolate=True, alpha=0.3,
        label=f"Integral: {integral:.2f} {integral_unit}"
    )

    ax.set_title(f"Kraft-Integral – Sensor {sensor_id}, Messung {measurement_id}")
    _setup_axes(ax, ylabel=f"Kraft $F$ [{integral_unit.split('·')[0]}]")
    ax.legend(loc='upper right')
    fig.tight_layout()
    return fig
