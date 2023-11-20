import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def plot_force_vs_time(measurement):
    """
    Plots the measurement.

    Parameters
    ----------
    measurement
    """

    plt.plot(measurement.df['sec_since_start'], measurement.df['force'])
    plt.xlabel('sec_since_start')
    plt.ylabel('force [kN]')
    plt.title(f"Measurement '{measurement.measurement_name}'")
    # plt.grid()
    # plt.tight_layout()
    # plot_manager.apply_matplotlib()
    # plot_manager.save_matplotlib()
    plt.close()


def plot_force_vs_time_with_max_and_release(plot_manager, measurement):
    """
    Plots the measurement.

    Parameters
    ----------
    measurement : the Measurement object

    plot_manager
    """
    plot_manager.apply_matplotlib()
    force_max = measurement.force_metadata['max']  # tuple with index and force
    release = measurement.force_metadata['release']  # float of force

    fig, ax = plt.subplots()
    ax.plot(measurement.df['sec_since_start'], measurement.df['force'], label='Force')

    # Plot the maximum force as a red dot
    ax.scatter(measurement.df.loc[force_max[0], 'sec_since_start'], force_max[1], color='r', marker='v', label='Max Force')

    # Plot the release force as a green horizontal line
    ax.axhline(y=release, color='g', label='Release Force')

    ax.set_xlabel('sec_since_start')
    ax.set_ylabel('force [kN]')
    ax.set_title("Force vs. Time with max and release Force", fontsize=16, ha='center')
    fig.suptitle(f"Sensor ID '{measurement.sensor_id}' Measurement ID '{measurement.measurement_id}'", fontsize=12, ha='center')
    ax.legend()
    ax.xaxis.set_major_locator(MaxNLocator(nbins=15))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=15))

    plot_manager.save_plot(fig, filename=f"force_vs_time_plot_{measurement.measurement_name}_{measurement.measurement_id}",
                           subdir="force_vs_time_1")

    plt.close()
