# fuentes/ — Información fuente original

Aquí va **todo lo descargado tal cual**: PDFs, capturas, transcripciones crudas.
Es la evidencia de la que sale todo lo que publica la web.

## Reglas

1. **Nunca se edita un archivo descargado.** Si cambia la fuente, se descarga una versión nueva con otra fecha en el nombre.
2. **Todo archivo se registra en el `fuentes.yaml` de su carpeta**, con la URL de origen, la fecha de descarga y el hash SHA-256.
3. Los nombres de archivo van en minúsculas, con guiones y fecha: `plan-de-trabajo_2026-11-14.pdf`.
4. Si una fuente no se puede descargar (por ejemplo, un video), se guarda el enlace en `fuentes.yaml` y, si se puede, una transcripción o captura.

## Estructura

```
fuentes/
├── nacional/                      # aplica a todas las ciudades
│   └── (COOTAD, calendario CNE, reglamento de debates...)
└── ciudades/
    └── <ciudad>/                  # quito, guayaquil, cuenca...
        ├── cne/                   # lista oficial de candidatos, resoluciones
        ├── debate/                # video/transcripción del debate
        └── candidatos/
            └── <slug-candidato>/
                ├── fuentes.yaml
                ├── plan-de-trabajo_AAAA-MM-DD.pdf
                └── foto_AAAA-MM-DD.jpg
```

## Formato de `fuentes.yaml`

```yaml
- archivo: plan-de-trabajo_2026-11-14.pdf
  tipo: plan_trabajo          # plan_trabajo | foto | lista_oficial | debate | articulo | otro
  url: https://...
  descargado: 2026-11-14
  sha256: <hash>
  notas: ""
```
