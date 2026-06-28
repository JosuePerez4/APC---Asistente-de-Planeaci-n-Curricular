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

from src.config.curriculum import MATERIAS, SEMESTRES
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


def obtener_semestres_por_perfil(perfil: PerfilEstudiante) -> dict[int, dict[str, dict]]:
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
            pr in aprobadas_set or pr in materias_vistas
            for pr in data["prereq"]
        )
        if prereqs_cumplidos:
            disponibles.append(codigo)

    return disponibles


def mejor_combinacion(
    disponibles: list[str], perfil: PerfilEstudiante
) -> list[str]:
    """
    Encuentra la combinación de materias disponibles que maximiza los créditos
    sin superar el límite de 20 créditos por semestre.

    Algoritmo: fuerza bruta O(2^n). Razonable para n ≤ 15 materias disponibles.

    Returns:
        Lista de códigos de la mejor combinación encontrada.
    """
    materias_perfil = obtener_materias_por_perfil(perfil)
    mejor: list[str] = []
    max_creditos = 0

    for r in range(1, len(disponibles) + 1):
        for combo in itertools.combinations(disponibles, r):
            total = sum(materias_perfil[c]["creditos"] for c in combo)
            if total <= 20 and total > max_creditos:
                mejor = list(combo)
                max_creditos = total

    return mejor


def generar_plan_personalizado(
    perfil: PerfilEstudiante,
) -> list[tuple[int, list[str]]]:
    """
    Genera el plan de estudios personalizado para las materias pendientes del perfil.

    Si el estudiante no tiene materias vistas, retorna el plan original en orden
    de semestres. Si tiene materias vistas, simula semestres de avance óptimo.

    Returns:
        Lista de tuplas (numero_semestre, [codigos_de_materias]).
    """
    materias_vistas = perfil.materias_vistas
    materias_perfil = obtener_materias_por_perfil(perfil)
    semestres_perfil = obtener_semestres_por_perfil(perfil)

    # Sin historial: devolver el plan original sin simulación
    if not materias_vistas:
        return [
            (num, list(mats.keys()))
            for num, mats in semestres_perfil.items()
        ]

    # Con historial: simular avance desde el estado actual
    aprobadas: list[str] = []
    creditos_acumulados = sum(
        materias_perfil[cod]["creditos"]
        for cod in materias_vistas
        if cod in materias_perfil
    )
    materias_faltantes = set(materias_perfil.keys()) - materias_vistas
    semestre_actual = 1
    plan: list[tuple[int, list[str]]] = []

    while len(aprobadas) < len(materias_faltantes):
        disponibles = materias_habilitadas(
            aprobadas, creditos_acumulados, materias_vistas, perfil
        )
        if not disponibles:
            break  # Bloqueo curricular — no hay más materias disponibles

        combo = mejor_combinacion(disponibles, perfil)
        if not combo:
            break  # No hay combinación válida (ej. todas exceden 20 créditos)

        plan.append((semestre_actual, combo))

        for cod in combo:
            aprobadas.append(cod)
            creditos_acumulados += materias_perfil[cod]["creditos"]

        semestre_actual += 1

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

