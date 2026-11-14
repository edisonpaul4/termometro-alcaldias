<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';
	import { etiqueta } from '../termometro';

	let {
		valor,
		compacto = false,
		titulo = 'Concreción'
	}: { valor: number | null; compacto?: boolean; titulo?: string } = $props();

	const animado = new Tween(0, { duration: 700, easing: cubicOut });
	$effect(() => {
		animado.target = valor ?? 0;
	});

	// Escala monocromática: más concreto = más oscuro (sin rojo/verde valorativo)
	const color = $derived(
		valor === null
			? 'var(--color-termo-0)'
			: valor >= 0.75
				? 'var(--color-termo-4)'
				: valor >= 0.5
					? 'var(--color-termo-3)'
					: valor >= 0.25
						? 'var(--color-termo-2)'
						: 'var(--color-termo-1)'
	);
	const porcentaje = $derived(valor === null ? null : Math.round(valor * 100));
</script>

<div
	class="w-full"
	role="meter"
	aria-label="{titulo}: {porcentaje === null ? 'sin propuestas' : `${porcentaje}%`}"
	aria-valuemin={0}
	aria-valuemax={100}
	aria-valuenow={porcentaje ?? 0}
>
	{#if !compacto}
		<div class="mb-1 flex items-baseline justify-between text-xs">
			<span class="font-medium text-tinta-suave">🌡️ {titulo}</span>
			<span class="font-semibold tabular-nums">
				{porcentaje === null ? '—' : `${porcentaje}%`}
				<span class="font-normal text-tinta-suave">· {etiqueta(valor)}</span>
			</span>
		</div>
	{/if}
	<div class="relative h-2.5 overflow-hidden rounded-full bg-termo-0">
		<div class="h-full rounded-full" style="width:{animado.current * 100}%;background:{color}"></div>
		<!-- marcas cada 25% -->
		{#each [25, 50, 75] as m (m)}
			<span class="absolute top-0 h-full w-px bg-white/70" style="left:{m}%"></span>
		{/each}
	</div>
</div>
