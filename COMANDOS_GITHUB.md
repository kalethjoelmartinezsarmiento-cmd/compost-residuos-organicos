# Comandos para subir el repositorio a GitHub

Este proyecto ya queda preparado como repositorio local de Git. Para publicarlo en GitHub, crea primero un repositorio vacío en GitHub con el nombre, por ejemplo:

```text
compost-residuos-organicos
```

Luego ejecuta estos comandos dentro de la carpeta del proyecto:

```bash
git remote add origin https://github.com/TU_USUARIO/compost-residuos-organicos.git
git branch -M main
git push -u origin main
```

Si usas GitHub CLI:

```bash
gh repo create compost-residuos-organicos --public --source=. --remote=origin --push
```

## Ver historial de commits

```bash
git log --oneline
```
