import { ciudadesActivas } from '#lib/server/datos.js';
import type { EntryGenerator } from './$types';

export const entries: EntryGenerator = () => ciudadesActivas().map((c) => ({ ciudad: c.id }));
