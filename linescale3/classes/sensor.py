from pathlib import Path
from typing import List, Optional
import pandas as pd

from .base_class import BaseClass
from .measurement import Measurement

from kj_logger import get_logger

logger = get_logger(__name__)


class Sensor(BaseClass):
    """
    A class to represent a sensor.

    Attributes:
    -----------
    name : str
        Name of the sensor.
    path : Path to the sensor.
    measurement_files : List of measurement files associated with the sensor.
    measurement_names : List of names of the measurements.
    measurements : List of Measurement instances.
    measurements_count : int
        Count of the measurements associated with the sensor.
    df : pd.DataFrame
        a pandas DataFrame object
    metadata_df : pd.DataFrame
        a pandas DataFrame object

    Properties:
    -----------
    df_list : List of dataframes of measurements.
    df : pd.DataFrame
        Combined dataframe of all measurements.

    Methods:
    --------
    __str__() -> str
        Returns the string representation of the Sensor instance.
    plot_force_vs_time()
        Plots force versus time for the measurements.
    df_x_experiment(experiment_df: pd.DataFrame, cols_to_merge: List[str], sensor_id_col: str) -> pd.DataFrame:
        Merges sensor data with experiment data and returns the updated sensor data.
    metadata_x_experiment(experiment_df: pd.DataFrame, cols_to_merge: List[str], sensor_id_col: str) -> pd.DataFrame:
        Merges sensor metadata with experiment data and returns the updated sensor metadata.
    """

    def __init__(self, name: str, path: Path):
        """
        Constructs all the necessary attributes for the Sensor object.

        Parameters
        ----------
        name : str
            Name of the sensor.
        path : Path to the sensor.
        """
        super().__init__()

        self.name = name
        self.path = path
        self.measurement_files: List[str] = []
        self.measurement_names: List[str] = []
        self.measurements: List[Measurement] = []
        self._df_list = None
        self._df = None
        self._metadata_df = None

        try:
            csv_files = [f for f in self.path.glob("**/*.CSV") if f.is_file()]
            for csv_file in csv_files:
                self.measurement_files.append(csv_file.name)
                measurement_name = str(csv_file)[-28:-4].replace("\\", "_")
                self.measurement_names.append(measurement_name)
                measurement_inst = Measurement.read_csv(measurement_name, csv_file)
                self.measurements.append(measurement_inst)

            self.measurements_count = len(self.measurement_files)
        except Exception as e:
            logger.error(f"{name} failed to setup Sensor. Error: {e}")
            raise

    def __str__(self) -> str:
        return f"Sensor: '{self.name}' in '{self.path}' with {self.measurements_count} measurements"

    @property
    def df_list(self) -> List[pd.DataFrame]:
        if self._df_list is None:
            self._df_list = [measurement.df for measurement in self.measurements]
        return self._df_list

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            try:
                self._df = pd.concat(self.df_list, ignore_index=True)
            except Exception as e:
                logger.error(f"{self} failed to concatenate dataframes. Error: {e}")
                raise
        return self._df

    @df.setter
    def df(self, df: pd.DataFrame):
        self._df = df

    @property
    def metadata_df(self) -> pd.DataFrame:
        """
        Property that returns a DataFrame containing metadata of all measurements.

        Returns
        -------
        pd.DataFrame containing metadata of all measurements
        """
        try:
            if self._metadata_df is None:
                metadata_list = [measurement.full_metadata for measurement in self.measurements]
                self._metadata_df = pd.DataFrame.from_records(metadata_list)

        except Exception as e:
            logger.error(f"Failed to create metadata DataFrame for sensor: '{self.name}'. Error: {e}")
            self._metadata_df = pd.DataFrame()

        return self._metadata_df

    @metadata_df.setter
    def metadata_df(self, df: pd.DataFrame):
        self._metadata_df = df

    def plot_force_vs_time(self):
        """
        Plots the measurements.

        Parameters
        ----------
        sensor
        """
        for measurement in self.measurements:
            measurement.plot_force_vs_time()

    def plot_force_vs_time_with_max_and_release(self):
        """
        Plots the measurements.

        Parameters
        ----------
        sensor
        """
        for measurement in self.measurements:
            measurement.plot_force_vs_time_with_max_and_release()

    def df_x_experiment(self, experiment_df: pd.DataFrame, cols_to_merge: List[str], sensor_id_col: str) \
            -> Optional[pd.DataFrame]:
        """
        Merges sensor data with experiment data.

        Parameters
        ----------
        experiment_df : pd.DataFrame
            The experiment data.
        cols_to_merge : List[str]
            The columns to merge from the experiment data.
        sensor_id_col : str
            The column name in the experiment data that corresponds to 'measurement_id' in sensor data.

        Returns
        -------
        pd.DataFrame
            The updated sensor data.
        """
        try:
            self.df = self.df.merge(experiment_df[cols_to_merge], left_on='measurement_id', right_on=sensor_id_col,
                                    how='left')
            self.df.drop([sensor_id_col], axis=1, inplace=True)
        except Exception as e:
            logger.error(f"Error while merging sensor data: {e}")
            return None

        return self.df

    def metadata_x_experiment(self, experiment_df: pd.DataFrame, cols_to_merge: List[str], sensor_id_col: str) -> \
            Optional[pd.DataFrame]:
        """
        Merges sensor metadata with experiment data.

        Parameters
        ----------
        experiment_df : pd.DataFrame
            The experiment data.
        cols_to_merge : List[str]
            The columns to merge from the experiment data.
        sensor_id_col : str
            The column name in the experiment data that corresponds to 'measurement_id' in sensor metadata.

        Returns
        -------
        pd.DataFrame
            The updated sensor metadata.
        """
        try:
            self.metadata_df = self.metadata_df.merge(experiment_df[cols_to_merge], left_on='measurement_id',
                                                      right_on=sensor_id_col, how='left')
            self.metadata_df.drop([sensor_id_col], axis=1, inplace=True)
        except Exception as e:
            logger.error(f"Error while merging sensor metadata: {e}")
            return None

        return self.metadata_df
