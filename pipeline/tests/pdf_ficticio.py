"""Genera un PDF de texto mínimo y válido (sin dependencias) para pruebas end-to-end."""


def _esc(t: str) -> str:
    return t.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_simple(paginas: list[list[str]]) -> bytes:
    """paginas: lista de páginas; cada página es una lista de líneas (latin-1)."""
    objetos: list[bytes] = []
    n = len(paginas)
    # 1 catálogo, 2 árbol de páginas, 3 fuente; luego (página, contenido) por cada página
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(n))
    objetos.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objetos.append(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    objetos.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    for i, lineas in enumerate(paginas):
        flujo = "BT /F1 11 Tf 14 TL 50 790 Td " + " ".join(f"({_esc(l)}) Tj T*" for l in lineas) + " ET"
        datos = flujo.encode("latin-1")
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>".encode()
        )
        objetos.append(b"<< /Length " + str(len(datos)).encode() + b" >>\nstream\n" + datos + b"\nendstream")
    salida = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, o in enumerate(objetos, start=1):
        offsets.append(len(salida))
        salida += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(salida)
    salida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    salida += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    salida += f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(salida)
