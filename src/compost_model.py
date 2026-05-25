from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SENSOR_REQUIRED_COLUMNS = {
    "Fecha_Hora",
    "Temp_Compost",
    "Humedad_Compost",
}

PERSON_REQUIRED_COLUMNS = {
    "persona",
    "residuo_inicial_kg",
    "k_descomposicion",
}


def load_sensor_data(path: str | Path) -> pd.DataFrame:
    """Carga el archivo Excel con los datos del compost."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de sensores: {path}")

    return pd.read_excel(path)


def load_people_data(path: str | Path) -> pd.DataFrame:
    """Carga la configuración de las cinco personas desde CSV."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de personas: {path}")

    return pd.read_csv(path)


def validate_columns(df: pd.DataFrame, required_columns: Iterable[str], dataset_name: str) -> None:
    """Valida que un DataFrame tenga las columnas requeridas."""
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"El dataset {dataset_name} no tiene estas columnas requeridas: "
            f"{sorted(missing_columns)}"
        )


def normalize_humidity(humidity: pd.Series) -> pd.Series:
    """
    Normaliza la humedad a un valor entre 0 y 1.

    Si la humedad viene en porcentaje, por ejemplo 89, se convierte a 0.89.
    Si ya viene como fracción, por ejemplo 0.89, se conserva.
    """
    humidity = pd.to_numeric(humidity, errors="coerce")

    if humidity.dropna().median() > 1:
        humidity = humidity / 100

    return humidity.clip(lower=0, upper=1)


def positive_temperature_factor(temperature: pd.Series) -> pd.Series:
    """
    Devuelve la temperatura útil para la ecuación.

    Si la temperatura es menor o igual a cero, se toma como 0 para evitar
    una descomposición negativa o incoherente en este modelo básico.
    """
    temperature = pd.to_numeric(temperature, errors="coerce")
    return temperature.where(temperature > 0, 0)


def prepare_sensor_data(sensor_df: pd.DataFrame) -> pd.DataFrame:
    """Limpia, ordena y prepara los datos del compost para la simulación."""
    validate_columns(sensor_df, SENSOR_REQUIRED_COLUMNS, "sensores")

    prepared = sensor_df.copy()
    prepared["Fecha_Hora"] = pd.to_datetime(prepared["Fecha_Hora"], errors="coerce")
    prepared["Temp_Compost"] = positive_temperature_factor(prepared["Temp_Compost"])
    prepared["Humedad_Compost"] = normalize_humidity(prepared["Humedad_Compost"])

    prepared = prepared.dropna(subset=["Fecha_Hora", "Temp_Compost", "Humedad_Compost"])
    prepared = prepared.sort_values("Fecha_Hora").reset_index(drop=True)

    if prepared.empty:
        raise ValueError("No hay datos válidos para ejecutar la simulación.")

    first_datetime = prepared["Fecha_Hora"].iloc[0]
    prepared["tiempo_horas"] = (
        prepared["Fecha_Hora"].sub(first_datetime).dt.total_seconds() / 3600
    )
    prepared["dt_horas"] = prepared["tiempo_horas"].diff().fillna(0)
    prepared["dt_horas"] = prepared["dt_horas"].where(prepared["dt_horas"] >= 0, 0)

    return prepared


def validate_people_data(people_df: pd.DataFrame) -> pd.DataFrame:
    """Valida datos de personas y conserva únicamente registros útiles."""
    validate_columns(people_df, PERSON_REQUIRED_COLUMNS, "personas")

    people = people_df.copy()
    people["residuo_inicial_kg"] = pd.to_numeric(people["residuo_inicial_kg"], errors="coerce")
    people["k_descomposicion"] = pd.to_numeric(people["k_descomposicion"], errors="coerce")
    people = people.dropna(subset=["persona", "residuo_inicial_kg", "k_descomposicion"])

    if len(people) < 5:
        raise ValueError("Se requieren mínimo cinco personas para el ejercicio.")

    if (people["residuo_inicial_kg"] <= 0).any():
        raise ValueError("El residuo inicial debe ser mayor que cero.")

    if (people["k_descomposicion"] <= 0).any():
        raise ValueError("La constante k debe ser mayor que cero.")

    return people.head(5).reset_index(drop=True)


def calculate_derivative(residue_kg: float, humidity: float, temperature: float, k: float) -> float:
    """Calcula dR/dt = -k * H(t) * T(t) * R(t)."""
    if residue_kg < 0:
        raise ValueError("El residuo no puede ser negativo.")

    if k <= 0:
        raise ValueError("La constante k debe ser mayor que cero.")

    if humidity < 0 or humidity > 1:
        raise ValueError("La humedad debe estar normalizada entre 0 y 1.")

    if temperature <= 0:
        return 0.0

    return -k * humidity * temperature * residue_kg


def classify_residue_status(percent_remaining: float) -> str:
    """Clasifica el estado del residuo restante usando condicionales."""
    if percent_remaining >= 70:
        return "Alto"
    if percent_remaining >= 40:
        return "Medio"
    if percent_remaining >= 15:
        return "Bajo"
    return "Muy bajo"


def simulate_person(sensor_df: pd.DataFrame, person: pd.Series) -> pd.DataFrame:
    """Ejecuta la simulación para una persona."""
    residue_initial = float(person["residuo_inicial_kg"])
    k = float(person["k_descomposicion"])
    person_name = str(person["persona"])

    residue = residue_initial
    records = []

    for row in sensor_df.itertuples(index=False):
        humidity = float(row.Humedad_Compost)
        temperature = float(row.Temp_Compost)
        dt_hours = float(row.dt_horas)

        derivative = calculate_derivative(residue, humidity, temperature, k)
        residue = max(residue + derivative * dt_hours, 0)
        percent_remaining = (residue / residue_initial) * 100

        records.append(
            {
                "persona": person_name,
                "fecha_hora": row.Fecha_Hora,
                "tiempo_horas": row.tiempo_horas,
                "humedad": humidity,
                "temperatura": temperature,
                "residuo_kg": residue,
                "dR_dt": derivative,
                "porcentaje_restante": percent_remaining,
                "estado": classify_residue_status(percent_remaining),
            }
        )

    return pd.DataFrame(records)


def run_simulation(sensor_df: pd.DataFrame, people_df: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta la simulación completa para las cinco personas."""
    prepared_sensor = prepare_sensor_data(sensor_df)
    people = validate_people_data(people_df)

    simulations = [simulate_person(prepared_sensor, person) for _, person in people.iterrows()]
    return pd.concat(simulations, ignore_index=True)


def build_summary(results_df: pd.DataFrame) -> pd.DataFrame:
    """Construye un resumen final por persona."""
    summary = (
        results_df.sort_values("fecha_hora")
        .groupby("persona", as_index=False)
        .tail(1)
        .loc[
            :,
            [
                "persona",
                "fecha_hora",
                "residuo_kg",
                "porcentaje_restante",
                "estado",
            ],
        ]
        .sort_values("persona")
        .reset_index(drop=True)
    )

    summary["residuo_kg"] = summary["residuo_kg"].round(4)
    summary["porcentaje_restante"] = summary["porcentaje_restante"].round(2)
    return summary


def save_outputs(results_df: pd.DataFrame, output_dir: str | Path) -> None:
    """Guarda resultados, resumen y gráfica."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "resultados_compost.csv"
    summary_path = output_dir / "resumen_personas.csv"
    chart_path = output_dir / "grafica_residuos.png"

    results_df.to_csv(results_path, index=False, encoding="utf-8-sig")
    build_summary(results_df).to_csv(summary_path, index=False, encoding="utf-8-sig")
    plot_results(results_df, chart_path)


def plot_results(results_df: pd.DataFrame, chart_path: str | Path) -> None:
    """Genera una gráfica de residuos restantes por persona."""
    chart_path = Path(chart_path)
    plt.figure(figsize=(11, 6))

    for person, group in results_df.groupby("persona"):
        ordered = group.sort_values("tiempo_horas")
        plt.plot(ordered["tiempo_horas"], ordered["residuo_kg"], label=person)

    plt.title("Descomposición de residuos orgánicos por persona")
    plt.xlabel("Tiempo transcurrido (horas)")
    plt.ylabel("Residuo restante (kg)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()


def run_from_files(sensor_path: str | Path, people_path: str | Path, output_dir: str | Path) -> pd.DataFrame:
    """Punto de entrada para ejecutar el proceso desde archivos."""
    sensor_df = load_sensor_data(sensor_path)
    people_df = load_people_data(people_path)
    results_df = run_simulation(sensor_df, people_df)
    save_outputs(results_df, output_dir)
    return results_df
