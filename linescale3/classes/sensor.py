from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
import pandas as pd

from .base_class import BaseClass
from .measurement import Measurement

from kj_logger import get_logger
logger = get_logger(__name__)


class Sensor(BaseClass):
    """
    Repräsentiert einen einzelnen Sensor mit mehreren Messungen.

    Attributes
    ----------
    name : str
        Sensor-Kennung (z. B. MAC-Adresse).
    path : Path
        Verzeichnis des Sensors, in dem Messdateien liegen.
    measurements : List[Measurement]
        Liste aller Measurement-Objekte dieses Sensors.
    measurement_files : List[str]
        Dateinamen der CSV-Messungen.
    measurement_names : List[str]
        Kurzbezeichnungen der Messungen.
    measurements_count : int
        Anzahl der geladenen Messungen.

    Properties
    ----------
    df_list : List[pd.DataFrame]
        Liste der DataFrames einzelner Messungen.
    df : pd.DataFrame
        Kombinierter DataFrame aller Messungen.
    metadata_df : pd.DataFrame
        DataFrame der Metadaten aller Messungen.
    """

    def __init__(self, name: str, path: Path) -> None:
        super().__init__()
        self.name: str = name
        self.path: Path = path
        self.measurement_files: List[str] = []
        self.measurement_names: List[str] = []
        self.measurements: List[Measurement] = []
        self.measurements_count: int = 0
        self._df_list: Optional[List[pd.DataFrame]] = None
        self._df: Optional[pd.DataFrame] = None
        self._metadata_df: Optional[pd.DataFrame] = None

        try:
            csv_files = [f for f in self.path.glob("**/*.CSV") if f.is_file()]
            for csv_file in csv_files:
                self.measurement_files.append(csv_file.name)
                meas_name = csv_file.stem
                self.measurement_names.append(meas_name)
                inst = Measurement.read_csv(meas_name, csv_file)
                if inst is not None:
                    self.measurements.append(inst)
            self.measurements_count = len(self.measurement_files)
        except Exception as e:
            logger.error(f"Sensor '{self.name}' setup failed: {e}")
            raise

    def __repr__(self) -> str:
        """
        Detaillierte Repräsentation des Sensor-Objekts.
        """
        return (
            f"<Sensor '{self.name}'>\n"
            f"  Pfad:      {self.path}\n"
            f"  Messungen: {self.measurements_count}\n"
            f"  Dateien:   {self.measurement_files}\n"
        )

    def __str__(self) -> str:
        return f"Sensor: '{self.name}' mit {self.measurements_count} Messungen"

    def __getattr__(self, name: str) -> Any:
        """
        Hebt Methodenaufrufe automatisch auf alle Measurement-Instanzen hoch.
        Rückgabewerte werden nur weitergegeben, wenn sie nicht None sind.
        """
        if hasattr(Measurement, name) and callable(getattr(Measurement, name)):
            def _batch(*args: Any, **kwargs: Any) -> Optional[List[Any]]:
                results: List[Any] = []
                any_value = False
                for m in self.measurements:
                    res = getattr(m, name)(*args, **kwargs)
                    if res is not None:
                        any_value = True
                        results.append(res)
                return results if any_value else None

            return _batch
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    @property
    def df_list(self) -> List[pd.DataFrame]:
        """
        DataFrames aller Messungen als Liste.
        """
        if self._df_list is None:
            self._df_list = [m.df for m in self.measurements]
        return self._df_list

    @property
    def df(self) -> pd.DataFrame:
        """
        Kombinierter DataFrame aller Messungen.
        """
        if self._df is None:
            try:
                self._df = pd.concat(self.df_list, ignore_index=True)
            except Exception as e:
                logger.error(f"Sensor '{self.name}': df concat failed: {e}")
                raise
        return self._df

    @df.setter
    def df(self, df: pd.DataFrame) -> None:
        """
        Setzt den kombinierten DataFrame manuell.
        """
        self._df = df

    @property
    def metadata_df(self) -> pd.DataFrame:
        """
        DataFrame mit Metadaten aller Messungen.
        """
        if self._metadata_df is None:
            records = [m.full_metadata for m in self.measurements]
            self._metadata_df = pd.DataFrame.from_records(records)
        return self._metadata_df

    # @metadata_df.setter
    # def metadata_df(self, df: pd.DataFrame) -> None:
    #     """
    #     Setzt den Metadaten-DataFrame manuell.
    #     """
    #     self._metadata_df = df
