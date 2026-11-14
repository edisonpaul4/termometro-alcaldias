<script lang="ts">
	/** Marca: un termómetro-cápsula con el degradado aurora. */
	let { tam = 28, conTexto = true }: { tam?: number; conTexto?: boolean } = $props();
	const id = `aurora-${Math.random().toString(36).slice(2, 8)}`;
</script>

<span class="inline-flex items-center gap-2">
	<svg width={tam} height={tam} viewBox="0 0 32 32" aria-hidden="true">
		<defs>
			<linearGradient id={id} x1="0" y1="1" x2="1" y2="0">
				<stop offset="0" stop-color="#0d9488" />
				<stop offset=".5" stop-color="#0284c7" />
				<stop offset="1" stop-color="#4f46e5" />
			</linearGradient>
		</defs>
		<rect x="1" y="1" width="30" height="30" rx="9" fill="url(#{id})" />
		<rect x="13" y="6" width="6" height="15" rx="3" fill="#ffffff" />
		<circle cx="16" cy="22.5" r="5" fill="#ffffff" />
		<rect x="14.75" y="12" width="2.5" height="10" rx="1.25" fill="#0f766e" />
		<circle cx="16" cy="22.5" r="2.75" fill="#0f766e" />
	</svg>
	{#if conTexto}
		<span class="display text-[1.05rem] leading-none font-extrabold tracking-tight">
			termómetro<span class="text-acento">.</span>
		</span>
	{/if}
</span>
