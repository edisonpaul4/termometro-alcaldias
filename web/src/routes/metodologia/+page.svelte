<script lang="ts">
	import Icono from '#lib/componentes/Icono.svelte';
	import { PISO_CONCRECION, TOPE_COBERTURA, UMBRAL_EMPATE } from '#lib/afinidad.js';

	const principios = [
		['quotes', 'Sin fuente no se publica', 'Cada propuesta tiene su cita textual y la página del plan oficial.'],
		['scales', 'No opinamos', 'No decimos si una propuesta es buena o mala: solo si es concreta y si le corresponde al Municipio.'],
		['shuffle', 'Mismo trato para todos', 'Misma estructura y orden aleatorio en cada visita.'],
		['lock-simple', 'Tu privacidad', 'Tus respuestas se procesan solo en tu teléfono. No guardamos nada ni usamos cookies de rastreo.']
	];
	const criterios = [
		['target', 'Meta medible', '¿Dice cuánto o qué resultado verificable logrará?'],
		['calendar-check', 'Plazo', '¿Dice cuándo?'],
		['coins', 'Financiamiento', '¿Dice de dónde sale el dinero o cuánto cuesta?'],
		['bank', 'Competencia municipal', '¿Cumplirla está en manos del Municipio (COOTAD, arts. 54–55 y 84–85) o depende sobre todo de otro nivel de gobierno? No suma puntos: se muestra como alerta.']
	];
</script>

<svelte:head><title>Cómo funciona · termómetro</title></svelte:head>

<div class="contenedor pt-10">
	<h1 class="text-[2.6rem] leading-[0.95] font-extrabold tracking-tight">Cómo <span class="texto-aurora">funciona</span></h1>
	<p class="mt-4 text-lg text-texto-2">
		Todo sale de los <strong class="text-texto">planes de trabajo oficiales</strong> que cada candidatura inscribió en el CNE. El
		código, los datos, la rúbrica y los prompts son públicos.
	</p>

	<ul class="mt-8 grid gap-3 sm:grid-cols-2">
		{#each principios as [icono, titulo, texto] (titulo)}
			<li class="tarjeta p-5">
				<Icono nombre={icono} tipo="ui" tam={22} class="text-acento" />
				<p class="display mt-3 font-bold">{titulo}</p>
				<p class="mt-1 text-sm text-texto-2">{texto}</p>
			</li>
		{/each}
	</ul>

	<section class="mt-14">
		<h2 class="flex items-center gap-2 text-2xl font-extrabold"><Icono nombre="thermometer" tipo="ui" tam={24} class="text-acento" /> El termómetro</h2>
		<p class="mt-2 text-texto-2">Cada propuesta se califica Sí/No en cuatro criterios:</p>
		<ul class="mt-4 space-y-2">
			{#each criterios as [icono, titulo, texto] (titulo)}
				<li class="flex gap-3 rounded-2xl bg-black/[0.04] p-4">
					<Icono nombre={icono} tipo="ui" tam={20} class="mt-0.5 text-acento" />
					<span><strong>{titulo}.</strong> <span class="text-texto-2">{texto}</span></span>
				</li>
			{/each}
		</ul>
		<p class="mt-4 text-texto-2">
			Lo que ves en cada candidato es una <strong class="text-texto">proporción sobre una escala fija de 10</strong>: de cada 10
			propuestas de su plan, cuántas traen algún dato (cuánto, cuándo o con qué dinero), y cuántas traen cada uno. Así, un plan
			más largo no se ve más concreto solo por tener más propuestas. Cuando hay menos de 10 propuestas, o la proporción es
			menor a medio punto, mostramos el conteo exacto ("1 de 119") en lugar de redondear a cero. El tamaño del plan se
			muestra aparte, como dato, y no suma ni resta.
		</p>
	</section>

	<section class="mt-14">
		<h2 class="flex items-center gap-2 text-2xl font-extrabold"><Icono nombre="scales" tipo="ui" tam={24} class="text-acento" /> Un jurado de tres IA, a ciegas</h2>
		<p class="mt-3 text-texto-2">
			Una IA extrae las propuestas con su cita literal y un programa, <strong class="text-texto">sin IA</strong>, verifica que esa cita
			exista en la página indicada del PDF. Luego <strong class="text-texto">tres IA de empresas distintas</strong> (Anthropic, OpenAI y
			Google) califican cada criterio por separado, <strong class="text-texto">sin ver el nombre del candidato ni su partido</strong>. Ven la cita textual
			y su contexto en el plan (la fase o sección donde aparece y, si existe, la fila de la tabla que le pone meta, plazo o monto), no
			nuestro resumen. Se
			publica lo que decide la mayoría y se muestra cuántas coincidieron. Los desacuerdos y una muestra al azar los revisa una persona.
		</p>
	</section>

	<section class="mt-14">
		<h2 class="flex items-center gap-2 text-2xl font-extrabold"><Icono nombre="target" tipo="ui" tam={24} class="text-acento" /> Cómo se calcula tu resultado</h2>
		<ul class="mt-4 space-y-2 text-texto-2 [&>li]:flex [&>li]:gap-2.5">
			<li><span class="text-acento">→</span> Cada tema que eliges pesa según tu prioridad: con 5 temas, 5, 4, 3, 2 y 1.</li>
			<li><span class="text-acento">→</span> Si elegiste un enfoque: cuenta si el candidato lo propone, medido con la concreción de <em>esas</em> propuestas.</li>
			<li><span class="text-acento">→</span> Si marcaste “Ni idea”: cuenta si tiene propuestas sobre el tema (hasta {TOPE_COBERTURA}; más cantidad no suma).</li>
			<li><span class="text-acento">→</span> <span><strong class="text-texto">La concreción multiplica:</strong> proponer lo que quieres sin ningún detalle vale como máximo el {PISO_CONCRECION * 100}%.</span></li>
			<li><span class="text-acento">→</span> Las propuestas fuera de la competencia municipal no cuentan.</li>
			<li><span class="text-acento">→</span> Un monto o una meta de todo un eje o programa <strong class="text-texto">no cuenta</strong> para cada propuesta de ese eje: tiene que ser de esa propuesta.</li>
			<li><span class="text-acento">→</span> Si dos candidatos están a menos de {UMBRAL_EMPATE} puntos, es empate técnico.</li>
		</ul>
	</section>

	<section class="mt-14 rounded-3xl bg-alerta/[0.07] p-6 ring-1 ring-alerta/15">
		<h2 class="flex items-center gap-2 text-xl font-extrabold text-alerta"><Icono nombre="info" tipo="ui" tam={22} /> Límites</h2>
		<p class="mt-2 text-texto-2">
			Un plan de trabajo no garantiza lo que hará un candidato, y la concreción no mide si una idea es buena
			<strong class="text-texto">ni si es viable</strong>: una obra enorme con monto, fecha y fuente puntúa como concreta aunque sea
			difícil de cumplir. Por eso mostramos las cifras tal como las escribió cada candidato, para que tú las juzgues. Úsalo como
			punto de partida: lee las propuestas, revisa las citas y contrasta con otras fuentes.
		</p>
	</section>
</div>
