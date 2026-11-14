# Termómetro de Alcaldías — comandos principales
# Uso: make <objetivo> [CIUDAD=quito]

PY      := pipeline/.venv/bin
CIUDAD  ?= quito
DATOS_WEB := web/src/lib/server/datos.gen.json

.PHONY: ayuda setup test validar validar-produccion schema datos web build

ayuda:
	@echo "setup               Instala dependencias (pipeline + web)"
	@echo "test                Tests del pipeline y de la web"
	@echo "validar             Valida datos/ (modo desarrollo)"
	@echo "validar-produccion  Valida datos/ con reglas de publicación (sin mocks)"
	@echo "schema              Regenera JSON Schema + tipos TypeScript desde los modelos"
	@echo "web                 Servidor de desarrollo de la web"
	@echo "build               Build estático de PRODUCCIÓN (falla si hay mocks activos)"

setup:
	python3 -m venv pipeline/.venv
	$(PY)/pip install -q -e 'pipeline[dev]'
	cd web && npm install

test:
	$(PY)/pytest -q pipeline
	cd web && npm test

validar:
	$(PY)/termometro validar

validar-produccion:
	$(PY)/termometro validar --produccion

schema:
	$(PY)/termometro schema --out datos/schema.json
	cd web && npm run tipos

datos:
	$(PY)/termometro exportar --out $(DATOS_WEB)

web: datos
	cd web && npm run dev

build:
	$(PY)/termometro exportar --produccion --out $(DATOS_WEB)
	cd web && npm run build
