<script lang="ts">
	import './layout.css';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<title>Termómetro de Alcaldías · Elecciones 2026</title>
	<meta
		name="description"
		content="Compara a los candidatos a alcalde según los temas que te importan. Neutral, con fuentes verificables."
	/>
	<link
		rel="icon"
		href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌡️</text></svg>"
	/>
</svelte:head>

<div class="flex min-h-dvh flex-col">
	<header class="border-b border-borde bg-superficie/90 backdrop-blur">
		<nav class="contenedor flex h-14 items-center justify-between">
			<a href="/" class="flex items-center gap-2 font-bold tracking-tight">
				<span aria-hidden="true">🌡️</span> Termómetro de Alcaldías
			</a>
			<a href="/metodologia/" class="text-sm text-tinta-suave hover:text-tinta">Metodología</a>
		</nav>
	</header>

	<main class="flex-1">
		{@render children()}
	</main>

	<footer class="mt-16 border-t border-borde py-8 text-sm text-tinta-suave">
		<div class="contenedor space-y-2">
			<p>
				Proyecto ciudadano, <strong>independiente y sin afiliación política</strong>. Toda la información proviene
				de los planes de trabajo oficiales publicados por el CNE, con cita y página verificables.
			</p>
			<p>
				El orden de los candidatos es aleatorio en cada visita. Esto no es una recomendación de voto.
				<a href="/metodologia/" class="text-acento underline">Cómo lo hacemos</a> ·
				<a href="https://github.com/edisonpaul4/termometro-alcaldias" class="text-acento underline">Código y datos abiertos</a>
			</p>
		</div>
	</footer>
</div>
