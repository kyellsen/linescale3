from kj_core import get_logger
from kj_core.classes.core_base_class import CoreBaseClass

import linescale3

logger = get_logger(__name__)


class BaseClass(CoreBaseClass):
    """
    Base class built upon CoreBaseClass, using specific managers from treemotion.
    """

    def __init__(self):
        # Es wird angenommen, dass treemotion.CONFIG, usw. bereits initialisiert wurden
        # Initialisiere CoreBaseClass mit treemotion-Managern
        super().__init__(config=linescale3.CONFIG,
                         plot_manager=linescale3.PLOT_MANAGER)

