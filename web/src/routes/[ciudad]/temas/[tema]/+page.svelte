<script lang="ts">
	import { onMount } from 'svelte';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import Propuesta from '#lib/componentes/Propuesta.svelte';
	import Termometro from '#lib/componentes/Termometro.svelte';
	import { propuestasDelTema, termometroTema } from '#lib/termometro.js';
	import { barajar } from '#lib/util.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let orden = $state<string[] | null>(null);
	onMount(() => (orden = barajar(data.completos.map((x) => x.id))));
	const candidatos = $derived(
		orden ? orden.map((id) => data.completos.find((x) => x.id === id)!) : data.completos
	);
	const c = $derived(data.ciudad.id);
	const enfoques = $derived(data.enfoques.filter((e) => e.tema === data.tema.id));
	const con = $derived(candidatos.filter((x) => propuestasDelTema(x, data.tema.id).length));
	const sin = $derived(candidatos.filter((x) => !propuestasDelTema(x, data.tema.id).length));
	let abierto = $state<Record<string, boolean>>({});
</script>

<svelte:head><title>{data.tema.nombre} · {data.ciudad.nombre} · Termómetro</title></svelte:head>

<div class="contenedor pt-6">
	<a href="/{c}/" class="text-sm text-tinta-suave hover:text-tinta">← {data.ciudad.nombre}</a>

	<h1 class="mt-4 text-3xl font-extrabold tracking-tight">
		<span aria-hidden="true">{data.tema.icono}</span>
		{data.tema.nombre}
	</h1>
	<p class="mt-1 text-tinta-suave">{data.tema.descripcion}</p>

	{#if enfoques.length}
		<div class="mt-4 flex flex-wrap gap-2 text-sm">
			{#each enfoques as e (e.id)}
				<span class="rounded-full bg-acento-tenue px-3 py-1 text-acento-fuerte" title={e.descripcion}>{e.icono} {e.nombre}</span>
			{/each}
		</div>
	{/if}

	<ul class="mt-8 space-y-4">
		{#each con as cand (cand.id)}
			{@const lect = termometroTema(cand, data.tema.id)}
			{@const ps = propuestasDelTema(cand, data.tema.id)}
			<li class="tarjeta p-4">
				<div class="flex items-center gap-3">
					<Avatar candidato={cand} ciudad={c} tam={44} />
					<div class="min-w-0 flex-1">
						<a href="/{c}/candidatos/{cand.id}/#{data.tema.id}" class="font-semibold hover:underline">{cand.nombre}</a>
						<p class="truncate text-xs text-tinta-suave">Lista {cand.lista} · {cand.organizacion}</p>
					</div>
				</div>
				<div class="mt-3"><Termometro valor={lect.valor} /></div>
				<ul class="mt-3 space-y-1.5 text-sm">
					{#each ps.slice(0, abierto[cand.id] ? ps.length : 3) as p (p.id)}
						<li class="flex gap-2">
							<span aria-hidden="true" class="text-tinta-tenue">•</span>
							<span>
								{p.resumen}
								{#if !p.rubrica.competencia_municipal.valor}<span class="text-xs text-alerta">⚠️ fuera de competencia</span>{/if}
							</span>
						</li>
					{/each}
				</ul>
				{#if ps.length > 3}
					<button class="mt-2 text-sm text-acento hover:underline" onclick={() => (abierto[cand.id] = !abierto[cand.id])}>
						{abierto[cand.id] ? 'Ver menos' : `Ver las ${ps.length} propuestas`}
					</button>
				{/if}
				<details class="mt-2 text-sm">
					<summary class="cursor-pointer text-tinta-suave hover:text-tinta">Detalle, citas y calificación</summary>
					<div class="mt-3 space-y-3">
						{#each ps as p (p.id)}<Propuesta propuesta={p} candidato={cand} />{/each}
					</div>
				</details>
			</li>
		{/each}
	</ul>

	{#if sin.length}
		<section class="mt-8 rounded-2xl bg-borde/40 p-4 text-sm">
			<h2 class="font-semibold">Sin propuestas sobre este tema en su plan de trabajo</h2>
			<p class="mt-1 text-tinta-suave">{sin.map((x) => x.nombre).join(' · ')}</p>
		</section>
	{/if}
</div>
