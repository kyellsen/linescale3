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
        Reads a measurement from a CSV file and returns a Measurement instance.
    get_measurement_df():
        Returns a DataFrame representing the measurement.
    force_vs_time(path_plots: str, dpi: int):
        Plots the measurement.
    """

    def __init__(
        self,
        measurement_name: str,
        sensor_id: str,
        date: str,
        time: str,
        measurement_id: int,
        unit: str,
        mode: str,
        rel_zero: str,
        speed: int,
        trig: float,
        stop: float,
        pre: int,
        catch: int,
        total: int,
        force: np.array
    ):
        """
        Constructs all necessary attributes for the Measurement object.
        """
        super().__init__()
        self.measurement_name = measurement_name
        self.sensor_id = sensor_id
        self.datetime = pd.to_datetime(f"{date} {time}", format="%d\\%m\\%y %H:%M:%S")
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

        self._df: Optional[pd.DataFrame] = None
        self._force_intercept_edited: float = 0.0
        self._df_edited: Optional[pd.DataFrame] = None

        self._optional_metadata: Dict[str, any] = {}

        # self._force_integral: Optional[Dict[str, float]] = None

    def __str__(self) -> str:
        return (
            f"Measurement(id='{self.measurement_id}', "
            f"name='{self.measurement_name}', sensor_id='{self.sensor_id}')"
        )

    @classmethod
    def read_csv(cls, measurement_name: str, csv_file: Path) -> Optional['Measurement']:
        """
        Reads a measurement from a CSV file and returns a Measurement instance.
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

            measurement = cls(
                measurement_name, sensor_id, date, time, measurement_id,
                unit, mode, rel_zero, speed, trig, stop, pre, catch, total, force
            )
            logger.info(f"Read CSV for {measurement} successful.")
            return measurement
        except Exception as e:
            logger.error(f"Failed to read CSV file '{csv_file}': {e}")
            return None

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns a DataFrame representing the measurement.
        """
        if self._df is None:
            try:
                df = pd.DataFrame({
                    'force': self.force,
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
                    'total': self.total
                })
                df.insert(0, "id", df.index)
                df.insert(
                    1, "datetime",
                    self.datetime + pd.to_timedelta(df.index / self.speed, unit='s')
                )
                df.insert(
                    2, "sec_since_start",
                    (df['datetime'] - self.datetime).dt.total_seconds().astype(float)
                )

                self._df = df[self.CONFIG.df_cols]
            except Exception as e:
                logger.error(f"Failed to create dataframe for measurement '{self.measurement_name}': {e}")
        return self._df

    @property
    def metadata(self) -> Dict[str, Union[str, int, float]]:
        """
        Returns the metadata of this Measurement instance.
        """
        md: Dict[str, Union[str, int, float]] = {}
        try:
            for key in self.CONFIG.metadata_cols:
                if hasattr(self, key):
                    md[key] = getattr(self, key)
        except Exception as e:
            logger.error(f"Failed to retrieve metadata for measurement '{self.measurement_name}': {e}")
        return md

    @property
    def time_metadata(self) -> Dict[str, Union[str, int, float]]:
        """
        Returns the time-related metadata of this Measurement instance.
        """
        md: Dict[str, Union[str, int, float]] = {}
        try:
            cols = self.CONFIG.time_metadata_cols
            if 'datetime_start' in cols:
                md['datetime_start'] = self.df.datetime.min()
            if 'datetime_end' in cols:
                md['datetime_end'] = self.df.datetime.max()
            if 'duration' in cols:
                start = self.df.datetime.min()
                end = self.df.datetime.max()
                md['duration'] = (end - start).total_seconds()
            if 'length' in cols:
                md['length'] = len(self.df)
        except Exception as e:
            logger.error(f"Failed to retrieve time metadata for measurement '{self.measurement_name}': {e}")
        return md

    @property
    def force_metadata(self) -> Dict[str, Union[int, float]]:
        """
        Provides the force statistics specified in CONFIG.force_metadata_cols.
        Possible keys are:
          - 'max_index', 'max_force'
          - 'min_index', 'min_force'
          - 'mean', 'median'
        """
        md: Dict[str, Union[int, float]] = {}
        cols = self.CONFIG.force_metadata_cols

        # Max index and value
        if 'max_index' in cols or 'max_force' in cols:
            idx_max = int(np.argmax(self.force))
            if 'max_index' in cols:
                md['max_index'] = idx_max
            if 'max_force' in cols:
                md['max_force'] = float(self.force[idx_max])

        # Min index and value
        if 'min_index' in cols or 'min_force' in cols:
            idx_min = int(np.argmin(self.force))
            if 'min_index' in cols:
                md['min_index'] = idx_min
            if 'min_force' in cols:
                md['min_force'] = float(self.force[idx_min])

        # Mean & median
        if 'mean' in cols:
            md['mean'] = float(np.mean(self.force))
        if 'median' in cols:
            md['median'] = float(np.median(self.force))

        return md

    @property
    def optional_metadata(self) -> Dict[str, Union[int, float]]:
        """
        Returns any optional metadata entries (e.g. 'release')
        stored in self._optional_metadata and listed in CONFIG.optional_metadata_cols.
        """
        cols = set(self.CONFIG.optional_metadata_cols)
        md = {k: v for k, v in self._optional_metadata.items() if k in cols}
        if 'force_intercept_edited' in cols:
            md['intercept'] = self._force_intercept_edited
        return md

    @property
    def full_metadata(self) -> Dict[str, Union[str, int, float]]:
        """
        Returns the full metadata of this Measurement instance,
        combining standard, time-based, force-based, and optional entries.
        """
        try:
            return {
                **self.metadata,
                **self.time_metadata,
                **self.force_metadata,
                **self.optional_metadata
            }
        except Exception as e:
            logger.error(f"Failed to retrieve full metadata for measurement '{self.measurement_name}': {e}")

    @property
    def df_edited(self) -> pd.DataFrame:
        """
        Returns the edited DataFrame – on first access it is created
        as a copy of `self.df` and cached.
        """
        if self._df_edited is None:
            self._df_edited = self.df.copy()
        return self._df_edited

    @df_edited.setter
    def df_edited(self, df: pd.DataFrame) -> None:
        """
        Sets the edited DataFrame. Verifies that all required columns
        from CONFIG.df_cols are present.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df_edited must be a pandas DataFrame")
        missing = set(self.CONFIG.df_cols) - set(df.columns)
        if missing:
            raise ValueError(f"df_edited is missing columns: {sorted(missing)}")
        self._df_edited = df

    def apply_force_intercept(self, intercept: float) -> None:
        """
        Subtracts a manual intercept (in kN) from the force column
        in `df_edited` and stores the result in a new column 'force_cent'
        (negative values clipped to zero). If `df_edited` does not exist,
        it is created as a copy of `df`.
        """
        try:
            # lazy initialization
            df = self.df_edited
            # save intercept
            self._force_intercept_edited = float(intercept)
            # center + clip
            df['force_cent'] = (df['force'] - self._force_intercept_edited).clip(lower=0)
            # reset (revalidates columns)
            self.df_edited = df

            logger.info(
                f"apply_force_intercept successful for measurement '{self.measurement_name}': "
                f"intercept={self._force_intercept_edited:.3f}"
            )
        except Exception as e:
            logger.error(
                f"Failed to apply force intercept for measurement '{self.measurement_name}': {e}"
            )

    def auto_calculate_force_intercept(
        self,
        *,
        time_window: Optional[Tuple[float, float]] = None,
        index_window: Optional[Tuple[float, float]] = None,
        method: str = "mean"
    ) -> float:
        """
        Automatically determines an intercept value from the original force signal
        and applies it via `apply_force_intercept` to `df_edited`.

        Either specify `time_window=(t0, t1)` in seconds OR
        `index_window=(p_start, p_end)` as a fraction [0,1] of the data length.

        Parameters
        ----------
        time_window : optional
            (t0, t1) in seconds.
        index_window : optional
            (p_start, p_end) as fraction of the total number of rows (0 ≤ p_start < p_end ≤ 1).
        method : {"mean","median"}, default "mean"
            Statistical measure to use for the intercept.

        Returns
        -------
        float
            The calculated intercept.
        """
        if time_window is not None and index_window is not None:
            raise ValueError("Specify only one of `time_window` or `index_window`, not both.")
        if method not in ("mean", "median"):
            raise ValueError(f"Unknown method '{method}'; only 'mean' or 'median' allowed.")

        df = self.df  # original data

        # 1) Selection window
        if time_window is not None:
            t0, t1 = time_window
            df_sel = df[(df["sec_since_start"] >= t0) & (df["sec_since_start"] <= t1)]
        elif index_window is not None:
            p0, p1 = index_window
            if not (0 <= p0 < p1 <= 1):
                raise ValueError("Values in `index_window` must satisfy 0 ≤ p_start < p_end ≤ 1.")
            n = len(df)
            start_idx = int(n * p0)
            end_idx = int(n * p1)
            df_sel = df.iloc[start_idx:end_idx]
            logger.debug(f"Index window slicing: n={n}, start_idx={start_idx}, end_idx={end_idx}, rows={len(df_sel)}")
        else:
            # no restriction → entire series
            df_sel = df

        if df_sel.empty:
            raise ValueError("No data available in the specified window.")

        # 2) Calculate intercept
        intercept = float(getattr(df_sel["force"], method)())

        # 3) Apply to df_edited
        self.apply_force_intercept(intercept)
        return intercept

    def calculate_force_integral(self) -> None:
        """
        Calculates the time integral of the force measurements (only positive values)
        and stores the result in optional metadata.
        """
        df = self.df_edited
        integral = df['force_cent'].sum() * (1.0 / self.speed)

        # store directly in optional_metadata
        self._optional_metadata.update({
            'integral': integral,
            'integral_unit': f"{self.unit}·s"
        })
        logger.info(f"calculate_force_integral successful: integral={integral:.3f} {self.unit}·s")

    def calculate_release_force(
        self,
        min_force: float = 1,
        window_sec: int = 5,
        distance_to_end_sec: int = 3
    ) -> Optional[float]:
        """
        Calculates the mean release force from the force data within a specified
        time window before the end of the measurement.

        Parameters
        ----------
        min_force : float, optional
            Minimum force threshold (default 1).
        window_sec : int, optional
            Duration of the averaging window in seconds (default 5).
        distance_to_end_sec : int, optional
            Seconds from the end to start of the window (default 3).

        Returns
        -------
        float
            Mean release force.
        Raises
        ------
        ValueError
            If the selected window contains no data.
        """
        try:
            force = self.df['force']
            window = self.speed * window_sec
            distance = self.speed * distance_to_end_sec

            f = force[force > min_force].copy()
            f = f.iloc[-(window + distance):-distance]

            if f.empty:
                raise ValueError(
                    f"No force values in the specified window: "
                    f"min_force={min_force}, window_sec={window_sec}, "
                    f"distance_to_end_sec={distance_to_end_sec}"
                )

            release = float(f.mean())

            self._optional_metadata['release'] = release
            logger.info(f"calculate_release_force successful: release={release:.3f} {self.unit}")
            return release
        except Exception as e:
            logger.error(
                f"Failed to calculate release force for measurement "
                f"'{self.measurement_name}': {e}"
            )
            raise

    def plot_force_vs_time(self):
        """
        Plots force vs time with optional max and release markers.
        """
        try:
            fig = plot_measurement.plot_force_vs_time(
                df=self.df,
                sensor_id=self.sensor_id,
                measurement_id=self.measurement_id,
                max_index=self.force_metadata.get("max_index"),
                max_force=self.force_metadata.get("max_force"),
                release=self.optional_metadata.get('release')
            )
            self.PLOT_MANAGER.save_plot(
                fig,
                filename=slugify(f"f_vs_t_{self.sensor_id}_ID_{self.measurement_id}", separator="_"),
                subdir="force_vs_time"
            )
            logger.info(f"plot_force_vs_time for measurement '{self}'.")
        except Exception as e:
            logger.error(f"Failed to plot_force_vs_time for measurement '{self}': {e}")

    def plot_force_integral(self) -> None:
        """
        Creates and saves the integral plot (raw data + force_cent).
        """
        # ensure that integral has been calculated
        if 'integral' not in self._optional_metadata:
            raise RuntimeError("Call calculate_force_integral() before plotting.")
        try:
            fig = plot_measurement.plot_force_integral(
                df=self.df_edited,
                sensor_id=self.sensor_id,
                measurement_id=self.measurement_id,
                integral=self._optional_metadata['integral'],
                integral_unit=self._optional_metadata['integral_unit']
            )
            filename = slugify(f"force_int_{self.sensor_id}_ID_{self.measurement_id}")
            self.PLOT_MANAGER.save_plot(fig, filename, subdir="force_integrals")
            logger.info(f"plot_force_integral for measurement '{self}'.")
        except Exception as e:
            logger.error(f"Failed to plot_force_integral for measurement '{self}': {e}")
