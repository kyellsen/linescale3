def plot_force_vs_time(sensor):
    """
    Plots the measurements.

    Parameters
    ----------
    sensor
    """

    for measurement in sensor.measurements:
        measurement.plot_force_vs_time_with_max_and_release()
