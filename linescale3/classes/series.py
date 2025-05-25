from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
import pandas as pd

from .base_class import BaseClass
from .sensor import Sensor

from kj_logger import get_logger
logger = get_logger(__name__)


class Series(BaseClass):
    """
    Repräsentiert eine Serie von Sensoren und deren Messungen.

    Attributes
    ----------
    name : str
        Name der Serie.
    path : Path
        Basisverzeichnis für alle Sensor-Ordner.
    sensors : List[Sensor]
        Liste aller Sensor-Instanzen.
    sensor_names : List[str]
        Liste der Sensor-Kennungen.
    sensor_count : int
        Anzahl der Sensoren.

    Properties
    ----------
    df_list : List[pd.DataFrame]
        Liste aller DataFrames der Sensoren.
    df : pd.DataFrame
        Kombinierter DataFrame aller Sensoren.
    metadata_df : pd.DataFrame
        Kombinierter Metadaten-DataFrame aller Sensoren.
    """

    def __init__(self, name: str, path: str) -> None:
        super().__init__()
        self.name: str = name
        self.path: Path = Path(path)
        self.sensors: List[Sensor] = []
        self.sensor_names: List[str] = []
        self.sensor_count: int = 0
        self._df_list: Optional[List[pd.DataFrame]] = None
        self._df: Optional[pd.DataFrame] = None
        self._metadata_df: Optional[pd.DataFrame] = None

        dirs = [d for d in self.path.iterdir() if d.is_dir()]
        for d in dirs:
            mac = d.name[2:]
            sensor_id = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))
            inst = Sensor(sensor_id, d)
            self.sensors.append(inst)
            self.sensor_names.append(sensor_id)
        self.sensor_count = len(self.sensors)

    def __repr__(self) -> str:
        """
        Detaillierte Repräsentation der Series-Instanz.
        """
        return (
            f"<Series '{self.name}'>\n"
            f"  Basis-Pfad:  {self.path}\n"
            f"  Sensoren:    {self.sensor_count}\n"
            f"  IDs:         {self.sensor_names}\n"
        )

    def __str__(self) -> str:
        return f"Measurement Series: '{self.name}' mit {self.sensor_count} Sensoren"

    def __getattr__(self, name: str) -> Any:
        """
        Hebt Methodenaufrufe automatisch auf alle Sensor-Instanzen hoch.
        Sucht zuerst auf Sensor-Instanz, dann leitet Sensor hook eventuell an Measurement weiter.
        """
        # Prüfe, ob die erste Sensor-Instanz die Methode bietet
        if self.sensors:
            first = self.sensors[0]
            if hasattr(first, name) and callable(getattr(first, name)):
                def _batch(*args: Any, **kwargs: Any) -> List[Any]:
                    results: List[Any] = []
                    any_value = False
                    for s in self.sensors:
                        res = getattr(s, name)(*args, **kwargs)
                        if res is not None:
                            any_value = True
                            results.append(res)
                    return results if any_value else None
                return _batch
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    @property
    def df_list(self) -> List[pd.DataFrame]:
        """
        Liste der DataFrames aller Sensoren.
        """
        if self._df_list is None:
            self._df_list = [s.df for s in self.sensors]
        return self._df_list

    @property
    def df(self) -> pd.DataFrame:
        """
        Kombinierter DataFrame aller Sensoren.
        """
        if self._df is None:
            self._df = pd.concat(self.df_list, ignore_index=True)
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
        Kombinierter Metadaten-DataFrame aller Sensoren.
        """
        if self._metadata_df is None:
            self._metadata_df = pd.concat([s.metadata_df for s in self.sensors], ignore_index=True)
        return self._metadata_df

    def create_data_dict(self) -> Dict[str, dict]:
        """
        Loads the label dictionary from the configuration.
        """
        return self.CONFIG.load_label_dict()


