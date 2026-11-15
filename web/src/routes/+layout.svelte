<script lang="ts">
	import './layout.css';
	import Logo from '#lib/componentes/Logo.svelte';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<title>termómetro · ¿Quién propone lo que te importa?</title>
	<meta
		name="description"
		content="Elige lo que te importa y mira qué candidatos a alcalde lo proponen de forma concreta. Neutral, con fuentes del CNE."
	/>
	<meta name="theme-color" content="#f6f5f1" />
	<link
		rel="icon"
		href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><defs><linearGradient id='a' x1='0' y1='1' x2='1' y2='0'><stop offset='0' stop-color='%230d9488'/><stop offset='.5' stop-color='%230284c7'/><stop offset='1' stop-color='%234f46e5'/></linearGradient></defs><rect x='1' y='1' width='30' height='30' rx='9' fill='url(%23a)'/><rect x='13' y='6' width='6' height='15' rx='3' fill='%23ffffff'/><circle cx='16' cy='22.5' r='5' fill='%23ffffff'/></svg>"
	/>
</svelte:head>

<div class="flex min-h-dvh flex-col">
	<header class="sticky top-0 z-40 border-b border-black/[0.06] bg-fondo/80 backdrop-blur-xl">
		<nav class="contenedor-ancho flex h-14 items-center justify-between">
			<a href="/" aria-label="Inicio"><Logo /></a>
			<a href="/metodologia/" class="rounded-full px-3 py-1.5 text-sm font-medium text-texto-2 hover:bg-black/[0.04] hover:text-texto">
				Cómo funciona
			</a>
		</nav>
	</header>

	<main class="flex-1">
		{@render children()}
	</main>

	<footer class="mt-20 border-t border-black/[0.06] py-10 text-sm text-texto-3">
		<div class="contenedor space-y-3">
			<Logo tam={22} />
			<p>
				Proyecto ciudadano <strong class="text-texto-2">independiente y sin afiliación política</strong>. Todo sale de los
				planes de trabajo oficiales del CNE, con cita y página verificables.
			</p>
			<p>
				Orden de candidatos aleatorio en cada visita · No es una recomendación de voto ·
				<a href="/metodologia/" class="text-texto-2 underline-offset-2 hover:underline">Metodología</a> ·
				<a href="https://github.com/edisonpaul4/termometro-alcaldias" class="text-texto-2 underline-offset-2 hover:underline">Código abierto</a>
			</p>
		</div>
	</footer>
</div>
