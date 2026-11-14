<script lang="ts">
	import type { CandidatoMin } from '../termometro';
	import { fotoUrl, iniciales } from '../util';

	let { candidato, ciudad, tam = 56 }: { candidato: CandidatoMin; ciudad: string; tam?: number } = $props();
	const src = $derived(fotoUrl(ciudad, candidato));
</script>

{#if src}
	<img
		{src}
		alt="Foto de {candidato.nombre}"
		width={tam}
		height={tam}
		loading="lazy"
		class="shrink-0 rounded-full bg-borde object-cover"
		style="width:{tam}px;height:{tam}px"
	/>
{:else}
	<span
		aria-hidden="true"
		class="grid shrink-0 place-items-center rounded-full bg-borde font-semibold text-tinta-suave"
		style="width:{tam}px;height:{tam}px;font-size:{tam * 0.36}px"
	>
		{iniciales(candidato.nombre)}
	</span>
{/if}
