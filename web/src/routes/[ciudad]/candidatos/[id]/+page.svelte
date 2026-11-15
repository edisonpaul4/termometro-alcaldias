<script lang="ts">
	import Avatar from '#lib/componentes/Avatar.svelte';
	import Icono from '#lib/componentes/Icono.svelte';
	import Propuesta from '#lib/componentes/Propuesta.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import Proporcion from '#lib/componentes/Proporcion.svelte';
	import { masConcretas, proporcion, termometroGlobal, termometroTema } from '#lib/termometro.js';
	import { colorTema } from '#lib/visual.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const cand = $derived(data.candidato);
	const c = $derived(data.ciudad.id);
	const global = $derived(termometroGlobal(cand));
	const temasCon = $derived(data.temas.filter((t) => (cand.propuestas ?? []).some((p) => p.tema === t.id)));
	const temasSin = $derived(data.temas.filter((t) => !temasCon.includes(t)));
	const prop = $derived(proporcion(global.conAlgunDato, global.propuestas));
	const stats = $derived([
		[String(global.propuestas), 'propuestas'],
		[global.propuestas ? (prop.deCada10 >= 0.5 ? `${Math.round(prop.deCada10)}/10` : `${global.conAlgunDato}`) : '—', prop.deCada10 >= 0.5 ? 'con algún dato' : `de ${global.propuestas} con datos`],
		[`${temasCon.length}/${data.temas.length}`, 'temas']
	]);
	const destacadas = $derived(masConcretas(cand.propuestas ?? []));
</script>

<svelte:head><title>{cand.nombre} · Lista {cand.lista} · termómetro</title></svelte:head>

<div class="contenedor pt-5">
	<a href="/{c}/" class="inline-flex items-center gap-1 text-sm text-texto-3 hover:text-texto">
		<Icono nombre="arrow-left" tipo="ui" tam={14} /> {data.ciudad.nombre}
	</a>

	<!-- Cabecera tipo perfil -->
	<header class="mt-5 flex items-center gap-5">
		<Avatar candidato={cand} ciudad={c} tam={92} />
		<dl class="grid flex-1 grid-cols-3 text-center">
			{#each stats as [v, l] (l)}
				<div>
					<dd class="display text-2xl font-extrabold tabular-nums">{v}</dd>
					<dt class="text-xs text-texto-3">{l}</dt>
				</div>
			{/each}
		</dl>
	</header>
	<h1 class="mt-4 text-3xl leading-tight font-extrabold tracking-tight">{cand.nombre}</h1>
	<p class="text-texto-2">Lista {cand.lista} · {cand.organizacion}</p>

	<div class="mt-4 flex gap-2">
		{#if cand.plan_trabajo.disponible && cand.plan_trabajo.fuente}
			<a
				href={cand.plan_trabajo.fuente.url}
				target="_blank"
				rel="noopener"
				class="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-black/[0.08] py-2.5 text-sm font-semibold hover:bg-black/[0.12]"
			>
				<Icono nombre="file-pdf" tipo="ui" tam={16} /> Plan oficial · {cand.plan_trabajo.paginas} págs
			</a>
		{:else}
			<p class="flex-1 rounded-xl bg-black/[0.05] p-3 text-sm text-texto-2">{cand.plan_trabajo.nota}</p>
		{/if}
	</div>

	{#if global.propuestas}
		<!-- Destacadas por tema -->
		<nav class="sin-scrollbar -mx-4 mt-6 overflow-x-auto px-4" aria-label="Temas">
			<ul class="flex gap-4">
				{#each temasCon as t (t.id)}
					<li>
						<a href="#{t.id}" class="flex w-16 flex-col items-center gap-1.5 text-center">
							<span class="rounded-full p-[2px]" style="background:{colorTema(t.id)}">
								<span class="block rounded-full bg-fondo p-[2px]"><TemaIcono tema={t.id} icono={t.icono} tam={52} /></span>
							</span>
							<span class="text-[11px] leading-tight text-texto-2">{t.nombre_corto}</span>
						</a>
					</li>
				{/each}
			</ul>
		</nav>

		<section class="tarjeta mt-6 p-5">
			<Proporcion lectura={global} desglose pie="Plan de {global.propuestas} propuestas en {temasCon.length} temas. Se cuenta si la propuesta dice cuánto, cuándo o con qué dinero; no si es buena idea ni si es viable." />
			{#if global.fueraDeCompetencia}
				<p class="mt-3 flex items-center gap-1.5 rounded-2xl bg-alerta/10 p-3 text-sm text-alerta">
					<Icono nombre="warning" tipo="ui" tam={16} />
					{global.fueraDeCompetencia} propuesta{global.fueraDeCompetencia > 1 ? 's' : ''} no le corresponde{global.fueraDeCompetencia > 1 ? 'n' : ''} al Municipio
				</p>
			{/if}
		</section>

		<section class="mt-8">
			<h2 class="text-xl font-extrabold tracking-tight">Lo más concreto de su plan</h2>
			{#if destacadas.length}
				<p class="mt-1 text-sm text-texto-2">Las propuestas que más datos traen, con su cita.</p>
				<div class="mt-4 space-y-3">
					{#each destacadas as p (p.id)}
						<Propuesta propuesta={p} candidato={cand} />
					{/each}
				</div>
			{:else}
				<p class="mt-2 rounded-2xl bg-black/[0.035] p-4 text-sm text-texto-2">Ninguna propuesta de su plan dice cuánto, cuándo ni con qué dinero.</p>
			{/if}
		</section>

		{#each temasCon as t (t.id)}
			{@const lect = termometroTema(cand, t.id)}
			<section id={t.id} class="mt-10 scroll-mt-20">
				<div class="flex items-center gap-3">
					<TemaIcono tema={t.id} icono={t.icono} tam={40} />
					<h2 class="flex-1 text-xl leading-tight font-extrabold">{t.nombre}</h2>
					<a href="/{c}/temas/{t.id}/" class="inline-flex items-center gap-1 text-sm font-semibold text-texto-2 hover:text-texto">
						Comparar <Icono nombre="arrow-right" tipo="ui" tam={14} />
					</a>
				</div>
				<div class="mt-3"><Proporcion lectura={lect} color={colorTema(t.id)} /></div>
				<div class="mt-4 space-y-3">
					{#each (cand.propuestas ?? []).filter((p) => p.tema === t.id) as p (p.id)}
						<Propuesta propuesta={p} candidato={cand} />
					{/each}
				</div>
			</section>
		{/each}

		{#if temasSin.length}
			<section class="mt-10 rounded-3xl bg-black/[0.03] p-5 ring-1 ring-black/5">
				<h2 class="text-base font-bold text-texto-2">Sin propuestas en su plan sobre</h2>
				<ul class="mt-3 flex flex-wrap gap-2">
					{#each temasSin as t (t.id)}
						<li class="flex items-center gap-1.5 rounded-full bg-black/[0.04] py-1 pr-3 pl-1 text-sm text-texto-3">
							<TemaIcono tema={t.id} icono={t.icono} tam={24} />
							{t.nombre_corto}
						</li>
					{/each}
				</ul>
			</section>
		{/if}
	{:else if cand.plan_trabajo.disponible}
		<p class="mt-6 flex items-start gap-2 rounded-2xl bg-alerta/10 p-4 text-sm text-alerta ring-1 ring-alerta/20">
			<Icono nombre="info" tipo="ui" tam={18} /> Estamos procesando este plan de trabajo. Las propuestas aparecerán aquí pronto.
		</p>
	{/if}
</div>
