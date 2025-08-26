# tests/conftest.py  (wird von PyTest automatisch geladen)
import types
import pytest
import linescale3
from linescale3.config import Config


@pytest.fixture(scope="session", autouse=True)
def ls3_test_environment(tmp_path_factory):
    """
    Session-weite Testumgebung:
    – echte Config (mit temporärem Arbeitsverzeichnis)
    – stummer Plot-Manager
    """
    # 1) temporäres Arbeitsverzeichnis für die Tests
    workdir = tmp_path_factory.mktemp("ls3_work")

    # 2) Config erzeugen und global setzen
    linescale3.CONFIG = Config(working_directory=str(workdir))

    # 3) Dummy-Plot-Manager (verhindert Dateizugriff)
    linescale3.PLOT_MANAGER = types.SimpleNamespace(
        save_plot=lambda *_, **__: None
    )

    # 4) fertig – alle Tests können jetzt darauf zugreifen
    yield
