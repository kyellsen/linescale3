import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
from typing import Tuple


def plot_force_vs_time(df: pd.DataFrame, sensor_id: str, measurement_id: str,
                       force_max: Tuple[int, float]) -> plt.Figure:
    """
    Plots force vs time and returns the matplotlib figure object.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the force data.
    sensor_id : str
        ID of the sensor.
    measurement_id : str
        ID of the measurement.
    force_max : Tuple[int, float]
        Index and value of the maximum force.

    Returns
    -------
    fig : plt.Figure
        The matplotlib figure object for the plot.
    """
    fig, ax = plt.subplots()
    ax.plot(df['sec_since_start'], df['force'], label='Force')

    # Plot the maximum force as a red dot
    ax.scatter(df.loc[force_max[0], 'sec_since_start'], force_max[1], color='r', marker='v', label='Max Force')

    ax.set_xlabel('sec_since_start')
    ax.set_ylabel('force [kN]')
    ax.set_title("Force vs. Time", fontsize=16, ha='center')
    fig.suptitle(f"Sensor ID '{sensor_id}' Measurement ID '{measurement_id}'", fontsize=12, ha='center')
    ax.legend()
    ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=15))

    return fig


def plot_force_vs_time_with_max_and_release(df: pd.DataFrame, sensor_id: str, measurement_id: str,
                                            force_max: Tuple[int, float], release: float) -> plt.Figure:
    """
    Plots force vs time with maximum and release force.

    Parameters
    ----------
    df : pd.DataFrame
        Data containing force and time information.
    sensor_id : str
        ID of the sensor.
    measurement_id : str
        ID of the measurement.
    force_max : Tuple[int, float]
        Index and value of the maximum force.
    release : float
        The release force value.

    Returns
    -------
    fig : plt.Figure
        The matplotlib figure object for the plot.
    """
    fig, ax = plt.subplots()
    ax.plot(df['sec_since_start'], df['force'], label='Force')

    # Plot the maximum force as a red dot
    ax.scatter(df.loc[force_max[0], 'sec_since_start'], force_max[1], color='r', marker='v', label='Max Force')

    # Plot the release force as a green horizontal line with whiskers
    ax.axhline(y=release, color='g', label='Release Force')

    ax.set_xlabel('sec_since_start')
    ax.set_ylabel('force [kN]')
    ax.set_title("Force vs. Time with Max and Release Force", fontsize=16, ha='center')
    fig.suptitle(f"Sensor ID '{sensor_id}' Measurement ID '{measurement_id}'", fontsize=12, ha='center')
    ax.legend()
    ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=15))

    return fig
