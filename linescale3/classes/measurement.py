from pathlib import Path
from typing import Dict, Union, Optional, Tuple
import numpy as np
import pandas as pd

from slugify import slugify

from .base_class import BaseClass

from ..plotting import plot_measurement

from kj_logger import get_logger

logger = get_logger(__name__)


class Measurement(BaseClass):
    """
    A class to represent a measurement.

    Methods
    -------
    read_csv(measurement_name: str, csv_file: Path):
        Reads a measurement from a csv file and returns a Measurement instance.
    get_measurement_df():
        Returns a dataframe representing the measurement.
    force_vs_time(path_plots: str, dpi: int):
        Plots the measurement.
    """

    def __init__(self, measurement_name: str, sensor_id: str, date: str, time: str, measurement_id: int, unit: str,
                 mode: str, rel_zero: str, speed: int, trig: float, stop: float, pre: int, catch: int, total: int,
                 force: np.array):
        """
        Constructs all the necessary attributes for the Measurement object.
        """
        super().__init__()

        self.measurement_name = measurement_name
        self.sensor_id = sensor_id
        self.datetime = pd.to_datetime(date + ' ' + time, format='%d\\%m\\%y %H:%M:%S')
        self.measurement_id = measurement_id
        self.unit = unit
        self.mode = mode
        self.rel_zero = rel_zero
        self.speed = speed
        self.trig = trig
        self.stop = stop
        self.pre = pre
        self.catch = catch
        self.total = total
        self.force = force
        self.timing_correction_factor = 0.9
        self._df = None
        self._metadata: Dict = {}
        self._time_metadata: Dict = {}
        self._force_metadata: Dict = {}
        self._force_integral: Optional[Dict[str, float]] = None
        self._full_metadata: Dict = {}


    def __str__(self):
        return f"Measurement(id: '{self.measurement_id}', name: '{self.measurement_name}', sensor_id: '{self.sensor_id}')"

    @classmethod
    def read_csv(cls, measurement_name: str, csv_file: Path) -> Optional['Measurement']:
        """
        Reads a measurement from a csv file and returns a Measurement instance.
        """
        try:
            df = pd.read_csv(csv_file, header=None)
            sensor_id = str(df.loc[0, 0])
            date = str(df.loc[1, 0])
            time = str(df.loc[2, 0])
            measurement_id = int(df.loc[3, 0].split('=')[1])
            unit = str(df.loc[4, 0].split('=')[1])
            mode = str(df.loc[5, 0].split('=')[1])
            rel_zero = str(df.loc[6, 0].split('=')[1])
            speed = int(df.loc[7, 0].split('=')[1])
            trig = float(df.loc[8, 0].split('=')[1])
            stop = float(df.loc[9, 0].split('=')[1])
            pre = int(df.loc[10, 0].split('=')[1])
            catch = int(df.loc[11, 0].split('=')[1])
            total = int(df.loc[12, 0].split('=')[1])
            force = np.array(df.loc[13:, 0].astype(float))

            measurement = cls(measurement_name, sensor_id, date, time, measurement_id, unit, mode, rel_zero, speed,
                              trig, stop, pre, catch, total, force)
            logger.info(f"Read CSV for {measurement} successful.")
            return measurement
        except Exception as e:
            logger.error(f"Failed to read CSV file: '{csv_file}'. Error: {e}")
            return None

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns a dataframe representing the measurement.
        """
        if self._df is None:
            try:
                df = pd.DataFrame({'force': self.force,
                                   'sensor_id': self.sensor_id,
                                   'measurement_id': self.measurement_id,
                                   'unit': self.unit,
                                   'mode': self.mode,
                                   'rel_zero': self.rel_zero,
                                   'speed': self.speed,
                                   'trig': self.trig,
                                   'stop': self.stop,
                                   'pre': self.pre,
                                   'catch': self.catch,
                                   'total': self.total,
                                   'timing_correction_factor': self.timing_correction_factor})
                df.insert(0, "id", df.index)
                df.insert(1, "datetime",
                          self.datetime + pd.to_timedelta(df.index / self.speed * self.timing_correction_factor,
                                                          unit='s'))
                df.insert(2, "sec_since_start", (df['datetime'] - self.datetime).dt.total_seconds().astype(float))

                self._df = df[self.CONFIG.df_cols]
            except Exception as e:
                logger.error(f"Failed to create dataframe for measurement: '{self.measurement_name}'. Error: {e}")
        return self._df

    @df.setter
    def df(self, df: pd.DataFrame):
        """
        Setter method for df property.

        Parameters
        ----------
        df : pd.Dataframe to be set as df property
        """
        try:
            self._df = df
        except Exception as e:
            logger.error(f"Failed to set dataframe for measurement: '{self.measurement_name}'. Error: {e}")

    @property
    def metadata(self) -> Dict[str, Union[str, int, float]]:
        """
        Property that returns the metadata of the Measurement instance.

        Returns
        -------
        Dict[str, Union[str, int, float]]
            Dictionary containing metadata
        """
        try:
            attributes = self.CONFIG.metadata_cols

            for attr in attributes:
                if hasattr(self, attr):
                    self._metadata[attr] = getattr(self, attr)

        except Exception as e:
            logger.error(f"Failed to retrieve metadata for measurement: '{self.measurement_name}'. Error: {e}")

        return self._metadata

    @property
    def time_metadata(self) -> Dict[str, Union[str, int, float]]:
        """
        Property that returns the time metadata of the Measurement instance.

        Returns
        -------
        Dict[str, Union[str, int, float]]
            Dictionary containing time metadata
        """
        try:
            attributes = self.CONFIG.time_metadata_cols

            if 'datetime_start' in attributes:
                self._time_metadata['datetime_start'] = self.df.datetime.min()
            if 'datetime_end' in attributes:
                self._time_metadata['datetime_end'] = self.df.datetime.max()
            if 'duration' in attributes:
                start = self.df.datetime.min()
                end = self.df.datetime.max()
                self._time_metadata['duration'] = (end - start).total_seconds()
            if 'length' in attributes:
                self._time_metadata['length'] = len(self.df)

        except Exception as e:
            logger.error(f"Failed to retrieve time metadata for measurement: '{self.measurement_name}'. Error: {e}")

        return self._time_metadata

    @property
    def force_metadata(self) -> Dict[str, float]:
        """
        Property that returns the force metadata of the Measurement instance.

        Returns
        -------
        Dict[str, float]
            Dictionary containing force metadata
        """
        try:
            attributes = self.CONFIG.force_metadata_cols

            if 'max' in attributes:
                max_index = np.argmax(self.force)
                self._force_metadata['max'] = (max_index, self.force[max_index])
            if 'mean' in attributes:
                self._force_metadata['mean'] = np.mean(self.force)
            if 'median' in attributes:
                self._force_metadata['median'] = np.median(self.force)
            if 'min' in attributes:
                min_index = np.argmin(self.force)
                self._force_metadata['min'] = (min_index, self.force[min_index])
            # special for Plesse project
            if 'release' in attributes:
                self._force_metadata['release'] = self.get_release_force()
            # neu: nur wenn calculate_force_integral vorher aufgerufen wurde
            if self._force_integral is not None:
                # wir fügen alle Schlüssel/Werte aus _force_integral hinzu
                self._force_metadata.update(self._force_integral)

        except Exception as e:
            logger.error(f"Failed to retrieve force metadata for measurement: '{self.measurement_name}'. Error: {e}")

        return self._force_metadata

    @property
    def full_metadata(self) -> Dict[str, Union[str, int, float]]:
        """
        Property that returns the full metadata of the Measurement instance.

        Returns
        -------
        Dict[str, Union[str, int, float]]
            Dictionary containing full metadata
        """
        try:
            # bestehende Metadaten
            self._full_metadata = {
                **self.metadata,
                **self.time_metadata,
                **self.force_metadata
            }
        except Exception as e:
            logger.error(f"Failed to retrieve full metadata for measurement: '{self.measurement_name}'. Error: {e}")

        return self._full_metadata

    def plot_force_vs_time(self):
        """
        Method to plot force vs time with optional max force marker.
        """
        try:
            fig = plot_measurement.plot_force_vs_time(
                df=self.df,
                sensor_id=self.sensor_id,
                measurement_id=self.measurement_id,
                force_max=self.force_metadata.get("max")  # optional
            )
            self.PLOT_MANAGER.save_plot(
                fig,
                filename=slugify(f"f_vs_t_{self.sensor_id}_ID_{self.measurement_id}", separator="_"),
                subdir="force_vs_time"
            )

            logger.info(f"plot_force_vs_time for measurement: '{self}'.")
        except Exception as e:
            logger.error(f"Failed to plot_force_vs_time: '{self}'. Error: {e}")

    def plot_force_vs_time_with_max_and_release(self):
        """
        Method to plot force vs time with maximum and release force.
        """
        try:
            fig = plot_measurement.plot_force_vs_time(
                df=self.df,
                sensor_id=self.sensor_id,
                measurement_id=self.measurement_id,
                force_max=self.force_metadata.get("max"),
                release=self.force_metadata.get("release")
            )

            self.PLOT_MANAGER.save_plot(
                fig,
                filename=slugify(f"f_vs_t_{self.sensor_id}_ID_{self.measurement_id}", separator="_"),
                subdir="force_vs_time_with_max_and_release"
            )

            logger.info(f"plot_force_vs_time_with_max_and_release for measurement: '{self}'.")
        except Exception as e:
            logger.error(f"Failed to plot_force_vs_time_with_max_and_release for measurement: '{self}'. Error: {e}")

    def get_release_force(self, min_force: float = 1, window_sec: int = 5, distance_to_end_sec: int = 3) -> Optional[float]:
        """
        Calculate the mean release force from the force data and provide the window for plotting.

        This method identifies and calculates the average release force
        within a specified time window before the end of the measurement.

        Parameters
        ----------
        min_force : float, optional
            The minimum force threshold to be considered (default is 1).
        window_sec : int, optional
            The duration of the time window in seconds within which the force
            is averaged (default is 5 seconds).
        distance_to_end_sec : int, optional
            The duration in seconds from the end of the measurement to
            the start of the averaging window (default is 3 seconds).

        Returns
        -------
        Optional[float]

        Raises
        ------
        Exception
            If the calculation of the release force fails, an error message is logged and None is returned.
        """
        try:
            force = self.df.force
            window = self.speed * window_sec
            distance = self.speed * distance_to_end_sec

            f = force[force > min_force].copy()
            f = f.iloc[-(window + distance):-distance]
            release_force = f.mean()
            return release_force
        except Exception as e:
            logger.error(f"Failed to calculate release force for measurement: '{self.measurement_name}'. Error: {e}")
            return None

    def calculate_force_integral(
            self,
            last_frac: float = 0.20, plot=True
    ) -> None:
        """
        Berechnet das zeitliche Integral der Kraftmesswerte (nur positiv) und speichert die Ergebnisse.

        Dabei wird zunächst ein Intercept als Mittelwert der letzten `last_frac` Anteile der Werte
        bestimmt und von allen Messwerten abgezogen. Negative Werte werden auf Null gesetzt.

        Parameters
        ----------
        last_frac : float, optional
            Anteil der letzten Datenpunkte zur Berechnung des Intercepts. Muss im Bereich (0, 1]
            liegen. Standard ist 0.20 (20 %).

        Returns
        -------
        None

        Raises
        ------
        ValueError
            Wenn `last_frac` nicht im Bereich (0, 1] liegt.
        """
        # 1) Validierung
        if not (0 < last_frac <= 1):
            raise ValueError("last_frac must be in (0, 1]")

        # 2) DataFrame und Zeitintervall (sampling_interval) bestimmen
        df = self.df.copy()  # stellt sicher, dass df existiert
        sampling_interval = 1.0 / self.speed * self.timing_correction_factor

        # 3) Intercept aus letzten last_frac Werten
        values = df['force'].to_numpy()
        n = len(values)
        n_last = max(1, int(n * last_frac))
        intercept = values[-n_last:].mean()

        # 4) Zentrieren und Negatives auf 0 setzen
        centered = values - intercept
        centered = np.clip(centered, a_min=0, a_max=None)

        df['force_cent'] = centered

        # 5) Integral berechnen
        integral = centered.sum() * sampling_interval

        # 6) Ergebnisse speichern (optionales Attribut)
        self._force_integral = {
            'intercept': intercept,
            'sampling_interval': sampling_interval,
            'integral': integral,
            'unit': f"{self.unit}·s"
        }
        logger.info(
            f"calculate_force_integral erfolgreich: intercept={intercept:.3f}, integral={integral:.3f} {self.unit}·s"
        )

        if plot:
            fig = plot_measurement.plot_force_integral(
                df=df,
                sensor_id=self.sensor_id,
                measurement_id=self.measurement_id,
                integral_results=self._force_integral
            )
            filename = slugify(f"force_int_{self.sensor_id}_ID_{self.measurement_id}")
            self.PLOT_MANAGER.save_plot(fig, filename, subdir="force_integrals")
