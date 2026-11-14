# Plan de ejecución

> Complementa a [PLAN.md](PLAN.md) (el *qué*). Este archivo es el *cómo y en qué orden*.
> Principio: **construir todo con mocks y conectar la IA real al final.**

## Estrategia

```
     Contrato de datos (schemas)  ←── todo depende de esto
          │
   ┌──────┴───────────┐
   ▼                  ▼
 Web con          Pipeline con
 datos mock       IA mock (LLM_MODE=mock)
   │                  │
   └──────┬───────────┘
          ▼
   Conectar IA real (LLM_MODE=real)  →  datos reales  →  la web no cambia
```

- **El contrato de datos es la pieza clave.** La web y el pipeline solo hablan a través de los archivos de `datos/`. Si el mock respeta el schema, cambiar a datos reales no toca la web.
- **Los mocks usan una ciudad ficticia, `demo`, con candidatos inventados** ("Candidata A", "Candidato B"…). **Nunca se inventan propuestas atribuidas a candidatos reales**: un screenshot de un mock con el nombre de un candidato real circulando por WhatsApp sería un desastre. Esto además prueba de paso que la web ya funciona con varias ciudades.
- **Hay una protección en el build:** si una ciudad activa en producción tiene datos con `es_mock: true`, el build falla.
- **Las fuentes reales se descargan en paralelo desde el día 1**, porque son el mayor riesgo y no dependen de código.

---

## Fases

### F0 ✅ · Setup del repositorio
- [x] `git init`, `.gitignore` (`.env`, `node_modules`, `pipeline/.cache`, `pipeline/logs` crudos)
- [x] `web/`: proyecto SvelteKit con `adapter-static`, Tailwind y TypeScript
- [x] `pipeline/`: proyecto Python (venv + pip), Pydantic, pytest
- [x] `Makefile` en la raíz con `make web`, `make pipeline CIUDAD=x`, `make test` y `make build`
- [x] `.env.example` con `LLM_MODE=mock` y las claves vacías

✅ **Listo cuando:** `make test` y `make web` corren sin errores.

### F1 ✅ · Contrato de datos
- [x] Modelos Pydantic: `Ciudad`, `Tema`, `Enfoque`, `Candidato`, `Propuesta`, `Rubrica`, `VotoJurado`, `Consenso`, `Fuente`
- [x] Exportar JSON Schema y generar los tipos TypeScript para la web desde ese schema (una sola fuente de verdad)
- [x] `datos/temas.yaml` **real**: los 12 temas, con íconos y descripciones
- [x] `pipeline/rubrica.md` **real**: criterios del termómetro con ejemplos de sí y no
- [x] Validador: `make validar` revisa todo `datos/` contra el schema

✅ **Listo cuando:** existe un YAML de ejemplo que valida, y otro roto que falla con un error claro.

### F2 ✅ · Datos mock (ciudad `demo`)
- [x] `datos/ciudades/demo/` con 6 candidatos ficticios, marcados con `es_mock: true`
- [x] Variedad a propósito para probar la UI:
  - un candidato muy concreto (termómetro alto)
  - uno vago (termómetro bajo)
  - uno con promesas fuera de la competencia municipal
  - uno sin propuestas en algunos temas
  - dos casi empatados (para probar el "empate técnico")
  - votos de jurado con 3/3, 2/3 y un modelo caído
- [x] `enfoques.yaml` mock: 2 a 4 enfoques por tema

✅ **Listo cuando:** `make validar` pasa con la ciudad `demo`.

### F3 · Web (con datos mock)
Orden por valor:
1. [x] Layout base, home y selector de ciudad (solo ciudades activas), con orden aleatorio de candidatos
2. [x] **Ficha de candidato**: perfil, propuestas por tema, cita con enlace al PDF y página, y badge "3 de 3 IA coinciden"
3. [x] **Componente termómetro**: global y por tema, con desglose y alertas de competencia municipal
4. [x] **Comparador por tema**
5. [x] **Flujo "Lo que me importa"**:
   - [x] `lib/afinidad.ts` con **tests unitarios** (pesos, empates, candidato sin el tema, usuario sin enfoques)
   - [x] Paso 1: tarjetas seleccionables con orden de prioridad y reordenamiento con botones ↑↓ (más accesible que arrastrar en móvil)
   - [x] Paso 2: enfoques por tema
   - [x] Paso 3: ranking animado con el "por qué" desplegable y el empate técnico
   - [x] Estado en la URL para compartir el resultado (sin datos personales)
6. [x] Página de metodología: rúbrica, algoritmo, roles de cada IA y métricas
7. [ ] SEO, imágenes OG para compartir por WhatsApp y accesibilidad (teclado, contraste, lectores de pantalla)

✅ **Listo cuando:** la ciudad `demo` se puede recorrer entera en el celular y el build estático funciona.

### F4 · Pipeline (con IA mock)
- [ ] Interfaz `LLMProvider` con las implementaciones `MockProvider` (respuestas fijas desde `pipeline/fixtures/`), `ClaudeProvider`, `OpenAIProvider` y `GeminiProvider`. Los tres reales quedan como esqueleto.
- [ ] `LLM_MODE=mock|real` elige el proveedor
- [ ] Pasos implementados y probados con el mock:
  - [ ] [0] PDF → texto por página (más OCR de respaldo)
  - [ ] [1] Extracción
  - [ ] [2] **Verificación de citas** (lógica real, sin IA). Los fixtures incluyen a propósito una cita inventada para comprobar que se descarta.
  - [ ] [3] Auditoría de cobertura
  - [ ] [4] Jurado anonimizado (3 proveedores en paralelo)
  - [ ] [5] Consenso por mayoría, kappa de Fleiss y cola de revisión
  - [ ] [6] Enfoques
  - [ ] [7] Auditoría de neutralidad
  - [ ] [8] Exportación a `datos/` (valida contra el schema)
- [ ] Caché por hash, bitácora de llamadas y reporte de calidad
- [ ] **Herramienta de revisión humana**: CLI simple para aprobar, corregir o descartar los elementos de la cola
- [ ] Test end-to-end: un **plan de trabajo ficticio en PDF** → pipeline mock → `datos/ciudades/demo/` → build de la web

✅ **Listo cuando:** un solo comando lleva de un PDF ficticio a la web funcionando, sin ninguna API real.

### F5 · Fuentes reales (en paralelo desde el día 1)
- [x] Lista oficial de candidatos de Quito en el CNE: confirmar nombres, listas y estado de calificación
- [x] Los 10 planes de trabajo en PDF, en `fuentes/ciudades/quito/candidatos/<slug>/` (3 son escaneos: OCR pendiente)
- [x] Fotos oficiales (CNE o fuente pública, con la fuente registrada) — miniaturas
- [x] COOTAD (art. 55 y relacionados) en `fuentes/nacional/` (versión AME, vigente a RO 584 de jun 2024)
- [ ] Trayectoria básica de cada candidato con fuentes
- [x] `fuentes.yaml` con URL, fecha y sha256 en cada carpeta

✅ **Listo cuando:** los 10 planes están descargados y registrados, o hay un "no disponible" documentado.

### F6 · IA real 🔑 (requiere las 3 claves de API)
- [ ] Implementar los 3 proveedores reales con salida estructurada
- [ ] **Piloto con 1 candidato**: medir costo, tiempo y kappa por criterio
- [ ] Ajustar la rúbrica y los prompts si el kappa es bajo, y volver a correr el piloto
- [ ] Correr el pipeline con los 10 candidatos de Quito
- [ ] Revisión humana de la cola (🔴, 🟡 y 10% aleatorio de ✅)
- [ ] Activar Quito en `ciudades.yaml` y desactivar `demo` en producción

✅ **Listo cuando:** `datos/ciudades/quito/` valida, no tiene ningún `es_mock`, la cola de revisión está vacía y el reporte de calidad está publicado.

### F7 · Lanzamiento
- [ ] QA en celulares reales (Android de gama baja incluido)
- [ ] Deploy en Cloudflare Pages o GitHub Pages, con dominio
- [ ] Revisión final de neutralidad por una persona externa al proyecto
- [ ] Kit de difusión: mensaje para WhatsApp, imagen OG y post para redes

### F8 · Debate (22 nov)
- [ ] Grabar y transcribir el debate
- [ ] Correr el pipeline del debate (plan frente a lo dicho)
- [ ] Publicar la actualización (23–24 nov)

### F9 · Congelamiento (26 nov)
- [ ] Último deploy y congelar el contenido antes del silencio electoral
- [ ] Etiqueta `v-quito-2026-final` en el repositorio

---

## Calendario

| Día | Track A: código | Track B: fuentes |
|---|---|---|
| **Vie 14** | F0 Setup + F1 Contrato | F5: lista oficial del CNE y planes de trabajo |
| **Sáb 15** | F2 Mocks + F3 (fichas, termómetro, comparador) | F5: fotos, COOTAD, trayectorias |
| **Dom 16** | F3 flujo visual + metodología | F5: cerrar los faltantes |
| **Lun 17** | F4 pipeline con mocks, end-to-end | (conseguir las claves de API) |
| **Mar 18** | **F6 IA real**: piloto → 10 candidatos → revisión humana | |
| **Mié 19** | F6 terminar la revisión + F7 🚀 **Lanzamiento** | |
| 20–21 | Ajustes según el feedback, comparador directo | |
| **Dom 22** | F8: debate | |
| 23–24 | F8: publicar plan frente a debate | |
| **Jue 26** | F9 ❄️ Congelamiento | |

## Plan B si el tiempo no alcanza

Se recorta en este orden, de lo primero a lo último que se sacrifica:
1. Comparador directo de 2 o 3 candidatos (pasa después del lanzamiento)
2. Auditoría de neutralidad automática (queda solo la revisión humana)
3. Auditoría de cobertura (queda solo la revisión humana)
4. Jurado de 3 IA → jurado de 2

**No se recorta nunca:** la verificación de citas, la revisión humana y la neutralidad de la estructura.

## Interruptores

| Variable | Valores | Efecto |
|---|---|---|
| `LLM_MODE` | `mock` / `real` | Proveedor de IA del pipeline |
| `ciudades.yaml → activa` | `true` / `false` | Qué ciudades publica la web |
| `es_mock` en los datos | `true` | El build de producción falla si una ciudad activa lo tiene |
