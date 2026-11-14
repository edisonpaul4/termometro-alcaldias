<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	let { valor, retraso = 0, destacado = false }: { valor: number; retraso?: number; destacado?: boolean } = $props();

	const animado = new Tween(0, { duration: 1000, easing: cubicOut });
	$effect(() => {
		const v = valor;
		const t = setTimeout(() => (animado.target = v), retraso);
		return () => clearTimeout(t);
	});
</script>

<div class="flex items-center gap-3">
	<div class="h-2.5 flex-1 overflow-hidden rounded-full bg-black/[0.08]">
		<div
			class="h-full rounded-full {destacado ? 'fondo-aurora' : 'bg-acento'}"
			style="width:{animado.current}%"
		></div>
	</div>
	<span class="display w-14 text-right text-xl font-extrabold tabular-nums">{Math.round(animado.current)}%</span>
</div>
