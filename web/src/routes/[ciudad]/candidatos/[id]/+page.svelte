<script lang="ts">
	import Avatar from '#lib/componentes/Avatar.svelte';
	import Propuesta from '#lib/componentes/Propuesta.svelte';
	import Termometro from '#lib/componentes/Termometro.svelte';
	import { termometroGlobal, termometroTema } from '#lib/termometro.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const cand = $derived(data.candidato);
	const c = $derived(data.ciudad.id);
	const global = $derived(termometroGlobal(cand));
	const temasConPropuestas = $derived(
		data.temas.filter((t) => (cand.propuestas ?? []).some((p) => p.tema === t.id))
	);
	const temasSin = $derived(data.temas.filter((t) => !temasConPropuestas.includes(t)));
</script>

<svelte:head><title>{cand.nombre} · Lista {cand.lista} · Termómetro</title></svelte:head>

<div class="contenedor pt-6">
	<a href="/{c}/" class="text-sm text-tinta-suave hover:text-tinta">← Todos los candidatos</a>

	<header class="mt-4 flex items-center gap-4">
		<Avatar candidato={cand} ciudad={c} tam={80} />
		<div>
			<h1 class="text-2xl font-extrabold tracking-tight sm:text-3xl">{cand.nombre}</h1>
			<p class="text-tinta-suave">Lista {cand.lista} · {cand.organizacion}</p>
		</div>
	</header>

	{#if cand.plan_trabajo.disponible && cand.plan_trabajo.fuente}
		<a
			href={cand.plan_trabajo.fuente.url}
			target="_blank"
			rel="noopener"
			class="mt-4 inline-flex items-center gap-2 rounded-full border border-borde bg-superficie px-3 py-1.5 text-sm hover:border-acento"
		>
			📄 Plan de trabajo oficial (CNE) · {cand.plan_trabajo.paginas} págs
		</a>
	{:else}
		<p class="mt-4 rounded-2xl bg-borde/50 p-4 text-sm">📄 {cand.plan_trabajo.nota}</p>
	{/if}

	{#if global.propuestas}
		<section class="tarjeta mt-6 p-5">
			<Termometro valor={global.valor} titulo="Concreción global" />
			<dl class="mt-4 grid grid-cols-2 gap-3 text-center text-sm sm:grid-cols-4">
				<div><dt class="text-tinta-suave">🎯 Con meta</dt><dd class="text-lg font-semibold">{global.conMeta}/{global.propuestas}</dd></div>
				<div><dt class="text-tinta-suave">📅 Con plazo</dt><dd class="text-lg font-semibold">{global.conPlazo}/{global.propuestas}</dd></div>
				<div><dt class="text-tinta-suave">💰 Con financiamiento</dt><dd class="text-lg font-semibold">{global.conFinanciamiento}/{global.propuestas}</dd></div>
				<div>
					<dt class="text-tinta-suave">⚠️ Fuera de competencia</dt>
					<dd class="text-lg font-semibold {global.fueraDeCompetencia ? 'text-alerta' : ''}">{global.fueraDeCompetencia}</dd>
				</div>
			</dl>
		</section>

		<nav class="sticky top-0 z-10 -mx-4 mt-6 overflow-x-auto border-b border-borde bg-papel/95 px-4 py-2 backdrop-blur" aria-label="Temas">
			<ul class="flex gap-2 text-sm whitespace-nowrap">
				{#each temasConPropuestas as t (t.id)}
					<li><a href="#{t.id}" class="rounded-full border border-borde bg-superficie px-3 py-1 hover:border-acento">{t.icono} {t.nombre_corto}</a></li>
				{/each}
			</ul>
		</nav>

		{#each temasConPropuestas as t (t.id)}
			{@const lect = termometroTema(cand, t.id)}
			<section id={t.id} class="mt-8 scroll-mt-16">
				<div class="flex items-end justify-between gap-4">
					<h2 class="text-lg font-bold">{t.icono} {t.nombre}</h2>
					<a href="/{c}/temas/{t.id}/" class="shrink-0 text-sm text-acento hover:underline">Comparar →</a>
				</div>
				<div class="mt-2 max-w-sm"><Termometro valor={lect.valor} /></div>
				<div class="mt-3 space-y-3">
					{#each (cand.propuestas ?? []).filter((p) => p.tema === t.id) as p (p.id)}
						<Propuesta propuesta={p} candidato={cand} />
					{/each}
				</div>
			</section>
		{/each}

		{#if temasSin.length}
			<section class="mt-10 rounded-2xl bg-borde/40 p-4 text-sm">
				<h2 class="font-semibold">Temas sin propuestas en su plan</h2>
				<p class="mt-1 text-tinta-suave">{temasSin.map((t) => `${t.icono} ${t.nombre}`).join(' · ')}</p>
			</section>
		{/if}
	{:else if cand.plan_trabajo.disponible}
		<p class="mt-6 rounded-2xl bg-alerta-suave p-4 text-sm text-alerta">
			⏳ Estamos procesando este plan de trabajo. Las propuestas aparecerán aquí pronto.
		</p>
	{/if}
</div>
