<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';
	import Icono from './Icono.svelte';
	import { etiqueta } from '../termometro';

	let {
		valor,
		compacto = false,
		titulo = 'Concreción',
		color = 'var(--color-acento)'
	}: { valor: number | null; compacto?: boolean; titulo?: string; color?: string } = $props();

	const animado = new Tween(0, { duration: 800, easing: cubicOut });
	$effect(() => {
		animado.target = valor ?? 0;
	});
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
		<div class="mb-1.5 flex items-center justify-between gap-2 text-xs">
			<span class="flex items-center gap-1 font-medium text-texto-2">
				<Icono nombre="thermometer" tipo="ui" tam={14} />
				{titulo}
			</span>
			<span class="display font-bold tabular-nums">
				{porcentaje === null ? '—' : `${porcentaje}%`}
				<span class="font-sans font-normal text-texto-3">· {etiqueta(valor)}</span>
			</span>
		</div>
	{/if}
	<div class="relative h-2 overflow-hidden rounded-full bg-black/[0.08]">
		<div
			class="h-full rounded-full"
			style="width:{animado.current * 100}%;background:{color}"
		></div>
		{#each [25, 50, 75] as m (m)}
			<span class="absolute top-0 h-full w-0.5 bg-superficie" style="left:{m}%"></span>
		{/each}
	</div>
</div>
