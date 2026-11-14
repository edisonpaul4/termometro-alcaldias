<script lang="ts">
	/** Ícono de tema en su "burbuja" de color, estilo historias destacadas de Instagram. */
	import Icono from './Icono.svelte';
	import { colorTema, tinte } from '../visual';

	let {
		tema,
		icono,
		tam = 44,
		activo = false
	}: { tema: string; icono: string; tam?: number; activo?: boolean } = $props();

	const color = $derived(colorTema(tema));
</script>

<span
	class="grid shrink-0 place-items-center rounded-full transition"
	style="width:{tam}px;height:{tam}px;background:{activo ? color : tinte(color)};color:{activo ? '#ffffff' : color}"
>
	<Icono nombre={icono} tam={tam * 0.55} />
</span>
