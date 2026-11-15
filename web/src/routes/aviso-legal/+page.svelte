<script lang="ts">
	import Icono from '#lib/componentes/Icono.svelte';
	import { CORREO, mailto } from '#lib/contacto.js';

	const secciones: [string, string, string[]][] = [
		[
			'info',
			'Qué es este sitio',
			[
				'Un proyecto ciudadano, independiente y sin afiliación política, que ordena y analiza los planes de trabajo que cada candidatura inscribió en el Consejo Nacional Electoral (CNE).',
				'No recibe financiamiento de partidos, movimientos ni candidaturas.'
			]
		],
		[
			'scales',
			'Qué no es',
			[
				'No es una recomendación de voto, una encuesta ni un pronóstico electoral.',
				'No evalúa si una propuesta es buena, deseable o viable: solo si el plan dice cuánto, cuándo y con qué dinero, y si le corresponde al Municipio.',
				'El resultado de «Lo que me importa» refleja únicamente las prioridades que tú eliges, comparadas con lo que dicen los planes.'
			]
		],
		[
			'quotes',
			'De dónde sale cada dato',
			[
				'Cada propuesta muestra la cita textual del plan oficial, el número de página y el enlace al documento publicado por el CNE. Una cita que no aparece literalmente en el plan no se publica.',
				'Los resúmenes y las calificaciones los preparan modelos de inteligencia artificial con una rúbrica pública; ningún resumen puede incluir un dato que no esté en la cita o su contexto. La IA puede equivocarse: por eso todo es verificable contra la fuente.'
			]
		],
		[
			'lock-simple',
			'Tus datos',
			[
				'No pedimos registro. Tus respuestas en «Lo que me importa» se procesan en tu navegador y no se envían a ningún servidor.',
				'No usamos cookies de rastreo ni publicidad.'
			]
		]
	];
</script>

<svelte:head><title>Aviso legal y correcciones · termómetro</title></svelte:head>

<div class="contenedor pt-10 pb-6">
	<h1 class="text-[2.4rem] leading-[0.95] font-extrabold tracking-tight">Aviso legal y <span class="texto-aurora">correcciones</span></h1>

	<div class="mt-8 space-y-4">
		{#each secciones as [icono, titulo, parrafos] (titulo)}
			<section class="tarjeta p-5">
				<h2 class="flex items-center gap-2 text-lg font-extrabold"><Icono nombre={icono} tipo="ui" tam={20} class="text-acento" /> {titulo}</h2>
				{#each parrafos as p, i (i)}
					<p class="mt-2 text-texto-2">{p}</p>
				{/each}
			</section>
		{/each}

		<section id="correcciones" class="scroll-mt-20 rounded-3xl bg-acento/[0.07] p-5 ring-1 ring-acento/20">
			<h2 class="flex items-center gap-2 text-lg font-extrabold"><Icono nombre="flag" tipo="ui" tam={20} class="text-acento" /> Correcciones</h2>
			<p class="mt-2 text-texto-2">
				Si una candidatura, su equipo o cualquier persona encuentra un error —una cita mal atribuida, un resumen que no refleja el
				plan o una calificación que no sigue la rúbrica— puede escribirnos. Cada propuesta tiene además un enlace
				«Reportar un error en esta propuesta» que llena el correo por ti.
			</p>
			<p class="mt-2 text-texto-2">
				Revisamos cada reporte contra el plan oficial. Si corresponde, lo corregimos y la corrección queda registrada en el
				repositorio público del proyecto.
			</p>
			<a
				href={mailto('Corrección en el termómetro')}
				class="mt-4 inline-flex items-center gap-2 rounded-full bg-acento px-4 py-2.5 text-sm font-bold text-white"
			>
				<Icono nombre="envelope-simple" tipo="ui" tam={16} /> {CORREO}
			</a>
		</section>
	</div>
</div>
