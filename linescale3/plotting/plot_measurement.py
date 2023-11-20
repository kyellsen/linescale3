import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def plot_force_vs_time(df, sensor_id, measurement_id, measurement_name):
    """
    Plots force vs time and returns the matplotlib figure object.

    Parameters
    ----------
    df : DataFrame
        DataFrame containing the force data.
    measurement_name : str
        The name of the measurement.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The matplotlib figure object for the plot.
    """
    fig, ax = plt.subplots()
    ax.plot(df['sec_since_start'], df['force'])
    ax.set_xlabel('sec_since_start')
    ax.set_ylabel('force [kN]')
    ax.set_title("Force vs. Time", fontsize=16, ha='center')
    fig.suptitle(f"Sensor ID '{sensor_id}' Measurement ID '{measurement_id}'", fontsize=12, ha='center')

    return fig


def plot_force_vs_time_with_max_and_release(df, sensor_id, measurement_id, measurement_name, force_max, release):
    """
    Plots force vs time with maximum and release force.
    """
    fig, ax = plt.subplots()
    ax.plot(df['sec_since_start'], df['force'], label='Force')

    # Plot the maximum force as a red dot
    ax.scatter(df.loc[force_max[0], 'sec_since_start'], force_max[1], color='r', marker='v', label='Max Force')

    # Plot the release force as a green horizontal line
    ax.axhline(y=release, color='g', label='Release Force')

    ax.set_xlabel('sec_since_start')
    ax.set_ylabel('force [kN]')
    ax.set_title("Force vs. Time with max and release Force", fontsize=16, ha='center')
    fig.suptitle(f"Sensor ID '{sensor_id}' Measurement ID '{measurement_id}'", fontsize=12, ha='center')
    ax.legend()
    ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=15))

    return fig
