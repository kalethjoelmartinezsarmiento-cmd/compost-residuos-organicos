# Notebooks del proyecto de compostaje

Esta carpeta contiene notebooks para que cada integrante pueda ejecutar su parte de forma visual en Visual Studio Code.

## Distribución

1. `01_persona_1_datos.ipynb`: revisión y documentación de datos.
2. `02_persona_2_funciones_modelo.ipynb`: funciones del modelo matemático.
3. `03_persona_3_pandas.ipynb`: procesamiento con pandas.
4. `04_persona_4_condicionales.ipynb`: condicionales y clasificaciones.
5. `05_persona_5_pruebas_validacion.ipynb`: pruebas y validación.

## Requisitos en Visual Studio Code

Instalar las extensiones:

- Python, de Microsoft.
- Jupyter, de Microsoft.

Luego abrir cada archivo `.ipynb` y seleccionar el intérprete de Python del proyecto.

## Flujo sugerido por persona

Cada persona debe crear su propia rama, ejecutar su notebook, guardar los archivos generados y hacer commit.

Ejemplo:

```powershell
git checkout main
git pull origin main
git checkout -b feature/persona-1-datos
```

Después de ejecutar el notebook:

```powershell
git status
git add .
git commit -m "mensaje del aporte"
git push -u origin nombre-de-la-rama
```
