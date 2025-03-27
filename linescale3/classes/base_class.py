from kj_logger import get_logger
import linescale3

logger = get_logger(__name__)


class BaseClass():
    __abstract__ = True
    _config = None
    _plot_manager = None

    def __init__(self):
        super().__init__()

    @property
    def CONFIG(self):
        if self._config is None:
            self._config = linescale3.CONFIG
        return self._config  # TODO: Try to delete

    @property
    def PLOT_MANAGER(self):
        if self._plot_manager is None:
            self._plot_manager = linescale3.PLOT_MANAGER
        return self._plot_manager  # TODO: Try to delete

    @classmethod
    def get_config(cls):
        return linescale3.CONFIG

    @classmethod
    def get_plot_manager(cls):
        return linescale3.PLOT_MANAGER
