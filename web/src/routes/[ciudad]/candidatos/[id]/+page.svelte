<script lang="ts">
	/*
	 * Ficha del candidato, con revelación progresiva:
	 *  1. Resumen (quién es y qué tan concreto es su plan) — fijo a la izquierda en computador.
	 *  2. Lo más concreto de su plan — 3 tarjetas.
	 *  3. Todo el plan como índice de temas plegable, con filas compactas.
	 *  4. La cita, el contexto y los votos solo al tocar una propuesta (hoja inferior / panel lateral).
	 */
	import { onMount } from 'svelte';
	import { slide } from 'svelte/transition';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import HojaInferior from '#lib/componentes/HojaInferior.svelte';
	import Icono from '#lib/componentes/Icono.svelte';
	import Proporcion from '#lib/componentes/Proporcion.svelte';
	import Propuesta from '#lib/componentes/Propuesta.svelte';
	import PropuestaFila from '#lib/componentes/PropuestaFila.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import { concrecion, masConcretas, termometroGlobal } from '#lib/termometro.js';
	import { colorTema } from '#lib/visual.js';
	import type { Propuesta as TPropuesta } from '#lib/contrato.gen.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const cand = $derived(data.candidato);
	const c = $derived(data.ciudad.id);
	const todas = $derived(cand.propuestas ?? []);
	const global = $derived(termometroGlobal(cand));
	const destacadas = $derived(masConcretas(todas));
	const temasCon = $derived(data.temas.filter((t) => todas.some((p) => p.tema === t.id)));
	const temasSin = $derived(data.temas.filter((t) => !temasCon.includes(t)));
	const nombreTema = (id: string) => data.temas.find((t) => t.id === id)?.nombre_corto ?? id;

	// Filtro y acordeón
	let soloConDatos = $state(false);
	let abierto = $state<string | null>(null);
	let completos = $state<Record<string, boolean>>({});
	const MOSTRAR = 5;
	const delTema = (id: string) => todas.filter((p) => p.tema === id && (!soloConDatos || concrecion(p) > 0));
	const visibles = $derived(temasCon.filter((t) => delTema(t.id).length));

	onMount(() => {
		const h = decodeURIComponent(location.hash.slice(1));
		if (temasCon.some((t) => t.id === h)) {
			abierto = h;
			requestAnimationFrame(() => document.getElementById(h)?.scrollIntoView({ block: 'start' }));
		}
	});
	const alternar = (id: string) => {
		abierto = abierto === id ? null : id;
		history.replaceState(history.state, '', abierto ? `#${abierto}` : location.pathname);
	};

	// Detalle
	let hoja = $state(false);
	let actual = $state<TPropuesta | null>(null);
	const abrir = (p: TPropuesta) => {
		actual = p;
		hoja = true;
	};
</script>

<svelte:head><title>{cand.nombre} · Lista {cand.lista} · termómetro</title></svelte:head>

{#snippet sinTemas()}
	{#if temasSin.length && todas.length}
		<section class="rounded-3xl bg-black/[0.03] p-5 ring-1 ring-black/5">
			<h2 class="text-sm font-bold text-texto-2">Su plan no habla de</h2>
			<ul class="mt-3 flex flex-wrap gap-2">
				{#each temasSin as t (t.id)}
					<li class="flex items-center gap-1.5 rounded-full bg-black/[0.04] py-1 pr-3 pl-1 text-sm text-texto-3">
						<TemaIcono tema={t.id} icono={t.icono} tam={22} />
						{t.nombre_corto}
					</li>
				{/each}
			</ul>
		</section>
	{/if}
{/snippet}

<div class="contenedor-ancho pt-5 pb-16 lg:grid lg:grid-cols-[22rem_1fr] lg:items-start lg:gap-12">
	<!-- 1. Resumen -->
	<aside class="space-y-5 lg:sticky lg:top-20">
		<a href="/{c}/" class="inline-flex items-center gap-1 text-sm text-texto-3 hover:text-texto">
			<Icono nombre="arrow-left" tipo="ui" tam={14} /> Candidatos de {data.ciudad.nombre}
		</a>

		<header class="flex items-center gap-4">
			<Avatar candidato={cand} ciudad={c} tam={76} />
			<div class="min-w-0">
				<h1 class="text-2xl leading-tight font-extrabold tracking-tight text-balance">{cand.nombre}</h1>
				<p class="text-sm text-texto-2">Lista {cand.lista} · {cand.organizacion}</p>
			</div>
		</header>

		{#if todas.length}
			<section class="tarjeta p-5">
				<Proporcion lectura={global} desglose />
				{#if global.fueraDeCompetencia}
					<p class="mt-4 flex items-center gap-1.5 text-xs text-alerta">
						<Icono nombre="warning" tipo="ui" tam={14} />
						{global.fueraDeCompetencia} propuesta{global.fueraDeCompetencia > 1 ? 's no les corresponden' : ' no le corresponde'} al Municipio
					</p>
				{/if}
				<p class="mt-4 border-t border-black/5 pt-3 text-xs text-texto-3">
					Plan de {global.propuestas} propuestas en {temasCon.length} temas.
					<a href="/metodologia/" class="font-semibold text-texto-2 underline-offset-2 hover:underline">Cómo se mide</a>
				</p>
			</section>
		{/if}

		{#if cand.plan_trabajo.disponible && cand.plan_trabajo.fuente}
			<a
				href={cand.plan_trabajo.fuente.url}
				target="_blank"
				rel="noopener"
				class="flex items-center justify-center gap-1.5 rounded-2xl bg-black/[0.06] py-2.5 text-sm font-semibold hover:bg-black/[0.1]"
			>
				<Icono nombre="file-pdf" tipo="ui" tam={16} /> Plan oficial del CNE · {cand.plan_trabajo.paginas} págs
			</a>
		{:else if cand.plan_trabajo.nota}
			<p class="rounded-2xl bg-black/[0.05] p-3 text-sm text-texto-2">{cand.plan_trabajo.nota}</p>
		{/if}

		<div class="hidden lg:block">{@render sinTemas()}</div>
	</aside>

	<div class="mt-10 min-w-0 lg:mt-9">
		{#if todas.length}
			<!-- 2. Lo más concreto -->
			<section>
				<h2 class="text-xl font-extrabold tracking-tight">Lo más concreto de su plan</h2>
				{#if destacadas.length}
					<ul class="sin-scrollbar -mx-4 mt-3 flex snap-x snap-mandatory gap-3 overflow-x-auto px-4 pb-1 lg:mx-0 lg:grid lg:grid-cols-3 lg:overflow-visible lg:px-0">
						{#each destacadas as p (p.id)}
							<li class="w-[80%] shrink-0 snap-start lg:w-auto">
								<button onclick={() => abrir(p)} class="tarjeta group flex h-full w-full flex-col p-4 text-left transition hover:ring-black/20">
									<span class="flex items-center gap-1.5 text-xs font-semibold" style="color:{colorTema(p.tema)}">
										<TemaIcono tema={p.tema} icono={data.temas.find((t) => t.id === p.tema)?.icono ?? 'circle'} tam={20} />
										{nombreTema(p.tema)}
									</span>
									<span class="mt-2 line-clamp-4 flex-1 text-sm leading-snug">{p.resumen}</span>
									<span class="mt-3 flex flex-wrap gap-1 text-[11px] font-medium">
										{#each [['target', 'cuánto', p.rubrica.meta.valor], ['calendar-check', 'cuándo', p.rubrica.plazo.valor], ['coins', 'con qué dinero', p.rubrica.financiamiento.valor]] as const as [ic, n, si] (n)}
											{#if si}<span class="inline-flex items-center gap-1 rounded-full bg-acento/10 px-1.5 py-0.5 text-acento"><Icono nombre={ic} tipo="ui" tam={12} />{n}</span>{/if}
										{/each}
									</span>
									<span class="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-texto-2 group-hover:text-texto">
										<Icono nombre="quotes" tipo="ui" tam={13} /> Ver la cita
									</span>
								</button>
							</li>
						{/each}
					</ul>
				{:else}
					<p class="mt-3 rounded-2xl bg-black/[0.035] p-4 text-sm text-texto-2">
						Ninguna propuesta de su plan dice cuánto, cuándo ni con qué dinero.
					</p>
				{/if}
			</section>

			<!-- 3. Todo el plan por tema -->
			<section class="mt-10">
				<div class="flex flex-wrap items-end justify-between gap-3">
					<h2 class="text-xl font-extrabold tracking-tight">Todo su plan, por tema</h2>
					<div class="flex rounded-full bg-black/[0.05] p-1 text-xs font-semibold" role="group" aria-label="Filtrar propuestas">
						<button class="rounded-full px-3 py-1.5 {!soloConDatos ? 'bg-superficie shadow-sm' : 'text-texto-3'}" aria-pressed={!soloConDatos} onclick={() => (soloConDatos = false)}>
							Todas
						</button>
						<button class="rounded-full px-3 py-1.5 {soloConDatos ? 'bg-superficie shadow-sm' : 'text-texto-3'}" aria-pressed={soloConDatos} onclick={() => (soloConDatos = true)}>
							Solo con algún dato
						</button>
					</div>
				</div>

				{#if visibles.length}
					<ul class="tarjeta mt-4 divide-y divide-black/[0.06] overflow-hidden">
						{#each visibles as t (t.id)}
							{@const ps = delTema(t.id)}
							{@const conDatos = ps.filter((p) => concrecion(p) > 0).length}
							{@const esAbierto = abierto === t.id}
							<li id={t.id} class="scroll-mt-20">
								<button
									onclick={() => alternar(t.id)}
									aria-expanded={esAbierto}
									class="flex w-full items-center gap-3 px-4 py-3.5 text-left hover:bg-black/[0.02]"
								>
									<TemaIcono tema={t.id} icono={t.icono} tam={40} />
									<span class="min-w-0 flex-1">
										<span class="block font-bold">{t.nombre}</span>
										<span class="block text-xs text-texto-3">
											{ps.length} propuesta{ps.length === 1 ? '' : 's'}{#if !soloConDatos} · {conDatos ? `${conDatos} con algún dato` : 'ninguna con datos'}{/if}
										</span>
									</span>
									<span class="transition {esAbierto ? 'rotate-180' : ''}"><Icono nombre="caret-down" tipo="ui" tam={16} class="text-texto-3" /></span>
								</button>
								{#if esAbierto}
									<div transition:slide={{ duration: 200 }} class="px-4 pb-3">
										<ul class="divide-y divide-black/[0.05] border-t border-black/[0.05]">
											{#each completos[t.id] ? ps : ps.slice(0, MOSTRAR) as p (p.id)}
												<li><PropuestaFila propuesta={p} onabrir={() => abrir(p)} /></li>
											{/each}
										</ul>
										<div class="flex flex-wrap items-center justify-between gap-2 pt-2">
											{#if ps.length > MOSTRAR && !completos[t.id]}
												<button class="text-sm font-semibold text-acento" onclick={() => (completos[t.id] = true)}>
													Ver las {ps.length}
												</button>
											{:else}<span></span>{/if}
											<a href="/{c}/temas/{t.id}/" class="inline-flex items-center gap-1 text-sm font-semibold text-texto-2 hover:text-texto">
												Comparar con los demás <Icono nombre="arrow-right" tipo="ui" tam={14} />
											</a>
										</div>
									</div>
								{/if}
							</li>
						{/each}
					</ul>
				{:else}
					<p class="mt-4 rounded-2xl bg-black/[0.035] p-4 text-sm text-texto-2">Ninguna propuesta trae datos.</p>
				{/if}
			</section>

			<div class="mt-10 lg:hidden">{@render sinTemas()}</div>
		{:else if cand.plan_trabajo.disponible}
			<p class="flex items-start gap-2 rounded-2xl bg-alerta/10 p-4 text-sm text-alerta ring-1 ring-alerta/20">
				<Icono nombre="info" tipo="ui" tam={18} /> Estamos procesando este plan de trabajo. Las propuestas aparecerán aquí pronto.
			</p>
		{/if}
	</div>
</div>

<HojaInferior bind:abierto={hoja} titulo={actual ? nombreTema(actual.tema) : ''}>
	{#if actual}
		{#key actual.id}
			<Propuesta propuesta={actual} candidato={cand} detalle />
		{/key}
	{/if}
</HojaInferior>
