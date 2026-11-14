from termometro.citas import normalizar, verificar

PAGINAS = [
    "Plan de trabajo 2027-2031\nMovimiento Ejemplo",
    "EJE SEGURIDAD\nInstalaremos 500 cámaras de video-\nvigilancia conectadas al “ECU 911” en los barrios del sur.",
    "EJE MOVILIDAD\nAmpliaremos la flota del trolebús con 60 unidades eléctricas hasta 2028.",
]


def test_normalizar():
    assert normalizar("  Hola\n\n  MUNDO “x” — y ") == 'hola mundo "x" - y'
    assert normalizar("video-\n  vigilancia") == "videovigilancia"


def test_exacta_con_ruido_de_pdf():
    r = verificar('Instalaremos 500 cámaras de videovigilancia conectadas al "ECU 911"', PAGINAS, 2)
    assert r.verificada and r.metodo == "exacta" and r.pagina == 2 and not r.pagina_corregida


def test_corrige_pagina_equivocada():
    r = verificar("Ampliaremos la flota del trolebús con 60 unidades eléctricas", PAGINAS, 1)
    assert r.verificada and r.pagina == 3 and r.pagina_corregida


def test_aproximada_tolera_error_de_ocr():
    # un carácter mal reconocido (OCR): "unidadcs"
    r = verificar("Ampliaremos la flota del trolebús con 60 unidadcs eléctricas hasta 2028", PAGINAS, 3)
    assert r.verificada and r.metodo == "aproximada" and r.similitud >= 0.95


def test_cita_inventada_se_rechaza():
    r = verificar("Construiremos un metro aéreo de 40 kilómetros en el norte de la ciudad", PAGINAS, 2)
    assert not r.verificada and r.metodo == "no_encontrada"


def test_parafrasis_se_rechaza():
    # misma idea, distintas palabras: NO es una cita literal
    r = verificar("Vamos a poner 500 cámaras de seguridad en el sur conectadas al ECU", PAGINAS, 2)
    assert not r.verificada


def test_cita_muy_corta():
    assert verificar("seguridad", PAGINAS, 2).metodo == "muy_corta"
