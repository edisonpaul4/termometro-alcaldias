<script lang="ts">
	import Icono from './Icono.svelte';
	import { proporcion, type Lectura } from '../termometro';

	/**
	 * "De cada 10 propuestas, X traen algún dato": 10 casillas fijas, iguales para todos.
	 * Un plan más largo no llena más casillas; solo cuenta la proporción.
	 */
	let {
		lectura,
		desglose = false,
		pie = '',
		color = 'var(--color-acento)'
	}: { lectura: Lectura; desglose?: boolean; pie?: string; color?: string } = $props();

	const total = $derived(proporcion(lectura.conAlgunDato, lectura.propuestas));
	const criterios = $derived([
		['target', 'cuánto', proporcion(lectura.conMeta, lectura.propuestas)],
		['calendar-check', 'cuándo', proporcion(lectura.conPlazo, lectura.propuestas)],
		['coins', 'con qué dinero', proporcion(lectura.conFinanciamiento, lectura.propuestas)]
	] as const);
	const verbo = (s: boolean) => (s ? 'trae' : 'traen');
	const llenado = (x: number, i: number) => Math.max(0, Math.min(1, x - i)) * 100;
</script>

{#snippet casillas(x: number, grande: boolean)}
	<span class="flex gap-[3px]" aria-hidden="true">
		{#each { length: 10 } as _, i (i)}
			<span class="relative flex-1 overflow-hidden {grande ? 'h-3 rounded-[4px]' : 'h-2 rounded-[3px]'} bg-black/[0.08]">
				<span class="absolute inset-y-0 left-0 transition-[width] duration-700" style="width:{llenado(x, i)}%;background:{color}"></span>
			</span>
		{/each}
	</span>
{/snippet}

<div class="w-full">
	<p class="text-sm leading-snug text-texto-2">
		{#if total.texto === 'ninguna' && lectura.propuestas === 1}
			Su única propuesta <span class="display font-bold text-texto">no trae datos</span>
		{:else if total.texto === 'ninguna'}
			<span class="display font-bold text-texto">Ninguna</span> de sus {lectura.propuestas} propuestas trae datos
		{:else if lectura.propuestas === 1}
			Su única propuesta <span class="display font-bold text-texto">trae algún dato</span>
		{:else if total.texto.includes('de cada')}
			De cada 10 propuestas, <span class="display font-bold text-texto">{total.texto.split(' ')[0]}</span> {verbo(total.singular)} algún dato
		{:else}
			<span class="display font-bold text-texto">{total.texto}</span> propuestas {verbo(total.singular)} algún dato
		{/if}
	</p>
	<div class="mt-2" role="img" aria-label="{total.texto} propuestas traen algún dato: cuánto, cuándo o con qué dinero">
		{@render casillas(total.deCada10, true)}
	</div>

	{#if desglose}
		<p class="mt-4 text-xs font-medium text-texto-3">Cuántas dicen…</p>
		<ul class="mt-2 space-y-2 text-xs">
			{#each criterios as [icono, nombre, p] (nombre)}
				<li class="grid grid-cols-[1rem_6.6rem_1fr_5.2rem] items-center gap-2">
					<Icono nombre={icono} tipo="ui" tam={14} class="text-texto-3" />
					<span class="text-texto-2">{nombre}</span>
					{@render casillas(p.deCada10, false)}
					<span class="text-right text-texto-3 tabular-nums">{p.texto}</span>
				</li>
			{/each}
		</ul>
	{/if}

	{#if pie}<p class="mt-3 text-xs text-texto-3">{pie}</p>{/if}
</div>
