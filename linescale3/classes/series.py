from pathlib import Path
from typing import List, Dict
import pandas as pd

from .base_class import BaseClass
from .sensor import Sensor

from kj_logger import get_logger
logger = get_logger(__name__)


class Series(BaseClass):
    """
    A class to represent a series of measurements.

    Methods
    -------
    __str__():
        Returns the string representation of the MeasurementSeries instance.
    plot_sensor_measurements(path_plots: str, dpi: int):
        Plots the measurements for each sensor.
    df_x_experiment(experiment_df: pd.DataFrame, cols_to_merge: List[str], sensor_id_cols: Dict[str, str]) -> pd.DataFrame:
        Merges series sensor data with experiment data and returns the updated series data.
    metadata_x_experiment(experiment_df: pd.DataFrame, cols_to_merge: List[str], sensor_id_cols: Dict[str, str]) -> pd.DataFrame:
        Merges series sensor metadata with experiment data and returns the updated series metadata.
    """

    def __init__(self, name: str, path: str):
        """
        Constructs all the necessary attributes for the MeasurementSeries object.

        Parameters
        ----------
        name : str
            name of the measurement series
        path : str
            path of the measurement series
        """
        super().__init__()

        self.name = name
        self.path = Path(path)
        self.sensor_paths = [d for d in self.path.iterdir() if d.is_dir()]
        self.sensor_names = []
        self.sensors = []

        self._df_list = None
        self._df = None
        self._metadata_df = None

        for sensor_path in self.sensor_paths:
            if sensor_path.name not in self.sensor_paths:
                sensor_name = sensor_path.name[2:]
                sensor_name = ":".join([sensor_name[i:i + 2] for i in range(0, len(sensor_name), 2)])
                self.sensor_names.append(sensor_name)
                sensor_inst = Sensor(sensor_name, sensor_path)
                self.sensors.append(sensor_inst)

        self.sensor_count = len(self.sensors)

        self.measurements_lists = [sensor.measurements for sensor in self.sensors]
        self.measurements = [element for sublist in self.measurements_lists for element in sublist]

    def __str__(self):
        return f"Measurement Series: '{self.name}' with {self.sensor_count} sensors: {self.sensor_names}"

    @property
    def df_list(self) -> list:
        if self._df_list is None:
            self._df_list = [sensor.df for sensor in self.sensors]
        return self._df_list

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = pd.concat(self.df_list, ignore_index=True)
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    @property
    def metadata_df(self) -> pd.DataFrame:
        if self._metadata_df is None:
            metadata_df_list = [sensor.metadata_df for sensor in self.sensors]
            self._metadata_df = pd.concat(metadata_df_list, ignore_index=True)
        return self._metadata_df

    @metadata_df.setter
    def metadata_df(self, df):
        self._metadata_df = df

    def plot_force_vs_time(self):
        """
        Plots the measurements for each sensor.

        Parameters
        ----------
        series
        """

        for sensor in self.sensors:
            sensor.plot_force_vs_time()

    def plot_force_vs_time_with_max_and_release(self):
        """
        Plots the measurements for each sensor.

        Parameters
        ----------
        series
        """

        for sensor in self.sensors:
            sensor.plot_force_vs_time_with_max_and_release()
