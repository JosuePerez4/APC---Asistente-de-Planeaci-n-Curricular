"""
src/services/planner_service.py
================================
Lógica de negocio para la generación del plan personalizado de estudios.

Responsabilidades:
  - Filtrar materias según preferencias del perfil (con/sin Proyecto de Grado).
  - Determinar qué materias están habilitadas dado un conjunto de aprobadas.
  - Encontrar la mejor combinación de materias (máx. 20 créditos por semestre).
  - Generar el plan semestral completo de materias pendientes.
  - Calcular qué materias desbloquea cada materia del plan.

Esta capa es PURA (sin efectos secundarios de UI) y puede ser testeada de forma aislada.
"""

from __future__ import annotations

import itertools

from src.config.pensum_data import MATERIAS, SEMESTRES
from src.models.perfil import PerfilEstudiante


# ── Filtros por perfil ───────────────────────────────────────────────────────


def obtener_materias_por_perfil(perfil: PerfilEstudiante) -> dict[str, dict]:
    """
    Retorna una copia del diccionario de materias aplicando el filtro
    de Proyecto de Grado del perfil.
    """
    materias = MATERIAS.copy()
    if not perfil.incluir_proyecto_grado:
        materias.pop("1156001", None)
    return materias


def obtener_semestres_por_perfil(
    perfil: PerfilEstudiante,
) -> dict[int, dict[str, dict]]:
    """
    Retorna una copia del diccionario de semestres aplicando el filtro
    de Proyecto de Grado del perfil.
    """
    semestres = {k: dict(v) for k, v in SEMESTRES.items()}
    if not perfil.incluir_proyecto_grado and 10 in semestres:
        semestres[10] = {
            cod: mat for cod, mat in semestres[10].items() if cod != "1156001"
        }
    return semestres


# ── Algoritmo de planificación ────────────────────────────────────────────────


def materias_habilitadas(
    aprobadas: list[str],
    creditos_actuales: int,
    materias_vistas: set[str],
    perfil: PerfilEstudiante,
) -> list[str]:
    """
    Determina qué materias están disponibles para cursar dado el estado actual.

    Una materia está disponible si:
      1. No ha sido aprobada ni está en materias_vistas.
      2. Se cumplen los créditos mínimos requeridos (reqCred).
      3. Todos sus prerequisitos están en aprobadas o en materias_vistas.

    Args:
        aprobadas: Materias aprobadas en el plan simulado actual.
        creditos_actuales: Créditos acumulados hasta ahora.
        materias_vistas: Materias ya aprobadas antes de la simulación.
        perfil: Perfil del estudiante (determina el conjunto de materias).

    Returns:
        Lista de códigos de materias disponibles.
    """
    materias_perfil = obtener_materias_por_perfil(perfil)
    aprobadas_set = set(aprobadas)
    disponibles: list[str] = []

    for codigo, data in materias_perfil.items():
        # Saltar si ya aprobada o ya vista
        if codigo in aprobadas_set or codigo in materias_vistas:
            continue
        # Verificar créditos mínimos
        if creditos_actuales < data["reqCred"]:
            continue
        # Verificar prerequisitos
        prereqs_cumplidos = all(
            pr in aprobadas_set or pr in materias_vistas for pr in data["prereq"]
        )
        if prereqs_cumplidos:
            disponibles.append(codigo)

    return disponibles


def _sesiones_chocan(s1: dict, s2: dict) -> bool:
    """True si dos sesiones caen el mismo día y sus rangos de hora se cruzan."""
    return (
        s1["day"] == s2["day"]
        and s1["beginHour"] is not None
        and s2["beginHour"] is not None
        and s1["beginHour"] < s2["endHour"]
        and s2["beginHour"] < s1["endHour"]
    )


def _grupo_choca_con(grupo: dict, otros: list[dict]) -> bool:
    """True si `grupo` se cruza en horario con alguno de los grupos ya elegidos."""
    for otro in otros:
        for s1 in grupo.get("sessions", []):
            for s2 in otro.get("sessions", []):
                if _sesiones_chocan(s1, s2):
                    return True
    return False


def _asignar_grupos_sin_choque(
    codigos: list[str], materias_perfil: dict, grupos_ocupados: list[dict]
) -> dict[str, dict] | None:
    """
    Backtracking: intenta elegir un grupo por materia en `codigos` tal que
    ninguno se cruce entre sí ni con `grupos_ocupados` (materias ya fijadas
    del mismo semestre, p. ej. asignaciones manuales). Factible en la
    práctica: pocas materias por semestre y pocos grupos por materia.

    Returns:
        dict código→grupo elegido, o None si no existe asignación sin cruces.
    """
    asignacion: dict[str, dict] = {}

    def backtrack(idx: int) -> bool:
        if idx == len(codigos):
            return True
        cod = codigos[idx]
        grupos_cod = materias_perfil.get(cod, {}).get("grupos", [])
        if not grupos_cod:
            return backtrack(idx + 1)  # sin oferta registrada: no se valida horario
        ocupados_actuales = grupos_ocupados + list(asignacion.values())
        for grupo in grupos_cod:
            if not _grupo_choca_con(grupo, ocupados_actuales):
                asignacion[cod] = grupo
                if backtrack(idx + 1):
                    return True
                del asignacion[cod]
        return False

    return asignacion if backtrack(0) else None


def mejor_combinacion(
    disponibles: list[str],
    perfil: PerfilEstudiante,
    limite_creditos: int = 20,
    grupos_ocupados: list[dict] | None = None,
) -> tuple[list[str], dict[str, dict]]:
    """
    Encuentra la combinación de materias disponibles que maximiza los créditos
    sin superar el límite por semestre, descartando combinaciones cuyos grupos
    ofertados no puedan cursarse sin cruce de horario entre sí ni con
    `grupos_ocupados` (materias ya fijadas del mismo semestre).

    Algoritmo: fuerza bruta O(2^n) sobre las materias, con un backtracking
    adicional O(g^n) sobre grupos por combinación evaluada. Razonable para
    n ≤ 15 materias disponibles y pocos grupos por materia.

    Returns:
        (códigos de la mejor combinación, asignación código→grupo elegida).
        Si no hay materias, o ninguna combinación es libre de cruces, retorna
        ([], {}).
    """
    materias_perfil = obtener_materias_por_perfil(perfil)
    grupos_ocupados = grupos_ocupados or []
    mejor: list[str] = []
    mejor_asignacion: dict[str, dict] = {}
    max_creditos = 0

    for r in range(1, len(disponibles) + 1):
        for combo in itertools.combinations(disponibles, r):
            total = sum(materias_perfil[c]["creditos"] for c in combo)
            if total <= limite_creditos and total > max_creditos:
                asignacion = _asignar_grupos_sin_choque(
                    list(combo), materias_perfil, list(grupos_ocupados)
                )
                if asignacion is None:
                    continue  # combinación descartada: no hay horario sin cruces
                mejor = list(combo)
                mejor_asignacion = asignacion
                max_creditos = total

    return mejor, mejor_asignacion


def generar_plan_personalizado(
    perfil: PerfilEstudiante,
) -> list[tuple[int, list[str], dict[str, dict]]]:
    """
    Genera el plan de estudios personalizado para las materias pendientes del
    perfil, respetando asignaciones manuales y evitando cruces de horario
    entre las materias de un mismo semestre.

    Returns:
        Lista de tuplas (numero_semestre, [codigos_de_materias], asignacion_horario),
        donde asignacion_horario es un dict código→grupo elegido para ese semestre.
    """
    materias_vistas = perfil.materias_vistas
    materias_perfil = obtener_materias_por_perfil(perfil)
    semestres_perfil = obtener_semestres_por_perfil(perfil)
    materias_manuales = getattr(perfil, "materias_manuales", {})

    if not materias_vistas and not materias_manuales:
        # Sin historial: no hay simulación, así que tampoco hay forma de saber
        # qué grupo se elegiría; se entrega el plan original sin horario.
        return [(num, list(mats.keys()), {}) for num, mats in semestres_perfil.items()]

    asignadas: set[str] = set()
    creditos_acumulados = sum(
        materias_perfil[cod]["creditos"]
        for cod in materias_vistas
        if cod in materias_perfil
    )
    materias_faltantes = set(materias_perfil.keys()) - materias_vistas
    semestre_actual = 1
    plan: list[tuple[int, list[str], dict[str, dict]]] = []
    max_iteraciones = 30

    while (
        len(asignadas) < len(materias_faltantes) and semestre_actual <= max_iteraciones
    ):
        forced = [
            cod
            for cod in materias_faltantes
            if cod not in asignadas and materias_manuales.get(cod) == semestre_actual
        ]
        forced_creditos = sum(
            materias_perfil[cod]["creditos"] for cod in forced if cod in materias_perfil
        )
        # Grupo de las materias forzadas entre sí: si no hay combinación libre
        # de cruces, se dejan sin asignación de horario (el usuario las verá
        # listadas igual, solo sin rejilla).
        asignacion_forced = (
            _asignar_grupos_sin_choque(forced, materias_perfil, []) or {}
        )

        aprobadas_simuladas = list(asignadas)
        disponibles_candidatas = materias_habilitadas(
            aprobadas_simuladas, creditos_acumulados, materias_vistas, perfil
        )
        disponibles = [c for c in disponibles_candidatas if c not in materias_manuales]

        capacidad_restante = 20 - forced_creditos
        combo, asignacion_combo = [], {}
        if capacidad_restante > 0 and disponibles:
            combo, asignacion_combo = mejor_combinacion(
                disponibles,
                perfil,
                limite_creditos=capacidad_restante,
                grupos_ocupados=list(asignacion_forced.values()),
            )

        mats_semestre = forced + combo
        asignacion_semestre = {**asignacion_forced, **asignacion_combo}

        if mats_semestre:
            plan.append((semestre_actual, mats_semestre, asignacion_semestre))
            asignadas.update(mats_semestre)
            creditos_acumulados += sum(
                materias_perfil[cod]["creditos"]
                for cod in mats_semestre
                if cod in materias_perfil
            )
            semestre_actual += 1
        else:
            tiene_futuras = any(
                sem > semestre_actual
                for cod, sem in materias_manuales.items()
                if cod in materias_faltantes and cod not in asignadas
            )
            if tiene_futuras:
                plan.append((semestre_actual, [], {}))
                semestre_actual += 1
            else:
                remanentes = list(materias_faltantes - asignadas)
                if remanentes:
                    plan.append((semestre_actual, remanentes, {}))
                    asignadas.update(remanentes)
                break

    remanentes = list(materias_faltantes - asignadas)
    if remanentes:
        plan.append((semestre_actual, remanentes, {}))

    return plan


# ── Materias desbloqueadas ───────────────────────────────────────────────────


def obtener_desbloqueadas_por_materia(
    codigo: str,
    perfil: PerfilEstudiante,
) -> list[str]:
    """
    Retorna los nombres de las materias que tienen *codigo* como prerequisito directo.

    Útil para mostrar en la card de plan: "Desbloquea: Cálculo Integral, Álgebra Lineal".

    Args:
        codigo: Código de la materia evaluada.
        perfil: Perfil del estudiante (determina el conjunto de materias activo).

    Returns:
        Lista de nombres (str) de materias desbloqueadas directamente.
    """
    materias_perfil = obtener_materias_por_perfil(perfil)
    desbloqueadas: list[str] = [
        data["nombre"]
        for cod, data in materias_perfil.items()
        if codigo in data["prereq"]
    ]
    return desbloqueadas


# ── Verificación de conflictos en el plan ────────────────────────────────────


def verificar_conflictos_plan(
    plan: list[tuple[int, list[str]]],
    perfil: PerfilEstudiante,
) -> dict[str, list[str]]:
    """
    Verifica si hay conflictos de prerrequisitos o créditos mínimos en el plan actual.
    Retorna un diccionario de códigos de materias a listas de advertencias en formato de texto.
    """
    materias_perfil = obtener_materias_por_perfil(perfil)
    conflictos: dict[str, list[str]] = {}

    # Mapear materia -> semestre programado en el plan
    materia_a_semestre = {}
    for sem_num, materias_sem, _ in plan:
        for cod in materias_sem:
            materia_a_semestre[cod] = sem_num

    # Evaluar los requisitos semestre por semestre
    for sem_num, materias_sem, _ in plan:
        # Materias aprobadas antes de sem_num (vistas + programadas en semestres menores)
        aprobadas_antes = set(perfil.materias_vistas)
        creditos_antes = sum(
            materias_perfil[cod]["creditos"]
            for cod in perfil.materias_vistas
            if cod in materias_perfil
        )

        for prev_sem, prev_mats, _ in plan:
            if prev_sem < sem_num:
                for cod in prev_mats:
                    aprobadas_antes.add(cod)
                    if cod in materias_perfil:
                        creditos_antes += materias_perfil[cod]["creditos"]

        for cod in materias_sem:
            if cod not in materias_perfil:
                continue
            data = materias_perfil[cod]
            msgs = []

            # 1. Verificar prerrequisitos
            for pr in data["prereq"]:
                if pr not in aprobadas_antes:
                    pr_nombre = materias_perfil.get(pr, {}).get("nombre", pr)
                    # Revisar si el prerrequisito está programado en el mismo o un semestre posterior
                    if pr in materia_a_semestre:
                        pr_sem = materia_a_semestre[pr]
                        if pr_sem == sem_num:
                            msgs.append(
                                f"Prerrequisito '{pr_nombre}' está en el mismo semestre."
                            )
                        else:
                            msgs.append(
                                f"Prerrequisito '{pr_nombre}' programado para Semestre {pr_sem}."
                            )
                    else:
                        msgs.append(f"Falta cursar el prerrequisito '{pr_nombre}'.")

            # 2. Verificar créditos acumulados
            if creditos_antes < data["reqCred"]:
                msgs.append(
                    f"Requiere {data['reqCred']} créditos mínimos (tienes {creditos_antes})."
                )

            if msgs:
                conflictos[cod] = msgs

    return conflictos
