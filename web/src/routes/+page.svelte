<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<section class="contenedor pt-12 pb-8">
	<p class="text-sm font-medium tracking-wide text-acento uppercase">Elecciones seccionales · 29 de noviembre de 2026</p>
	<h1 class="mt-2 text-4xl font-extrabold tracking-tight text-balance sm:text-5xl">
		¿No sabes por quién votar para alcalde?
	</h1>
	<p class="mt-4 text-lg text-pretty text-tinta-suave">
		Elige los temas que te importan y descubre qué candidatos proponen soluciones
		<strong class="text-tinta">concretas</strong> en esos temas, según sus planes de trabajo oficiales.
	</p>
</section>

<section class="contenedor">
	<h2 class="sr-only">Elige tu ciudad</h2>
	<ul class="grid gap-3 sm:grid-cols-2">
		{#each data.ciudades as c (c.id)}
			<li>
				<a
					href="/{c.id}/"
					class="tarjeta block p-5 transition hover:-translate-y-0.5 hover:border-acento hover:shadow-md"
				>
					<div class="flex items-center justify-between">
						<span class="text-2xl font-bold">{c.nombre}</span>
						{#if c.es_mock}
							<span class="rounded-full bg-demo-suave px-2 py-0.5 text-xs font-semibold text-demo">DATOS DE PRUEBA</span>
						{/if}
					</div>
					<p class="mt-1 text-sm text-tinta-suave">{c.dignidad} · {c.candidatos} candidaturas</p>
					<p class="mt-4 font-medium text-acento">Ver candidatos →</p>
				</a>
			</li>
		{/each}
	</ul>
</section>
