import linescale3

from kj_core import get_logger

logger = get_logger(__name__)


class BaseClass:
    def __init__(self):
        managers_to_check = [linescale3.CONFIG, linescale3.PLOT_MANAGER]

        if any(manager is None for manager in managers_to_check):
            raise ValueError(f"The package has not been properly initialized. Please call the setup function first.")

        else:
            self.CONFIG = linescale3.CONFIG
            self.PLOT_MANAGER = linescale3.PLOT_MANAGER
