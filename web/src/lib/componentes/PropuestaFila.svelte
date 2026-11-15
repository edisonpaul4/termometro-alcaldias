<script lang="ts">
	import type { PropuestaMin } from '../termometro';
	import Icono from './Icono.svelte';

	/** Fila compacta: resumen + tres marcas (cuánto / cuándo / con qué dinero). Al tocarla se abre el detalle. */
	let { propuesta, onabrir }: { propuesta: PropuestaMin; onabrir: () => void } = $props();

	const r = $derived(propuesta.rubrica);
	const marcas = $derived([
		['target', 'cuánto', r.meta.valor],
		['calendar-check', 'cuándo', r.plazo.valor],
		['coins', 'con qué dinero', r.financiamiento.valor]
	] as const);
</script>

<button onclick={onabrir} class="group flex w-full items-start gap-3 py-3 text-left">
	<span class="flex-1">
		<span class="line-clamp-3 leading-snug text-pretty group-hover:text-acento">{propuesta.resumen}</span>
		<span class="mt-1.5 flex flex-wrap items-center gap-1.5">
			{#each marcas as [icono, nombre, si] (nombre)}
				<span
					class="inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[11px] font-medium {si ? 'bg-acento/10 text-acento' : 'text-texto-3/70'}"
					title="{si ? 'Dice' : 'No dice'} {nombre}"
				>
					<Icono nombre={icono} tipo="ui" tam={12} />
					{#if si}{nombre}{/if}
					<span class="sr-only">{si ? 'dice' : 'no dice'} {nombre}</span>
				</span>
			{/each}
			{#if !r.competencia_municipal.valor}
				<span class="inline-flex items-center gap-1 text-[11px] font-medium text-alerta">
					<Icono nombre="warning" tipo="ui" tam={12} /> no le corresponde al Municipio
				</span>
			{/if}
		</span>
	</span>
	<Icono nombre="caret-right" tipo="ui" tam={14} class="mt-1 shrink-0 text-texto-3 group-hover:text-acento" />
</button>
