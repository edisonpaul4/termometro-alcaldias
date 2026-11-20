"""Configuración del equipo real cuando Gemini no está disponible."""

from termometro import llm
from termometro.config import Config
from termometro.modelos import Proveedor


def test_equipo_real_sin_gemini(monkeypatch):
    cfg = Config(
        modo="real",
        modelo_anthropic="claude-opus-5-5",
        modelo_jurado_anthropic="claude-sonnet-5-5",
        modelo_openai="gpt-6.1-sol",
        modelo_gemini="gemini-4-carbon",
        max_usd=15,
        usar_anthropic=True,
        usar_gemini=False,
        _claves={"ANTHROPIC_API_KEY": "test", "OPENAI_API_KEY": "test"},
    )
    monkeypatch.setattr(llm, "config", lambda: cfg)

    eq = llm.equipo()

    assert eq.transcriptor.proveedor == Proveedor.anthropic
    assert eq.cobertura.proveedor == Proveedor.openai
    assert [j.proveedor for j in eq.jurado] == [Proveedor.anthropic, Proveedor.openai]


def test_equipo_real_sin_anthropic_usa_solo_cache(monkeypatch):
    cfg = Config(
        modo="real",
        modelo_anthropic="claude-opus-5-5",
        modelo_jurado_anthropic="claude-sonnet-5-5",
        modelo_openai="gpt-6.1-sol",
        modelo_gemini="gemini-4-carbon",
        max_usd=15,
        usar_anthropic=False,
        usar_gemini=False,
        _claves={"OPENAI_API_KEY": "test"},
    )
    monkeypatch.setattr(llm, "config", lambda: cfg)
    monkeypatch.setattr(llm.AnthropicIA, "__init__", lambda *_: (_ for _ in ()).throw(AssertionError("SDK Anthropic usado")))

    eq = llm.equipo()

    assert isinstance(eq.extractor, llm.SoloCacheIA)
    assert isinstance(eq.transcriptor, llm.SoloCacheIA)
    assert isinstance(eq.enfoques_valida, llm.SoloCacheIA)
    assert eq.extractor.modelo == "claude-opus-5-5"
    assert eq.jurado[0].modelo == "claude-sonnet-5-5"
