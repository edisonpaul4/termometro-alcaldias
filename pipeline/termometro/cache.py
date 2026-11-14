"""Caché direccionada por contenido: el corazón del pipeline incremental.

Cada resultado se guarda bajo una clave = sha256(paso, versión, modelo, hash de la entrada).
Si la clave existe, no se vuelve a llamar a la IA. Cambiar la versión de un prompt invalida
solo la caché de ese paso; cambiar un documento invalida solo lo que depende de él.
"""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from .config import DIR_CACHE

M = TypeVar("M", bound=BaseModel)


def sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 16), b""):
            h.update(bloque)
    return h.hexdigest()


def huella(obj: Any) -> str:
    """Hash estable de cualquier estructura JSON-serializable (o modelo Pydantic)."""
    if isinstance(obj, BaseModel):
        obj = obj.model_dump(mode="json")
    return sha256_texto(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str))


@dataclass
class Estadisticas:
    aciertos: int = 0
    calculos: int = 0
    por_paso: dict[str, list[int]] = field(default_factory=dict)

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def registrar(self, paso: str, acierto: bool) -> None:
        with self._lock:
            self._registrar(paso, acierto)

    def _registrar(self, paso: str, acierto: bool) -> None:
        a, c = self.por_paso.setdefault(paso, [0, 0])
        self.por_paso[paso] = [a + acierto, c + (not acierto)]
        if acierto:
            self.aciertos += 1
        else:
            self.calculos += 1

    def resumen(self) -> str:
        filas = [f"  {p:<14} {a:>4} en caché · {c:>4} calculados" for p, (a, c) in sorted(self.por_paso.items())]
        return "\n".join(filas) or "  (sin pasos)"


class Cache:
    def __init__(self, directorio: Path = DIR_CACHE):
        self.dir = directorio
        self.stats = Estadisticas()

    def clave(self, paso: str, version: str, modelo: str, entrada: str) -> str:
        return sha256_texto(f"{paso}\x00{version}\x00{modelo}\x00{entrada}")

    def _ruta(self, paso: str, clave: str) -> Path:
        return self.dir / paso / clave[:2] / f"{clave}.json"

    def obtener(self, paso: str, version: str, modelo: str, entrada: str, tipo: type[M], calcular: Callable[[], M]) -> M:
        clave = self.clave(paso, version, modelo, entrada)
        ruta = self._ruta(paso, clave)
        if ruta.exists():
            self.stats.registrar(paso, True)
            return tipo.model_validate_json(ruta.read_text(encoding="utf-8"))
        resultado = calcular()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        tmp = ruta.with_suffix(".tmp")
        tmp.write_text(resultado.model_dump_json(), encoding="utf-8")
        tmp.replace(ruta)  # escritura atómica: una corrida interrumpida no deja basura válida
        self.stats.registrar(paso, False)
        return resultado
