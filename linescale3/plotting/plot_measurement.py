import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import pandas as pd
from typing import Optional, Tuple


def plot_force_vs_time(
    df: pd.DataFrame,
    sensor_id: str,
    measurement_id: int,
    force_max: Optional[Tuple[int, float]] = None,
    release: Optional[float] = None
) -> plt.Figure:
    """
    Plots force vs time using seaborn styling and optionally highlights max and release forces.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'sec_since_start' and 'force' columns.
    sensor_id : str
        Sensor identifier.
    measurement_id : int
        Measurement identifier.
    force_max : tuple, optional
        Index and value of max force (highlighted as red marker).
    release : float, optional
        Release force (horizontal green line).

    Returns
    -------
    fig : plt.Figure
        The matplotlib figure object.
    """
    # Seaborn-Styling aktivieren
    sns.set(style="whitegrid")

    # Plot erstellen
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    sns.lineplot(data=df, x='sec_since_start', y='force', ax=ax, label=r"$F$ [kN]", linewidth=2)

    # Optional: horizontale Linie für Vorspannkraft bei Release
    if release is not None:
        ax.axhline(release, color='green', linestyle='--',
                   label=r"$F_{\mathrm{release}}$ [kN]")

    # Optional: Marker für Kraftspitze
    if force_max is not None:
        ax.scatter(df.loc[force_max[0], 'sec_since_start'], force_max[1],
                   color='red', marker='v', s=100,
                   label=r"$F_{\mathrm{max}}$ [kN]")

    # Achsenbeschriftungen & Titel
    ax.set_xlabel(r"Zeit $t$ [s]")
    ax.set_ylabel(r"Kraft $F$ [kN]")
    ax.set_title(rf"Kraftverlauf – Sensor ID '{sensor_id}', Messung {measurement_id}", fontsize=14)

    # Ticks optimieren
    ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=15))

    # Legende anzeigen
    ax.legend()

    return fig


def plot_force_integral(
        df,
        sensor_id: str,
        measurement_id: int,
        integral_results: dict
) -> plt.Figure:
    """
    Plots raw and centered force data along with the positive integral area.
    Annotates the plot with computed intercept and integral.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'sec_since_start', 'force' and 'force_cent' columns.
    sensor_id : str
        Sensor identifier.
    measurement_id : int
        Measurement identifier.
    integral_results : dict
        Dictionary with keys:
          - 'intercept': float
          - 'sampling_interval': float
          - 'integral': float
          - 'unit': str

    Returns
    -------
    fig : plt.Figure
    """
    times = df['sec_since_start']
    raw = df['force']
    cent = df['force_cent']  # vorausgesetzt, du hast centriert in df angelegt

    # entpacke Ergebnisse
    intercept = integral_results['intercept']
    integral = integral_results['integral']
    unit = integral_results.get('unit', '')

    # Figure
    fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
    ax.plot(times, raw, label='Rohdaten', linewidth=1)
    ax.plot(times, cent, label='Zentriert', linewidth=1)

    # Fill positive integral area
    ax.fill_between(
        times, cent, 0,
        where=cent >= 0, interpolate=True,
        alpha=0.3, color='C2',
        label=f"Integral: {integral:.2f} {unit}"
    )

    # Achsen, Titel, Grid
    ax.set_xlabel("Zeit $t$ [s]")
    ax.set_ylabel(f"Kraft $F$ [{unit.split('·')[0]}]")
    ax.set_title(f"Kraft-Integral – Sensor {sensor_id}, Messung {measurement_id}")
    ax.grid(True, linestyle='--', alpha=0.5)

    # Annotation mit Intercept & Integral
    text = (
        f"Intercept: {intercept:.2f} {unit.split('·')[0]}\n"
        f"Integral:  {integral:.2f} {unit}"
    )
    ax.text(
        0.98, 0.95, text,
        ha='right', va='top', transform=ax.transAxes,
        bbox=dict(boxstyle='round,pad=0.3', alpha=0.2)
    )

    # Ticks
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    return fig
