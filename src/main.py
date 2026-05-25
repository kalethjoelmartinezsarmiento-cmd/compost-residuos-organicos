from pathlib import Path

from compost_model import build_summary, run_from_files


BASE_DIR = Path(__file__).resolve().parent.parent
SENSOR_PATH = BASE_DIR / "data" / "datos_compost.xlsx"
PEOPLE_PATH = BASE_DIR / "data" / "personas.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def main() -> None:
    results = run_from_files(SENSOR_PATH, PEOPLE_PATH, OUTPUT_DIR)
    summary = build_summary(results)

    print("Simulación finalizada correctamente.")
    print(f"Registros generados: {len(results)}")
    print("\nResumen final por persona:")
    print(summary.to_string(index=False))
    print(f"\nArchivos guardados en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
