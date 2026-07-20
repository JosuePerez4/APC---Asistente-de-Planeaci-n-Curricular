"""
src/services/pensum_import_service.py
=====================================
Traduce el pénsum del portal universitario al modelo de la app.

Capa pura, sin UI y sin efectos secundarios: recibe el HTML del portal y
devuelve un `ResultadoImportacion` que describe exactamente qué pasaría si se
aplicara. Quien llama decide si escribir o no en el perfil, tras mostrarle el
resumen al usuario.

El trabajo real es la conciliación de electivas: el portal usa códigos reales
(1155513, 1157004…) mientras que `curriculum.py` las modela como placeholders
genéricos (SOCIOHUMANISTICA_I, ELECTIVA_PROFESIONAL_III…). Volcar los códigos
reales rompería el conteo de créditos, así que hay que asignar cada electiva
aprobada a un slot equivalente.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.config.curriculum import MATERIAS, SEMESTRES
from src.services.pensum_parser import APROBADA, parse_pensum


@dataclass
class ResultadoImportacion:
    """
    Lo que produciría una importación, antes de tocar el perfil.

    Atributos:
        materias_vistas: códigos a asignar al perfil (obligatorias + slots).
        electivas_mapeadas: (nombre real en el portal, slot asignado).
        desmarcadas: códigos que el perfil tenía y el portal no reporta aprobados.
        avisos: problemas que el usuario debe ver antes de aplicar.
        total_portal: materias encontradas en el HTML.
        aprobadas: cuántas de ellas están aprobadas.
    """
    materias_vistas: set[str] = field(default_factory=set)
    electivas_mapeadas: list[tuple[str, str]] = field(default_factory=list)
    desmarcadas: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    total_portal: int = 0
    aprobadas: int = 0


def _slots_por_creditos() -> dict[int, list[str]]:
    """
    Agrupa los placeholders de electiva de `curriculum.py` por número de créditos,
    en orden de semestre.

    No se hardcodean: si cambias los placeholders en `curriculum.py`, el mapeo se
    adapta solo. Un código es placeholder si no es numérico — las materias reales
    del pénsum siempre tienen código de 7 dígitos.
    """
    slots: dict[int, list[str]] = {}
    for _sem_num, materias_sem in sorted(SEMESTRES.items()):
        for codigo, materia in materias_sem.items():
            if not codigo.isdigit():
                slots.setdefault(materia["creditos"], []).append(codigo)
    return slots


def construir_importacion(
    html: str,
    materias_vistas_actuales: set[str] | None = None,
) -> ResultadoImportacion:
    """
    Analiza el HTML del portal y describe la importación resultante.

    No modifica nada. `materias_vistas_actuales` sirve solo para calcular qué
    se desmarcaría, ya que el portal es la autoridad y `materias_vistas` se
    reemplaza en vez de fusionarse.

    Complejidad O(n) sobre las materias del portal; el único paso ordenado es
    el de electivas aprobadas, O(k log k) con k ≤ 9.
    """
    pensum = parse_pensum(html)
    resultado = ResultadoImportacion()
    resultado.avisos.extend(pensum["avisos"])

    obligatorias, electivas = pensum["materias"], pensum["electivas"]
    resultado.total_portal = len(obligatorias) + len(electivas)

    if resultado.total_portal == 0:
        resultado.avisos.append(
            "No se encontró ninguna materia en el HTML. "
            "¿Copiaste la tabla completa del pénsum?"
        )
        return resultado

    # ── Obligatorias: mapean 1:1 por código ────────────────────────────────
    aprobadas_oblig = [m for m in obligatorias if m["estado"] == APROBADA]
    for materia in aprobadas_oblig:
        if materia["codigo"] in MATERIAS:
            resultado.materias_vistas.add(materia["codigo"])
        else:
            resultado.avisos.append(
                f"{materia['codigo']} ({materia['nombre']}) está aprobada en el portal "
                f"pero no existe en el plan de la app; se ignora."
            )

    # ── Electivas: se asignan a placeholders del mismo número de créditos ──
    # Se ordenan por periodo cursado para que la asignación sea determinista y
    # las electivas más antiguas caigan en los slots de semestres más tempranos.
    aprobadas_elect = sorted(
        (m for m in electivas if m["estado"] == APROBADA),
        key=lambda m: (m["periodo"] or "", m["codigo"]),
    )
    resultado.aprobadas = len(aprobadas_oblig) + len(aprobadas_elect)

    slots = _slots_por_creditos()
    usados: dict[int, int] = {}

    for materia in aprobadas_elect:
        creditos = materia["creditos"]
        disponibles = slots.get(creditos, [])
        indice = usados.get(creditos, 0)

        if indice >= len(disponibles):
            resultado.avisos.append(
                f"{materia['codigo']} ({materia['nombre']}, {creditos} cr) está aprobada "
                f"pero ya no quedan slots de electiva de {creditos} créditos en el plan; "
                f"no se importa."
            )
            continue

        slot = disponibles[indice]
        usados[creditos] = indice + 1
        resultado.materias_vistas.add(slot)
        resultado.electivas_mapeadas.append((materia["nombre"], slot))

    # ── Qué se perdería al reemplazar ──────────────────────────────────────
    if materias_vistas_actuales:
        resultado.desmarcadas = sorted(materias_vistas_actuales - resultado.materias_vistas)

    return resultado


def resumen_legible(resultado: ResultadoImportacion) -> str:
    """Formatea el resultado para mostrarlo en el diálogo antes de aplicar."""
    lineas = [
        f"Se encontraron {resultado.total_portal} materias en el portal, "
        f"{resultado.aprobadas} aprobadas.",
        "",
        f"Se marcarán {len(resultado.materias_vistas)} materias como vistas:",
        f"  · {len(resultado.materias_vistas) - len(resultado.electivas_mapeadas)} obligatorias",
        f"  · {len(resultado.electivas_mapeadas)} electivas",
    ]

    if resultado.electivas_mapeadas:
        lineas += ["", "Electivas asignadas a los slots del plan:"]
        lineas += [
            f"  · {nombre}  →  {MATERIAS[slot]['nombre']}"
            for nombre, slot in resultado.electivas_mapeadas
        ]

    if resultado.desmarcadas:
        lineas += [
            "",
            f"Se DESMARCARÁN {len(resultado.desmarcadas)} materias que tenías marcadas "
            f"y el portal no reporta como aprobadas:",
        ]
        lineas += [
            f"  · {cod} — {MATERIAS[cod]['nombre'] if cod in MATERIAS else 'desconocida'}"
            for cod in resultado.desmarcadas
        ]

    if resultado.avisos:
        lineas += ["", "Avisos:"] + [f"  ! {a}" for a in resultado.avisos]

    return "\n".join(lineas)
