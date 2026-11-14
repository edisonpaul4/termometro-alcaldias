# Plan: web de candidatos a la Alcaldía de Quito 2026

> Estado: **borrador de planificación**, todavía sin código.
> Última actualización: 14 nov 2026

## 1. Objetivo

Una web estática, neutral y verificable para que un votante indeciso de Quito pueda **decidir su voto según los temas que le importan**, comparando lo que cada candidato propone realmente.

**Lo que aportamos frente a "Voto Informado" del CNE:**
- Propuestas ordenadas por tema y comparables lado a lado.
- **Termómetro de concreción**: qué tan específica es cada propuesta.
- **Flujo visual "¿Quién se apega a lo que me importa?"**.
- Comparación entre el plan de trabajo y lo dicho en el debate.

## 2. Contexto y fechas

| Fecha | Hito |
|---|---|
| 12 nov | Inicio de la campaña oficial |
| **22 nov** | **Debate obligatorio para la Alcaldía de Quito (CNE)** |
| **26 nov** | Fin de campaña. **Contenido congelado** |
| 27–29 nov | Silencio electoral |
| **29 nov** | **Elecciones seccionales** |

### Candidatos (10)

✅ **Verificada contra Voto Informado del CNE (14 nov 2026).** Planes de trabajo en `fuentes/`.

| Lista | Candidato | Organización | Nota |
|---|---|---|---|
| 1 | Galo Almeida Garzón | Centro Democrático | |
| 2-17-70 | Pabel Muñoz | Alianza Ciudadana | Alcalde actual, busca la reelección |
| 3 | Bernardo Jijón | Sociedad Patriótica | |
| 4 | César Díaz | Pueblo, Igualdad y Democracia | |
| 6 | Linda Romero | Partido Social Cristiano | |
| 7 | Harold Burbano | ADN | |
| 8 | Jorge Yunda | Avanza | Exalcalde 2019–2021 |
| 20 | Paúl Desamblanc | Futuro | |
| 21 | Carla Larrea | CREO | |
| 79 | Wilson Merino | Imparables | Exconcejal |

## 3. Principios de neutralidad (no negociables)

1. **Sin fuente, no se publica.** Cada dato enlaza a su origen; cada propuesta lleva cita textual y página.
2. **Misma estructura y mismo espacio** para todos los candidatos.
3. **Orden aleatorio** de los candidatos en cada visita.
4. **No opinamos sobre si una propuesta es buena o mala.** Solo medimos criterios objetivos: concreción y competencia municipal.
5. **Sin encuestas ni métricas de popularidad**, por riesgo legal y de manipulación.
6. **Metodología pública:** prompts, rúbrica y datos en un repositorio público.
7. **Privacidad:** el flujo del usuario se calcula en su navegador. No guardamos respuestas, no usamos cookies de rastreo y no hay login.
8. El resultado **nunca dice "vota por X"**. Dice "estos candidatos coinciden más con tus prioridades, y por esto".

## 4. Temas (ejes)

Lista tentativa. Se ajusta según los 4 ejes del debate del CNE y lo que realmente aparezca en los planes.

| Ícono | Tema |
|---|---|
| 🛡️ | Seguridad ciudadana |
| 🚇 | Movilidad y transporte (Metro, buses, tránsito) |
| 💧 | Agua y servicios básicos |
| ♻️ | Basura y ambiente |
| 💼 | Empleo y economía local |
| 🏪 | Espacio público y comercio autónomo |
| 🏔️ | Gestión de riesgos (El Niño, quebradas, incendios) |
| 🌾 | Parroquias rurales |
| 🏛️ | Transparencia y anticorrupción |
| 🤝 | Inclusión social (niñez, adultos mayores, discapacidad) |
| 🎭 | Cultura, turismo y patrimonio |
| 🏘️ | Vivienda y ordenamiento territorial |

## 5. Funcionalidades

| # | Funcionalidad | Prioridad | Para cuándo |
|---|---|---|---|
| F1 | Fichas de candidatos (perfil, trayectoria, propuestas por tema, fuentes) | MVP | 19 nov |
| F2 | Comparador por tema (un tema, todos los candidatos) | MVP | 19 nov |
| F3 | Termómetro de concreción | MVP | 19 nov |
| F4 | **Flujo visual "Lo que me importa"** (sección 6) | MVP | 19–20 nov |
| F5 | Comparador directo de 2 o 3 candidatos | Fase 2 | 21 nov |
| F6 | Plan frente a debate | Fase 2 | 23–24 nov |
| F7 | Página de metodología | MVP | 19 nov |

## 6. Flujo visual "¿Quién se apega a lo que me importa?"

Es la experiencia principal de la web. Pensada para el celular, se completa en unos 2 minutos y es muy visual: tarjetas grandes, íconos y poco texto.

### Paso 1: Elige tus temas
Tarjetas grandes con ícono. Se tocan para elegir **de 3 a 5 temas**. **El orden en que las tocas define la prioridad** y se ve con un número sobre cada tarjeta. También se puede reordenar arrastrando.

```
┌─────────────────────────────────┐
│  ¿Qué es lo que más te importa  │
│  para Quito? Elige de 3 a 5     │
│                                 │
│ ┌──────┐ ┌──────┐ ┌──────┐      │
│ │ 🛡️ ①│ │ 🚇 ②│ │  💧  │      │
│ │Segur.│ │Movil.│ │ Agua │      │
│ └──────┘ └──────┘ └──────┘      │
│ ┌──────┐ ┌──────┐ ┌──────┐      │
│ │  ♻️  │ │ 💼 ③│ │  🏪  │      │
│ │Basura│ │Empleo│ │Espac.│      │
│ └──────┘ └──────┘ └──────┘      │
│            [ Siguiente → ]      │
└─────────────────────────────────┘
```

### Paso 2: ¿Cómo lo resolverías? (opcional por tema)
Para cada tema elegido se muestran de 2 a 4 **enfoques** en tarjetas. Se puede elegir uno o varios, o "no estoy seguro".
Los enfoques **salen de las propuestas reales de los candidatos**, agrupadas por la IA y revisadas a mano. No son inventados.

```
┌─────────────────────────────────┐
│ 🛡️ Seguridad: ¿qué priorizas?   │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 📹 Tecnología: cámaras,     │ │
│ │    alarmas, monitoreo       │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 💡 Recuperar espacios:      │ │
│ │    luminarias, parques      │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 👮 Más control: agentes     │ │
│ │    metropolitanos           │ │
│ └─────────────────────────────┘ │
│    [ No estoy seguro ]  [ → ]   │
└─────────────────────────────────┘
```

### Paso 3: Resultado
- Ranking visual con barras de afinidad y foto de cada candidato.
- **Si la diferencia es menor a 5 puntos se muestra "empate técnico"**, para no fingir una precisión que no tenemos.
- Cada candidato se puede expandir para ver **por qué**: tema por tema, sus propuestas con la cita del plan y su termómetro.
- Botones para **compartir el resultado** como imagen o link con las selecciones en la URL (sin datos personales) y para **ver la ficha completa**.
- Aviso: "Esto es una guía basada en los planes de trabajo, no una recomendación de voto".

### Algoritmo de afinidad (transparente y explicado en Metodología)

Implementado y probado en `web/src/lib/afinidad.ts`.

- **Pesos por prioridad:** con *n* temas, el tema en la posición *i* pesa `n − i + 1` (5, 4, 3, 2, 1).
- **Solo cuentan las propuestas dentro de la competencia municipal.**
- **Puntaje de un tema:** `S = base × (0.5 + 0.5 × concreción)`. La concreción *multiplica*: proponer lo que quieres sin ningún detalle vale como máximo la mitad.
  - Si el usuario eligió un enfoque: `base` = qué parte de sus enfoques propone el candidato, y `concreción` se mide **solo sobre las propuestas de esos enfoques**.
  - Si eligió "Ni idea": `base` = cobertura del tema (hasta 3 propuestas; más cantidad no suma).
  - Si el candidato no tiene propuestas en el tema: `S = 0`.
- **Afinidad** = `Σ peso·S / Σ peso × 100%`.
- **Empate técnico** cuando la diferencia con el primero de su grupo es menor a 5 puntos (no se encadena).

### Decisiones de UX: público de Instagram y TikTok, que se aburre rápido

- **Flujo inmersivo tipo stories:** pantalla completa oscura, segmentos de progreso arriba y una decisión por pantalla.
- **Toca y avanza:** el paso 2 es de una sola elección por tema, con "👌 Todas me sirven" y "🤷 Ni idea". Botones en la zona del pulgar y una vibración sutil al tocar.
- **Pantalla "calculando" de unos 2 s:** genera suspenso y muestra el trabajo real detrás ("Leyendo 473 páginas de 10 planes…").
- **Revelación escalonada** del resultado y "¿Por qué?" a un toque.
- **Compartir:** una imagen 9:16 para Stories con **tus prioridades, nunca un ranking de candidatos**. Un ranking circularía como propaganda y chocaría con el silencio electoral.
- **Gancho en el inicio:** "¿No sabes por quién votar? Descúbrelo en 60 segundos" y un solo botón.
- **Identidad visual (v3, clara y profesional):** fondo papel cálido, tinta oscura y un único acento verde azulado. La tipografía es Bricolage Grotesque. Un degradado frío y discreto (verde azulado → azul → índigo) se usa solo en los anillos de las fotos y en los titulares.
- **Íconos:** Phosphor duotone, de un registro curado en `web/src/lib/iconos.ts`. Cada tema tiene su color y su ícono, como las historias destacadas de Instagram. El contrato exige que `icono` sea un nombre de ese registro, nunca un emoji.
- **Patrones de app:** anillos tipo historia en las fotos, fila de candidatos como barra de historias, ficha con formato de perfil (estadísticas y destacados por tema), comparador en carrusel deslizable con puntos y "¿Por qué?" en hoja inferior (bottom sheet).
- **Ningún color de partido:** los 12 tonos de los temas recorren todo el círculo cromático.
- **Se respeta `prefers-reduced-motion`.**

## 7. Termómetro de concreción

Se evalúa **cada propuesta** con una rúbrica de 4 criterios, cada uno con valor 0 o 1:

| Criterio | Pregunta | Ejemplo de "sí" |
|---|---|---|
| 🎯 Meta medible | ¿Tiene un número o resultado verificable? | "5.000 nuevas luminarias" |
| 📅 Plazo | ¿Dice cuándo? | "en los primeros 100 días" |
| 💰 Financiamiento | ¿Dice de dónde sale el dinero? | "con crédito del BID / reasignando X" |
| 🏛️ Competencia municipal | ¿Le corresponde al Municipio según el COOTAD (art. 55 y relacionados)? | Tránsito y basura sí; Policía Nacional no |

- **Concreción de una propuesta** = (meta + plazo + financiamiento) / 3.
- La **competencia municipal** no suma al puntaje: se muestra como una **alerta visible** del tipo "⚠️ Fuera de la competencia del Municipio".
- **Termómetro por tema** = promedio de concreción de las propuestas del candidato en ese tema.
- **Termómetro global** = promedio de todos sus temas.
- Visualmente es un termómetro o barra de color, siempre con el desglose a la vista: "3 de 12 propuestas tienen meta medible".

## 8. Pipeline automatizado con varias IA

Todo se procesa **antes de publicar**. La web es estática y no llama a ninguna IA en vivo.

### Idea central: separar poderes

**Ninguna IA se califica a sí misma.** Una IA extrae, otras califican de forma independiente y otra audita. Así se evita que el sesgo o los errores de un solo modelo terminen publicados.

| Rol | Quién | Por qué |
|---|---|---|
| ✍️ **Extractor** | Claude | Lee PDFs largos y es preciso con citas literales |
| 🔍 **Auditor de cobertura** | Gemini | Contexto muy largo: relee el plan completo y busca lo que el extractor **omitió** |
| ⚖️ **Jurado de calificación** (×3) | Claude + GPT + Gemini | Cada uno aplica la rúbrica **por separado y sin ver a los otros** |
| 🧭 **Clasificador de enfoques** | GPT propone y Claude valida | Dos miradas sobre cómo se agrupan las propuestas |
| 🕊️ **Auditor de neutralidad** | Un modelo distinto al extractor | Revisa el lenguaje cargado y la equidad de los resúmenes entre candidatos |
| 🧑 **Humano** | Nosotros | Revisa solo los desacuerdos y una muestra aleatoria |

> Los modelos concretos de cada proveedor se fijan al implementar y quedan registrados en cada salida.

### Flujo

```
 fuentes/ciudades/<ciudad>/candidatos/*/plan-de-trabajo.pdf
        │
        ▼
 [0] Texto por página (pdftotext, con OCR como respaldo)         🛠️ script
        │
        ▼
 [1] EXTRACCIÓN                                                  ✍️ Claude
     → propuestas {tema, resumen, cita literal, página}
        │
        ▼
 [2] VERIFICACIÓN DE CITAS (determinística, sin IA)              🛠️ script
     ¿la cita existe en esa página? (coincidencia exacta o fuzzy ≥ 95% para OCR)
     ✗ → descartada y registrada en el reporte
        │
        ▼
 [3] AUDITORÍA DE COBERTURA                                      🔍 Gemini
     "¿Qué propuestas del plan NO están en esta lista?"
     → las faltantes vuelven al paso [1]/[2] (máx. 1 vuelta)
        │
        ▼
 [4] JURADO A CIEGAS (en paralelo)                         ⚖️ Claude │ GPT │ Gemini
     Cada uno califica: meta / plazo / financiamiento / competencia municipal
     🙈 Anonimizado: los jurados NO ven el nombre del candidato ni el partido
        │
        ▼
 [5] CONSENSO                                                    🛠️ script
     voto mayoritario por criterio (2 de 3)
     3/3 de acuerdo → ✅ consenso alto
     2/3 de acuerdo → 🟡 publicado, marcado como "consenso parcial"
     modelos caídos o respuesta inválida → 🔴 a revisión humana
        │
        ▼
 [6] ENFOQUES POR TEMA                                           🧭 GPT → Claude
     agrupa las propuestas de TODOS los candidatos en 2–4 enfoques por tema
        │
        ▼
 [7] AUDITORÍA DE NEUTRALIDAD                                    🕊️ Gemini/GPT
     ¿adjetivos valorativos? ¿un candidato tiene resúmenes más largos o favorables?
        │
        ▼
 [8] REVISIÓN HUMANA                                             🧑
     solo la cola: 🔴 + 🟡 + 10% aleatorio de los ✅
        │
        ▼
 datos/ciudades/<ciudad>/  +  reporte de calidad  →  build de la web
```

### Valor extra que llega a la web: "consenso de IA"

Cada calificación muestra cuántos modelos coincidieron. Ejemplo:

> 🎯 Meta medible: **Sí** · *3 de 3 IA coinciden*
> 💰 Financiamiento: **No** · *2 de 3 IA coinciden* (ver por qué)

Al hacer clic se ven las 3 justificaciones. Esto le da al votante **transparencia sobre la certeza** de cada dato, en lugar de pedirle que confíe a ciegas en "la IA".

### Métricas de calidad (publicadas en Metodología)

- **Acuerdo entre jurados** (kappa de Fleiss) por criterio. Si es bajo, la rúbrica es ambigua y se corrige antes de publicar.
- % de citas verificadas literalmente.
- Propuestas recuperadas por el auditor de cobertura.
- Número de cambios hechos en la revisión humana.

### Detalles de ingeniería

- **Orquestación:** Python, con un paso = un módulo. Se ejecuta con `make pipeline CIUDAD=quito` o con un paso suelto (`make jurado CIUDAD=quito`).
- **Multi-ciudad:** todo se parametriza por ciudad; los temas y la rúbrica son comunes.
- **Pipeline incremental (diseño central):** cada documento es una unidad independiente identificada por el **sha256 de su contenido**. Cada paso guarda su resultado con la clave `hash(entrada) + paso + versión del prompt + modelo` en `pipeline/.cache/`. Al correr, solo se procesa lo que falta, como `make`:
  - un documento nuevo o editado → solo ese documento
  - un prompt nuevo → solo ese paso, para todos
  - nada cambió → USD 0
  - los pasos globales (enfoques, auditoría de neutralidad) se recalculan sobre resultados ya cacheados y cuestan centavos
- **IDs de propuesta estables:** se derivan del candidato y de la cita normalizada. Así una nueva corrida no rompe enlaces ni decisiones humanas ya tomadas.
- **Decisiones humanas persistentes:** van en `datos/ciudades/<c>/revision.yaml` y se re-aplican en cada exportación.
- **Salidas estructuradas** (JSON schema) en todos los proveedores y validación con Pydantic.
- **Prompts versionados** en `pipeline/prompts/`, con la versión en el nombre (cambiar el prompt invalida solo la caché de su paso). No se usa `temperature`: los modelos actuales de Claude la rechazan. El determinismo viene de la caché y de las salidas estructuradas.
- **Bitácora completa:** cada llamada (prompt, modelo, respuesta, costo) se guarda en `pipeline/logs/`. Es auditable y publicable.
- **Tolerancia a fallos:** reintentos con backoff. Si un proveedor cae, el jurado funciona con 2 y esas calificaciones van automáticamente a 🟡.
- **Claves de API** en `.env`, que **nunca se sube al repositorio**.
- **Costo estimado:** bajo, del orden de decenas de dólares por ciudad incluyendo los 3 jurados. Se mide en la primera corrida con un candidato.

### Fase 2: debate (22 nov)

Transcripción del debate (Whisper u otro). Luego el mismo patrón: Claude clasifica cada afirmación como *en el plan*, *nueva* o *contradice el plan*, con marca de tiempo; GPT y Gemini validan; los desacuerdos van a revisión humana.

## 9. Modelo de datos (borrador)

```yaml
# data/candidatos/pabel-munoz.yaml
id: pabel-munoz
nombre: Pabel Muñoz
lista: "2-17-70"
organizacion: Alianza Ciudadana
foto: fotos/pabel-munoz.jpg
foto_fuente: <url>
trayectoria:
  - cargo: Alcalde de Quito
    periodo: 2023–2027
    fuente: <url>
plan_trabajo:
  url: <url CNE>
  paginas: 48
propuestas:
  - id: pm-seg-01
    tema: seguridad
    resumen: "Instalar X cámaras de videovigilancia en barrios"
    cita: "texto literal del plan..."
    pagina: 12
    enfoques: [tecnologia]
    rubrica:
      meta: true
      plazo: false
      financiamiento: false
      competencia_municipal: true
      justificacion: "Meta numérica clara, sin plazo ni fuente de financiamiento"
```

## 10. Stack técnico

- **SvelteKit + `adapter-static`**: todas las páginas se prerenderizan como HTML estático.
  - Por qué Svelte: el flujo "Lo que me importa" es muy interactivo y visual. Svelte trae transiciones y animaciones incluidas (`transition:`, `animate:flip` para reordenar tarjetas, `tweened` para las barras de afinidad y el termómetro), genera bundles chicos (importante en celulares con datos móviles) y la reactividad de Svelte 5 (runes) simplifica el estado del flujo.
  - Alternativa descartada: Astro con islas de Svelte. Mandaría menos JS en las fichas, pero agrega otra herramienta; con SvelteKit prerenderizado la diferencia es mínima para este tamaño de sitio.
- **Tailwind CSS**.
- Los datos van en YAML/JSON dentro de `/data`, separados del código.
- Scripts del pipeline en `/pipeline` (Python: extracción de PDFs y verificación de citas).
- Hosting en **Cloudflare Pages o GitHub Pages** (gratis, rápido y aguanta picos de tráfico).
- Repositorio **público**.
- Diseño mobile-first, imágenes OG para compartir por WhatsApp y accesibilidad (contraste y lectores de pantalla).

**Multi-ciudad desde el inicio:** el enfoque actual es Quito, pero todo se organiza por ciudad para poder sumar Guayaquil, Cuenca, etc. sin reescribir nada. Las rutas de la web serán `/quito`, `/quito/candidatos/<slug>`, `/quito/lo-que-me-importa`, y luego `/guayaquil/...`. Los temas y la rúbrica son comunes; los enfoques son por ciudad.

```
PLAN.md
README.md
fuentes/                         info original descargada (inmutable, con hash)
├── nacional/                    COOTAD, calendario CNE, reglamento de debates
└── ciudades/<ciudad>/
    ├── cne/                     lista oficial, resoluciones
    ├── debate/
    └── candidatos/<slug>/       plan de trabajo, foto, fuentes.yaml
datos/                           salida revisada (lo único que lee la web)
├── temas.yaml                   comunes a todas las ciudades
├── ciudades.yaml                registro de ciudades activas
└── ciudades/<ciudad>/
    ├── ciudad.yaml              fechas y metadatos
    ├── enfoques.yaml
    └── candidatos/<slug>.yaml
pipeline/                        extracción, verificación de citas
└── prompts/                     prompts versionados (públicos)
web/                             sitio SvelteKit (routes, componentes, lib/afinidad.ts)
```

## 11. Cronograma

> El plan de ejecución detallado (fases, mocks e interruptores) está en [EJECUCION.md](EJECUCION.md).

| Fecha | Tarea |
|---|---|
| **14–15 nov** | Verificar la lista oficial en el CNE y conseguir los 10 planes de trabajo y las fotos oficiales |
| **15 nov** | Pipeline multi-IA: probarlo con 1 candidato, medir costo y acuerdo, ajustar la rúbrica |
| **16 nov** | Correr el pipeline con los 10 candidatos y revisar la cola humana |
| **16–18 nov** | Construir el sitio: fichas, comparador, termómetro y flujo visual |
| **19 nov** | 🚀 **Publicar** y empezar la difusión |
| 20–21 nov | Comparador directo y ajustes según el feedback |
| 22 nov | Debate: grabar y transcribir |
| 23–24 nov | Publicar la sección plan frente a debate |
| **26 nov** | ❄️ Congelar el contenido antes del silencio electoral |

## 12. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Algún plan de trabajo no está disponible o es un PDF escaneado | Buscarlo hoy mismo; usar OCR; si falta, mostrar "plan no disponible" de forma explícita |
| La IA inventa propuestas o citas | Verificación literal automática de citas más revisión humana |
| La IA omite propuestas | Auditor de cobertura con un modelo distinto al extractor |
| Sesgo de un solo modelo | Jurado de 3 proveedores, anonimizado y con voto mayoritario |
| Un proveedor de IA cae o cambia | Jurado degradable a 2 modelos, caché y bitácora completa |
| Acusaciones de sesgo | Metodología pública, misma estructura para todos, orden aleatorio, repositorio abierto |
| Impugnaciones que cambian la lista a último momento | Los datos están separados del código, así que es fácil sacar a un candidato |
| Normativa electoral (silencio, propaganda) | Sitio informativo sin pauta pagada; congelar el 26 nov; consultar si hace falta |
| Pico de tráfico el día de la difusión | Sitio estático en una CDN |

## 13. Decisiones pendientes

- [ ] Nombre y dominio de la web
- [ ] Identidad: ¿a nombre personal, anónima o como proyecto ciudadano?
- [ ] Lista final de temas (después de leer los planes)
- [ ] ¿Los enfoques admiten "se opone"?
- [ ] ¿Quién revisa los datos además de nosotros?
- [ ] Claves de API: Anthropic, OpenAI y Google (Gemini)
- [ ] Presupuesto máximo de API por ciudad

## 14. Próximo paso inmediato

👉 **Conseguir los 10 planes de trabajo del CNE** y verificar la lista oficial de candidatos.

## 15. Fases futuras (después del lanzamiento): noticias y redes oficiales

Ambas entran al **mismo pipeline incremental** como tipos de fuente nuevos (`noticia`, `post_oficial`, `comunicado`). Solo se procesa lo nuevo.

### Noticias
- **Mismo trato para todos:** la misma lista pública de medios (nacionales y locales), los mismos términos de búsqueda y el mismo período para cada candidato.
- **Sin "buena/mala":** se clasifica por **tipo**: propuesta o anuncio · hecho de gestión verificable · proceso judicial o administrativo (con su estado) · controversia o declaración. El jurado de 3 IA a ciegas aplica la clasificación.
- **Solo lo verificable:** que tenga autor, fecha y fuente identificable. Sin columnas de opinión ni redes de terceros.
- **Archivo:** copia local y enlace a Internet Archive, porque las notas se editan o se borran.
- **Deduplicación:** la misma historia publicada en varios medios se cuenta una sola vez.
- **Presentación:** sección "En las noticias" de la ficha, como línea de tiempo con fuentes. **No afecta al termómetro ni a la afinidad.**

### Redes y comunicados oficiales
- **Solo por caminos legítimos:**
  - Instagram con la API oficial de Meta (función *Business Discovery*: posts públicos de cuentas de empresa o creador). Requiere una cuenta profesional de Instagram y una app de Meta.
  - Webs y salas de prensa de campaña, respetando `robots.txt`.
  - Curaduría manual por link.
  - Facebook y TikTok requieren revisiones o aprobaciones lentas; X es de pago.
- **Nunca** raspar plataformas que lo prohíben, ni saltar logins o bloqueos anti-bot.
- **Solo cuentas oficiales** del candidato y de su organización. Sin comentarios ni seguidores.
- **Valor:** **lo que promete en redes vs. lo que inscribió en su plan** (📄 en el plan · 🆕 promesa nueva · ↔️ contradice). Mismo análisis que el debate.
- **Derechos de autor:** en la web, solo una cita corta y el link o la inserción oficial del post.

