<script lang="ts">
	import Icono from '#lib/componentes/Icono.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import { colorTema } from '#lib/visual.js';
	import { diasHasta } from '#lib/util.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const reales = $derived(data.ciudades.filter((c) => !c.es_mock));
	const principal = $derived(reales[0] ?? data.ciudades[0]);
	const dias = $derived(principal ? diasHasta(principal.eleccion) : 0);
	// Dos vueltas para el carrusel infinito
	const cinta = $derived([...data.temas, ...data.temas]);

	const pasos = [
		['hand-tap', 'Toca lo que te importa', 'Seguridad, movilidad, agua… y en qué orden.'],
		['target', 'Elige cómo lo resolverías', 'Las opciones salen de propuestas reales.'],
		['thermometer', 'Mira quién lo propone en serio', 'Con metas, plazos y de dónde sale la plata.']
	];
</script>

<!-- HERO -->
<section class="relative isolate overflow-hidden">
	<div class="pointer-events-none absolute -top-48 left-1/2 -z-10 size-[44rem] -translate-x-1/2 rounded-full opacity-[0.12] blur-3xl fondo-aurora"></div>

	<div class="contenedor pt-10 pb-6 text-center sm:pt-16">
		<p class="inline-flex items-center gap-2 rounded-full bg-black/[0.06] py-1.5 pr-3.5 pl-2 text-sm font-medium ring-1 ring-black/10">
			<span class="relative flex size-2">
				<span class="absolute inline-flex size-full animate-ping rounded-full bg-acento opacity-60"></span>
				<span class="relative inline-flex size-2 rounded-full bg-acento"></span>
			</span>
			Elecciones 29 de noviembre {#if dias > 0}<span class="text-texto-2">· faltan {dias} días</span>{/if}
		</p>

		<h1 class="mx-auto mt-6 max-w-2xl text-[2.9rem] leading-[0.95] font-extrabold tracking-tight text-balance sm:text-7xl">
			¿No sabes por quién votar?
			<span class="texto-aurora">Descúbrelo en 60&nbsp;segundos.</span>
		</h1>
		<p class="mx-auto mt-5 max-w-md text-lg text-pretty text-texto-2">
			Toca lo que te importa y mira qué candidatos a alcalde lo proponen <strong class="text-texto">de verdad</strong>, según
			sus planes oficiales.
		</p>

		<div class="mt-8 flex flex-col items-center gap-3">
			{#each data.ciudades as c (c.id)}
				{#if !c.es_mock}
					<a
						href="/{c.id}/lo-que-me-importa/"
						class="group relative inline-flex items-center gap-3 rounded-full p-[2px] fondo-aurora shadow-[0_8px_40px_-8px_rgba(15,118,110,0.28)] transition active:scale-95"
					>
						<span class="inline-flex items-center gap-3 rounded-full bg-fondo py-3.5 pr-3.5 pl-7 text-lg font-bold">
							Empezar · {c.nombre}
							<span class="grid size-9 place-items-center rounded-full bg-acento text-white transition group-hover:translate-x-0.5">
								<Icono nombre="arrow-right" tipo="ui" tam={18} />
							</span>
						</span>
					</a>
				{:else}
					<a href="/{c.id}/lo-que-me-importa/" class="inline-flex items-center gap-1.5 text-sm font-medium text-texto-3 hover:text-texto-2">
						<Icono nombre="sparkle" tipo="ui" tam={14} /> Probar con una ciudad ficticia
					</a>
				{/if}
			{/each}
		</div>

		<ul class="mt-7 flex flex-wrap justify-center gap-x-5 gap-y-2 text-sm text-texto-3">
			<li class="inline-flex items-center gap-1.5"><Icono nombre="scales" tipo="ui" tam={15} /> Neutral</li>
			<li class="inline-flex items-center gap-1.5"><Icono nombre="lock-simple" tipo="ui" tam={15} /> Sin registro</li>
			<li class="inline-flex items-center gap-1.5"><Icono nombre="seal-check" tipo="ui" tam={15} /> Fuentes del CNE</li>
		</ul>
	</div>

	<!-- Cinta de temas (tipo "historias destacadas") -->
	<div class="relative mt-6 overflow-hidden py-2 [mask-image:linear-gradient(90deg,transparent,#000_12%,#000_88%,transparent)]" aria-hidden="true">
		<ul class="flex w-max animate-[cinta_40s_linear_infinite] gap-4">
			{#each cinta as t, i (i)}
				<li class="flex w-20 flex-col items-center gap-2">
					<span class="rounded-full p-[2px]" style="background:{colorTema(t.id)}">
						<span class="block rounded-full bg-fondo p-[3px]"><TemaIcono tema={t.id} icono={t.icono} tam={58} /></span>
					</span>
					<span class="text-xs font-medium text-texto-2">{t.nombre_corto}</span>
				</li>
			{/each}
		</ul>
	</div>
</section>

<!-- CÓMO FUNCIONA -->
<section class="contenedor mt-16">
	<h2 class="text-3xl font-extrabold tracking-tight">Así de simple</h2>
	<ol class="mt-6 grid gap-3 sm:grid-cols-3">
		{#each pasos as [icono, titulo, texto], i (titulo)}
			<li class="tarjeta relative overflow-hidden p-5">
				<span class="display absolute -top-3 -right-1 text-8xl font-extrabold text-white/[0.04]">{i + 1}</span>
				<span class="grid size-11 place-items-center rounded-2xl bg-acento/10 text-acento">
					<Icono nombre={icono} tipo="ui" tam={22} />
				</span>
				<p class="display mt-4 text-lg leading-tight font-bold">{titulo}</p>
				<p class="mt-1 text-sm text-texto-2">{texto}</p>
			</li>
		{/each}
	</ol>
</section>

<!-- CIUDADES -->
<section class="contenedor mt-16">
	<h2 class="text-3xl font-extrabold tracking-tight">Revisa a los candidatos</h2>
	<ul class="mt-6 grid gap-3 sm:grid-cols-2">
		{#each data.ciudades as c (c.id)}
			<li>
				<a href="/{c.id}/" class="tarjeta group block p-5 transition hover:ring-black/20">
					<div class="flex items-center justify-between">
						<span class="display text-2xl font-extrabold">{c.nombre}</span>
						{#if c.es_mock}
							<span class="rounded-full bg-demo/10 px-2 py-0.5 text-xs font-semibold text-demo">Datos de prueba</span>
						{:else}
							<Icono nombre="arrow-up-right" tipo="ui" tam={20} class="text-texto-3 transition group-hover:text-acento" />
						{/if}
					</div>
					<p class="mt-1 text-sm text-texto-2">{c.dignidad} · {c.candidatos} candidaturas</p>
					{#if c.paginas}<p class="mt-3 text-xs text-texto-3">{c.paginas} páginas de planes de trabajo analizadas</p>{/if}
				</a>
			</li>
		{/each}
	</ul>
</section>

<style>
	@keyframes -global-cinta {
		to {
			transform: translateX(calc(-50% - 0.5rem));
		}
	}
</style>
