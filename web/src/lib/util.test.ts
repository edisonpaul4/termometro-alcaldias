import { expect, it } from 'vitest';
import type { Calificacion } from './contrato.gen';
import { textoConsenso } from './util';

it('distingue la revisión editorial de IA de una decisión humana y de un tercer voto', () => {
	const votos: Calificacion['votos'] = [
		{ proveedor: 'anthropic', modelo: 'a', valor: true, justificacion: 'Sí' },
		{ proveedor: 'openai', modelo: 'o', valor: false, justificacion: 'No' }
	];
	const calificacion: Calificacion = {
		valor: false,
		consenso: 'revision_ia',
		votos,
		nota_revision: 'La cita no fija un plazo.'
	};
	expect(textoConsenso(calificacion)).toBe('Resuelto en revisión editorial de IA');
	expect(calificacion.votos).toHaveLength(2);
});
