<script lang="ts">
	import type { Calificacion, Candidato, Propuesta } from '../contrato.gen';
	import { enlacePagina, textoConsenso } from '../util';
	import Icono from './Icono.svelte';

	/** `detalle`: muestra cita, contexto y votos sin botón (dentro de la hoja o panel lateral). */
	let { propuesta, candidato, detalle = false }: { propuesta: Propuesta; candidato: Candidato; detalle?: boolean } = $props();

	const r = $derived(propuesta.rubrica);
	const criterios = $derived<[string, string, Calificacion][]>([
		['target', 'Meta', r.meta],
		['calendar-check', 'Plazo', r.plazo],
		['coins', 'Financiamiento', r.financiamiento],
		['bank', 'Competencia municipal', r.competencia_municipal]
	]);
	const enlace = $derived(enlacePagina(candidato, propuesta.pagina));
	const fuera = $derived(!r.competencia_municipal.valor);
	let abierto = $state(false);
</script>

<article class={detalle ? '' : 'tarjeta p-4'}>
	<p class="leading-snug text-pretty">{propuesta.resumen}</p>

	<ul class="mt-3 flex flex-wrap gap-1.5 text-xs font-medium" aria-label="Criterios de concreción">
		{#each criterios.slice(0, 3) as [icono, nombre, c] (nombre)}
			<li
				class="inline-flex items-center gap-1 rounded-full py-1 pr-2.5 pl-2 {c.valor
					? 'bg-acento/10 text-acento'
					: 'bg-black/[0.04] text-texto-3 line-through decoration-texto-3/60'}"
			>
				<Icono nombre={c.valor ? icono : 'x'} tipo="ui" tam={13} />
				{nombre}<span class="sr-only">: {c.valor ? 'sí' : 'no'}</span>
			</li>
		{/each}
		{#if fuera}
			<li class="inline-flex items-center gap-1 rounded-full bg-alerta/12 py-1 pr-2.5 pl-2 text-alerta">
				<Icono nombre="warning" tipo="ui" tam={13} /> No es competencia del Municipio
			</li>
		{/if}
	</ul>

	{#if !detalle}
	<button
		class="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-texto-2 hover:text-texto"
		aria-expanded={abierto}
		onclick={() => (abierto = !abierto)}
	>
		<Icono nombre="quotes" tipo="ui" tam={14} />
		{abierto ? 'Ocultar fuente' : 'Ver la cita y cómo se calificó'}
		<span class="transition {abierto ? 'rotate-180' : ''}"><Icono nombre="caret-down" tipo="ui" tam={12} /></span>
	</button>
	{/if}

	{#if abierto || detalle}
		<div class="mt-3 space-y-3">
			<blockquote class="rounded-2xl bg-fondo px-4 py-3 text-sm text-texto-2 italic ring-1 ring-black/5">
				“{propuesta.cita}”
				<footer class="mt-2 flex flex-wrap items-center gap-2 text-xs not-italic">
					<span class="text-texto-3">Plan de trabajo · pág. {propuesta.pagina}</span>
					{#if enlace}
						<a href={enlace} target="_blank" rel="noopener" class="inline-flex items-center gap-1 font-semibold text-acento">
							<Icono nombre="file-pdf" tipo="ui" tam={13} /> Abrir PDF oficial del CNE
						</a>
					{/if}
				</footer>
			</blockquote>

			{#if propuesta.contexto.length}
				<div class="rounded-2xl bg-fondo px-4 py-3 text-sm ring-1 ring-black/5">
					<p class="text-xs font-semibold text-texto-2">Contexto en el mismo plan (también lo vieron los jurados)</p>
					<ul class="mt-1.5 space-y-1 text-texto-2">
						{#each propuesta.contexto as f, i (i)}
							<li>“{f.texto}” <span class="text-xs text-texto-3">· pág. {f.pagina}</span></li>
						{/each}
					</ul>
				</div>
			{/if}

			<dl class="divide-y divide-black/5 overflow-hidden rounded-2xl bg-fondo ring-1 ring-black/5">
				{#each criterios as [icono, nombre, c] (nombre)}
					<div class="p-3 text-sm">
						<dt class="flex items-center justify-between gap-2">
							<span class="flex items-center gap-1.5 font-semibold">
								<Icono nombre={icono} tipo="ui" tam={15} />
								{nombre}: <span class={c.valor ? 'text-acento' : 'text-texto-3'}>{c.valor ? 'Sí' : 'No'}</span>
							</span>
							<span class="shrink-0 rounded-full bg-black/[0.04] px-2 py-0.5 text-[11px] text-texto-2">{textoConsenso(c)}</span>
						</dt>
						<dd class="mt-1.5 space-y-1 text-xs text-texto-3">
							{#each c.votos as v, i (i)}
								<p>
									<span class="font-semibold text-texto-2">{v.modelo}</span> ·
									{#if v.valor === null}<em>no respondió</em>{:else}{v.valor ? 'Sí' : 'No'} — {v.justificacion}{/if}
								</p>
							{/each}
							{#if c.nota_revision}<p class="text-texto-2">Revisión humana: {c.nota_revision}</p>{/if}
						</dd>
					</div>
				{/each}
			</dl>
		</div>
	{/if}
</article>
