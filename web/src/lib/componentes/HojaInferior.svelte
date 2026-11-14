<script lang="ts">
	/** Bottom sheet nativo: sube desde abajo, se cierra tocando fuera, con Esc o arrastrando hacia abajo. */
	import type { Snippet } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';

	let {
		abierto = $bindable(false),
		titulo,
		children
	}: { abierto: boolean; titulo: string; children: Snippet } = $props();

	let inicioY = 0;
	let desplazamiento = $state(0);

	const cerrar = () => {
		abierto = false;
		desplazamiento = 0;
	};
	const tocar = (e: TouchEvent) => (inicioY = e.touches[0].clientY);
	const mover = (e: TouchEvent) => (desplazamiento = Math.max(0, e.touches[0].clientY - inicioY));
	const soltar = () => (desplazamiento > 90 ? cerrar() : (desplazamiento = 0));
</script>

<svelte:window onkeydown={(e) => abierto && e.key === 'Escape' && cerrar()} />

{#if abierto}
	<div class="fixed inset-0 z-[60]">
		<button class="absolute inset-0 bg-black/30 backdrop-blur-sm" aria-label="Cerrar" onclick={cerrar} transition:fade={{ duration: 180 }}></button>
		<div
			role="dialog"
			aria-modal="true"
			aria-label={titulo}
			class="absolute inset-x-0 bottom-0 mx-auto max-h-[85dvh] max-w-lg overflow-y-auto rounded-t-[2rem] bg-superficie px-5 pt-3 pb-[max(1.5rem,env(safe-area-inset-bottom))] ring-1 ring-black/10"
			style="transform:translateY({desplazamiento}px)"
			transition:fly={{ y: 400, duration: 320, easing: cubicOut }}
		>
			<div role="presentation" class="sticky top-0 -mx-5 -mt-3 bg-superficie px-5 pt-3 pb-2" ontouchstart={tocar} ontouchmove={mover} ontouchend={soltar}>
				<div class="mx-auto h-1.5 w-10 rounded-full bg-black/15"></div>
				<p class="display mt-3 text-lg font-bold">{titulo}</p>
			</div>
			{@render children()}
		</div>
	</div>
{/if}
