<script lang="ts">
	/**
	 * Flujo "¿Quién propone lo que te importa?"
	 *  - Móvil: inmersivo tipo stories, una decisión por pantalla, botones en la zona del pulgar.
	 *  - Escritorio (≥1024px): pantalla dividida. Contexto + acción principal a la izquierda
	 *    (siempre visible), contenido interactivo a la derecha sin scroll, atajos de teclado
	 *    y el "¿Por qué?" como panel lateral.
	 */
	import { onMount } from 'svelte';
	import { fly, fade, scale } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import { replaceState } from '$app/navigation';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import BarraAfinidad from '#lib/componentes/BarraAfinidad.svelte';
	import HojaInferior from '#lib/componentes/HojaInferior.svelte';
	import Icono from '#lib/componentes/Icono.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import { aURL, calcularAfinidad, desdeURL, type Resultado, type Seleccion } from '#lib/afinidad.js';
	import { compartirHistoria } from '#lib/historia.js';
	import type { CandidatoMin } from '#lib/termometro.js';
	import { barajar, pct } from '#lib/util.js';
	import { colorTema, tinte } from '#lib/visual.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const MIN = 3;
	const MAX = 5;
	const c = $derived(data.ciudad.id);
	const temaPorId = $derived(new Map(data.temas.map((t) => [t.id, t])));
	const enfoquesDe = (t: string) => data.enfoques.filter((e) => e.tema === t);
	const enfoquePorId = $derived(new Map(data.enfoques.map((e) => [e.id, e])));
	const totalPaginas = $derived(data.candidatos.reduce((s, x) => s + (x.plan_trabajo.paginas ?? 0), 0));
	const totalPropuestas = $derived(data.candidatos.reduce((s, x) => s + (x.propuestas?.length ?? 0), 0));
	const conPlan = $derived(data.candidatos.filter((x) => x.plan_trabajo.disponible).length);

	type Pantalla = 'temas' | 'enfoque' | 'calculando' | 'resultado';
	let pantalla = $state<Pantalla>('temas');
	let temas = $state<string[]>([]);
	let enfoques = $state<Record<string, string[]>>({});
	let iTema = $state(0);
	let elegidoAhora = $state<string | null>(null);
	let resultados = $state<Resultado<CandidatoMin>[]>([]);
	let detalle = $state<Resultado<CandidatoMin> | null>(null);
	let hojaAbierta = $state(false);
	let aviso = $state<string | null>(null);
	let mensajeCalculo = $state(0);
	let direccion = $state(1);

	const temasConEnfoques = $derived(temas.filter((t) => enfoquesDe(t).length));
	const temaActual = $derived(temasConEnfoques[iTema]);
	const segmentos = $derived(1 + Math.max(temasConEnfoques.length, 1) + 1);
	const segmentoActual = $derived(pantalla === 'temas' ? 0 : pantalla === 'enfoque' ? 1 + iTema : segmentos - 1);

	const vibrar = () => navigator.vibrate?.(8);
	const ir = (p: Pantalla, dir = 1) => {
		direccion = dir;
		pantalla = p;
		document.getElementById('lienzo')?.scrollTo({ top: 0 });
	};

	function alternarTema(id: string) {
		vibrar();
		if (temas.includes(id)) temas = temas.filter((t) => t !== id);
		else if (temas.length < MAX) temas = [...temas, id];
	}
	function mover(i: number, d: -1 | 1) {
		const j = i + d;
		if (j < 0 || j >= temas.length) return;
		const t = [...temas];
		[t[i], t[j]] = [t[j], t[i]];
		temas = t;
	}

	function listoTemas() {
		if (temas.length < MIN) return;
		vibrar();
		enfoques = Object.fromEntries(Object.entries(enfoques).filter(([t]) => temas.includes(t)));
		iTema = 0;
		if (temasConEnfoques.length) ir('enfoque');
		else calcular();
	}

	function responder(valor: string[], id: string) {
		if (!temaActual || elegidoAhora) return;
		vibrar();
		elegidoAhora = id;
		enfoques = { ...enfoques, [temaActual]: valor };
		setTimeout(() => {
			elegidoAhora = null;
			if (iTema < temasConEnfoques.length - 1) {
				direccion = 1;
				iTema++;
			} else calcular();
		}, 300);
	}

	function atras() {
		vibrar();
		if (pantalla === 'enfoque' && iTema > 0) {
			direccion = -1;
			iTema--;
		} else ir('temas', -1);
	}

	function calcular(animar = true) {
		const sel: Seleccion = { temas, enfoques };
		resultados = calcularAfinidad(barajar(data.candidatos), sel);
		replaceState(`?${aURL(sel)}`, {});
		if (!animar || matchMedia('(prefers-reduced-motion: reduce)').matches) return ir('resultado');
		ir('calculando');
		mensajeCalculo = 0;
		const t = setInterval(() => mensajeCalculo++, 600);
		setTimeout(() => {
			clearInterval(t);
			vibrar();
			ir('resultado');
		}, 2200);
	}

	function verPorQue(r: Resultado<CandidatoMin>) {
		vibrar();
		detalle = r;
		hojaAbierta = true;
	}

	function repetir() {
		replaceState('?', {});
		ir('temas', -1);
	}

	async function compartirImagen() {
		vibrar();
		const r = await compartirHistoria({
			ciudad: data.ciudad.nombre,
			temas: temas.map((t) => ({ id: t, icono: temaPorId.get(t)!.icono, nombre: temaPorId.get(t)!.nombre_corto })),
			url: `${location.origin}/${c}/`
		});
		if (r === 'descargado') mostrarAviso('Imagen guardada · súbela a tus historias');
	}
	async function copiarLink() {
		vibrar();
		await navigator.clipboard.writeText(location.href);
		mostrarAviso('Link copiado');
	}
	function mostrarAviso(t: string) {
		aviso = t;
		setTimeout(() => (aviso = null), 2500);
	}

	/** Atajos de teclado (escritorio). */
	function teclado(e: KeyboardEvent) {
		if (hojaAbierta || e.metaKey || e.ctrlKey || e.altKey) return;
		if ((e.target as HTMLElement)?.closest('input, textarea')) return;
		const k = e.key.toLowerCase();
		if (pantalla === 'temas' && k === 'enter') {
			e.preventDefault();
			listoTemas();
		} else if (pantalla === 'enfoque' && temaActual) {
			const opciones = enfoquesDe(temaActual);
			const n = Number(k);
			if (n >= 1 && n <= opciones.length) responder([opciones[n - 1].id], opciones[n - 1].id);
			else if (k === 't') responder(opciones.map((o) => o.id), '__todas');
			else if (k === 'n') responder([], '__nose');
			else if (k === 'arrowleft' || k === 'backspace') atras();
		}
	}

	onMount(() => {
		const sel = desdeURL(
			location.search.slice(1),
			new Set(data.temas.map((t) => t.id)),
			new Map(data.enfoques.map((e) => [e.id, e.tema]))
		);
		if (sel.temas.length >= MIN) {
			temas = sel.temas;
			enfoques = sel.enfoques;
			calcular(false);
		}
	});

	const mensajes = $derived([
		`Leyendo ${totalPaginas.toLocaleString('es-EC')} páginas de ${conPlan} planes de trabajo`,
		`Revisando ${totalPropuestas} propuestas`,
		'Midiendo qué tan concretas son',
		'Cruzando con lo que te importa'
	]);

	const grupos = $derived(
		resultados
			.filter((r) => !r.sinPlan)
			.reduce<Resultado<CandidatoMin>[][]>((gs, r) => {
				(gs[r.grupo] ??= []).push(r);
				return gs;
			}, [])
			.filter(Boolean)
	);
	const sinPlan = $derived(resultados.filter((r) => r.sinPlan));
	const hayPropuestas = $derived(totalPropuestas > 0);
</script>

<svelte:window onkeydown={teclado} />

<svelte:head>
	<title>¿Quién propone lo que te importa? · {data.ciudad.nombre}</title>
</svelte:head>

{#snippet tecla(t: string)}
	<kbd class="ml-1 hidden min-w-6 place-items-center rounded-md bg-black/[0.06] px-1.5 py-0.5 font-sans text-[11px] font-semibold text-texto-3 ring-1 ring-black/10 lg:inline-grid">{t}</kbd>
{/snippet}

{#snippet chipsPrioridad()}
	<ul class="flex flex-wrap gap-1.5">
		{#each temas as id, i (id)}
			<li class="flex items-center gap-1.5 rounded-full py-1 pr-2.5 pl-1 text-xs font-semibold" style="background:{tinte(colorTema(id), 0.12)};color:{colorTema(id)}">
				<span class="display grid size-5 place-items-center rounded-full text-[11px] font-extrabold text-white" style="background:{colorTema(id)}">{i + 1}</span>
				{temaPorId.get(id)?.nombre_corto}
			</li>
		{/each}
	</ul>
{/snippet}

<div id="lienzo" class="fixed inset-0 z-50 overflow-y-auto bg-fondo text-texto">
	<div class="pointer-events-none fixed -top-40 left-1/2 size-[30rem] -translate-x-1/2 rounded-full opacity-[0.10] blur-3xl fondo-aurora lg:hidden"></div>

	<div class="relative mx-auto flex min-h-full max-w-lg flex-col px-4 lg:max-w-6xl lg:px-10">
		<!-- Progreso tipo stories + cerrar -->
		<div class="sticky top-0 z-10 -mx-4 bg-fondo/85 px-4 pt-3 pb-2 backdrop-blur-xl lg:-mx-10 lg:px-10 lg:pt-5">
			<div class="flex gap-1" aria-hidden="true">
				{#each Array(segmentos) as _, i (i)}
					<div class="h-[3px] flex-1 overflow-hidden rounded-full bg-black/10">
						<div
							class="h-full rounded-full bg-texto transition-all duration-500"
							style="width:{i < segmentoActual ? 100 : i === segmentoActual ? (pantalla === 'calculando' ? 60 : 100) : 0}%"
						></div>
					</div>
				{/each}
			</div>
			<div class="mt-2 flex h-9 items-center justify-between">
				{#if pantalla === 'enfoque'}
					<button onclick={atras} class="-ml-2 flex h-9 items-center gap-1 rounded-full px-2 text-texto-2 hover:bg-black/[0.05]" aria-label="Atrás">
						<Icono nombre="arrow-left" tipo="ui" tam={20} />
						<span class="hidden text-sm font-medium lg:inline">Atrás</span>
						{@render tecla('←')}
					</button>
				{:else}
					<span class="display text-sm font-semibold text-texto-2">{data.ciudad.nombre}{data.ciudad.es_mock ? ' · demo' : ''}</span>
				{/if}
				<a href="/{c}/" class="-mr-2 grid size-9 place-items-center rounded-full text-texto-2 hover:bg-black/[0.05]" aria-label="Cerrar">
					<Icono nombre="x" tipo="ui" tam={20} />
				</a>
			</div>
		</div>

		{#key pantalla + iTema}
			<section class="flex flex-1 flex-col" in:fly={{ x: 60 * direccion, duration: 280, delay: 90 }} out:fade={{ duration: 80 }}>
				<!-- ── TEMAS ───────────────────────────────────────────── -->
				{#if pantalla === 'temas'}
					<div class="lg:mt-6 lg:grid lg:flex-1 lg:grid-cols-[minmax(0,5fr)_minmax(0,8fr)] lg:items-start lg:gap-14">
						<!-- Izquierda: contexto + acción -->
						<div class="lg:sticky lg:top-24">
							<h1 class="mt-4 text-[2.5rem] leading-[1] font-extrabold tracking-tight text-balance lg:mt-0 lg:text-6xl">
								¿Qué te importa <span class="texto-aurora">más</span>?
							</h1>
							<p class="mt-2 text-texto-2 lg:mt-4 lg:text-lg">Toca de {MIN} a {MAX}. El primero que toques es tu prioridad #1.</p>

							{#if !hayPropuestas}
								<p class="mt-4 flex items-start gap-2 rounded-2xl bg-alerta/10 p-3 text-sm text-alerta">
									<Icono nombre="info" tipo="ui" tam={16} /> Aún procesamos los planes de {data.ciudad.nombre}. El resultado todavía no refleja propuestas.
								</p>
							{/if}

							<!-- Prioridad (escritorio) -->
							<div class="mt-8 hidden lg:block">
								<p class="text-xs font-semibold tracking-wider text-texto-3 uppercase">Tu prioridad</p>
								<ol class="mt-3 space-y-2">
									{#each temas as id, i (id)}
										{@const t = temaPorId.get(id)!}
										<li class="tarjeta flex items-center gap-3 py-2 pr-2 pl-3" in:fly={{ x: -12, duration: 200 }}>
											<span class="display grid size-7 place-items-center rounded-full text-sm font-extrabold text-white" style="background:{colorTema(id)}">{i + 1}</span>
											<TemaIcono tema={id} icono={t.icono} tam={30} />
											<span class="flex-1 font-semibold">{t.nombre}</span>
											<button class="grid size-8 place-items-center rounded-full text-texto-3 hover:bg-black/[0.05] hover:text-texto disabled:opacity-25" disabled={i === 0} onclick={() => mover(i, -1)} aria-label="Subir {t.nombre}">
												<Icono nombre="arrow-left" tipo="ui" tam={14} class="rotate-90" />
											</button>
											<button class="grid size-8 place-items-center rounded-full text-texto-3 hover:bg-black/[0.05] hover:text-texto disabled:opacity-25" disabled={i === temas.length - 1} onclick={() => mover(i, 1)} aria-label="Bajar {t.nombre}">
												<Icono nombre="arrow-left" tipo="ui" tam={14} class="-rotate-90" />
											</button>
											<button class="grid size-8 place-items-center rounded-full text-texto-3 hover:bg-black/[0.05] hover:text-texto" onclick={() => alternarTema(id)} aria-label="Quitar {t.nombre}">
												<Icono nombre="x" tipo="ui" tam={14} />
											</button>
										</li>
									{/each}
									{#each Array(Math.max(0, MIN - temas.length)) as _, i (i)}
										<li class="flex h-[3.25rem] items-center gap-3 rounded-3xl border-2 border-dashed border-black/10 px-3 text-sm text-texto-3">
											<span class="display grid size-7 place-items-center rounded-full bg-black/[0.05] text-sm font-bold">{temas.length + i + 1}</span>
											Elige un tema
										</li>
									{/each}
								</ol>
								<button
									type="button"
									disabled={temas.length < MIN}
									onclick={listoTemas}
									class="mt-6 flex w-full items-center justify-center gap-2 rounded-full bg-texto py-4 text-lg font-bold text-white transition hover:bg-black active:scale-[0.98] disabled:bg-black/[0.06] disabled:text-texto-3"
								>
									{#if temas.length < MIN}
										Elige {MIN - temas.length} más
									{:else}
										Listo <Icono nombre="arrow-right" tipo="ui" tam={20} />
										<kbd class="ml-1 rounded-md bg-white/15 px-1.5 py-0.5 font-sans text-xs">Enter ↵</kbd>
									{/if}
								</button>
							</div>
						</div>

						<!-- Derecha: los 12 temas, sin scroll en escritorio -->
						<ul class="mt-6 grid grid-cols-3 gap-2.5 pb-44 lg:mt-0 lg:grid-cols-4 lg:gap-3 lg:pb-10">
							{#each data.temas as t (t.id)}
								{@const pos = temas.indexOf(t.id)}
								{@const elegido = pos >= 0}
								{@const color = colorTema(t.id)}
								<li>
									<button
										type="button"
										onclick={() => alternarTema(t.id)}
										aria-pressed={elegido}
										disabled={!elegido && temas.length >= MAX}
										class="relative flex aspect-[4/5] w-full flex-col items-center justify-center gap-2.5 rounded-[1.6rem] p-2 text-center text-[13px] font-semibold transition duration-200 active:scale-90 disabled:opacity-25 lg:aspect-auto lg:h-[8.5rem] lg:text-sm lg:active:scale-95
											{elegido ? 'animar-pop' : 'bg-superficie shadow-[0_1px_2px_rgba(21,23,28,0.04)] ring-1 ring-black/[0.07] hover:-translate-y-0.5 hover:shadow-[0_8px_24px_-12px_rgba(21,23,28,0.25)] hover:ring-black/15'}"
										style={elegido ? `background:${color};color:#ffffff;box-shadow:0 10px 30px -10px ${color}` : ''}
									>
										<span class="grid size-12 place-items-center rounded-full transition" style="background:{elegido ? 'rgba(255,255,255,0.22)' : tinte(color)};color:{elegido ? '#ffffff' : color}">
											<Icono nombre={t.icono} tam={28} />
										</span>
										<span class="leading-tight">{t.nombre_corto}</span>
										{#if elegido}
											<span in:scale={{ duration: 260, easing: backOut }} class="display absolute top-2 right-2 grid size-7 place-items-center rounded-full bg-fondo text-sm font-extrabold" style="color:{color}">
												{pos + 1}
											</span>
										{/if}
									</button>
								</li>
							{/each}
						</ul>
					</div>

					<!-- Barra inferior (solo móvil) -->
					<div class="fixed inset-x-0 bottom-0 z-10 bg-gradient-to-t from-fondo via-fondo/95 to-transparent pt-12 pb-[max(1rem,env(safe-area-inset-bottom))] lg:hidden">
						<div class="mx-auto max-w-lg px-4">
							{#if temas.length}
								<ol class="sin-scrollbar mb-3 flex gap-1.5 overflow-x-auto" aria-label="Tu orden de prioridad">
									{#each temas as id, i (id)}
										{@const t = temaPorId.get(id)!}
										<li in:fly={{ y: 10, duration: 200 }}>
											<button
												onclick={() => alternarTema(id)}
												class="flex items-center gap-1.5 rounded-full py-1 pr-2.5 pl-1 text-xs font-semibold whitespace-nowrap"
												style="background:{tinte(colorTema(id), 0.12)};color:{colorTema(id)}"
												aria-label="Quitar {t.nombre}"
											>
												<span class="display grid size-5 place-items-center rounded-full text-[11px] font-extrabold text-white" style="background:{colorTema(id)}">{i + 1}</span>
												{t.nombre_corto}
												<Icono nombre="x" tipo="ui" tam={11} />
											</button>
										</li>
									{/each}
								</ol>
							{/if}
							<button
								type="button"
								disabled={temas.length < MIN}
								onclick={listoTemas}
								class="flex w-full items-center justify-center gap-2 rounded-full bg-texto py-4 text-lg font-bold text-white transition active:scale-95 disabled:bg-black/[0.06] disabled:text-texto-3"
							>
								{#if temas.length < MIN}
									Elige {MIN - temas.length} más
								{:else}
									Listo <Icono nombre="arrow-right" tipo="ui" tam={20} />
								{/if}
							</button>
						</div>
					</div>

				<!-- ── ENFOQUE ─────────────────────────────────────────── -->
				{:else if pantalla === 'enfoque' && temaActual}
					{@const t = temaPorId.get(temaActual)!}
					{@const color = colorTema(temaActual)}
					{@const opciones = enfoquesDe(temaActual)}
					<div class="flex flex-1 flex-col lg:mt-6 lg:grid lg:flex-none lg:grid-cols-[minmax(0,5fr)_minmax(0,8fr)] lg:items-start lg:gap-14">
						<div class="lg:sticky lg:top-24">
							<div class="mt-5 flex items-center gap-2.5 lg:mt-0">
								<TemaIcono tema={t.id} icono={t.icono} tam={34} />
								<p class="text-sm font-semibold" style="color:{color}">{t.nombre} · {iTema + 1} de {temasConEnfoques.length}</p>
							</div>
							<h1 class="mt-3 text-[2.5rem] leading-[1] font-extrabold tracking-tight text-balance lg:mt-5 lg:text-6xl">¿Qué harías primero?</h1>
							<p class="mt-2 text-texto-2 lg:mt-4 lg:text-lg">Las opciones salen de lo que proponen los candidatos.</p>

							<!-- Alternativas (escritorio) -->
							<div class="mt-8 hidden gap-2 lg:flex">
								<button type="button" onclick={() => responder(opciones.map((e) => e.id), '__todas')} class="flex flex-1 items-center justify-center gap-1.5 rounded-full bg-superficie py-3.5 font-semibold ring-1 ring-black/10 transition hover:ring-black/25 {elegidoAhora === '__todas' ? 'bg-texto text-white' : ''}">
									<Icono nombre="thumbs-up" tipo="ui" tam={18} /> Todas {@render tecla('T')}
								</button>
								<button type="button" onclick={() => responder([], '__nose')} class="flex flex-1 items-center justify-center gap-1.5 rounded-full bg-superficie py-3.5 font-semibold ring-1 ring-black/10 transition hover:ring-black/25 {elegidoAhora === '__nose' ? 'bg-texto text-white' : ''}">
									<Icono nombre="question" tipo="ui" tam={18} /> Ni idea {@render tecla('N')}
								</button>
							</div>
						</div>

						<ul class="mt-6 space-y-3 lg:mt-0">
							{#each opciones as e, i (e.id)}
								{@const activo = elegidoAhora === e.id}
								<li in:fly={{ y: 24, duration: 260, delay: 120 + i * 70 }}>
									<button
										type="button"
										onclick={() => responder([e.id], e.id)}
										class="group flex w-full items-center gap-4 rounded-[1.6rem] p-4 text-left transition duration-200 active:scale-[0.97] lg:p-5
											{activo ? 'animar-pop' : 'bg-superficie shadow-[0_1px_2px_rgba(21,23,28,0.04)] ring-1 ring-black/[0.07] hover:-translate-y-0.5 hover:shadow-[0_10px_28px_-14px_rgba(21,23,28,0.3)] hover:ring-black/15'}"
										style={activo ? `background:${color};color:#ffffff` : ''}
									>
										<span class="grid size-14 shrink-0 place-items-center rounded-2xl lg:size-16" style="background:{activo ? 'rgba(255,255,255,0.22)' : tinte(color)};color:{activo ? '#ffffff' : color}">
											<Icono nombre={e.icono} tam={30} />
										</span>
										<span class="flex-1">
											<span class="display block text-lg leading-tight font-bold lg:text-xl">{e.nombre}</span>
											<span class="mt-0.5 block text-sm {activo ? 'text-white/80' : 'text-texto-3'}">{e.descripcion}</span>
										</span>
										<kbd class="hidden size-8 shrink-0 place-items-center rounded-lg font-sans text-sm font-bold ring-1 lg:grid {activo ? 'ring-white/40' : 'text-texto-3 ring-black/10 group-hover:text-texto'}">{i + 1}</kbd>
									</button>
								</li>
							{/each}
						</ul>
					</div>

					<!-- Alternativas (móvil) -->
					<div class="mt-auto grid grid-cols-2 gap-2 pt-8 pb-[max(1rem,env(safe-area-inset-bottom))] lg:hidden">
						<button
							type="button"
							onclick={() => responder(opciones.map((e) => e.id), '__todas')}
							class="flex items-center justify-center gap-1.5 rounded-full py-3.5 font-semibold ring-1 transition active:scale-95 {elegidoAhora === '__todas' ? 'bg-texto text-white ring-texto' : 'ring-black/15 hover:bg-black/[0.04]'}"
						>
							<Icono nombre="thumbs-up" tipo="ui" tam={18} /> Todas
						</button>
						<button
							type="button"
							onclick={() => responder([], '__nose')}
							class="flex items-center justify-center gap-1.5 rounded-full py-3.5 font-semibold ring-1 transition active:scale-95 {elegidoAhora === '__nose' ? 'bg-texto text-white ring-texto' : 'ring-black/15 hover:bg-black/[0.04]'}"
						>
							<Icono nombre="question" tipo="ui" tam={18} /> Ni idea
						</button>
					</div>

				<!-- ── CALCULANDO ──────────────────────────────────────── -->
				{:else if pantalla === 'calculando'}
					<div class="flex flex-1 flex-col items-center justify-center text-center">
						<div class="relative">
							<div class="relative h-60 w-16 overflow-hidden rounded-full bg-black/[0.05] ring-1 ring-black/10">
								<div class="absolute inset-x-0 bottom-0 animate-[llenar_2.2s_cubic-bezier(.2,.8,.2,1)_forwards] rounded-full fondo-aurora"></div>
							</div>
							<div class="absolute -bottom-6 left-1/2 size-24 -translate-x-1/2 rounded-full fondo-aurora opacity-30 blur-2xl"></div>
						</div>
						<div class="mt-12 flex gap-1.5" aria-hidden="true">
							{#each mensajes as _, i (i)}
								<span class="h-1 rounded-full transition-all duration-300 {i <= mensajeCalculo ? 'w-6 bg-acento' : 'w-2 bg-black/10'}"></span>
							{/each}
						</div>
						{#key mensajeCalculo}
							<p class="display mt-5 h-16 max-w-xs text-xl font-bold text-balance lg:max-w-md lg:text-2xl" in:fly={{ y: 12, duration: 250 }} role="status">
								{mensajes[Math.min(mensajeCalculo, mensajes.length - 1)]}
							</p>
						{/key}
					</div>

				<!-- ── RESULTADO ───────────────────────────────────────── -->
				{:else if pantalla === 'resultado'}
					<div class="lg:mt-6 lg:grid lg:grid-cols-[minmax(0,5fr)_minmax(0,8fr)] lg:items-start lg:gap-14">
						<!-- Izquierda: resumen + acciones, siempre visibles -->
						<div class="lg:sticky lg:top-24">
							<h1 class="mt-4 text-[2.5rem] leading-[1] font-extrabold tracking-tight text-balance lg:mt-0 lg:text-6xl">
								Quién propone <span class="texto-aurora">lo que te importa</span>
							</h1>
							<div class="mt-4">{@render chipsPrioridad()}</div>

							<div class="mt-8 hidden space-y-2 lg:block">
								<button type="button" onclick={compartirImagen} class="flex w-full items-center justify-center rounded-full p-[2px] fondo-aurora transition active:scale-[0.98]">
									<span class="flex w-full items-center justify-center gap-2 rounded-full bg-superficie py-3.5 text-lg font-bold">
										<Icono nombre="instagram-logo" tipo="ui" tam={20} /> Compartir mis prioridades
									</span>
								</button>
								<div class="grid grid-cols-2 gap-2 text-sm">
									<button type="button" onclick={copiarLink} class="flex items-center justify-center gap-1.5 rounded-full bg-superficie py-3 font-semibold ring-1 ring-black/10 hover:ring-black/25">
										<Icono nombre="link" tipo="ui" tam={16} /> Copiar link
									</button>
									<button type="button" onclick={repetir} class="flex items-center justify-center gap-1.5 rounded-full bg-superficie py-3 font-semibold ring-1 ring-black/10 hover:ring-black/25">
										<Icono nombre="arrow-counter-clockwise" tipo="ui" tam={16} /> Otra vez
									</button>
								</div>
								<p class="pt-4 text-xs text-texto-3">
									No es una recomendación de voto. Mide quién propone lo que priorizaste y qué tan concreto es, según sus
									planes oficiales. <a href="/metodologia/" class="underline">Cómo se calcula</a>
								</p>
							</div>
						</div>

						<!-- Derecha: ranking -->
						<div class="mt-7 space-y-4 lg:mt-0 lg:pb-12">
							{#each grupos as grupo, gi (gi)}
								<section class={grupo.length > 1 ? 'rounded-[2rem] p-1.5 ring-1 ring-black/10 ring-inset' : ''}>
									{#if grupo.length > 1}
										<p class="flex items-center gap-1.5 px-3 pt-2 pb-2 text-xs font-semibold tracking-wide text-texto-2 uppercase">
											<Icono nombre="scales" tipo="ui" tam={14} /> Empate técnico · menos de 5 puntos
										</p>
									{/if}
									<ol class="space-y-2">
										{#each grupo as r, i (r.candidato.id)}
											{@const n = gi * 3 + i}
											{@const primero = gi === 0}
											<li in:fly={{ y: 40, duration: 450, delay: 150 + n * 110, easing: backOut }}>
												<button
													type="button"
													onclick={() => verPorQue(r)}
													class="group w-full rounded-[1.6rem] p-4 text-left transition active:scale-[0.98] lg:p-5 lg:hover:-translate-y-0.5 lg:hover:shadow-[0_12px_32px_-16px_rgba(21,23,28,0.3)]
														{primero ? 'bg-superficie shadow-[0_6px_24px_-12px_rgba(15,118,110,0.35)] ring-2 ring-acento/30' : 'bg-superficie ring-1 ring-black/[0.06]'}"
												>
													<span class="flex items-center gap-3">
														<Avatar candidato={r.candidato} ciudad={c} tam={primero ? 58 : 46} anillo={primero} />
														<span class="min-w-0 flex-1">
															<span class="display block truncate {primero ? 'text-lg' : ''} font-bold">{r.candidato.nombre}</span>
															<span class="block truncate text-xs text-texto-3">Lista {r.candidato.lista} · {r.candidato.organizacion}</span>
														</span>
													</span>
													<span class="mt-3 block"><BarraAfinidad valor={r.afinidad} retraso={300 + n * 110} destacado={primero} /></span>
													<span class="mt-1 flex items-center gap-1 text-sm font-semibold text-texto-2 group-hover:text-texto">
														¿Por qué? <Icono nombre="caret-right" tipo="ui" tam={13} />
													</span>
												</button>
											</li>
										{/each}
									</ol>
								</section>
							{/each}

							{#if sinPlan.length}
								<p class="rounded-2xl bg-black/[0.04] p-4 text-sm text-texto-3">
									Sin plan de trabajo disponible: {sinPlan.map((r) => r.candidato.nombre).join(', ')}.
								</p>
							{/if}
						</div>
					</div>

					<!-- Acciones (móvil) -->
					<p class="mt-6 text-center text-xs text-texto-3 lg:hidden">
						No es una recomendación de voto. Mide quién propone lo que priorizaste y qué tan concreto es, según sus planes
						oficiales. <a href="/metodologia/" class="underline">Cómo se calcula</a>
					</p>
					<div class="sticky bottom-0 -mx-4 mt-6 bg-gradient-to-t from-fondo via-fondo to-transparent px-4 pt-10 pb-[max(1rem,env(safe-area-inset-bottom))] lg:hidden">
						<button type="button" onclick={compartirImagen} class="flex w-full items-center justify-center gap-2 rounded-full p-[2px] fondo-aurora transition active:scale-95">
							<span class="flex w-full items-center justify-center gap-2 rounded-full bg-superficie py-3.5 text-lg font-bold">
								<Icono nombre="instagram-logo" tipo="ui" tam={20} /> Compartir mis prioridades
							</span>
						</button>
						<div class="mt-2 grid grid-cols-2 gap-2 text-sm">
							<button type="button" onclick={copiarLink} class="flex items-center justify-center gap-1.5 rounded-full py-3 font-semibold ring-1 ring-black/15">
								<Icono nombre="link" tipo="ui" tam={16} /> Copiar link
							</button>
							<button type="button" onclick={repetir} class="flex items-center justify-center gap-1.5 rounded-full py-3 font-semibold ring-1 ring-black/15">
								<Icono nombre="arrow-counter-clockwise" tipo="ui" tam={16} /> Otra vez
							</button>
						</div>
					</div>
				{/if}
			</section>
		{/key}
	</div>

	{#if aviso}
		<div class="fixed inset-x-0 bottom-32 z-20 mx-auto flex w-fit items-center gap-1.5 rounded-full bg-texto px-4 py-2 text-sm font-semibold text-white shadow-xl lg:bottom-10" transition:fly={{ y: 20, duration: 200 }} role="status">
			<Icono nombre="check" tipo="ui" tam={16} /> {aviso}
		</div>
	{/if}
</div>

<HojaInferior bind:abierto={hojaAbierta} titulo={detalle ? `¿Por qué ${detalle.candidato.nombre}?` : ''}>
	{#if detalle}
		<div class="flex items-center gap-3">
			<Avatar candidato={detalle.candidato} ciudad={c} tam={48} />
			<div class="flex-1">
				<p class="text-xs text-texto-3">Lista {detalle.candidato.lista} · {detalle.candidato.organizacion}</p>
				<p class="display text-3xl font-extrabold">{Math.round(detalle.afinidad)}%</p>
			</div>
		</div>
		<ul class="mt-5 space-y-3">
			{#each detalle.detalle as d (d.tema)}
				{@const t = temaPorId.get(d.tema)!}
				{@const color = colorTema(d.tema)}
				<li class="rounded-2xl bg-black/[0.03] p-3.5 ring-1 ring-black/[0.04]">
					<div class="flex items-center gap-2.5">
						<TemaIcono tema={t.id} icono={t.icono} tam={32} />
						<span class="flex-1 font-semibold">{t.nombre_corto}</span>
						<span class="text-xs text-texto-3">prioridad ×{d.peso}</span>
						<span class="display w-12 text-right font-extrabold" style="color:{color}">{pct(d.puntaje)}</span>
					</div>
					<p class="mt-2 text-sm text-texto-2">
						{#if d.modo === 'sin-propuestas'}
							Sin propuestas sobre este tema{d.propuestasExcluidas ? ' dentro de la competencia del Municipio' : ''}.
						{:else if d.modo === 'enfoques'}
							{#if d.enfoquesCoincidentes.length}
								Propone <strong class="text-texto">{d.enfoquesCoincidentes.map((e) => enfoquePorId.get(e)?.nombre).join(', ')}</strong>
								· concreción {pct(d.concrecion)}.
							{:else}
								No propone lo que elegiste.
							{/if}
						{:else}
							{d.propuestasValidas} propuesta{d.propuestasValidas === 1 ? '' : 's'} · concreción {pct(d.concrecion)}.
						{/if}
					</p>
					{#if d.propuestasExcluidas}
						<p class="mt-1 flex items-center gap-1 text-xs text-alerta">
							<Icono nombre="warning" tipo="ui" tam={12} /> {d.propuestasExcluidas} fuera de competencia municipal (no cuentan)
						</p>
					{/if}
				</li>
			{/each}
		</ul>
		<a href="/{c}/candidatos/{detalle.candidato.id}/" class="mt-5 flex items-center justify-center gap-2 rounded-full bg-texto py-3.5 font-bold text-white hover:bg-black">
			Ver propuestas y citas <Icono nombre="arrow-right" tipo="ui" tam={18} />
		</a>
	{/if}
</HojaInferior>

<style>
	@keyframes -global-llenar {
		from {
			height: 10%;
		}
		to {
			height: 92%;
		}
	}
</style>
