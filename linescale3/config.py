from pathlib import Path
from typing import Optional, Dict
import json

from kj_core.core_config import CoreConfig

from kj_logger import get_logger

logger = get_logger(__name__)

class Config(CoreConfig):
    """
    Configuration class for the package, extending the core configuration.
    Provides package-specific settings and default values.
    """
    # Override default working directory specific
    package_name = "linescale3"
    package_name_short = "ls3"
    # Override default working directory specific
    default_working_directory = r"C:\kyellsen\006_Packages\linescale3\working_directory_ls3"

    def __init__(self, working_directory: Optional[str] = None):
        """
        Initializes the configuration settings, building upon the core configuration.

        """
        super().__init__(f"{working_directory}/{self.package_name_short}")

        # Dataframe column names for measurements and metadata
        self.df_cols = ['id', 'datetime', 'sec_since_start', 'force', 'sensor_id', 'measurement_id', 'speed']
        self.metadata_cols = ['measurement_name', 'sensor_id', 'datetime', 'measurement_id', 'unit', 'mode', 'rel_zero',
                              'speed', 'trig', 'stop', 'pre', 'catch', 'total', 'true_speed']
        self.time_metadata_cols = ['datetime_start', 'datetime_end', 'duration', 'length']
        self.force_metadata_cols = ['max_index', 'max_force', 'mean', 'median', 'min_index', 'min_force']
        self.optional_metadata_cols = ['intercept', 'integral', 'release']
        # Path to label dictionary
        self.label_dict_path = Path(__file__).parent / "ls3_data_dict.json"
        self._label_dict = self.load_label_dict(log_on_success=False)

    def load_label_dict(self, log_on_success: bool = True) -> Dict[str, Dict[str, str]]:
        """
        Loads the label dictionary from JSON file.
        """
        try:
            if not self.label_dict_path.exists():
                logger.warning(f"Label dictionary not found at: {self.label_dict_path}")
                return {}

            with open(self.label_dict_path, encoding="utf-8") as f:
                data = json.load(f)

            if log_on_success:
                logger.info(f"Label dictionary loaded with {len(data)} entries.")
            return data

        except Exception as e:
            logger.error(f"Error loading label dictionary: {e}")
            return {}

    @property
    def label_dict(self) -> Dict[str, Dict[str, str]]:
        """
        Returns the currently loaded label dictionary.
        """
        return self._label_dict
