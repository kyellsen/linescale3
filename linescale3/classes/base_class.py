from kj_core import get_logger

import linescale3

logger = get_logger(__name__)


class BaseClass:
    """
    Base class built upon CoreBaseClass, using specific managers from treemotion.
    """

    def __init__(self):
        self.CONFIG = linescale3.CONFIG
        self.PLOT_MANAGER = linescale3.PLOT_MANAGER


