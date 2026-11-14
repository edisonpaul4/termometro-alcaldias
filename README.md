# Termómetro de Alcaldías — Ecuador 2026

Web estática y neutral para que votantes indecisos comparen a los candidatos a alcalde
según los temas que les importan. Arranca con **Quito**; preparada para más ciudades.

- [PLAN.md](PLAN.md): qué construimos y por qué
- [EJECUCION.md](EJECUCION.md): fases, orden y estado
- [pipeline/rubrica.md](pipeline/rubrica.md): rúbrica pública del termómetro

## Estructura

```
├── fuentes/         información original descargada (inmutable, con sha256)
├── datos/           datos procesados y revisados: lo único que lee la web
│   ├── temas.yaml   temas comunes a todas las ciudades
│   ├── ciudades.yaml
│   ├── schema.json  JSON Schema del contrato (generado)
│   └── ciudades/<ciudad>/
├── pipeline/        Python: contrato de datos (Pydantic), validación, pipeline multi-IA
└── web/             SvelteKit estático (adapter-static + Tailwind)
```

## Contrato de datos

`pipeline/termometro/modelos.py` es la **única fuente de verdad** del formato de `datos/`.
`make schema` genera `datos/schema.json` y, desde ese schema, los tipos TypeScript de la web
(`web/src/lib/contrato.gen.ts`).

## Comandos

```bash
make setup               # instala dependencias
make test                # tests del pipeline y de la web
make validar             # valida datos/ (desarrollo)
make validar-produccion  # reglas de publicación: sin mocks, lista verificada
make schema              # regenera schema + tipos TS tras cambiar los modelos
make web                 # servidor de desarrollo
make build               # build estático de producción
```

Requisitos: Python ≥ 3.12, Node ≥ 22, `pdftotext` (poppler).

## Licencia

GPL-3.0
