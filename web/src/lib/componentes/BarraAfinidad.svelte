<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	let { valor, retraso = 0 }: { valor: number; retraso?: number } = $props();

	const animado = new Tween(0, { duration: 900, easing: cubicOut });
	$effect(() => {
		const v = valor;
		const t = setTimeout(() => (animado.target = v), retraso);
		return () => clearTimeout(t);
	});
</script>

<div class="flex items-center gap-3">
	<div class="h-3 flex-1 overflow-hidden rounded-full bg-termo-0">
		<div class="h-full rounded-full bg-acento" style="width:{animado.current}%"></div>
	</div>
	<span class="w-12 text-right text-lg font-bold tabular-nums">{Math.round(animado.current)}%</span>
</div>
