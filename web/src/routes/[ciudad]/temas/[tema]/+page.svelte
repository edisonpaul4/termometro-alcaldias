<script lang="ts">
	import { onMount } from 'svelte';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import Icono from '#lib/componentes/Icono.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import Proporcion from '#lib/componentes/Proporcion.svelte';
	import { propuestasDelTema, termometroTema } from '#lib/termometro.js';
	import { barajar } from '#lib/util.js';
	import { colorTema, tinte } from '#lib/visual.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let orden = $state<string[] | null>(null);
	onMount(() => (orden = barajar(data.completos.map((x) => x.id))));
	const candidatos = $derived(orden ? orden.map((id) => data.completos.find((x) => x.id === id)!) : data.completos);
	const c = $derived(data.ciudad.id);
	const color = $derived(colorTema(data.tema.id));
	const enfoques = $derived(data.enfoques.filter((e) => e.tema === data.tema.id));
	const con = $derived(candidatos.filter((x) => propuestasDelTema(x, data.tema.id).length));
	const sin = $derived(candidatos.filter((x) => !propuestasDelTema(x, data.tema.id).length));

	// Indicador de posición del carrusel
	let carrusel = $state<HTMLElement>();
	let actual = $state(0);
	const alDesplazar = () => {
		if (!carrusel) return;
		const ancho = (carrusel.firstElementChild as HTMLElement)?.offsetWidth ?? 1;
		actual = Math.round(carrusel.scrollLeft / (ancho + 12));
	};
</script>

<svelte:head><title>{data.tema.nombre} · {data.ciudad.nombre} · termómetro</title></svelte:head>

<section class="relative isolate overflow-hidden">
	<div class="pointer-events-none absolute -top-40 left-1/2 -z-10 size-[28rem] -translate-x-1/2 rounded-full opacity-[0.12] blur-3xl" style="background:{color}"></div>
	<div class="contenedor pt-5">
		<a href="/{c}/" class="inline-flex items-center gap-1 text-sm text-texto-3 hover:text-texto">
			<Icono nombre="arrow-left" tipo="ui" tam={14} /> {data.ciudad.nombre}
		</a>
		<div class="mt-6 flex items-center gap-4">
			<TemaIcono tema={data.tema.id} icono={data.tema.icono} tam={64} />
			<div>
				<h1 class="text-3xl leading-tight font-extrabold tracking-tight">{data.tema.nombre}</h1>
				<p class="text-sm text-texto-2">{con.length} de {candidatos.length} candidatos tienen propuestas</p>
			</div>
		</div>
		<p class="mt-4 text-texto-2">{data.tema.descripcion}</p>

		{#if enfoques.length}
			<ul class="mt-4 flex flex-wrap gap-2 text-sm">
				{#each enfoques as e (e.id)}
					<li class="inline-flex items-center gap-1.5 rounded-full py-1 pr-3 pl-1.5" style="background:{tinte(color)};color:{color}" title={e.descripcion}>
						<Icono nombre={e.icono} tam={16} />
						{e.nombre}
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</section>

<!-- Carrusel deslizable en móvil, grilla en escritorio -->
<div class="mx-auto mt-8 max-w-3xl">
	<ul
		bind:this={carrusel}
		onscroll={alDesplazar}
		class="sin-scrollbar flex snap-x snap-mandatory gap-3 overflow-x-auto px-4 pb-2 sm:grid sm:grid-cols-2 sm:overflow-visible"
	>
		{#each con as cand (cand.id)}
			{@const lect = termometroTema(cand, data.tema.id)}
			{@const ps = propuestasDelTema(cand, data.tema.id)}
			<li class="tarjeta flex w-[85%] shrink-0 snap-center flex-col p-5 sm:w-auto">
				<div class="flex items-center gap-3">
					<Avatar candidato={cand} ciudad={c} tam={48} />
					<div class="min-w-0 flex-1">
						<p class="display truncate font-bold">{cand.nombre}</p>
						<p class="truncate text-xs text-texto-3">Lista {cand.lista} · {cand.organizacion}</p>
					</div>
				</div>
				<div class="mt-4"><Proporcion lectura={lect} {color} /></div>
				<ul class="mt-4 flex-1 space-y-2.5 text-sm">
					{#each ps.slice(0, 4) as p (p.id)}
						<li class="flex gap-2.5">
							<span class="mt-1.5 size-1.5 shrink-0 rounded-full" style="background:{color}"></span>
							<span class="text-texto-2">
								{p.resumen}
								{#if !p.rubrica.competencia_municipal.valor}
									<span class="inline-flex items-center gap-0.5 text-xs text-alerta"><Icono nombre="warning" tipo="ui" tam={11} /> no es competencia municipal</span>
								{/if}
							</span>
						</li>
					{/each}
				</ul>
				<a href="/{c}/candidatos/{cand.id}/#{data.tema.id}" class="mt-4 inline-flex items-center gap-1 text-sm font-semibold" style="color:{color}">
					{ps.length > 4 ? `Ver las ${ps.length} propuestas y citas` : 'Ver citas y calificación'}
					<Icono nombre="arrow-right" tipo="ui" tam={14} />
				</a>
			</li>
		{/each}
	</ul>
	{#if con.length > 1}
		<div class="mt-3 flex justify-center gap-1.5 sm:hidden" aria-hidden="true">
			{#each con as _, i (i)}
				<span class="h-1.5 rounded-full transition-all {i === actual ? 'w-5' : 'w-1.5 bg-black/15'}" style={i === actual ? `background:${color}` : ''}></span>
			{/each}
		</div>
	{/if}
</div>

{#if sin.length}
	<section class="contenedor mt-10">
		<div class="rounded-3xl bg-black/[0.03] p-5 ring-1 ring-black/5">
			<h2 class="text-base font-bold text-texto-2">Sin propuestas sobre este tema</h2>
			<ul class="mt-3 flex flex-wrap gap-3">
				{#each sin as cand (cand.id)}
					<li class="flex items-center gap-2 text-sm text-texto-3">
						<Avatar candidato={cand} ciudad={c} tam={28} anillo={false} />
						{cand.nombre}
					</li>
				{/each}
			</ul>
		</div>
	</section>
{/if}
