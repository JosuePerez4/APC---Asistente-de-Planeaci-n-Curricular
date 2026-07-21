"""
src/services/pensum_parser.py
=============================
Parseo del HTML del pénsum del portal universitario a estructuras neutras.

Capa pura: no toca disco, no imprime nada y no conoce la UI. Los problemas
encontrados se devuelven en la clave "avisos" en vez de escribirse a stderr,
para que tanto el CLI (`tools/scrape_pensum.py`) como el diálogo de importación
puedan presentarlos a su manera.

El HTML se obtiene en el portal con la sesión abierta: F12 → clic derecho
sobre la <table> del pénsum → Copy → Copy outerHTML.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

# ── Constantes de parseo ───────────────────────────────────────────────────
# Precompilados a nivel de módulo: dentro del bucle se recompilarían una vez
# por materia (~110 veces) sin ninguna ganancia.

# Separa "Nombre -  Prerrequisito:  1155304 - 1155305 Cre:75" en sus dos mitades.
# El nombre puede contener guiones ("Catedra de paz, desarrollo y posconflicto"),
# por eso se corta por la palabra clave y no por el separador " - ".
_RE_PRERREQ = re.compile(r"\bPrerrequisito\s*:", re.IGNORECASE)
_RE_CRE = re.compile(r"\bCre\s*:\s*(\d+)", re.IGNORECASE)
_RE_CODIGO = re.compile(r"\d{7}")
_RE_HORAS_CRED = re.compile(
    r"horas\s*:\s*(\d+).*?Cred\s*:\s*(\d+)", re.IGNORECASE | re.DOTALL
)
_RE_PERIODO = re.compile(r"\b(\d{4}-\d)\b")

# Ordinal en español → número de semestre. Lookup O(1).
_SEMESTRES = {
    "PRIMER": 1,
    "SEGUNDO": 2,
    "TERCER": 3,
    "CUARTO": 4,
    "QUINTO": 5,
    "SEXTO": 6,
    "SEPTIMO": 7,
    "SÉPTIMO": 7,
    "OCTAVO": 8,
    "NOVENO": 9,
    "DECIMO": 10,
    "DÉCIMO": 10,
}

# Una materia está aprobada si y solo si lleva esta clase (verde). Cualquier
# otro color -- incluido el amarillo de "matriculada" -- cuenta como pendiente,
# porque matriculada todavía no es aprobada.
_CLASE_APROBADA = "td_color3"

APROBADA = "aprobada"
PENDIENTE = "pendiente"


def _texto_tooltip(span) -> str:
    """
    Devuelve el texto del tooltip de una materia.

    Bootstrap vacía `title` y mueve su contenido a `data-original-title` en
    cuanto el tooltip se muestra una vez, así que el atributo poblado depende
    de con qué materias interactuó el usuario antes de copiar el HTML. Hay que
    aceptar ambos.
    """
    return (span.get("data-original-title") or span.get("title") or "").strip()


def _parse_tooltip(texto: str) -> tuple[str, list[str], int]:
    """
    Descompone el tooltip en (nombre, prerrequisitos, créditos mínimos).

    El nombre del tooltip es el completo; el que aparece en el <font> de la
    tarjeta viene truncado con "…" y no sirve.

    >>> _parse_tooltip("Bases de datos -  Prerrequisito:  1155304 - 1155305")
    ('Bases de datos', ['1155304', '1155305'], 0)
    >>> _parse_tooltip("Ingles basico conversacional -  Prerrequisito:   Cre:31")
    ('Ingles basico conversacional', [], 31)
    >>> _parse_tooltip("Calculo diferencial")
    ('Calculo diferencial', [], 0)
    """
    partes = _RE_PRERREQ.split(texto, maxsplit=1)
    nombre_bruto = partes[0]
    resto = partes[1] if len(partes) > 1 else ""

    # El separador " - " que precede a "Prerrequisito:" queda colgando al final.
    nombre = nombre_bruto.strip().rstrip("-").strip()

    m_cre = _RE_CRE.search(resto)
    req_cred = int(m_cre.group(1)) if m_cre else 0

    # Los códigos se extraen por patrón (7 dígitos) en vez de partir por " - ":
    # es inmune a espaciados irregulares y al sufijo "Cre:NN" residual, que
    # nunca tiene 7 dígitos.
    codigos = _RE_CODIGO.findall(resto[: m_cre.start()] if m_cre else resto)

    return nombre, codigos, req_cred


def _parse_materia(span, semestre: int, avisos: list[str]) -> dict | None:
    """
    Construye el registro de una materia, o None si la tarjeta no es parseable
    (en cuyo caso añade el motivo a `avisos`).
    """
    etiqueta_codigo = span.find("b")
    codigo = etiqueta_codigo.get_text(strip=True) if etiqueta_codigo else ""
    if not codigo:
        avisos.append(f"tarjeta sin código en semestre {semestre}, se omite")
        return None

    tooltip = _texto_tooltip(span)
    if not tooltip:
        avisos.append(f"{codigo} sin tooltip (title ni data-original-title), se omite")
        return None

    nombre, prereq, req_cred = _parse_tooltip(tooltip)

    etiqueta_font = span.find("font")
    cuerpo = etiqueta_font.get_text(" ", strip=True) if etiqueta_font else ""

    m_hc = _RE_HORAS_CRED.search(cuerpo)
    horas, creditos = (int(m_hc.group(1)), int(m_hc.group(2))) if m_hc else (0, 0)

    m_periodo = _RE_PERIODO.search(cuerpo)

    return {
        "codigo": codigo,
        "nombre": nombre,
        "semestre": semestre,
        "creditos": creditos,
        "horas": horas,
        "prereq": prereq,
        "req_cred": req_cred,
        "estado": APROBADA if _CLASE_APROBADA in span.get("class", []) else PENDIENTE,
        "periodo": m_periodo.group(1) if m_periodo else None,
        "electiva": "Electiva" in cuerpo,
    }


def parse_pensum(html: str) -> dict:
    """
    Parsea el HTML del pénsum y devuelve
    {"materias": [...], "electivas": [...], "avisos": [...]}.

    Las electivas van aparte: en el modelo de la app están representadas por
    placeholders genéricos (ELECTIVA_PROFESIONAL_I..VI, SOCIOHUMANISTICA_I..III),
    así que volcar aquí los códigos reales duplicaría el conteo de créditos.
    El HTML las marca todas como "Electiva" sin distinguir profesional de
    sociohumanística, por lo que asignarlas a un placeholder concreto es
    responsabilidad de `pensum_import_service`.

    Una sola pasada sobre el árbol: O(n) en el número de materias. El sort
    final es O(n log n) y domina la cota, pero con n ≈ 100 el coste real está
    dominado por la construcción del árbol de BeautifulSoup (~80 % del tiempo).
    """
    soup = BeautifulSoup(html, "html.parser")

    materias: list[dict] = []
    electivas: list[dict] = []
    avisos: list[str] = []
    semestre = 0

    for fila in soup.find_all("tr"):
        encabezado = fila.find("th")
        if encabezado:
            # "PRIMER<br>SEMESTRE" → separador explícito o quedaría "PRIMERSEMESTRE".
            texto = encabezado.get_text(" ", strip=True).split()
            ordinal = texto[0].upper() if texto else ""
            if ordinal in _SEMESTRES:
                semestre = _SEMESTRES[ordinal]
            elif ordinal:
                avisos.append(f"encabezado de semestre no reconocido: {ordinal!r}")

        for span in fila.find_all("span", class_="badge_pen"):
            materia = _parse_materia(span, semestre, avisos)
            if materia is None:
                continue
            (electivas if materia["electiva"] else materias).append(materia)

    def clave(m):
        return (m["semestre"], m["codigo"])

    return {
        "materias": sorted(materias, key=clave),
        "electivas": sorted(electivas, key=clave),
        "avisos": avisos,
    }
