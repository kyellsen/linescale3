def plot_force_vs_time(series):
    """
    Plots the measurements for each sensor.

    Parameters
    ----------
    series
    """

    for sensor in series.sensors:
        sensor.plot_force_vs_time()
