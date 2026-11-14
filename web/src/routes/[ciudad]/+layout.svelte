<script lang="ts">
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();
</script>

{#if data.ciudad.es_mock}
	<div class="bg-demo text-center text-sm font-medium text-white">
		<p class="contenedor py-2">
			🧪 <strong>Ciudad ficticia con datos de prueba.</strong> Candidatos y propuestas inventados para desarrollo.
		</p>
	</div>
{/if}

{@render children()}
