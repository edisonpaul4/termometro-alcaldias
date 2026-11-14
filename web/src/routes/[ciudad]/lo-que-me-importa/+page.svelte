<script lang="ts">
	import { onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import { fly, fade } from 'svelte/transition';
	import { replaceState } from '$app/navigation';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import BarraAfinidad from '#lib/componentes/BarraAfinidad.svelte';
	import { aURL, calcularAfinidad, desdeURL, type Resultado, type Seleccion } from '#lib/afinidad.js';
	import { barajar, pct } from '#lib/util.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const MIN = 3;
	const MAX = 5;
	const c = $derived(data.ciudad.id);
	const temaPorId = $derived(new Map(data.temas.map((t) => [t.id, t])));
	const enfoquesDe = (t: string) => data.enfoques.filter((e) => e.tema === t);
	const enfoquePorId = $derived(new Map(data.enfoques.map((e) => [e.id, e])));
	const hayPropuestas = $derived(data.candidatos.some((x) => x.propuestas?.length));

	let paso = $state<1 | 2 | 3>(1);
	let temas = $state<string[]>([]);
	let enfoques = $state<Record<string, string[]>>({});
	let iTema = $state(0); // índice dentro de temasConEnfoques en el paso 2
	let resultados = $state<Resultado[]>([]);
	let abierto = $state<string | null>(null);
	let copiado = $state(false);

	const temasConEnfoques = $derived(temas.filter((t) => enfoquesDe(t).length));
	const temaActual = $derived(temasConEnfoques[iTema]);

	function alternarTema(id: string) {
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
	function alternarEnfoque(t: string, e: string) {
		const actual = enfoques[t] ?? [];
		enfoques = { ...enfoques, [t]: actual.includes(e) ? actual.filter((x) => x !== e) : [...actual, e] };
	}

	function irAPaso2() {
		// Limpiar enfoques de temas que ya no están elegidos
		enfoques = Object.fromEntries(Object.entries(enfoques).filter(([t]) => temas.includes(t)));
		iTema = 0;
		if (temasConEnfoques.length) paso = 2;
		else verResultados();
	}
	function siguienteTema(noSeguro = false) {
		if (noSeguro && temaActual) enfoques = { ...enfoques, [temaActual]: [] };
		if (iTema < temasConEnfoques.length - 1) iTema++;
		else verResultados();
	}
	function anteriorTema() {
		if (iTema > 0) iTema--;
		else paso = 1;
	}

	function verResultados() {
		const sel: Seleccion = { temas, enfoques };
		// Barajar antes de ordenar: los empates exactos quedan en orden aleatorio.
		resultados = calcularAfinidad(barajar(data.candidatos), sel);
		paso = 3;
		abierto = null;
		replaceState(`?${aURL(sel)}`, {});
		scrollTo({ top: 0, behavior: 'smooth' });
	}
	function reiniciar() {
		paso = 1;
		replaceState('?', {});
	}

	async function compartir() {
		const url = location.href;
		const texto = `Descubre qué candidatos a ${data.registro.dignidad.toLowerCase()} de ${data.ciudad.nombre} proponen soluciones concretas en lo que te importa:`;
		if (navigator.share) {
			try {
				await navigator.share({ title: 'Termómetro de Alcaldías', text: texto, url });
				return;
			} catch {
				/* cancelado */
			}
		}
		await navigator.clipboard.writeText(url);
		copiado = true;
		setTimeout(() => (copiado = false), 2500);
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
			verResultados();
		}
	});

	const grupos = $derived(
		resultados
			.filter((r) => !r.sinPlan)
			.reduce<Resultado[][]>((gs, r) => {
				(gs[r.grupo] ??= []).push(r);
				return gs;
			}, [])
			.filter(Boolean)
	);
	const sinPlan = $derived(resultados.filter((r) => r.sinPlan));
</script>

<svelte:head><title>Lo que me importa · {data.ciudad.nombre} · Termómetro</title></svelte:head>

<div class="contenedor pt-6 pb-10">
	<a href="/{c}/" class="text-sm text-tinta-suave hover:text-tinta">← {data.ciudad.nombre}</a>

	<!-- Progreso -->
	<ol class="mt-4 flex gap-2" aria-label="Progreso">
		{#each ['Tus temas', 'Cómo resolverlos', 'Resultado'] as nombre, i (nombre)}
			<li class="flex-1">
				<div class="h-1.5 rounded-full {paso > i ? 'bg-acento' : 'bg-borde'} transition-colors"></div>
				<p class="mt-1 text-xs {paso === i + 1 ? 'font-semibold text-tinta' : 'text-tinta-suave'}">{nombre}</p>
			</li>
		{/each}
	</ol>

	{#if !hayPropuestas}
		<p class="mt-6 rounded-2xl bg-alerta-suave p-4 text-sm text-alerta">
			⏳ Todavía estamos procesando los planes de trabajo de {data.ciudad.nombre}. Puedes probar el recorrido, pero
			los resultados aún no reflejan las propuestas.
		</p>
	{/if}

	{#key paso}
		<div in:fly={{ x: 40, duration: 250, delay: 120 }} out:fade={{ duration: 100 }}>
			<!-- ── PASO 1: elegir temas ─────────────────────────────── -->
			{#if paso === 1}
				<h1 class="mt-6 text-2xl font-extrabold tracking-tight text-balance sm:text-3xl">
					¿Qué es lo que más te importa para {data.ciudad.nombre}?
				</h1>
				<p class="mt-1 text-tinta-suave">
					Elige de {MIN} a {MAX} temas. <strong class="text-tinta">El orden en que los tocas es tu prioridad.</strong>
				</p>

				<ul class="mt-5 grid grid-cols-3 gap-2 sm:grid-cols-4">
					{#each data.temas as t (t.id)}
						{@const pos = temas.indexOf(t.id)}
						{@const elegido = pos >= 0}
						<li>
							<button
								type="button"
								onclick={() => alternarTema(t.id)}
								aria-pressed={elegido}
								disabled={!elegido && temas.length >= MAX}
								class="relative flex aspect-square w-full flex-col items-center justify-center gap-1.5 rounded-2xl border-2 p-2 text-center text-sm transition active:scale-95 disabled:opacity-40
									{elegido ? 'border-acento bg-acento-tenue font-semibold shadow-sm' : 'border-borde bg-superficie hover:border-tinta-tenue'}"
							>
								<span class="text-3xl transition {elegido ? 'scale-110' : ''}" aria-hidden="true">{t.icono}</span>
								<span class="leading-tight">{t.nombre_corto}</span>
								{#if elegido}
									<span
										in:fly={{ y: -6, duration: 200 }}
										class="absolute top-1.5 right-1.5 grid size-6 place-items-center rounded-full bg-acento text-xs font-bold text-white"
									>
										{pos + 1}
									</span>
								{/if}
							</button>
						</li>
					{/each}
				</ul>

				{#if temas.length >= 2}
					<section class="mt-6" transition:fade={{ duration: 150 }}>
						<h2 class="text-sm font-semibold text-tinta-suave">Tu prioridad (puedes reordenar)</h2>
						<ol class="mt-2 space-y-2">
							{#each temas as id, i (id)}
								{@const t = temaPorId.get(id)!}
								<li animate:flip={{ duration: 250 }} class="tarjeta flex items-center gap-3 px-3 py-2">
									<span class="grid size-7 place-items-center rounded-full bg-acento text-sm font-bold text-white">{i + 1}</span>
									<span class="flex-1">{t.icono} {t.nombre}</span>
									<button class="rounded-lg p-1.5 hover:bg-borde disabled:opacity-30" disabled={i === 0} onclick={() => mover(i, -1)} aria-label="Subir {t.nombre}">↑</button>
									<button class="rounded-lg p-1.5 hover:bg-borde disabled:opacity-30" disabled={i === temas.length - 1} onclick={() => mover(i, 1)} aria-label="Bajar {t.nombre}">↓</button>
								</li>
							{/each}
						</ol>
					</section>
				{/if}

				<div class="sticky bottom-0 -mx-4 mt-6 bg-gradient-to-t from-papel via-papel to-transparent px-4 pt-6 pb-4">
					<button
						type="button"
						disabled={temas.length < MIN}
						onclick={irAPaso2}
						class="w-full rounded-2xl bg-acento py-4 text-lg font-semibold text-white shadow-lg transition hover:bg-acento-fuerte disabled:bg-tinta-tenue disabled:shadow-none"
					>
						{temas.length < MIN ? `Elige ${MIN - temas.length} tema${MIN - temas.length > 1 ? 's' : ''} más` : 'Siguiente →'}
					</button>
				</div>

			<!-- ── PASO 2: enfoques por tema ─────────────────────────── -->
			{:else if paso === 2 && temaActual}
				{@const t = temaPorId.get(temaActual)!}
				<p class="mt-6 text-sm text-tinta-suave">Tema {iTema + 1} de {temasConEnfoques.length}</p>
				<h1 class="mt-1 text-2xl font-extrabold tracking-tight text-balance sm:text-3xl">
					<span aria-hidden="true">{t.icono}</span> {t.nombre}: ¿qué priorizarías?
				</h1>
				<p class="mt-1 text-tinta-suave">Puedes elegir más de uno. Estas opciones salen de lo que proponen los candidatos.</p>

				{#key temaActual}
					<ul class="mt-5 space-y-3" in:fly={{ x: 30, duration: 200 }}>
						{#each enfoquesDe(temaActual) as e (e.id)}
							{@const sel = (enfoques[temaActual] ?? []).includes(e.id)}
							<li>
								<button
									type="button"
									aria-pressed={sel}
									onclick={() => alternarEnfoque(temaActual, e.id)}
									class="flex w-full items-center gap-4 rounded-2xl border-2 p-4 text-left transition active:scale-[0.98]
										{sel ? 'border-acento bg-acento-tenue' : 'border-borde bg-superficie hover:border-tinta-tenue'}"
								>
									<span class="text-3xl" aria-hidden="true">{e.icono}</span>
									<span class="flex-1">
										<span class="block font-semibold">{e.nombre}</span>
										<span class="block text-sm text-tinta-suave">{e.descripcion}</span>
									</span>
									<span
										class="grid size-6 shrink-0 place-items-center rounded-md border-2 text-sm text-white transition
											{sel ? 'border-acento bg-acento' : 'border-tinta-tenue'}"
										aria-hidden="true">{sel ? '✓' : ''}</span
									>
								</button>
							</li>
						{/each}
					</ul>
				{/key}

				<div class="sticky bottom-0 -mx-4 mt-6 flex gap-2 bg-gradient-to-t from-papel via-papel to-transparent px-4 pt-6 pb-4">
					<button type="button" onclick={anteriorTema} class="rounded-2xl border border-borde bg-superficie px-4 py-4 font-medium" aria-label="Atrás">←</button>
					<button type="button" onclick={() => siguienteTema(true)} class="flex-1 rounded-2xl border border-borde bg-superficie py-4 font-medium">
						No estoy seguro
					</button>
					<button
						type="button"
						disabled={!(enfoques[temaActual] ?? []).length}
						onclick={() => siguienteTema()}
						class="flex-1 rounded-2xl bg-acento py-4 font-semibold text-white transition hover:bg-acento-fuerte disabled:bg-tinta-tenue"
					>
						{iTema < temasConEnfoques.length - 1 ? 'Siguiente →' : 'Ver resultado'}
					</button>
				</div>

			<!-- ── PASO 3: resultado ─────────────────────────────────── -->
			{:else if paso === 3}
				<h1 class="mt-6 text-2xl font-extrabold tracking-tight text-balance sm:text-3xl">
					Quiénes se apegan más a lo que te importa
				</h1>
				<p class="mt-2 flex flex-wrap gap-1.5 text-sm">
					{#each temas as id, i (id)}
						<span class="rounded-full bg-acento-tenue px-2.5 py-0.5 text-acento-fuerte">{i + 1}. {temaPorId.get(id)?.icono} {temaPorId.get(id)?.nombre_corto}</span>
					{/each}
				</p>

				<div class="mt-6 space-y-5">
					{#each grupos as grupo, gi (gi)}
						<section class={grupo.length > 1 ? 'rounded-3xl border-2 border-dashed border-borde p-2' : ''}>
							{#if grupo.length > 1}
								<p class="px-2 pt-1 pb-2 text-xs font-semibold tracking-wide text-tinta-suave uppercase">
									⚖️ Empate técnico · diferencia menor a 5 puntos
								</p>
							{/if}
							<ol class="space-y-2">
								{#each grupo as r, i (r.candidato.id)}
									{@const k = r.candidato.id}
									<li class="tarjeta p-4" in:fly={{ y: 20, duration: 300, delay: (gi * 2 + i) * 80 }}>
										<div class="flex items-center gap-3">
											<Avatar candidato={r.candidato} ciudad={c} tam={48} />
											<div class="min-w-0 flex-1">
												<p class="truncate font-semibold">{r.candidato.nombre}</p>
												<p class="truncate text-xs text-tinta-suave">Lista {r.candidato.lista} · {r.candidato.organizacion}</p>
											</div>
										</div>
										<div class="mt-3"><BarraAfinidad valor={r.afinidad} retraso={(gi * 2 + i) * 80 + 200} /></div>

										<button
											type="button"
											class="mt-2 text-sm text-acento hover:underline"
											aria-expanded={abierto === k}
											onclick={() => (abierto = abierto === k ? null : k)}
										>
											{abierto === k ? 'Ocultar' : '¿Por qué?'}
										</button>

										{#if abierto === k}
											<ul class="mt-3 space-y-3 border-t border-borde pt-3 text-sm" transition:fade={{ duration: 150 }}>
												{#each r.detalle as d (d.tema)}
													{@const t = temaPorId.get(d.tema)!}
													<li>
														<div class="flex items-center justify-between gap-2">
															<span class="font-medium">{t.icono} {t.nombre}</span>
															<span class="text-xs text-tinta-suave">peso {d.peso} · {pct(d.puntaje)}</span>
														</div>
														<p class="mt-0.5 text-tinta-suave">
															{#if d.modo === 'sin-propuestas'}
																No tiene propuestas sobre este tema{d.propuestasExcluidas ? ' dentro de la competencia del Municipio' : ''}.
															{:else if d.modo === 'enfoques'}
																{#if d.enfoquesCoincidentes.length}
																	Propone {d.enfoquesCoincidentes.map((e) => enfoquePorId.get(e)?.nombre).join(', ')}
																	({d.enfoquesCoincidentes.length} de {(enfoques[d.tema] ?? []).length} que elegiste).
																{:else}
																	No propone los enfoques que elegiste.
																{/if}
																Concreción en el tema: {pct(d.concrecion)}.
															{:else}
																{d.propuestasValidas} propuesta{d.propuestasValidas === 1 ? '' : 's'} sobre el tema · concreción {pct(d.concrecion)}.
															{/if}
															{#if d.propuestasExcluidas}
																<span class="text-alerta">⚠️ {d.propuestasExcluidas} fuera de competencia (no cuentan).</span>
															{/if}
														</p>
													</li>
												{/each}
												<li>
													<a href="/{c}/candidatos/{k}/" class="font-medium text-acento hover:underline">Ver todas sus propuestas y citas →</a>
												</li>
											</ul>
										{/if}
									</li>
								{/each}
							</ol>
						</section>
					{/each}

					{#if sinPlan.length}
						<p class="rounded-2xl bg-borde/40 p-4 text-sm text-tinta-suave">
							📄 Sin plan de trabajo disponible: {sinPlan.map((r) => r.candidato.nombre).join(', ')}.
						</p>
					{/if}
				</div>

				<p class="mt-6 rounded-2xl bg-acento-tenue p-4 text-sm text-acento-fuerte">
					Esto <strong>no es una recomendación de voto</strong>. Mide qué candidatos proponen —en sus planes de trabajo
					oficiales— lo que tú priorizaste, y qué tan concretas son esas propuestas.
					<a href="/metodologia/" class="underline">Cómo se calcula</a>.
				</p>

				<div class="mt-6 grid grid-cols-2 gap-2">
					<button type="button" onclick={reiniciar} class="rounded-2xl border border-borde bg-superficie py-3 font-medium">
						↺ Cambiar respuestas
					</button>
					<button type="button" onclick={compartir} class="rounded-2xl bg-acento py-3 font-semibold text-white hover:bg-acento-fuerte">
						{copiado ? '✓ Link copiado' : 'Compartir'}
					</button>
				</div>
			{/if}
		</div>
	{/key}
</div>
