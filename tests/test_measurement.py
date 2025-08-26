# tests/test_measurement.py
import numpy as np
import pytest
from linescale3.classes.measurement import Measurement


@pytest.fixture
def simple_measurement():
    force = np.array([0.0, 0.5, 1.0, 2.0, 3.0,
                      4.0, 5.0, 2.0, 1.0, 0.5])
    return Measurement(
        measurement_name="test",
        sensor_id="S01",
        date="01\\01\\24",
        time="00:00:00",
        measurement_id=1,
        unit="kN",
        mode="TEST",
        rel_zero="0",
        speed=1,
        trig=0, stop=0, pre=0, catch=0, total=len(force),
        force=force
    )

# --------------------------------------------------------------------------- #
# 1) apply_force_intercept
# --------------------------------------------------------------------------- #
def test_apply_force_intercept(simple_measurement):
    m = simple_measurement
    intercept = 1.5
    m.apply_force_intercept(intercept)

    expected = np.clip(m.force - intercept, 0, None)
    np.testing.assert_allclose(m.df_edited["force_cent"], expected)

    assert m._force_intercept_edited == pytest.approx(intercept)


# --------------------------------------------------------------------------- #
# 2) auto_calculate_force_intercept  (Index-Fenster & Fehlervalidierung)
# --------------------------------------------------------------------------- #
def test_auto_calc_force_intercept_index(simple_measurement):
    m = simple_measurement
    # Mittelwert über alle Daten
    intercept = m.auto_calculate_force_intercept(index_window=(0.0, 1.0), method="mean")
    assert intercept == pytest.approx(m.force.mean())

    # force_cent nach Anwendung kontrollieren
    centered = np.clip(m.force - intercept, 0, None)
    np.testing.assert_allclose(m.df_edited["force_cent"], centered)


def test_auto_calc_force_intercept_error(simple_measurement):
    m = simple_measurement
    # Gleichzeitige Angabe von index_ und time_window muss ValueError werfen
    with pytest.raises(ValueError):
        m.auto_calculate_force_intercept(time_window=(0, 3), index_window=(0, 1))


# --------------------------------------------------------------------------- #
# 3) calculate_force_integral
# --------------------------------------------------------------------------- #
def test_calculate_force_integral(simple_measurement):
    m = simple_measurement
    m.apply_force_intercept(0.0)           # keine Zentrierung
    m.calculate_force_integral()

    expected = m.force.sum()               # Δt = 1 s bei speed = 1 Hz
    assert m._optional_metadata["integral"] == pytest.approx(expected)
    assert m._optional_metadata["integral_unit"] == "kN·s"


# --------------------------------------------------------------------------- #
# 4) calculate_release_force
# --------------------------------------------------------------------------- #
def test_calculate_release_force(simple_measurement):
    m = simple_measurement
    release = m.calculate_release_force(
        min_force=0.6, window_sec=3, distance_to_end_sec=1
    )

    expected = np.array([4.0, 5.0, 2.0]).mean()   # = 11/3
    assert release == pytest.approx(expected)
    assert m._optional_metadata["release"] == pytest.approx(expected)


def test_calculate_release_force_empty(simple_measurement):
    m = simple_measurement
    # distance = 0 → Slice leer → ValueError
    with pytest.raises(ValueError):
        m.calculate_release_force(
            min_force=0.6, window_sec=3, distance_to_end_sec=0
        )
