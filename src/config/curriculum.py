"""
src/config/curriculum.py
========================
Datos estáticos del plan curricular del programa de Ingeniería de Sistemas.

Contiene el diccionario SEMESTRES (estructura jerárquica por semestre)
y MATERIAS (diccionario plano para búsqueda directa por código).
Esta es la única fuente de verdad del plan académico — nunca duplicar
estos datos en otro módulo.
"""

# ── Plan curricular completo — 10 semestres ────────────────────────────────
# Estructura: semestre_num → { código: { nombre, creditos, prereq, reqCred } }
#   - prereq: lista de códigos que deben estar aprobados antes
#   - reqCred: mínimo de créditos acumulados para poder cursar la materia
SEMESTRES: dict[int, dict[str, dict]] = {
    1: {
        "1155101": {"nombre": "CALCULO DIFERENCIAL",             "creditos": 4, "prereq": [], "reqCred": 0},
        "1155102": {"nombre": "MATEMATICAS DISCRETAS",           "creditos": 3, "prereq": [], "reqCred": 0},
        "1155104": {"nombre": "FUNDAMENTOS DE PROGRAMACION",     "creditos": 3, "prereq": [], "reqCred": 0},
        "1155105": {"nombre": "INTRO A INGENIERIA DE SISTEMAS",  "creditos": 3, "prereq": [], "reqCred": 0},
        "1155106": {"nombre": "COMUNICACION I",                  "creditos": 2, "prereq": [], "reqCred": 0},
        "1155108": {"nombre": "INTROD. A LA VIDA UNIVERSITARIA", "creditos": 1, "prereq": [], "reqCred": 0},
    },
    2: {
        "1155201": {"nombre": "CALCULO INTEGRAL",            "creditos": 4, "prereq": ["1155101"], "reqCred": 0},
        "1155202": {"nombre": "ALGEBRA LINEAL",              "creditos": 3, "prereq": ["1155101"], "reqCred": 0},
        "1155203": {"nombre": "FISICA MECANICA",             "creditos": 4, "prereq": ["1155101"], "reqCred": 0},
        "1155204": {"nombre": "PROGR ORIENTADA A OBJETOS I", "creditos": 3, "prereq": ["1155104"], "reqCred": 0},
        "1155206": {"nombre": "COMUNICACION II",             "creditos": 2, "prereq": ["1155106"], "reqCred": 0},
        "1155209": {"nombre": "SEMINARIO INTEGRADOR I",      "creditos": 1, "prereq": ["1155104"], "reqCred": 0},
    },
    3: {
        "1155301": {"nombre": "CALCULO VECTORIAL",            "creditos": 4, "prereq": ["1155201"],           "reqCred": 0},
        "1155303": {"nombre": "FISICA ELECTROMAGNETICA",      "creditos": 4, "prereq": ["1155203"],           "reqCred": 0},
        "1155304": {"nombre": "ESTRUCTURA DE DATOS",          "creditos": 3, "prereq": ["1155204"],           "reqCred": 0},
        "1155305": {"nombre": "PROGR ORIENTADA A OBJETOS II", "creditos": 3, "prereq": ["1155204"],           "reqCred": 0},
        "1155306": {"nombre": "SEMINARIO DE INVESTIGACION I", "creditos": 2, "prereq": ["1155209"],           "reqCred": 23},
    },
    4: {
        "1155401": {"nombre": "ECUACIONES DIFERENCIALES",  "creditos": 4, "prereq": ["1155301"], "reqCred": 0},
        "1155402": {"nombre": "PROBABILIDAD Y ESTADISTICA", "creditos": 3, "prereq": ["1155102"], "reqCred": 0},
        "1155403": {"nombre": "ONDAS Y PARTICULAS",         "creditos": 3, "prereq": ["1155303"], "reqCred": 0},
        "1155404": {"nombre": "ANALISIS DE ALGORITMOS",     "creditos": 3, "prereq": ["1155304"], "reqCred": 0},
        "1155405": {"nombre": "TEORIA DE LA COMPUTACION",   "creditos": 3, "prereq": ["1155304"], "reqCred": 0},
    },
    5: {
        "1155501":          {"nombre": "ANALISIS NUMERICO",            "creditos": 3, "prereq": ["1155401"], "reqCred": 0},
        "1155502":          {"nombre": "INVESTIGACIÓN DE OPERACIONES",  "creditos": 3, "prereq": ["1155402"], "reqCred": 0},
        "1155503":          {"nombre": "ELECTRONICA",                  "creditos": 3, "prereq": ["1155403"], "reqCred": 0},
        "1155504":          {"nombre": "ARQUITECTURA DE COMPUTADORES",  "creditos": 3, "prereq": ["1155304"], "reqCred": 0},
        "1155506":          {"nombre": "SEMINARIO DE INVESTIGACIÓN II", "creditos": 2, "prereq": ["1155306"], "reqCred": 0},
        "SOCIOHUMANISTICA_I": {"nombre": "ELECTIVA SOCIOHUMANISTICA I", "creditos": 2, "prereq": [],         "reqCred": 0},
    },
    6: {
        "1155604":             {"nombre": "SISTEMAS OPERATIVOS",          "creditos": 3, "prereq": ["1155504"],           "reqCred": 0},
        "1155605":             {"nombre": "BASES DE DATOS",               "creditos": 3, "prereq": ["1155304","1155305"], "reqCred": 0},
        "1155606":             {"nombre": "PROGRAMACION WEB",             "creditos": 3, "prereq": ["1155305","1155304"], "reqCred": 0},
        "1155607":             {"nombre": "CONSTITUCION Y CIVISMO",       "creditos": 2, "prereq": [],                   "reqCred": 20},
        "1155608":             {"nombre": "PLANEACION ESTRATEGICA DE SI", "creditos": 3, "prereq": [],                   "reqCred": 48},
        "1155609":             {"nombre": "SEMINARIO INTEGRADOR II",      "creditos": 2, "prereq": ["1155209","1155304"],"reqCred": 75},
        "ELECTIVA_PROFESIONAL_I": {"nombre": "ELECTIVA PROFESIONAL I",   "creditos": 3, "prereq": [],                   "reqCred": 0},
    },
    7: {
        "1155704": {"nombre": "TEORÍA GENERAL DE LAS COMUNICACIONES",    "creditos": 3, "prereq": ["1155604"], "reqCred": 0},
        "1155705": {"nombre": "ANÁLISIS Y DISEÑO DE SISTEMAS",           "creditos": 4, "prereq": ["1155605"], "reqCred": 0},
        "1155706": {"nombre": "SEMINARIO DE INVESTIGACION III",          "creditos": 2, "prereq": ["1155506"], "reqCred": 0},
        "1155707": {"nombre": "ETICA PROFESIONAL",                       "creditos": 2, "prereq": [],          "reqCred": 90},
        "1155708": {"nombre": "ADMINISTACION DE PROYECTOS INFORMÁTICOS", "creditos": 3, "prereq": ["1155608"], "reqCred": 0},
        "ELECTIVA_PROFESIONAL_II": {"nombre": "ELECTIVA PROFESIONAL II", "creditos": 3, "prereq": [],          "reqCred": 0},
    },
    8: {
        "1155804": {"nombre": "REDES DE COMPUTADORES",                             "creditos": 3, "prereq": ["1155704"],                    "reqCred": 0},
        "1155805": {"nombre": "INGENIERÍA DE SOFTWARE",                            "creditos": 4, "prereq": ["1155705"],                    "reqCred": 0},
        "1155808": {"nombre": "FORMULACION Y EVALUACION DE PROYECTOS DE SISTEMAS", "creditos": 3, "prereq": ["1155708"],                    "reqCred": 0},
        "1155809": {"nombre": "SEMINARIO INTEGRADOR III",                          "creditos": 2, "prereq": ["1155705","1155606","1155609"],"reqCred": 0},
        "ELECTIVA_PROFESIONAL_III": {"nombre": "ELECTIVA PROFESIONAL III",         "creditos": 3, "prereq": [],                             "reqCred": 0},
        "SOCIOHUMANISTICA_II":      {"nombre": "ELECTIVA SOCIOHUMANISTICA II",     "creditos": 2, "prereq": [],                             "reqCred": 0},
    },
    9: {
        "1155908": {"nombre": "GESTION DE TIC",           "creditos": 2, "prereq": ["1155808"], "reqCred": 0},
        "1155909": {"nombre": "PRACTICA EN SISTEMAS",     "creditos": 6, "prereq": [],          "reqCred": 130},
        "1155905": {"nombre": "ARQUITECTURA DE SOFTWARE", "creditos": 3, "prereq": ["1155805"], "reqCred": 0},
        "ELECTIVA_PROFESIONAL_IV": {"nombre": "ELECTIVA PROFESIONAL IV", "creditos": 3, "prereq": [], "reqCred": 0},
    },
    10: {
        "1156001":              {"nombre": "PROYECTO DE GRADO",            "creditos": 8, "prereq": [], "reqCred": 100},
        "ELECTIVA_PROFESIONAL_V":  {"nombre": "ELECTIVA PROFESIONAL V",   "creditos": 3, "prereq": [], "reqCred": 0},
        "ELECTIVA_PROFESIONAL_VI": {"nombre": "ELECTIVA PROFESIONAL VI",  "creditos": 3, "prereq": [], "reqCred": 0},
        "SOCIOHUMANISTICA_III":    {"nombre": "ELECTIVA SOCIOHUMANISTICA III", "creditos": 2, "prereq": [], "reqCred": 0},
    },
}

# ── Diccionario plano de todas las materias ────────────────────────────────
# Generado automáticamente desde SEMESTRES para búsqueda O(1) por código.
MATERIAS: dict[str, dict] = {}
for _materias_sem in SEMESTRES.values():
    MATERIAS.update(_materias_sem)
