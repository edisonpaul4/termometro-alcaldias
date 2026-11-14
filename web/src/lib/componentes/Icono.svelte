<script lang="ts">
	import { contenido, ui } from '../iconos';

	let {
		nombre,
		tam = 24,
		tipo = 'contenido',
		class: clase = ''
	}: { nombre: string; tam?: number; tipo?: 'contenido' | 'ui'; class?: string } = $props();

	const svg = $derived((tipo === 'ui' ? ui : contenido)[nombre] ?? contenido['sparkle']);
</script>

<span class="icono inline-block shrink-0 {clase}" style="width:{tam}px;height:{tam}px" aria-hidden="true">
	<!-- eslint-disable-next-line svelte/no-at-html-tags -- SVG local y curado (iconos.ts), no contenido de usuario -->
	{@html svg}
</span>

<style>
	.icono :global(svg) {
		display: block;
		width: 100%;
		height: 100%;
	}
</style>
