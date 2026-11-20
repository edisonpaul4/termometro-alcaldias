# datos/ — Datos procesados y revisados

Salida del pipeline (IA y revisiones editoriales con origen explícito). **Es lo único que lee la web.**
Todo dato aquí debe apuntar a un archivo en `fuentes/`.

```
datos/
├── temas.yaml                     # temas comunes a todas las ciudades
├── ciudades.yaml                  # registro de ciudades (activa o no)
└── ciudades/
    └── <ciudad>/
        ├── ciudad.yaml            # nombre, fechas (debate, elección), notas
        ├── enfoques.yaml          # enfoques por tema (para el flujo visual)
        └── candidatos/
            └── <slug-candidato>.yaml
```

Para agregar una ciudad nueva: crear `fuentes/ciudades/<ciudad>/` y `datos/ciudades/<ciudad>/`,
registrarla en `ciudades.yaml` y correr el pipeline. La web la toma automáticamente.
