<script lang="ts">
	import { onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import Icono from '#lib/componentes/Icono.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import Proporcion from '#lib/componentes/Proporcion.svelte';
	import { soloIntenciones, termometroGlobal } from '#lib/termometro.js';
	import { barajar, diasHasta } from '#lib/util.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Orden estable en el HTML prerenderizado; se baraja al cargar (neutralidad).
	let orden = $state<string[] | null>(null);
	onMount(() => {
		orden = barajar(data.candidatos.map((c) => c.id));
	});
	const candidatos = $derived(orden ? orden.map((id) => data.candidatos.find((c) => c.id === id)!) : data.candidatos);
	const sinPropuestas = $derived(data.candidatos.every((c) => !c.propuestas?.length));
	const dias = $derived(diasHasta(data.ciudad.eleccion));
	const paginas = $derived(data.candidatos.reduce((s, x) => s + (x.plan_trabajo.paginas ?? 0), 0));
	const c = $derived(data.ciudad.id);
	const contexto = $derived(soloIntenciones(data.candidatos));
	const temasDe = (cand: (typeof data.candidatos)[number]) => new Set((cand.propuestas ?? []).map((p) => p.tema)).size;
	const primerNombre = (n: string) => n.replace(/\(.*?\)/, '').trim().split(/\s+/).slice(0, 2).join(' ');
</script>

<svelte:head><title>{data.registro.dignidad} de {data.ciudad.nombre} · termómetro</title></svelte:head>

{#snippet llamado()}
	<a
		href="/{c}/lo-que-me-importa/"
		class="group block rounded-[1.75rem] p-[2px] fondo-aurora shadow-[0_10px_50px_-12px_rgba(15,118,110,0.22)] transition active:scale-[0.98]"
	>
		<span class="flex items-center gap-4 rounded-[1.65rem] bg-superficie p-5">
			<span class="flex-1">
				<span class="display block text-2xl leading-[1.05] font-extrabold text-balance">¿Quién propone lo que te importa?</span>
				<span class="mt-1.5 flex items-center gap-1.5 text-sm text-texto-2">
					<Icono nombre="hand-tap" tipo="ui" tam={14} /> 60 segundos · nada sale de tu teléfono
				</span>
			</span>
			<span class="grid size-14 shrink-0 place-items-center rounded-full bg-acento text-white transition group-hover:scale-105">
				<Icono nombre="play" tipo="ui" tam={22} />
			</span>
		</span>
	</a>
{/snippet}

<section class="relative isolate overflow-hidden">
	<div class="pointer-events-none absolute -top-40 -right-40 -z-10 size-[30rem] rounded-full opacity-[0.10] blur-3xl fondo-aurora"></div>
	<div class="contenedor-ancho lg:grid lg:grid-cols-[1fr_24rem] lg:items-end lg:gap-12">
		<div class="pt-6 pb-2">
			<a href="/" class="inline-flex items-center gap-1 text-sm text-texto-3 hover:text-texto"><Icono nombre="arrow-left" tipo="ui" tam={14} /> Inicio</a>
			<h1 class="mt-4 text-[2.6rem] leading-[0.95] font-extrabold tracking-tight sm:text-6xl">
				{data.registro.dignidad} de <span class="texto-aurora">{data.ciudad.nombre}</span>
			</h1>
			<p class="mt-3 text-texto-2">
				{data.candidatos.length} candidaturas{#if paginas} · {paginas} páginas de planes oficiales{/if}
				{#if dias > 0}<span class="text-acento"> · faltan {dias} días</span>{/if}
			</p>
		</div>
		<div class="hidden lg:block">
			{@render llamado()}
		</div>
	</div>

	<!-- Fila tipo "historias" -->
	<ul class="sin-scrollbar contenedor-ancho mt-5 lg:mt-8 flex gap-4 overflow-x-auto pb-2" aria-label="Candidatos">
		{#each candidatos as cand (cand.id)}
			<li animate:flip={{ duration: 400 }}>
				<a href="/{c}/candidatos/{cand.id}/" class="flex w-[4.5rem] flex-col items-center gap-1.5 text-center">
					<Avatar candidato={cand} ciudad={c} tam={68} />
					<span class="line-clamp-2 text-[11px] leading-tight text-texto-2">{primerNombre(cand.nombre)}</span>
				</a>
			</li>
		{/each}
	</ul>

	<div class="contenedor-ancho mt-5 lg:hidden">{@render llamado()}</div>

</section>

{#if sinPropuestas}
	<div class="contenedor-ancho mt-6">
		<p class="flex items-start gap-2 rounded-2xl bg-alerta/10 p-4 text-sm text-alerta ring-1 ring-alerta/20">
			<Icono nombre="info" tipo="ui" tam={18} />
			Estamos procesando los planes de trabajo oficiales. Las propuestas y el termómetro aparecerán aquí pronto.
		</p>
	</div>
{/if}

<section class="contenedor-ancho mt-12">
	<div class="flex items-end justify-between">
		<h2 class="text-2xl font-extrabold tracking-tight">Candidatos</h2>
		<p class="flex items-center gap-1 text-xs text-texto-3">
			<Icono nombre="shuffle" tipo="ui" tam={13} /> {orden ? 'Orden aleatorio' : ''}
		</p>
	</div>
	{#if contexto.total}
		<div class="mt-4 flex items-start gap-3 rounded-2xl bg-black/[0.035] p-4 text-sm text-texto-2 ring-1 ring-black/5">
			<Icono nombre="info" tipo="ui" tam={18} class="mt-0.5 shrink-0 text-texto-3" />
			<p>
				En {data.ciudad.nombre}, <strong class="text-texto">{Math.round((100 * contexto.sinDatos) / contexto.total)}% de las {contexto.total} propuestas</strong>
				son solo intenciones: no dicen cuánto, cuándo ni con qué dinero. Por eso todas las barras se ven bajas.
				<a href="/metodologia/" class="font-semibold text-acento underline-offset-2 hover:underline">Cómo se mide</a>
			</p>
		</div>
	{/if}
	<ul class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 lg:gap-4">
		{#each candidatos as cand (cand.id)}
			{@const t = termometroGlobal(cand)}
			<li animate:flip={{ duration: 400 }}>
				<a href="/{c}/candidatos/{cand.id}/" class="tarjeta flex h-full flex-col gap-4 p-4 transition hover:ring-black/20">
					<div class="flex items-center gap-3">
						<Avatar candidato={cand} ciudad={c} tam={52} />
						<div class="min-w-0 flex-1">
							<p class="display truncate font-bold">{cand.nombre}</p>
							<p class="truncate text-sm text-texto-3">Lista {cand.lista} · {cand.organizacion}</p>
						</div>
						<Icono nombre="caret-right" tipo="ui" tam={16} class="text-texto-3" />
					</div>
					{#if !cand.plan_trabajo.disponible}
						<p class="text-sm text-texto-3">Plan de trabajo no disponible</p>
					{:else if t.propuestas}
						<div class="flex flex-1 flex-col">
							<Proporcion lectura={t} desglose />
							<p class="mt-auto pt-3 text-xs text-texto-3">
								Plan de {t.propuestas} propuestas en {temasDe(cand)} temas{#if t.fueraDeCompetencia}<span class="text-alerta"> · {t.fueraDeCompetencia} fuera de competencia</span>{/if}
							</p>
						</div>
					{/if}
				</a>
			</li>
		{/each}
	</ul>
</section>

<section class="contenedor-ancho mt-12">
	<h2 class="text-2xl font-extrabold tracking-tight">Compara por tema</h2>
	<p class="mt-1 text-sm text-texto-2">Qué propone cada uno, lado a lado.</p>
	<ul class="mt-5 grid grid-cols-4 gap-x-2 gap-y-5 sm:grid-cols-6 lg:grid-cols-12">
		{#each data.temas as tema (tema.id)}
			<li>
				<a href="/{c}/temas/{tema.id}/" class="group flex flex-col items-center gap-2 text-center">
					<span class="transition group-hover:scale-110"><TemaIcono tema={tema.id} icono={tema.icono} tam={56} /></span>
					<span class="text-xs leading-tight text-texto-2">{tema.nombre_corto}</span>
				</a>
			</li>
		{/each}
	</ul>
</section>

<!-- CTA flotante en móvil -->
<a
	href="/{c}/lo-que-me-importa/"
	class="fixed inset-x-4 bottom-[max(1rem,env(safe-area-inset-bottom))] z-30 flex items-center justify-center gap-2 rounded-full bg-acento py-3.5 font-bold text-white shadow-[0_10px_40px_-6px_rgba(15,118,110,0.35)] transition active:scale-95 sm:hidden"
>
	<Icono nombre="play" tipo="ui" tam={16} /> ¿Quién propone lo que te importa?
</a>
