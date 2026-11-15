<script lang="ts">
	/*
	 * Comparar un tema entre candidatos.
	 *  - Filtro por enfoque ("cómo lo resolverían"): la comparación real es quién propone qué.
	 *  - Tarjetas compactas: proporción con datos y las 2 propuestas más concretas.
	 *  - El resto de propuestas y el detalle (cita, votos) se abren en la hoja / panel lateral.
	 */
	import { onMount } from 'svelte';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import HojaInferior from '#lib/componentes/HojaInferior.svelte';
	import Icono from '#lib/componentes/Icono.svelte';
	import Proporcion from '#lib/componentes/Proporcion.svelte';
	import Propuesta from '#lib/componentes/Propuesta.svelte';
	import PropuestaFila from '#lib/componentes/PropuestaFila.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import { concrecion, termometroTema } from '#lib/termometro.js';
	import { barajar } from '#lib/util.js';
	import { colorTema, tinte } from '#lib/visual.js';
	import type { Propuesta as TPropuesta } from '#lib/contrato.gen.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	type Cand = (typeof data.completos)[number];

	let orden = $state<string[] | null>(null);
	onMount(() => (orden = barajar(data.completos.map((x) => x.id))));
	const candidatos = $derived(orden ? orden.map((id) => data.completos.find((x) => x.id === id)!) : data.completos);
	const c = $derived(data.ciudad.id);
	const color = $derived(colorTema(data.tema.id));
	const enfoques = $derived(data.enfoques.filter((e) => e.tema === data.tema.id));

	// Filtro por enfoque
	let enfoque = $state<string | null>(null);
	const de = (cand: Cand) => (cand.propuestas ?? []).filter((p) => !enfoque || p.enfoques.includes(enfoque));
	const conTema = $derived(candidatos.filter((x) => x.propuestas?.length));
	const sin = $derived(candidatos.filter((x) => !x.propuestas?.length));
	const visibles = $derived(conTema.filter((x) => de(x).length));
	const noEnEnfoque = $derived(conTema.filter((x) => !de(x).length));
	const candidatosPor = (eid: string) => conTema.filter((x) => (x.propuestas ?? []).some((p) => p.enfoques.includes(eid))).length;
	const actualEnfoque = $derived(enfoques.find((e) => e.id === enfoque));

	/** Más concretas primero; ante empate, el orden del plan. */
	const ordenadas = (ps: TPropuesta[]) =>
		ps.map((p, i) => ({ p, i })).sort((a, b) => concrecion(b.p) - concrecion(a.p) || a.i - b.i).map((x) => x.p);
	const MOSTRAR = 2;

	// Hoja: lista del candidato → detalle de una propuesta
	let hoja = $state(false);
	let hojaCand = $state<Cand | null>(null);
	let hojaProp = $state<TPropuesta | null>(null);
	const verTodas = (cand: Cand) => {
		hojaCand = cand;
		hojaProp = null;
		hoja = true;
	};
	const verUna = (cand: Cand, p: TPropuesta) => {
		hojaCand = cand;
		hojaProp = p;
		hoja = true;
	};
</script>

<svelte:head><title>{data.tema.nombre} · {data.ciudad.nombre} · termómetro</title></svelte:head>

<section class="relative isolate overflow-hidden">
	<div class="pointer-events-none absolute -top-40 left-1/2 -z-10 size-[28rem] -translate-x-1/2 rounded-full opacity-[0.12] blur-3xl" style="background:{color}"></div>
	<div class="contenedor-ancho pt-5">
		<a href="/{c}/" class="inline-flex items-center gap-1 text-sm text-texto-3 hover:text-texto">
			<Icono nombre="arrow-left" tipo="ui" tam={14} /> Candidatos de {data.ciudad.nombre}
		</a>
		<div class="mt-5 flex items-center gap-4">
			<TemaIcono tema={data.tema.id} icono={data.tema.icono} tam={56} />
			<div class="min-w-0">
				<h1 class="text-3xl leading-tight font-extrabold tracking-tight">{data.tema.nombre}</h1>
				<p class="text-sm text-texto-2">{conTema.length} de {candidatos.length} candidatos proponen algo</p>
			</div>
		</div>

		{#if enfoques.length}
			<div class="mt-6">
				<p class="text-sm font-semibold text-texto-2">¿Cómo lo resolverían?</p>
				<ul class="sin-scrollbar -mx-4 mt-2 flex gap-2 overflow-x-auto px-4 pb-1 text-sm lg:mx-0 lg:flex-wrap lg:px-0" role="group" aria-label="Filtrar por enfoque">
					<li>
						<button
							onclick={() => (enfoque = null)}
							aria-pressed={!enfoque}
							class="rounded-full px-3.5 py-1.5 font-semibold whitespace-nowrap ring-1 transition {!enfoque ? 'text-white ring-transparent' : 'bg-superficie text-texto-2 ring-black/10'}"
							style={!enfoque ? `background:${color}` : ''}
						>
							Todos los enfoques
						</button>
					</li>
					{#each enfoques as e (e.id)}
						{@const sel = enfoque === e.id}
						<li>
							<button
								onclick={() => (enfoque = sel ? null : e.id)}
								aria-pressed={sel}
								title={e.descripcion}
								class="inline-flex items-center gap-1.5 rounded-full py-1.5 pr-3.5 pl-2 font-medium whitespace-nowrap ring-1 transition {sel ? 'text-white ring-transparent' : 'ring-black/[0.06]'}"
								style={sel ? `background:${color}` : `background:${tinte(color)};color:${color}`}
							>
								<Icono nombre={e.icono} tam={16} />
								{e.nombre}
								<span class="text-xs opacity-70">· {candidatosPor(e.id)}</span>
							</button>
						</li>
					{/each}
				</ul>
				{#if actualEnfoque}
					<p class="mt-3 max-w-2xl text-sm text-texto-2">{actualEnfoque.descripcion}</p>
				{/if}
			</div>
		{/if}
	</div>
</section>

<section class="contenedor-ancho mt-6">
	<ul class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 lg:gap-4">
		{#each visibles as cand (cand.id)}
			{@const ps = ordenadas(de(cand))}
			<li class="tarjeta flex flex-col p-4">
				<a href="/{c}/candidatos/{cand.id}/#{data.tema.id}" class="group flex items-center gap-3">
					<Avatar candidato={cand} ciudad={c} tam={44} />
					<span class="min-w-0 flex-1">
						<span class="display block truncate font-bold group-hover:underline">{cand.nombre}</span>
						<span class="block truncate text-xs text-texto-3">Lista {cand.lista} · {cand.organizacion}</span>
					</span>
				</a>
				<div class="mt-3"><Proporcion lectura={termometroTema({ propuestas: ps }, data.tema.id)} {color} /></div>
				<ul class="mt-2 flex-1 divide-y divide-black/[0.05] text-sm">
					{#each ps.slice(0, MOSTRAR) as p (p.id)}
						<li><PropuestaFila propuesta={p} onabrir={() => verUna(cand, p)} /></li>
					{/each}
				</ul>
				{#if ps.length > MOSTRAR}
					<button onclick={() => verTodas(cand)} class="mt-1 self-start text-sm font-semibold" style="color:{color}">
						+ {ps.length - MOSTRAR} propuesta{ps.length - MOSTRAR === 1 ? '' : 's'} más
					</button>
				{/if}
			</li>
		{/each}
	</ul>

	{#if noEnEnfoque.length || sin.length}
		<div class="mt-8 space-y-4 rounded-3xl bg-black/[0.03] p-5 ring-1 ring-black/5">
			{#if noEnEnfoque.length}
				<div>
					<h2 class="text-sm font-bold text-texto-2">Proponen otras cosas en este tema, no «{actualEnfoque?.nombre}»</h2>
					<ul class="mt-2 flex flex-wrap gap-x-4 gap-y-2">
						{#each noEnEnfoque as cand (cand.id)}
							<li class="flex items-center gap-2 text-sm text-texto-3"><Avatar candidato={cand} ciudad={c} tam={26} anillo={false} />{cand.nombre}</li>
						{/each}
					</ul>
				</div>
			{/if}
			{#if sin.length}
				<div>
					<h2 class="text-sm font-bold text-texto-2">Sin propuestas sobre este tema</h2>
					<ul class="mt-2 flex flex-wrap gap-x-4 gap-y-2">
						{#each sin as cand (cand.id)}
							<li class="flex items-center gap-2 text-sm text-texto-3"><Avatar candidato={cand} ciudad={c} tam={26} anillo={false} />{cand.nombre}</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>
	{/if}
</section>

<HojaInferior bind:abierto={hoja} titulo={hojaCand ? `${hojaCand.nombre} · ${data.tema.nombre_corto}` : ''}>
	{#if hojaCand}
		{#if hojaProp}
			{#if de(hojaCand).length > 1}
				<button onclick={() => (hojaProp = null)} class="mb-3 inline-flex items-center gap-1 text-sm font-semibold text-texto-2 hover:text-texto">
					<Icono nombre="arrow-left" tipo="ui" tam={14} /> Todas sus propuestas del tema
				</button>
			{/if}
			{#key hojaProp.id}<Propuesta propuesta={hojaProp} candidato={hojaCand} detalle />{/key}
		{:else}
			<ul class="divide-y divide-black/[0.05]">
				{#each ordenadas(de(hojaCand)) as p (p.id)}
					<li><PropuestaFila propuesta={p} onabrir={() => (hojaProp = p)} /></li>
				{/each}
			</ul>
		{/if}
	{/if}
</HojaInferior>
