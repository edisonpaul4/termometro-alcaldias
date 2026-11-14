<script lang="ts">
	import type { Calificacion, Candidato, Propuesta } from '../contrato.gen';
	import { enlacePagina, textoConsenso } from '../util';

	let { propuesta, candidato }: { propuesta: Propuesta; candidato: Candidato } = $props();

	const r = $derived(propuesta.rubrica);
	const criterios = $derived<[string, string, Calificacion][]>([
		['🎯', 'Meta medible', r.meta],
		['📅', 'Plazo', r.plazo],
		['💰', 'Financiamiento', r.financiamiento],
		['🏛️', 'Competencia municipal', r.competencia_municipal]
	]);
	const enlace = $derived(enlacePagina(candidato, propuesta.pagina));
	const fuera = $derived(!r.competencia_municipal.valor);
</script>

<article class="tarjeta p-4">
	<p class="leading-snug">{propuesta.resumen}</p>

	<ul class="mt-3 flex flex-wrap gap-1.5 text-xs" aria-label="Criterios de concreción">
		{#each criterios.slice(0, 3) as [icono, nombre, c] (nombre)}
			<li
				class="rounded-full px-2 py-0.5 {c.valor
					? 'bg-acento-suave text-acento-fuerte'
					: 'bg-borde/60 text-tinta-suave line-through decoration-tinta-tenue'}"
			>
				<span aria-hidden="true">{icono}</span>
				{nombre}<span class="sr-only">: {c.valor ? 'sí' : 'no'}</span>
			</li>
		{/each}
		{#if fuera}
			<li class="rounded-full bg-alerta-suave px-2 py-0.5 font-medium text-alerta">⚠️ Fuera de la competencia del Municipio</li>
		{/if}
	</ul>

	<details class="group mt-3 text-sm">
		<summary class="cursor-pointer list-none text-acento hover:underline">
			<span class="group-open:hidden">Ver cita del plan y cómo se calificó ↓</span>
			<span class="hidden group-open:inline">Ocultar ↑</span>
		</summary>

		<blockquote class="mt-3 border-l-4 border-acento-suave pl-3 text-tinta-suave italic">
			“{propuesta.cita}”
		</blockquote>
		<p class="mt-1 text-xs text-tinta-suave">
			Plan de trabajo, página {propuesta.pagina}
			{#if enlace}· <a href={enlace} target="_blank" rel="noopener" class="text-acento underline">abrir PDF oficial del CNE</a>{/if}
		</p>

		<dl class="mt-3 divide-y divide-borde rounded-xl border border-borde">
			{#each criterios as [icono, nombre, c] (nombre)}
				<div class="p-3">
					<dt class="flex items-center justify-between gap-2 font-medium">
						<span>{icono} {nombre}: <strong>{c.valor ? 'Sí' : 'No'}</strong></span>
						<span
							class="shrink-0 rounded-full px-2 py-0.5 text-xs font-normal {c.consenso === 'unanime'
								? 'bg-acento-tenue text-acento-fuerte'
								: 'bg-borde/60 text-tinta-suave'}"
						>
							{textoConsenso(c)}
						</span>
					</dt>
					<dd class="mt-1 space-y-1 text-xs text-tinta-suave">
						{#each c.votos as v, i (i)}
							<p>
								<span class="font-medium text-tinta">{v.modelo}</span>:
								{#if v.valor === null}<em>no respondió</em>{:else}{v.valor ? 'Sí' : 'No'} — {v.justificacion}{/if}
							</p>
						{/each}
						{#if c.nota_revision}<p class="font-medium text-tinta">🧑 Revisión humana: {c.nota_revision}</p>{/if}
					</dd>
				</div>
			{/each}
		</dl>
	</details>
</article>
