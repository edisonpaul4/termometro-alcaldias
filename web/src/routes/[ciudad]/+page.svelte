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

<section class="relative overflow-hidden bg-noche text-white">
	<div class="pointer-events-none absolute -top-32 -right-24 size-80 rounded-full bg-menta/20 blur-3xl"></div>
	<div class="contenedor relative pt-8 pb-10">
		<a href="/" class="text-sm text-white/60 hover:text-white">← Inicio</a>
		<p class="mt-4 inline-flex rounded-full bg-white/10 px-3 py-1 text-sm font-medium">
			🗳️ {dias > 0 ? `Faltan ${dias} días` : 'Hoy se vota'}
		</p>
		<h1 class="mt-3 text-4xl leading-none font-extrabold tracking-tight sm:text-5xl">
			{data.registro.dignidad} de {data.ciudad.nombre}
		</h1>
		<p class="mt-2 text-white/70">{data.candidatos.length} candidaturas · planes de trabajo oficiales del CNE</p>

		<a
			href="/{c}/lo-que-me-importa/"
			class="group mt-6 flex items-center justify-between gap-4 rounded-3xl bg-menta p-5 text-noche shadow-[0_0_40px_-10px] shadow-menta transition active:scale-[0.98]"
		>
			<span>
				<span class="display block text-xl leading-tight font-extrabold text-balance">¿Quién propone lo que te importa?</span>
				<span class="mt-1 block text-sm font-medium text-noche/70">60 segundos · sin registro · nada sale de tu teléfono</span>
			</span>
			<span class="grid size-12 shrink-0 place-items-center rounded-full bg-noche text-xl text-menta transition group-hover:translate-x-1">▶</span>
		</a>
	</div>
</section>

{#if sinPropuestas}
	<p class="contenedor mt-6">
		<span class="block rounded-2xl bg-alerta-suave p-4 text-sm text-alerta">
			⏳ Estamos procesando los planes de trabajo oficiales. Las propuestas y el termómetro aparecerán aquí pronto.
		</span>
	</p>
{/if}

<section class="contenedor mt-10">
	<div class="flex items-baseline justify-between">
		<h2 class="text-2xl font-extrabold tracking-tight">Candidatos</h2>
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
	<h2 class="text-2xl font-extrabold tracking-tight">Comparar por tema</h2>
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

<a
	href="/{c}/lo-que-me-importa/"
	class="fixed inset-x-4 bottom-[max(1rem,env(safe-area-inset-bottom))] z-30 flex items-center justify-center gap-2 rounded-full bg-noche py-3.5 font-bold text-white shadow-2xl ring-1 ring-white/10 transition active:scale-95 sm:hidden"
>
	<span class="text-menta">▶</span> ¿Quién propone lo que te importa?
</a>
