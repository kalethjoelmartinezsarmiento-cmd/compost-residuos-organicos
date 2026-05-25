# Modelo de descomposición de residuos orgánicos

Repositorio académico para simular la disminución de residuos orgánicos usando la ecuación diferencial:

```text
dR/dt = -k * H(t) * T(t) * R(t)
```

Donde:

- `R(t)`: cantidad de residuos orgánicos en kg.
- `k`: constante de descomposición.
- `H(t)`: humedad del compost en función del tiempo.
- `T(t)`: temperatura del compost en función del tiempo.

El proyecto usa datos de sensores del archivo `data/datos_compost.xlsx` y una tabla con cinco personas en `data/personas.csv`.

## Estructura

```text
compost-residuos-organicos/
├── data/
│   ├── datos_compost.xlsx
│   └── personas.csv
├── outputs/
├── src/
│   ├── compost_model.py
│   └── main.py
├── tests/
│   └── test_compost_model.py
├── COMANDOS_GITHUB.md
├── requirements.txt
└── README.md
```

## Cómo ejecutarlo desde Visual Studio Code

1. Abre la carpeta del proyecto en VS Code.
2. Abre una terminal integrada.
3. Crea el entorno virtual:

```bash
python -m venv .venv
```

4. Activa el entorno:

En Windows PowerShell:

```bash
.venv\Scripts\activate
```

En Git Bash o Linux/Mac:

```bash
source .venv/bin/activate
```

5. Instala dependencias:

```bash
pip install -r requirements.txt
```

6. Ejecuta el modelo:

```bash
python src/main.py
```

7. Ejecuta pruebas:

```bash
pytest
```

## Archivos generados

Al ejecutar `python src/main.py`, se crean:

- `outputs/resultados_compost.csv`: resultados detallados por persona y tiempo.
- `outputs/resumen_personas.csv`: resumen final para cada persona.
- `outputs/grafica_residuos.png`: gráfica de residuos restantes por persona.

## Fórmula implementada

El modelo resuelve la ecuación mediante aproximación de Euler:

```text
R_nuevo = R_actual + (-k * H(t) * T(t) * R_actual) * Δt
```

Se usan condicionales para validar datos, normalizar humedad y clasificar el estado del residuo según el porcentaje restante.
