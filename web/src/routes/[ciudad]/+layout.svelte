<script lang="ts">
	import Icono from '#lib/componentes/Icono.svelte';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();
</script>

{#if data.ciudad.es_mock}
	<div class="border-b border-demo/20 bg-demo/10 text-center text-sm text-demo">
		<p class="contenedor flex items-center justify-center gap-1.5 py-2">
			<Icono nombre="sparkle" tipo="ui" tam={14} />
			<span><strong>Ciudad ficticia.</strong> Candidatos y propuestas inventados para probar.</span>
		</p>
	</div>
{/if}

{@render children()}
