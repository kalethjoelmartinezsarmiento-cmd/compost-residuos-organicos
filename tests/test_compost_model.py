import pandas as pd
import pytest

from src.compost_model import (
    calculate_derivative,
    classify_residue_status,
    normalize_humidity,
    prepare_sensor_data,
    run_simulation,
)


def test_normalize_humidity_with_percentage_values_should_return_fraction_values():
    humidity = pd.Series([80, 90, 100])

    result = normalize_humidity(humidity)

    assert result.tolist() == [0.8, 0.9, 1.0]


def test_calculate_derivative_with_valid_values_should_return_negative_value():
    result = calculate_derivative(residue_kg=10, humidity=0.8, temperature=20, k=0.0003)

    assert result == pytest.approx(-0.048)


def test_classify_residue_status_with_percentages_should_return_expected_status():
    assert classify_residue_status(80) == "Alto"
    assert classify_residue_status(50) == "Medio"
    assert classify_residue_status(20) == "Bajo"
    assert classify_residue_status(10) == "Muy bajo"


def test_prepare_sensor_data_with_unsorted_dates_should_sort_and_calculate_time():
    sensor_df = pd.DataFrame(
        {
            "Fecha_Hora": ["2026-05-16 01:00:00", "2026-05-16 00:00:00"],
            "Temp_Compost": [20, 18],
            "Humedad_Compost": [80, 90],
        }
    )

    result = prepare_sensor_data(sensor_df)

    assert result["Fecha_Hora"].iloc[0] == pd.Timestamp("2026-05-16 00:00:00")
    assert result["tiempo_horas"].iloc[-1] == pytest.approx(1.0)


def test_run_simulation_with_five_people_should_generate_decreasing_residue_values():
    sensor_df = pd.DataFrame(
        {
            "Fecha_Hora": ["2026-05-16 00:00:00", "2026-05-16 01:00:00"],
            "Temp_Compost": [20, 20],
            "Humedad_Compost": [80, 80],
        }
    )
    people_df = pd.DataFrame(
        {
            "persona": ["A", "B", "C", "D", "E"],
            "residuo_inicial_kg": [10, 11, 12, 13, 14],
            "k_descomposicion": [0.0003, 0.0003, 0.0003, 0.0003, 0.0003],
        }
    )

    result = run_simulation(sensor_df, people_df)
    first_person = result[result["persona"] == "A"].sort_values("fecha_hora")

    assert len(result) == 10
    assert first_person["residuo_kg"].iloc[-1] < first_person["residuo_kg"].iloc[0]
