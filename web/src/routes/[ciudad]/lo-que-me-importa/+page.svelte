<script lang="ts">
	/**
	 * Flujo inmersivo tipo "stories": una decisión por pantalla, toques que avanzan solos,
	 * botones al alcance del pulgar, vibración sutil y una revelación escalonada.
	 * Pensado para gente que llega desde Instagram/TikTok con poca paciencia.
	 */
	import { onMount } from 'svelte';
	import { fly, fade, scale } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import { replaceState } from '$app/navigation';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import BarraAfinidad from '#lib/componentes/BarraAfinidad.svelte';
	import { aURL, calcularAfinidad, desdeURL, type Resultado, type Seleccion } from '#lib/afinidad.js';
	import { compartirHistoria } from '#lib/historia.js';
	import type { CandidatoMin } from '#lib/termometro.js';
	import { barajar, pct } from '#lib/util.js';
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
	let elegidoAhora = $state<string | null>(null); // feedback visual antes de avanzar
	let resultados = $state<Resultado<CandidatoMin>[]>([]);
	let abierto = $state<string | null>(null);
	let aviso = $state<string | null>(null);
	let mensajeCalculo = $state(0);
	let direccion = $state(1);

	const temasConEnfoques = $derived(temas.filter((t) => enfoquesDe(t).length));
	const temaActual = $derived(temasConEnfoques[iTema]);

	// Segmentos de progreso estilo stories: temas + un segmento por tema con enfoques + resultado
	const segmentos = $derived(1 + Math.max(temasConEnfoques.length, 1) + 1);
	const segmentoActual = $derived(
		pantalla === 'temas' ? 0 : pantalla === 'enfoque' ? 1 + iTema : segmentos - 1
	);

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

	function listoTemas() {
		vibrar();
		enfoques = Object.fromEntries(Object.entries(enfoques).filter(([t]) => temas.includes(t)));
		iTema = 0;
		if (temasConEnfoques.length) ir('enfoque');
		else calcular();
	}

	function responder(valor: string[], id: string | null = null) {
		if (!temaActual || elegidoAhora) return;
		vibrar();
		elegidoAhora = id ?? '__';
		enfoques = { ...enfoques, [temaActual]: valor };
		setTimeout(() => {
			elegidoAhora = null;
			if (iTema < temasConEnfoques.length - 1) {
				direccion = 1;
				iTema++;
			} else calcular();
		}, 280);
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
		abierto = null;
		if (!animar || matchMedia('(prefers-reduced-motion: reduce)').matches) return ir('resultado');
		ir('calculando');
		mensajeCalculo = 0;
		const t = setInterval(() => mensajeCalculo++, 650);
		setTimeout(() => {
			clearInterval(t);
			vibrar();
			ir('resultado');
		}, 2000);
	}

	function repetir() {
		replaceState('?', {});
		ir('temas', -1);
	}

	async function compartirImagen() {
		vibrar();
		const r = await compartirHistoria({
			ciudad: data.ciudad.nombre,
			temas: temas.map((t) => ({ icono: temaPorId.get(t)!.icono, nombre: temaPorId.get(t)!.nombre })),
			url: `${location.origin}/${c}/`
		});
		if (r === 'descargado') mostrarAviso('Imagen descargada 📲 Súbela a tus historias');
	}
	async function copiarLink() {
		vibrar();
		await navigator.clipboard.writeText(location.href);
		mostrarAviso('Link copiado ✓');
	}
	function mostrarAviso(t: string) {
		aviso = t;
		setTimeout(() => (aviso = null), 2500);
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
		`Leyendo ${totalPaginas.toLocaleString('es-EC')} páginas de ${conPlan} planes de trabajo…`,
		`Revisando ${totalPropuestas} propuestas…`,
		'Midiendo qué tan concretas son…',
		'Cruzando con tus prioridades…'
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

<svelte:head>
	<title>¿Quién propone lo que te importa? · {data.ciudad.nombre}</title>
	<meta name="theme-color" content="#0c0a09" />
</svelte:head>

<div id="lienzo" class="fixed inset-0 z-50 overflow-y-auto bg-noche text-white">
	<div class="mx-auto flex min-h-full max-w-lg flex-col px-4">
		<!-- Barra superior: progreso tipo stories + cerrar -->
		<div class="sticky top-0 z-10 -mx-4 bg-noche/90 px-4 pt-3 pb-2 backdrop-blur">
			<div class="flex gap-1" aria-hidden="true">
				{#each Array(segmentos) as _, i (i)}
					<div class="h-1 flex-1 overflow-hidden rounded-full bg-white/15">
						<div
							class="h-full rounded-full bg-menta transition-all duration-500"
							style="width:{i < segmentoActual ? 100 : i === segmentoActual ? (pantalla === 'calculando' ? 60 : 100) : 0}%"
						></div>
					</div>
				{/each}
			</div>
			<div class="mt-2 flex h-9 items-center justify-between">
				{#if pantalla === 'enfoque'}
					<button onclick={atras} class="-ml-2 rounded-full px-2 py-1 text-white/70 hover:text-white" aria-label="Atrás">←</button>
				{:else}
					<span class="text-sm font-medium text-white/60">🌡️ {data.ciudad.nombre}</span>
				{/if}
				<a href="/{c}/" class="-mr-2 grid size-9 place-items-center rounded-full text-xl text-white/70 hover:bg-white/10 hover:text-white" aria-label="Cerrar">×</a>
			</div>
		</div>

		{#if data.ciudad.es_mock}
			<p class="mt-1 rounded-xl bg-demo/30 px-3 py-1.5 text-center text-xs text-demo-suave">🧪 Ciudad ficticia · datos de prueba</p>
		{/if}

		{#key pantalla + iTema}
			<section
				class="flex flex-1 flex-col"
				in:fly={{ x: 60 * direccion, duration: 280, delay: 90 }}
				out:fade={{ duration: 80 }}
			>
				<!-- ── TEMAS ───────────────────────────────────────────────── -->
				{#if pantalla === 'temas'}
					<h1 class="mt-4 text-4xl leading-[1.05] font-extrabold tracking-tight text-balance">
						¿Qué te importa <span class="text-menta">más</span> para {data.ciudad.nombre}?
					</h1>
					<p class="mt-2 text-white/60">Toca de {MIN} a {MAX}. El primero que toques = lo más importante.</p>

					{#if !hayPropuestas}
						<p class="mt-4 rounded-2xl bg-white/10 p-3 text-sm text-white/80">
							⏳ Aún procesamos los planes de {data.ciudad.nombre}. Puedes probar, pero el resultado todavía no refleja las propuestas.
						</p>
					{/if}

					<ul class="mt-6 grid grid-cols-3 gap-2.5 pb-40">
						{#each data.temas as t (t.id)}
							{@const pos = temas.indexOf(t.id)}
							{@const elegido = pos >= 0}
							<li>
								<button
									type="button"
									onclick={() => alternarTema(t.id)}
									aria-pressed={elegido}
									disabled={!elegido && temas.length >= MAX}
									class="relative flex aspect-[4/5] w-full flex-col items-center justify-center gap-2 rounded-3xl p-2 text-center text-sm font-semibold transition duration-200 active:scale-90 disabled:opacity-30
										{elegido ? 'animar-pop bg-menta text-noche shadow-[0_0_32px_-4px] shadow-menta/50' : 'bg-noche-2 text-white/90 ring-1 ring-white/10 hover:bg-noche-3'}"
								>
									<span class="text-4xl transition {elegido ? 'scale-110' : ''}" aria-hidden="true">{t.icono}</span>
									<span class="leading-tight">{t.nombre_corto}</span>
									{#if elegido}
										<span
											in:scale={{ duration: 250, easing: backOut }}
											class="absolute top-2 right-2 grid size-7 place-items-center rounded-full bg-noche text-sm font-extrabold text-menta"
										>
											{pos + 1}
										</span>
									{/if}
								</button>
							</li>
						{/each}
					</ul>

					<!-- Zona del pulgar -->
					<div class="fixed inset-x-0 bottom-0 z-10 bg-gradient-to-t from-noche via-noche/95 to-transparent pt-10 pb-[max(1rem,env(safe-area-inset-bottom))]">
						<div class="mx-auto max-w-lg px-4">
							{#if temas.length}
								<ol class="mb-3 flex gap-1.5 overflow-x-auto pb-1" aria-label="Tu orden de prioridad">
									{#each temas as id, i (id)}
										<li in:fly={{ y: 10, duration: 200 }}>
											<button
												onclick={() => alternarTema(id)}
												class="flex items-center gap-1 rounded-full bg-white/10 py-1 pr-2.5 pl-1 text-xs whitespace-nowrap"
												aria-label="Quitar {temaPorId.get(id)?.nombre}"
											>
												<span class="grid size-5 place-items-center rounded-full bg-menta font-bold text-noche">{i + 1}</span>
												{temaPorId.get(id)?.icono}
												{temaPorId.get(id)?.nombre_corto}
												<span class="text-white/40">×</span>
											</button>
										</li>
									{/each}
								</ol>
							{/if}
							<button
								type="button"
								disabled={temas.length < MIN}
								onclick={listoTemas}
								class="w-full rounded-full bg-menta py-4 text-lg font-bold text-noche transition active:scale-95 disabled:bg-white/10 disabled:text-white/40"
							>
								{temas.length < MIN
									? `Elige ${MIN - temas.length} más`
									: `Listo · ${temas.length} tema${temas.length > 1 ? 's' : ''} →`}
							</button>
						</div>
					</div>

				<!-- ── ENFOQUE (uno por pantalla, toca y avanza) ──────────── -->
				{:else if pantalla === 'enfoque' && temaActual}
					{@const t = temaPorId.get(temaActual)!}
					<p class="mt-6 text-sm font-semibold tracking-wide text-menta uppercase">
						{t.icono} {t.nombre_corto} · {iTema + 1} de {temasConEnfoques.length}
					</p>
					<h1 class="mt-2 text-4xl leading-[1.05] font-extrabold tracking-tight text-balance">
						¿Qué harías primero?
					</h1>
					<p class="mt-2 text-white/60">Las opciones salen de lo que proponen los candidatos.</p>

					<ul class="mt-6 space-y-3">
						{#each enfoquesDe(temaActual) as e, i (e.id)}
							{@const activo = elegidoAhora === e.id}
							<li in:fly={{ y: 24, duration: 260, delay: 120 + i * 70 }}>
								<button
									type="button"
									onclick={() => responder([e.id], e.id)}
									class="flex w-full items-center gap-4 rounded-3xl p-5 text-left transition duration-200 active:scale-[0.97]
										{activo ? 'animar-pop bg-menta text-noche' : 'bg-noche-2 ring-1 ring-white/10 hover:bg-noche-3'}"
								>
									<span class="text-4xl" aria-hidden="true">{e.icono}</span>
									<span class="flex-1">
										<span class="display block text-lg leading-tight font-bold">{e.nombre}</span>
										<span class="mt-0.5 block text-sm {activo ? 'text-noche/70' : 'text-white/55'}">{e.descripcion}</span>
									</span>
								</button>
							</li>
						{/each}
					</ul>

					<div class="mt-auto grid grid-cols-2 gap-2 pt-8 pb-[max(1rem,env(safe-area-inset-bottom))]">
						<button
							type="button"
							onclick={() => responder(enfoquesDe(temaActual).map((e) => e.id), '__todas')}
							class="rounded-full py-3.5 font-semibold ring-1 transition active:scale-95
								{elegidoAhora === '__todas' ? 'bg-menta text-noche ring-menta' : 'ring-white/20 hover:bg-white/5'}"
						>
							👌 Todas me sirven
						</button>
						<button
							type="button"
							onclick={() => responder([], '__nose')}
							class="rounded-full py-3.5 font-semibold ring-1 transition active:scale-95
								{elegidoAhora === '__nose' ? 'bg-white text-noche ring-white' : 'ring-white/20 hover:bg-white/5'}"
						>
							🤷 Ni idea
						</button>
					</div>

				<!-- ── CALCULANDO (suspenso + muestra el trabajo detrás) ─── -->
				{:else if pantalla === 'calculando'}
					<div class="flex flex-1 flex-col items-center justify-center text-center">
						<div class="relative h-56 w-14 overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10">
							<div class="absolute inset-x-0 bottom-0 animate-[llenar_2s_ease-out_forwards] rounded-full bg-gradient-to-t from-menta-fuerte to-menta"></div>
						</div>
						{#key mensajeCalculo}
							<p class="display mt-8 h-14 max-w-xs text-xl font-semibold text-balance" in:fly={{ y: 12, duration: 250 }}>
								{mensajes[Math.min(mensajeCalculo, mensajes.length - 1)]}
							</p>
						{/key}
					</div>

				<!-- ── RESULTADO ───────────────────────────────────────────── -->
				{:else if pantalla === 'resultado'}
					<h1 class="mt-4 text-4xl leading-[1.05] font-extrabold tracking-tight text-balance">
						Quién propone <span class="text-menta">lo que te importa</span>
					</h1>
					<div class="mt-3 flex flex-wrap gap-1.5 text-xs">
						{#each temas as id, i (id)}
							<span class="rounded-full bg-white/10 px-2.5 py-1">{i + 1}. {temaPorId.get(id)?.icono} {temaPorId.get(id)?.nombre_corto}</span>
						{/each}
					</div>

					<div class="mt-6 space-y-4">
						{#each grupos as grupo, gi (gi)}
							<section class={grupo.length > 1 ? 'rounded-[1.75rem] p-1.5 ring-1 ring-white/15 ring-inset' : ''}>
								{#if grupo.length > 1}
									<p class="px-3 pt-2 pb-2 text-xs font-semibold tracking-wide text-white/60 uppercase">
										⚖️ Empate técnico · menos de 5 puntos de diferencia
									</p>
								{/if}
								<ol class="space-y-2">
									{#each grupo as r, i (r.candidato.id)}
										{@const k = r.candidato.id}
										{@const n = gi * 3 + i}
										{@const primero = gi === 0}
										<li
											class="rounded-3xl p-4 {primero ? 'bg-noche-3 ring-1 ring-menta/40' : 'bg-noche-2'}"
											in:fly={{ y: 40, duration: 400, delay: 150 + n * 110, easing: backOut }}
										>
											<div class="flex items-center gap-3">
												<Avatar candidato={r.candidato} ciudad={c} tam={primero ? 56 : 44} />
												<div class="min-w-0 flex-1">
													<p class="display truncate {primero ? 'text-lg' : ''} font-bold">{r.candidato.nombre}</p>
													<p class="truncate text-xs text-white/50">Lista {r.candidato.lista} · {r.candidato.organizacion}</p>
												</div>
											</div>
											<div class="mt-3 [&_.bg-acento]:bg-menta [&_.bg-termo-0]:bg-white/10">
												<BarraAfinidad valor={r.afinidad} retraso={300 + n * 110} />
											</div>
											<button
												type="button"
												class="mt-1 text-sm font-medium text-menta"
												aria-expanded={abierto === k}
												onclick={() => (abierto = abierto === k ? null : k)}
											>
												{abierto === k ? 'Ocultar' : '¿Por qué?'}
											</button>
											{#if abierto === k}
												<ul class="mt-3 space-y-3 border-t border-white/10 pt-3 text-sm" transition:fade={{ duration: 150 }}>
													{#each r.detalle as d (d.tema)}
														{@const t = temaPorId.get(d.tema)!}
														<li>
															<div class="flex items-center justify-between gap-2">
																<span class="font-semibold">{t.icono} {t.nombre_corto}</span>
																<span class="text-xs text-white/50">peso {d.peso} · {pct(d.puntaje)}</span>
															</div>
															<p class="mt-0.5 text-white/65">
																{#if d.modo === 'sin-propuestas'}
																	Sin propuestas sobre este tema{d.propuestasExcluidas ? ' dentro de la competencia del Municipio' : ''}.
																{:else if d.modo === 'enfoques'}
																	{#if d.enfoquesCoincidentes.length}
																		Propone {d.enfoquesCoincidentes.map((e) => enfoquePorId.get(e)?.nombre).join(', ')}
																		· concreción {pct(d.concrecion)}.
																	{:else}
																		No propone lo que elegiste.
																	{/if}
																{:else}
																	{d.propuestasValidas} propuesta{d.propuestasValidas === 1 ? '' : 's'} · concreción {pct(d.concrecion)}.
																{/if}
																{#if d.propuestasExcluidas}
																	<span class="text-amber-300">⚠️ {d.propuestasExcluidas} fuera de competencia (no cuentan).</span>
																{/if}
															</p>
														</li>
													{/each}
													<li><a href="/{c}/candidatos/{k}/" class="font-semibold text-menta">Ver sus propuestas y citas →</a></li>
												</ul>
											{/if}
										</li>
									{/each}
								</ol>
							</section>
						{/each}

						{#if sinPlan.length}
							<p class="rounded-2xl bg-white/5 p-4 text-sm text-white/60">
								📄 Sin plan de trabajo disponible: {sinPlan.map((r) => r.candidato.nombre).join(', ')}.
							</p>
						{/if}
					</div>

					<p class="mt-6 text-center text-xs text-white/50">
						No es una recomendación de voto. Mide quién propone lo que priorizaste y qué tan concreto es, según sus planes
						oficiales. <a href="/metodologia/" class="underline">Cómo se calcula</a>
					</p>

					<div class="sticky bottom-0 -mx-4 mt-6 bg-gradient-to-t from-noche via-noche to-transparent px-4 pt-8 pb-[max(1rem,env(safe-area-inset-bottom))]">
						<button
							type="button"
							onclick={compartirImagen}
							class="w-full rounded-full bg-menta py-4 text-lg font-bold text-noche transition active:scale-95"
						>
							📲 Compartir mis prioridades
						</button>
						<div class="mt-2 grid grid-cols-2 gap-2 text-sm">
							<button type="button" onclick={copiarLink} class="rounded-full py-3 font-semibold ring-1 ring-white/20">🔗 Copiar link</button>
							<button type="button" onclick={repetir} class="rounded-full py-3 font-semibold ring-1 ring-white/20">↺ Otra vez</button>
						</div>
					</div>
				{/if}
			</section>
		{/key}
	</div>

	{#if aviso}
		<div
			class="fixed inset-x-0 bottom-28 z-20 mx-auto w-fit rounded-full bg-white px-4 py-2 text-sm font-semibold text-noche shadow-xl"
			transition:fly={{ y: 20, duration: 200 }}
			role="status"
		>
			{aviso}
		</div>
	{/if}
</div>

<style>
	@keyframes -global-llenar {
		from {
			height: 8%;
		}
		to {
			height: 92%;
		}
	}
</style>
