<script lang="ts">
	import { onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import Avatar from '#lib/componentes/Avatar.svelte';
	import Icono from '#lib/componentes/Icono.svelte';
	import TemaIcono from '#lib/componentes/TemaIcono.svelte';
	import Termometro from '#lib/componentes/Termometro.svelte';
	import { termometroGlobal } from '#lib/termometro.js';
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
	const primerNombre = (n: string) => n.replace(/\(.*?\)/, '').trim().split(/\s+/).slice(0, 2).join(' ');
</script>

<svelte:head><title>{data.registro.dignidad} de {data.ciudad.nombre} · termómetro</title></svelte:head>

<section class="relative isolate overflow-hidden">
	<div class="pointer-events-none absolute -top-40 -right-40 -z-10 size-[30rem] rounded-full opacity-[0.10] blur-3xl fondo-aurora"></div>
	<div class="contenedor pt-6 pb-2">
		<a href="/" class="inline-flex items-center gap-1 text-sm text-texto-3 hover:text-texto"><Icono nombre="arrow-left" tipo="ui" tam={14} /> Inicio</a>
		<h1 class="mt-4 text-[2.6rem] leading-[0.95] font-extrabold tracking-tight sm:text-6xl">
			{data.registro.dignidad} de <span class="texto-aurora">{data.ciudad.nombre}</span>
		</h1>
		<p class="mt-3 text-texto-2">
			{data.candidatos.length} candidaturas{#if paginas} · {paginas} páginas de planes oficiales{/if}
			{#if dias > 0}<span class="text-acento"> · faltan {dias} días</span>{/if}
		</p>
	</div>

	<!-- Fila tipo "historias" -->
	<ul class="sin-scrollbar contenedor mt-5 flex gap-4 overflow-x-auto pb-2" aria-label="Candidatos">
		{#each candidatos as cand (cand.id)}
			<li animate:flip={{ duration: 400 }}>
				<a href="/{c}/candidatos/{cand.id}/" class="flex w-[4.5rem] flex-col items-center gap-1.5 text-center">
					<Avatar candidato={cand} ciudad={c} tam={68} />
					<span class="line-clamp-2 text-[11px] leading-tight text-texto-2">{primerNombre(cand.nombre)}</span>
				</a>
			</li>
		{/each}
	</ul>

	<div class="contenedor mt-5">
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
	</div>
</section>

{#if sinPropuestas}
	<div class="contenedor mt-6">
		<p class="flex items-start gap-2 rounded-2xl bg-alerta/10 p-4 text-sm text-alerta ring-1 ring-alerta/20">
			<Icono nombre="info" tipo="ui" tam={18} />
			Estamos procesando los planes de trabajo oficiales. Las propuestas y el termómetro aparecerán aquí pronto.
		</p>
	</div>
{/if}

<section class="contenedor mt-12">
	<div class="flex items-end justify-between">
		<h2 class="text-2xl font-extrabold tracking-tight">Candidatos</h2>
		<p class="flex items-center gap-1 text-xs text-texto-3">
			<Icono nombre="shuffle" tipo="ui" tam={13} /> {orden ? 'Orden aleatorio' : ''}
		</p>
	</div>
	<ul class="mt-4 grid gap-3 sm:grid-cols-2">
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
						<div class="mt-auto">
							<Termometro valor={t.valor} />
							<p class="mt-1.5 text-xs text-texto-3">
								{t.propuestas} propuestas{#if t.fueraDeCompetencia}<span class="text-alerta"> · {t.fueraDeCompetencia} fuera de competencia</span>{/if}
							</p>
						</div>
					{/if}
				</a>
			</li>
		{/each}
	</ul>
</section>

<section class="contenedor mt-12">
	<h2 class="text-2xl font-extrabold tracking-tight">Compara por tema</h2>
	<p class="mt-1 text-sm text-texto-2">Qué propone cada uno, lado a lado.</p>
	<ul class="mt-5 grid grid-cols-4 gap-x-2 gap-y-5 sm:grid-cols-6">
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
