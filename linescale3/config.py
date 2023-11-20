from pathlib import Path
from typing import Optional

from kj_core.core_config import CoreConfig


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

    def __init__(self, working_directory: Optional[str] = None, log_level: Optional[str] = None):
        """
        Initializes the configuration settings, building upon the core configuration.

        """
        super().__init__(working_directory, log_level)

        # Dataframe column names for measurements and metadata
        self.df_cols = ['id', 'datetime', 'sec_since_start', 'force', 'sensor_id', 'measurement_id', 'speed']
        self.metadata_cols = ['measurement_name', 'sensor_id', 'datetime', 'measurement_id', 'unit', 'mode', 'rel_zero',
                              'speed', 'trig', 'stop', 'pre', 'catch', 'total', 'timing_correction_factor']
        self.time_metadata_cols = ['datetime_start', 'datetime_end', 'duration', 'length']
        self.force_metadata_cols = ['max', 'mean', 'median', 'min', 'release']
