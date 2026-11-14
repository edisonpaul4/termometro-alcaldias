<script lang="ts">
	/** Foto con anillo tipo "historia" de Instagram (degradado aurora). */
	import type { CandidatoMin } from '../termometro';
	import { fotoUrl, iniciales } from '../util';

	let {
		candidato,
		ciudad,
		tam = 56,
		anillo = true
	}: { candidato: CandidatoMin; ciudad: string; tam?: number; anillo?: boolean } = $props();
	const src = $derived(fotoUrl(ciudad, candidato));
	const borde = $derived(Math.max(2, Math.round(tam / 22)));
</script>

<span
	class="inline-grid shrink-0 place-items-center rounded-full {anillo ? 'fondo-aurora' : 'bg-linea'}"
	style="width:{tam}px;height:{tam}px;padding:{borde}px"
>
	<span class="block size-full overflow-hidden rounded-full bg-fondo" style="padding:{borde}px">
		{#if src}
			<img {src} alt="Foto de {candidato.nombre}" loading="lazy" class="size-full rounded-full object-cover" />
		{:else}
			<span
				aria-hidden="true"
				class="display grid size-full place-items-center rounded-full bg-superficie-2 font-bold text-texto-2"
				style="font-size:{tam * 0.32}px"
			>
				{iniciales(candidato.nombre)}
			</span>
		{/if}
	</span>
</span>
