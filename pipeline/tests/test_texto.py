"""La extracción conserva el texto Unicode que entrega pdftotext."""

from termometro.texto import _extraer

from .pdf_ficticio import pdf_simple


def test_extraer_conserva_tildes_en_pdf(tmp_path):
    pdf = tmp_path / "plan.pdf"
    pdf.write_bytes(pdf_simple([["Paute: gestión hídrica y participación"]]))

    texto = _extraer(pdf, "hash-de-prueba")

    assert texto.paginas == ["Paute: gestión hídrica y participación\n\n"]
