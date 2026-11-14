<script lang="ts">
	import { onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import Termometro from '#lib/componentes/Termometro.svelte';
	import { termometroGlobal } from '#lib/termometro.js';
	import { barajar, diasHasta } from '#lib/util.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Orden estable en el HTML prerenderizado; se baraja al cargar (neutralidad).
	let orden = $state<string[] | null>(null);
	onMount(() => {
		orden = barajar(data.candidatos.map((c) => c.id));
	});
	const barajado = $derived(orden !== null);
	const candidatos = $derived(
		orden ? orden.map((id) => data.candidatos.find((c) => c.id === id)!) : data.candidatos
	);
	const sinPropuestas = $derived(data.candidatos.every((c) => !c.propuestas?.length));
	const dias = $derived(diasHasta(data.ciudad.eleccion));
	const c = $derived(data.ciudad.id);
</script>

<svelte:head><title>Candidatos a {data.registro.dignidad} de {data.ciudad.nombre} · Termómetro</title></svelte:head>

<section class="contenedor pt-10">
	<p class="text-sm font-medium tracking-wide text-acento uppercase">
		{data.registro.dignidad} de {data.ciudad.nombre} · {dias > 0 ? `faltan ${dias} días` : 'día de elecciones'}
	</p>
	<h1 class="mt-1 text-3xl font-extrabold tracking-tight sm:text-4xl">{data.candidatos.length} candidaturas</h1>

	<a
		href="/{c}/lo-que-me-importa/"
		class="group mt-6 block rounded-3xl bg-acento p-6 text-white shadow-lg shadow-acento/20 transition hover:bg-acento-fuerte"
	>
		<p class="text-sm font-medium text-acento-suave">2 minutos · sin registro · nada sale de tu teléfono</p>
		<p class="mt-1 text-2xl font-bold text-balance">¿Quién se apega más a lo que te importa?</p>
		<p class="mt-3 inline-flex items-center gap-1 font-semibold">
			Empezar <span class="transition group-hover:translate-x-1">→</span>
		</p>
	</a>

	{#if sinPropuestas}
		<p class="mt-6 rounded-2xl bg-alerta-suave p-4 text-sm text-alerta">
			⏳ Estamos procesando los planes de trabajo oficiales. Las propuestas y el termómetro aparecerán aquí pronto.
		</p>
	{/if}
</section>

<section class="contenedor mt-10">
	<div class="flex items-baseline justify-between">
		<h2 class="text-xl font-bold">Candidatos</h2>
		<p class="text-xs text-tinta-suave">{barajado ? 'Orden aleatorio' : ''}</p>
	</div>
	<ul class="mt-4 grid gap-3 sm:grid-cols-2">
		{#each candidatos as cand (cand.id)}
			{@const t = termometroGlobal(cand)}
			<li animate:flip={{ duration: 400 }}>
				<a href="/{c}/candidatos/{cand.id}/" class="tarjeta flex h-full flex-col gap-4 p-4 transition hover:border-acento">
					<div class="flex items-center gap-3">
						<Avatar candidato={cand} ciudad={c} />
						<div class="min-w-0">
							<p class="truncate font-semibold">{cand.nombre}</p>
							<p class="truncate text-sm text-tinta-suave">Lista {cand.lista} · {cand.organizacion}</p>
						</div>
					</div>
					{#if !cand.plan_trabajo.disponible}
						<p class="text-sm text-tinta-suave">📄 Plan de trabajo no disponible</p>
					{:else if t.propuestas}
						<div class="mt-auto">
							<Termometro valor={t.valor} />
							<p class="mt-1 text-xs text-tinta-suave">
								{t.propuestas} propuestas{#if t.fueraDeCompetencia}<span class="text-alerta">
										· ⚠️ {t.fueraDeCompetencia} fuera de competencia</span
									>{/if}
							</p>
						</div>
					{/if}
				</a>
			</li>
		{/each}
	</ul>
</section>

<section class="contenedor mt-12">
	<h2 class="text-xl font-bold">Comparar por tema</h2>
	<p class="mt-1 text-sm text-tinta-suave">Qué propone cada candidato en un mismo tema, lado a lado.</p>
	<ul class="mt-4 grid grid-cols-3 gap-2 sm:grid-cols-4">
		{#each data.temas as tema (tema.id)}
			<li>
				<a
					href="/{c}/temas/{tema.id}/"
					class="tarjeta flex flex-col items-center gap-1 p-3 text-center text-sm transition hover:border-acento"
				>
					<span class="text-2xl" aria-hidden="true">{tema.icono}</span>
					<span class="leading-tight">{tema.nombre_corto}</span>
				</a>
			</li>
		{/each}
	</ul>
</section>
