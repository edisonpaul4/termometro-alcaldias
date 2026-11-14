/**
 * Imagen 1080×1920 para compartir en Stories/TikTok/WhatsApp.
 * DECISIÓN DE NEUTRALIDAD: la imagen muestra TUS PRIORIDADES, nunca un ranking de
 * candidatos. Compartir un ranking circularía como propaganda (y chocaría con el
 * silencio electoral); compartir prioridades invita a otros a hacer el recorrido.
 */
import { contenido } from './iconos';
import { colorTema } from './visual';

export interface DatosHistoria {
	ciudad: string;
	temas: { id: string; icono: string; nombre: string }[];
	url: string;
}

const ANCHO = 1080;
const ALTO = 1920;
const DISPLAY = "'Bricolage Grotesque Variable', system-ui, sans-serif";

function cargarIcono(nombre: string, color: string): Promise<HTMLImageElement> {
	const svg = (contenido[nombre] ?? contenido.sparkle).replace('currentColor', color);
	return new Promise((ok, mal) => {
		const img = new Image();
		img.onload = () => ok(img);
		img.onerror = mal;
		img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
	});
}

export async function generarHistoria(d: DatosHistoria): Promise<Blob> {
	await document.fonts.ready;
	const cv = document.createElement('canvas');
	cv.width = ANCHO;
	cv.height = ALTO;
	const g = cv.getContext('2d')!;

	// Fondo con "aurora"
	g.fillStyle = '#f6f5f1';
	g.fillRect(0, 0, ANCHO, ALTO);
	for (const [x, y, r, c] of [
		[900, 180, 560, 'rgba(79,70,229,0.10)'],
		[120, 520, 480, 'rgba(13,148,136,0.10)'],
		[980, 1700, 560, 'rgba(2,132,199,0.08)']
	] as const) {
		const rg = g.createRadialGradient(x, y, 0, x, y, r);
		rg.addColorStop(0, c);
		rg.addColorStop(1, 'rgba(246,245,241,0)');
		g.fillStyle = rg;
		g.fillRect(0, 0, ANCHO, ALTO);
	}

	// Encabezado
	g.fillStyle = '#0f766e';
	g.font = `700 40px ${DISPLAY}`;
	g.fillText(`ELECCIONES ${d.ciudad.toUpperCase()} · 29 NOV`, 90, 210);
	g.fillStyle = '#15171c';
	g.font = `800 120px ${DISPLAY}`;
	['Lo que me', 'importa'].forEach((l, i) => g.fillText(l, 90, 380 + i * 128));
	const aur = g.createLinearGradient(90, 0, 900, 0);
	aur.addColorStop(0, '#0d9488');
	aur.addColorStop(0.5, '#0284c7');
	aur.addColorStop(1, '#4f46e5');
	g.fillStyle = aur;
	g.fillText(`para ${d.ciudad}`, 90, 636, ANCHO - 180);

	// Prioridades
	const iconos = await Promise.all(d.temas.map((t) => cargarIcono(t.icono, colorTema(t.id))));
	d.temas.forEach((t, i) => {
		const y = 760 + i * 172;
		const color = colorTema(t.id);
		g.fillStyle = '#ffffff';
		g.beginPath();
		g.roundRect(90, y, ANCHO - 180, 140, 44);
		g.fill();
		// burbuja de color
		g.fillStyle = color + '1a';
		g.beginPath();
		g.arc(190, y + 70, 48, 0, Math.PI * 2);
		g.fill();
		g.drawImage(iconos[i], 160, y + 40, 60, 60);
		g.fillStyle = '#15171c';
		g.font = `700 54px ${DISPLAY}`;
		g.fillText(t.nombre, 270, y + 88, ANCHO - 470);
		g.fillStyle = color;
		g.font = `800 56px ${DISPLAY}`;
		g.textAlign = 'right';
		g.fillText(`#${i + 1}`, ANCHO - 140, y + 90);
		g.textAlign = 'left';
	});

	// Llamado
	g.fillStyle = '#15171c';
	g.font = `800 66px ${DISPLAY}`;
	g.fillText('¿Y a ti qué te importa?', 90, ALTO - 300);
	g.fillStyle = '#4b4f58';
	g.font = `500 42px ${DISPLAY}`;
	g.fillText('Mira quién lo propone en serio en 60 seg', 90, ALTO - 225);
	g.fillStyle = '#0f766e';
	g.font = `700 42px ${DISPLAY}`;
	g.fillText(d.url.replace(/^https?:\/\//, ''), 90, ALTO - 150);

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
