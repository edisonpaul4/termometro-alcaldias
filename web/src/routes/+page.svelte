<script lang="ts">
	import { diasHasta } from '#lib/util.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const reales = $derived(data.ciudades.filter((c) => !c.es_mock));
	const principal = $derived(reales[0] ?? data.ciudades[0]);
	const dias = $derived(principal ? diasHasta(principal.eleccion) : 0);
	const pasos = [
		['👆', 'Elige lo que te importa', 'Seguridad, movilidad, agua… tú decides el orden.'],
		['🎯', 'Dinos cómo lo resolverías', 'Las opciones salen de las propuestas reales.'],
		['🌡️', 'Mira quién lo propone en serio', 'Con metas, plazos y de dónde sale la plata.']
	];
</script>

<section class="relative overflow-hidden bg-noche text-white">
	<div class="pointer-events-none absolute -top-40 -right-32 size-[28rem] rounded-full bg-menta/20 blur-3xl"></div>
	<div class="contenedor relative pt-12 pb-14 sm:pt-20 sm:pb-20">
		<p class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-sm font-medium">
			🗳️ 29 de noviembre
			{#if dias > 0}<span class="text-menta">· faltan {dias} días</span>{/if}
		</p>
		<h1 class="mt-5 text-5xl leading-[0.95] font-extrabold tracking-tight text-balance sm:text-7xl">
			¿No sabes por quién votar para alcalde?
		</h1>
		<p class="display mt-4 text-2xl font-semibold text-menta sm:text-3xl">Descúbrelo en 60 segundos.</p>
		<p class="mt-4 max-w-xl text-lg text-white/70">
			Elige lo que te importa y mira qué candidatos lo proponen <strong class="text-white">de forma concreta</strong>,
			según sus planes de trabajo oficiales.
		</p>

		<div class="mt-8 flex flex-col gap-3 sm:flex-row">
			{#each data.ciudades as c (c.id)}
				<a
					href="/{c.id}/lo-que-me-importa/"
					class="group inline-flex items-center justify-center gap-2 rounded-full px-7 py-4 text-lg font-bold transition active:scale-95
						{c.es_mock ? 'bg-white/10 text-white ring-1 ring-white/20' : 'bg-menta text-noche shadow-[0_0_40px_-8px] shadow-menta'}"
				>
					{c.es_mock ? '🧪 Probar con datos ficticios' : `Empezar · ${c.nombre}`}
					<span class="transition group-hover:translate-x-1">→</span>
				</a>
			{/each}
		</div>

		<ul class="mt-8 flex flex-wrap gap-x-5 gap-y-2 text-sm text-white/60">
			<li>✓ Neutral, sin partido</li>
			<li>✓ Sin registro</li>
			<li>✓ Cada dato con su fuente del CNE</li>
		</ul>
	</div>
</section>

<section class="contenedor mt-14">
	<h2 class="text-3xl font-extrabold tracking-tight">Así funciona</h2>
	<ol class="mt-6 grid gap-3 sm:grid-cols-3">
		{#each pasos as [icono, titulo, texto], i (titulo)}
			<li class="tarjeta p-5">
				<div class="flex items-center gap-3">
					<span class="display grid size-8 place-items-center rounded-full bg-tinta text-sm font-bold text-white">{i + 1}</span>
					<span class="text-3xl" aria-hidden="true">{icono}</span>
				</div>
				<p class="display mt-3 text-lg leading-tight font-bold">{titulo}</p>
				<p class="mt-1 text-sm text-tinta-suave">{texto}</p>
			</li>
		{/each}
	</ol>
</section>

<section class="contenedor mt-14">
	<h2 class="text-3xl font-extrabold tracking-tight">O revisa los candidatos</h2>
	<ul class="mt-6 grid gap-3 sm:grid-cols-2">
		{#each data.ciudades as c (c.id)}
			<li>
				<a href="/{c.id}/" class="tarjeta block p-5 transition hover:-translate-y-0.5 hover:border-tinta">
					<div class="flex items-center justify-between">
						<span class="display text-2xl font-bold">{c.nombre}</span>
						{#if c.es_mock}
							<span class="rounded-full bg-demo-suave px-2 py-0.5 text-xs font-semibold text-demo">DATOS DE PRUEBA</span>
						{/if}
					</div>
					<p class="mt-1 text-sm text-tinta-suave">{c.dignidad} · {c.candidatos} candidaturas</p>
					<p class="mt-4 font-semibold">Ver candidatos y propuestas →</p>
				</a>
			</li>
		{/each}
	</ul>
</section>
