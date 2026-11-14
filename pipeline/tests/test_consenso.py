import pytest

from termometro.consenso import consolidar, kappa_fleiss, resolver_humano
from termometro.modelos import VotoJurado


def v(*valores):
    return [VotoJurado(proveedor="mock", modelo=f"m{i}", valor=x, justificacion=None if x is None else "j") for i, x in enumerate(valores)]


def test_unanime():
    c = consolidar(v(True, True, True))
    assert c.valor is True and c.consenso == "unanime"


def test_mayoria():
    c = consolidar(v(False, True, False))
    assert c.valor is False and c.consenso == "mayoria"


def test_jurado_caido_dos_coinciden():
    c = consolidar(v(True, None, True))
    assert c.valor is True and c.consenso == "mayoria"


@pytest.mark.parametrize("vals", [(True, False, None), (None, None, None)])
def test_sin_decision_va_a_humano(vals):
    assert consolidar(v(*vals)) is None
    h = resolver_humano(v(*vals), True, "Revisado contra la cita")
    assert h.consenso == "humano"


def test_kappa():
    assert kappa_fleiss([[True, True, True], [False, False, False]] * 5) == 1.0
    k = kappa_fleiss([[True, True, False], [False, True, False], [True, False, True], [False, False, True]])
    assert k < 0.2  # acuerdo pobre
    assert kappa_fleiss([[True, None, True]]) is None  # ítems incompletos no cuentan
