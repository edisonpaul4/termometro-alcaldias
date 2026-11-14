<script lang="ts">
	/**
	 * Panel contextual responsivo:
	 *  - móvil: bottom sheet (sube desde abajo, se cierra arrastrando hacia abajo)
	 *  - escritorio (≥1024px): panel lateral derecho, para comparar sin perder la lista
	 * Se cierra tocando fuera o con Esc.
	 */
	import type { Snippet } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import Icono from './Icono.svelte';

	let {
		abierto = $bindable(false),
		titulo,
		children
	}: { abierto: boolean; titulo: string; children: Snippet } = $props();

	let escritorio = $state(false);
	$effect(() => {
		if (abierto) escritorio = matchMedia('(min-width: 1024px)').matches;
	});

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
		<button class="absolute inset-0 bg-black/30 backdrop-blur-sm lg:bg-black/10" aria-label="Cerrar" onclick={cerrar} transition:fade={{ duration: 180 }}></button>
		<div
			role="dialog"
			aria-modal="true"
			aria-label={titulo}
			class="absolute inset-x-0 bottom-0 mx-auto max-h-[85dvh] max-w-lg overflow-y-auto rounded-t-[2rem] bg-superficie px-5 pb-[max(1.5rem,env(safe-area-inset-bottom))] shadow-2xl ring-1 ring-black/10
				lg:inset-y-0 lg:right-0 lg:left-auto lg:max-h-none lg:w-[440px] lg:max-w-none lg:rounded-none lg:rounded-l-[2rem] lg:px-7"
			style="transform:translateY({desplazamiento}px)"
			transition:fly={escritorio ? { x: 460, duration: 320, easing: cubicOut } : { y: 400, duration: 320, easing: cubicOut }}
		>
			<div
				role="presentation"
				class="sticky top-0 z-10 -mx-5 mb-2 bg-superficie px-5 pt-3 pb-2 lg:-mx-7 lg:px-7 lg:pt-6"
				ontouchstart={tocar}
				ontouchmove={mover}
				ontouchend={soltar}
			>
				<div class="mx-auto h-1.5 w-10 rounded-full bg-black/15 lg:hidden"></div>
				<div class="mt-3 flex items-center justify-between gap-3 lg:mt-0">
					<p class="display text-lg font-bold">{titulo}</p>
					<button
						onclick={cerrar}
						class="hidden size-9 shrink-0 place-items-center rounded-full text-texto-2 hover:bg-black/[0.05] lg:grid"
						aria-label="Cerrar panel"
					>
						<Icono nombre="x" tipo="ui" tam={18} />
					</button>
				</div>
			</div>
			{@render children()}
		</div>
	</div>
{/if}
