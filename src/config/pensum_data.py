"""
src/config/pensum_data.py
==========================
Carga del pénsum y horarios vigentes desde el JSON generado por
`tools/importar_horario_pensum.py`.

Reemplaza a `curriculum.py`: en vez de un plan curricular hardcodeado, la
fuente de verdad ahora es `data/pensum_horarios.json`, regenerable en
cualquier momento (botón "Regenerar Pénsum" en perfiles, o corriendo el
script directamente) para traer los grupos y horarios del periodo actual.

Expone las mismas estructuras que usaba `curriculum.py` (SEMESTRES, MATERIAS)
para no romper los servicios que ya las consumen, y añade a cada materia la
clave "grupos": las secciones ofertadas con sus sesiones de horario, que usa
`planner_service` para evitar cruces al armar el plan.
"""

from __future__ import annotations

import json
from pathlib import Path

_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent
PENSUM_FILE: Path = _RAIZ_PROYECTO / "data" / "pensum_horarios.json"

# La API reporta el día como índice 0-6 empezando en lunes (0=Lunes, 1=Martes...).
# Se acepta también texto en inglés/español por si el endpoint cambia de formato.
_DIAS_NORMALIZADOS: dict[str, str] = {
    "0": "Lunes",
    "MONDAY": "Lunes",
    "LUNES": "Lunes",
    "MON": "Lunes",
    "1": "Martes",
    "TUESDAY": "Martes",
    "MARTES": "Martes",
    "TUE": "Martes",
    "2": "Miércoles",
    "WEDNESDAY": "Miércoles",
    "MIERCOLES": "Miércoles",
    "MIÉRCOLES": "Miércoles",
    "WED": "Miércoles",
    "3": "Jueves",
    "THURSDAY": "Jueves",
    "JUEVES": "Jueves",
    "THU": "Jueves",
    "4": "Viernes",
    "FRIDAY": "Viernes",
    "VIERNES": "Viernes",
    "FRI": "Viernes",
    "5": "Sábado",
    "SATURDAY": "Sábado",
    "SABADO": "Sábado",
    "SÁBADO": "Sábado",
    "SAT": "Sábado",
    "6": "Domingo",
    "SUNDAY": "Domingo",
    "DOMINGO": "Domingo",
    "SUN": "Domingo",
}

# La API reporta beginHour/endHour como índice de franja horaria, no como hora
# de reloj: la franja 0 es 06:00-07:00. Se suma este valor para obtener la
# hora real que consume HorarioWidget (ver tabla de franjas del portal).
_HORA_BASE_FRANJA = 6


def _hora_real(valor) -> int | None:
    """Convierte un índice de franja horaria de la API a hora de reloj (0-23)."""
    return _HORA_BASE_FRANJA + valor if valor is not None else None


# La API reporta cada oferta puntual de electiva con su propio código real,
# pero el plan solo exige 3 casillas de sociohumanística (2 créditos) y 6 de
# profesional (3 créditos) — igual que el curriculum.py anterior. En vez de
# convertir cada oferta en una materia obligatoria distinta (lo que duplicaría
# el plan con decenas de "materias" que en el fondo son la misma casilla), se
# agrupan en estos placeholders fijos, y cada uno hereda los grupos/horarios
# de TODAS las electivas de su mismo tipo de crédito.
_SLOTS_SOCIOHUMANISTICA: list[tuple[str, str, int]] = [
    ("SOCIOHUMANISTICA_I", "Electiva Sociohumanística I", 5),
    ("SOCIOHUMANISTICA_II", "Electiva Sociohumanística II", 8),
    ("SOCIOHUMANISTICA_III", "Electiva Sociohumanística III", 10),
]
_SLOTS_PROFESIONAL: list[tuple[str, str, int]] = [
    ("ELECTIVA_PROFESIONAL_I", "Electiva Profesional I", 6),
    ("ELECTIVA_PROFESIONAL_II", "Electiva Profesional II", 7),
    ("ELECTIVA_PROFESIONAL_III", "Electiva Profesional III", 8),
    ("ELECTIVA_PROFESIONAL_IV", "Electiva Profesional IV", 9),
    ("ELECTIVA_PROFESIONAL_V", "Electiva Profesional V", 10),
    ("ELECTIVA_PROFESIONAL_VI", "Electiva Profesional VI", 10),
]
_CREDITOS_SOCIOHUMANISTICA = 2
_CREDITOS_PROFESIONAL = 3


def _normalizar_dia(valor) -> str:
    """Convierte el día reportado por la API (texto o número) a nombre en español."""
    if valor is None:
        return ""
    return _DIAS_NORMALIZADOS.get(str(valor).strip().upper(), str(valor))


def _cargar_subjects() -> list[dict]:
    if not PENSUM_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró '{PENSUM_FILE}'. Ejecuta primero "
            f"'python tools/importar_horario_pensum.py TU_TOKEN' o usa el botón "
            f"'Regenerar Pénsum' en la pantalla de perfiles."
        )
    with open(PENSUM_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("subjects", [])


def _construir_estructuras() -> tuple[dict[int, dict[str, dict]], dict[str, dict]]:
    """
    Traduce la lista plana `subjects` del JSON al mismo formato jerárquico que
    producía `curriculum.py`: SEMESTRES (por número) y MATERIAS (plano).

    Las obligatorias (type != "ELECTIVE") se cargan 1:1 por código real. Las
    electivas (type == "ELECTIVE") NO se cargan una por una: se agrupan en los
    placeholders fijos de `_SLOTS_SOCIOHUMANISTICA` / `_SLOTS_PROFESIONAL`
    según sus créditos, y cada placeholder hereda los grupos de todas las
    ofertas reales de ese tipo, para que el planificador pueda elegir
    cualquiera al armar el horario.
    """
    semestres: dict[int, dict[str, dict]] = {}
    materias: dict[str, dict] = {}
    grupos_socio: list[dict] = []
    grupos_prof: list[dict] = []

    for subject in _cargar_subjects():
        codigo = subject.get("code")
        sem = subject.get("semester") or 0
        creditos = subject.get("credits", 0)
        if not codigo:
            continue

        grupos = [
            {
                "id": g.get("id"),
                "code": g.get("code"),
                "teacher": g.get("teacher"),
                "materia_nombre": subject.get("name", codigo),  # para HorarioWidget
                "sessions": [
                    {
                        "day": _normalizar_dia(s.get("day")),
                        "beginHour": _hora_real(s.get("beginHour")),
                        "endHour": _hora_real(s.get("endHour")),
                        "classroom": s.get("classroom"),
                    }
                    for s in g.get("sessions", [])
                ],
            }
            for g in subject.get("groups", [])
        ]

        if subject.get("type") == "ELECTIVE":
            # No se agrega como materia individual: sus grupos se acumulan en
            # el pool según sus créditos. Créditos que no calcen con ninguna
            # casilla (ni 2 ni 3) se ignoran.
            if creditos == _CREDITOS_SOCIOHUMANISTICA:
                grupos_socio.extend(grupos)
            elif creditos == _CREDITOS_PROFESIONAL:
                grupos_prof.extend(grupos)
            continue

        materia = {
            "nombre": subject.get("name", codigo),
            "creditos": creditos,
            "prereq": [
                r.get("code") for r in subject.get("requisites", []) if r.get("code")
            ],
            "reqCred": subject.get("requiredCredits", 0),
            "grupos": grupos,
        }
        materias[codigo] = materia
        semestres.setdefault(sem, {})[codigo] = materia

    for codigo, nombre, sem in _SLOTS_SOCIOHUMANISTICA:
        materia = {
            "nombre": nombre,
            "creditos": _CREDITOS_SOCIOHUMANISTICA,
            "prereq": [],
            "reqCred": 0,
            "grupos": grupos_socio,
        }
        materias[codigo] = materia
        semestres.setdefault(sem, {})[codigo] = materia

    for codigo, nombre, sem in _SLOTS_PROFESIONAL:
        materia = {
            "nombre": nombre,
            "creditos": _CREDITOS_PROFESIONAL,
            "prereq": [],
            "reqCred": 0,
            "grupos": grupos_prof,
        }
        materias[codigo] = materia
        semestres.setdefault(sem, {})[codigo] = materia

    semestres = dict(sorted(semestres.items()))
    return semestres, materias


SEMESTRES: dict[int, dict[str, dict]] = {}
MATERIAS: dict[str, dict] = {}


def recargar() -> None:
    """
    Vuelve a leer `data/pensum_horarios.json` y refresca SEMESTRES/MATERIAS en
    memoria. Se llama al importar el módulo y después de regenerar el pénsum
    desde la UI, para que el resto de la app vea los datos nuevos sin
    reiniciar el programa.
    """
    global SEMESTRES, MATERIAS
    SEMESTRES, MATERIAS = _construir_estructuras()


recargar()
