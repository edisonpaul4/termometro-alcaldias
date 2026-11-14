/**
 * Imagen 1080×1920 para compartir en Stories/TikTok/WhatsApp.
 * DECISIÓN DE NEUTRALIDAD: la imagen muestra TUS PRIORIDADES, nunca un ranking de
 * candidatos. Compartir un ranking circularía como propaganda (y chocaría con el
 * silencio electoral); compartir prioridades invita a otros a hacer el recorrido.
 */
export interface DatosHistoria {
	ciudad: string;
	temas: { icono: string; nombre: string }[];
	url: string;
}

const ANCHO = 1080;
const ALTO = 1920;

export async function generarHistoria(d: DatosHistoria): Promise<Blob> {
	await document.fonts.ready;
	const cv = document.createElement('canvas');
	cv.width = ANCHO;
	cv.height = ALTO;
	const g = cv.getContext('2d')!;
	const display = "'Bricolage Grotesque Variable', system-ui, sans-serif";

	// Fondo
	const fondo = g.createLinearGradient(0, 0, 0, ALTO);
	fondo.addColorStop(0, '#0c0a09');
	fondo.addColorStop(1, '#134e4a');
	g.fillStyle = fondo;
	g.fillRect(0, 0, ANCHO, ALTO);

	// Encabezado
	g.fillStyle = '#5eead4';
	g.font = `600 44px ${display}`;
	g.fillText(`🌡️ ELECCIONES ${d.ciudad.toUpperCase()} 2026`, 90, 220);

	g.fillStyle = '#ffffff';
	g.font = `800 112px ${display}`;
	['Lo que me', 'importa para', `${d.ciudad}:`].forEach((l, i) => g.fillText(l, 90, 400 + i * 124));

	// Prioridades
	d.temas.forEach((t, i) => {
		const y = 820 + i * 170;
		g.fillStyle = 'rgba(255,255,255,0.08)';
		g.beginPath();
		g.roundRect(90, y - 100, ANCHO - 180, 140, 36);
		g.fill();
		g.fillStyle = '#5eead4';
		g.font = `800 64px ${display}`;
		g.fillText(`${i + 1}`, 140, y);
		g.font = '72px system-ui, sans-serif';
		g.fillText(t.icono, 220, y + 4);
		g.fillStyle = '#ffffff';
		g.font = `700 56px ${display}`;
		g.fillText(t.nombre, 330, y - 4, ANCHO - 420);
	});

	// Llamado
	g.fillStyle = '#ffffff';
	g.font = `700 60px ${display}`;
	g.fillText('¿Y a ti qué te importa?', 90, ALTO - 300);
	g.fillStyle = '#5eead4';
	g.font = `500 44px ${display}`;
	g.fillText('Descubre quién propone lo concreto 👉', 90, ALTO - 220);
	g.fillStyle = 'rgba(255,255,255,0.6)';
	g.font = `400 38px system-ui, sans-serif`;
	g.fillText(d.url.replace(/^https?:\/\//, ''), 90, ALTO - 140);

	return new Promise((ok) => cv.toBlob((b) => ok(b!), 'image/png'));
}

/** Comparte la imagen con la hoja nativa del teléfono; si no se puede, la descarga. */
export async function compartirHistoria(d: DatosHistoria): Promise<'compartido' | 'descargado' | 'cancelado'> {
	const blob = await generarHistoria(d);
	const archivo = new File([blob], `mis-prioridades-${d.ciudad.toLowerCase()}.png`, { type: 'image/png' });
	if (navigator.canShare?.({ files: [archivo] })) {
		try {
			await navigator.share({ files: [archivo], text: `Lo que me importa para ${d.ciudad}. ¿Y a ti? ${d.url}` });
			return 'compartido';
		} catch {
			return 'cancelado';
		}
	}
	const a = document.createElement('a');
	a.href = URL.createObjectURL(archivo);
	a.download = archivo.name;
	a.click();
	URL.revokeObjectURL(a.href);
	return 'descargado';
}
