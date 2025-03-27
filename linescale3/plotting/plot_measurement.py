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
