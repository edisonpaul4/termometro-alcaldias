/* GENERADO desde pipeline/termometro/modelos.py — no editar. Regenerar: make schema */

/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Consenso".
 */
export type Consenso = "unanime" | "mayoria" | "humano";
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Proveedor".
 */
export type Proveedor = "anthropic" | "openai" | "google" | "mock";

/**
 * Todo lo que la web necesita. Se exporta como JSON Schema → tipos TS.
 */
export interface DatosSitio {
  version_schema?: 1;
  temas: Tema[];
  ciudades: CiudadRegistro[];
  datos: {
    [k: string]: DatosCiudad;
  };
}
/**
 * Eje temático común a todas las ciudades (seguridad, movilidad...).
 *
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Tema".
 */
export interface Tema {
  /**
   * Identificador en minúsculas con guiones
   */
  id: string;
  nombre: string;
  /**
   * Para tarjetas pequeñas en móvil
   */
  nombre_corto: string;
  icono: string;
  descripcion: string;
}
/**
 * Entrada de `datos/ciudades.yaml`.
 *
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "CiudadRegistro".
 */
export interface CiudadRegistro {
  /**
   * Identificador en minúsculas con guiones
   */
  id: string;
  nombre: string;
  nombre_oficial: string;
  dignidad?: string;
  activa: boolean;
}
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "DatosCiudad".
 */
export interface DatosCiudad {
  ciudad: Ciudad;
  enfoques: Enfoque[];
  candidatos: Candidato[];
}
/**
 * `datos/ciudades/<id>/ciudad.yaml`.
 *
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Ciudad".
 */
export interface Ciudad {
  /**
   * Identificador en minúsculas con guiones
   */
  id: string;
  nombre: string;
  eleccion: string;
  debate?: string | null;
  fin_campana: string;
  /**
   * Lista confirmada contra la fuente oficial del CNE
   */
  candidatos_verificados: boolean;
  es_mock?: boolean;
}
/**
 * Forma de abordar un tema, agrupada a partir de propuestas reales (paso 2 del flujo).
 *
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Enfoque".
 */
export interface Enfoque {
  /**
   * Identificador en minúsculas con guiones
   */
  id: string;
  /**
   * Identificador en minúsculas con guiones
   */
  tema: string;
  nombre: string;
  descripcion: string;
  icono: string;
}
/**
 * `datos/ciudades/<ciudad>/candidatos/<id>.yaml`.
 *
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Candidato".
 */
export interface Candidato {
  /**
   * Identificador en minúsculas con guiones
   */
  id: string;
  nombre: string;
  lista: string;
  organizacion: string;
  foto?: string | null;
  foto_fuente?: Fuente | null;
  trayectoria?: Trayectoria[];
  plan_trabajo: PlanTrabajo;
  propuestas?: Propuesta[];
  es_mock?: boolean;
}
/**
 * Referencia pública a una fuente. `archivo` apunta a la copia en `fuentes/`.
 *
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Fuente".
 */
export interface Fuente {
  url: string;
  titulo: string;
  consultado: string;
  /**
   * Ruta relativa a la raíz del repo
   */
  archivo?: string | null;
}
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Trayectoria".
 */
export interface Trayectoria {
  cargo: string;
  periodo: string;
  fuente: Fuente;
}
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "PlanTrabajo".
 */
export interface PlanTrabajo {
  disponible: boolean;
  fuente?: Fuente | null;
  paginas?: number | null;
  sha256?: string | null;
  nota?: string | null;
}
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Propuesta".
 */
export interface Propuesta {
  /**
   * Identificador en minúsculas con guiones
   */
  id: string;
  /**
   * Identificador en minúsculas con guiones
   */
  tema: string;
  /**
   * Resumen neutral, sin adjetivos valorativos
   */
  resumen: string;
  /**
   * Texto LITERAL del plan de trabajo
   */
  cita: string;
  pagina: number;
  /**
   * La cita se encontró en el texto de esa página
   */
  cita_verificada: boolean;
  /**
   * Items: Identificador en minúsculas con guiones
   */
  enfoques?: string[];
  rubrica: Rubrica;
}
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Rubrica".
 */
export interface Rubrica {
  meta: Calificacion;
  plazo: Calificacion;
  financiamiento: Calificacion;
  competencia_municipal: Calificacion;
}
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "Calificacion".
 */
export interface Calificacion {
  valor: boolean;
  consenso: Consenso;
  /**
   * @minItems 1
   */
  votos: [VotoJurado, ...VotoJurado[]];
  /**
   * Obligatoria si consenso = humano
   */
  nota_revision?: string | null;
}
/**
 * This interface was referenced by `DatosSitio`'s JSON-Schema
 * via the `definition` "VotoJurado".
 */
export interface VotoJurado {
  proveedor: Proveedor;
  modelo: string;
  /**
   * null = el modelo falló o devolvió una respuesta inválida
   */
  valor: boolean | null;
  justificacion?: string | null;
}
