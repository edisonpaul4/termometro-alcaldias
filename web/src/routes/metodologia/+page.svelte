<script lang="ts">
	import { PESO_COBERTURA, PESO_ENFOQUE, TOPE_COBERTURA, UMBRAL_EMPATE } from '#lib/afinidad.js';
</script>

<svelte:head><title>Metodología · Termómetro de Alcaldías</title></svelte:head>

<article class="contenedor space-y-8 pt-10 leading-relaxed [&_h2]:text-xl [&_h2]:font-bold [&_li]:ml-5 [&_li]:list-disc">
	<header>
		<h1 class="text-3xl font-extrabold tracking-tight">Cómo lo hacemos</h1>
		<p class="mt-2 text-tinta-suave">
			Todo lo que ves aquí sale de los <strong>planes de trabajo oficiales</strong> que cada candidatura inscribió en el
			CNE. El código, los datos, la rúbrica y los prompts son públicos.
		</p>
	</header>

	<section>
		<h2>Principios</h2>
		<ul class="mt-2 space-y-1">
			<li>Sin fuente no se publica: cada propuesta tiene su <strong>cita textual y la página</strong> del plan.</li>
			<li>No opinamos si una propuesta es buena o mala; solo medimos si es <strong>concreta</strong> y si le <strong>corresponde al Municipio</strong>.</li>
			<li>Misma estructura para todos y <strong>orden aleatorio</strong> en cada visita.</li>
			<li>Sin encuestas ni métricas de popularidad.</li>
			<li>Tus respuestas se procesan <strong>solo en tu teléfono</strong>: no guardamos nada, no hay cookies de rastreo.</li>
		</ul>
	</section>

	<section>
		<h2>🌡️ El termómetro de concreción</h2>
		<p class="mt-2">Cada propuesta se califica Sí/No en cuatro criterios:</p>
		<ul class="mt-2 space-y-1">
			<li><strong>🎯 Meta medible:</strong> ¿dice cuánto o qué resultado verificable logrará?</li>
			<li><strong>📅 Plazo:</strong> ¿dice cuándo?</li>
			<li><strong>💰 Financiamiento:</strong> ¿dice de dónde sale el dinero o cuánto cuesta?</li>
			<li>
				<strong>🏛️ Competencia municipal:</strong> ¿le corresponde al Municipio según el COOTAD? No suma puntos: se
				muestra como alerta ⚠️.
			</li>
		</ul>
		<p class="mt-2">
			Concreción de una propuesta = (meta + plazo + financiamiento) ÷ 3. El termómetro de un tema es el promedio de
			sus propuestas; el global, el promedio de los temas (para que la cantidad no pese más que la calidad).
		</p>
	</section>

	<section>
		<h2>⚖️ Jurado de tres IA, a ciegas</h2>
		<p class="mt-2">
			Una IA extrae las propuestas con su cita literal, y un programa (sin IA) verifica que esa cita exista en la
			página indicada del PDF. Luego <strong>tres IA de empresas distintas</strong> (Anthropic, OpenAI y Google) califican
			cada criterio por separado, <strong>sin ver el nombre del candidato ni su partido</strong>. Se publica lo que decide
			la mayoría y se muestra cuántas coincidieron. Los desacuerdos y una muestra aleatoria los revisa una persona.
		</p>
	</section>

	<section>
		<h2>🧭 Cómo se calcula “lo que me importa”</h2>
		<ul class="mt-2 space-y-1">
			<li>Cada tema que eliges pesa según tu prioridad: con 5 temas, los pesos son 5, 4, 3, 2 y 1.</li>
			<li>
				Si elegiste enfoques: puntaje del tema = {PESO_ENFOQUE * 100}% coincidencia de enfoques + {Math.round((1 - PESO_ENFOQUE) * 100)}%
				concreción.
			</li>
			<li>
				Si marcaste “no estoy seguro”: {PESO_COBERTURA * 100}% cobertura del tema (hasta {TOPE_COBERTURA} propuestas; más
				cantidad no suma) + {PESO_COBERTURA * 100}% concreción.
			</li>
			<li>Las propuestas <strong>fuera de la competencia municipal no cuentan</strong>.</li>
			<li>Afinidad = promedio ponderado de los temas.</li>
			<li>Si dos candidatos están a menos de {UMBRAL_EMPATE} puntos, se muestran como <strong>empate técnico</strong>.</li>
		</ul>
	</section>

	<section>
		<h2>Límites</h2>
		<p class="mt-2">
			Un plan de trabajo no garantiza lo que hará un candidato, y la concreción no mide si una idea es buena.
			Úsalo como punto de partida: lee las propuestas, revisa las citas y contrasta con otras fuentes.
		</p>
	</section>
</article>
