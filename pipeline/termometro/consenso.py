"""[5] Consenso del jurado y acuerdo entre jurados (kappa de Fleiss). Lógica pura, sin IA."""

from __future__ import annotations

from .modelos import Calificacion, Consenso, VotoJurado


def consolidar(votos: list[VotoJurado]) -> Calificacion | None:
    """Voto mayoritario. None = no hay decisión posible (empate o sin votos válidos): revisión humana."""
    validos = [v.valor for v in votos if v.valor is not None]
    if not validos:
        return None
    si = sum(validos)
    if si * 2 == len(validos):
        return None
    valor = si * 2 > len(validos)
    unanime = len(set(validos)) == 1 and len(validos) >= 3
    return Calificacion(valor=valor, consenso=Consenso.unanime if unanime else Consenso.mayoria, votos=votos)


def resolver_humano(votos: list[VotoJurado], valor: bool, nota: str) -> Calificacion:
    return Calificacion(valor=valor, consenso=Consenso.humano, votos=votos, nota_revision=nota)


def kappa_fleiss(items: list[list[bool | None]]) -> float | None:
    """Kappa de Fleiss para decisiones Sí/No. Solo usa ítems donde TODOS los jurados votaron.

    ≥0.8 casi perfecto · 0.6–0.8 sustancial · 0.4–0.6 moderado · <0.4 la rúbrica es ambigua.
    """
    completos = [it for it in items if it and all(v is not None for v in it)]
    if len(completos) < 2:
        return None
    n = len(completos[0])
    if n < 2 or any(len(it) != n for it in completos):
        return None
    N = len(completos)
    p_si = sum(sum(it) for it in completos) / (N * n)
    pe = p_si**2 + (1 - p_si) ** 2
    p_barra = sum((s * s + (n - s) ** 2 - n) / (n * (n - 1)) for s in (sum(it) for it in completos)) / N
    if pe == 1:
        return 1.0
    return round((p_barra - pe) / (1 - pe), 3)
