"""Representacion intermedia de un automata para dibujarlo.

Tanto el generador de DOT como el de SVG parten de la misma estructura, de modo
que ambos dibujan exactamente el mismo grafo: los mismos nodos, las mismas
aristas y las mismas etiquetas agrupadas.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..constants import display_symbol
from ..models.dfa import DFA
from ..models.nfa import NFA


@dataclass(frozen=True)
class GraphNode:
    """Un estado dibujable.

    Attributes:
        key: Identidad del nodo dentro del grafo.
        label: Texto que se muestra dentro del nodo.
        accepting: Se dibuja con doble borde.
        start: Recibe la flecha externa de entrada.
    """

    key: str
    label: str
    accepting: bool
    start: bool


@dataclass(frozen=True)
class GraphEdge:
    """Una transicion dibujable, con los simbolos ya agrupados."""

    source: str
    target: str
    label: str


@dataclass(frozen=True)
class AutomatonGraph:
    """Grafo listo para dibujar, con orden determinista."""

    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    start: str

    def node(self, key: str) -> GraphNode:
        """Devuelve el nodo con esa clave."""
        for nodo in self.nodes:
            if nodo.key == key:
                return nodo
        raise KeyError(key)


def _run_class(symbol: str) -> str | None:
    """Familia de caracteres dentro de la cual tiene sentido abreviar rangos."""
    if len(symbol) != 1:
        return None
    if "0" <= symbol <= "9":
        return "digito"
    if "a" <= symbol <= "z":
        return "minuscula"
    if "A" <= symbol <= "Z":
        return "mayuscula"
    return None


def format_symbols(symbols: list[str]) -> str:
    """Une los simbolos de una arista abreviando rangos consecutivos.

    Tres o mas letras o digitos seguidos se escriben como rango, de modo que
    una arista que viene de ``[a-zA-Z0-9]`` se lee ``0-9,A-Z,a-z`` en lugar de
    62 simbolos separados por comas. Los demas simbolos se listan tal cual.
    """
    ordenados = sorted(set(symbols))
    partes: list[str] = []
    indice = 0
    while indice < len(ordenados):
        inicio = ordenados[indice]
        familia = _run_class(inicio)
        fin = indice
        while (
            familia is not None
            and fin + 1 < len(ordenados)
            and _run_class(ordenados[fin + 1]) == familia
            and ord(ordenados[fin + 1]) == ord(ordenados[fin]) + 1
        ):
            fin += 1
        if fin - indice >= 2:
            partes.append(f"{inicio}-{ordenados[fin]}")
        else:
            partes.extend(ordenados[indice : fin + 1])
        indice = fin + 1
    return ",".join(partes)


def _group(pairs: list[tuple[str, str, str]]) -> tuple[GraphEdge, ...]:
    """Agrupa ``(origen, destino, simbolo)`` que comparten origen y destino."""
    agrupadas: dict[tuple[str, str], list[str]] = {}
    for origen, destino, simbolo in pairs:
        agrupadas.setdefault((origen, destino), []).append(simbolo)
    return tuple(
        GraphEdge(origen, destino, format_symbols(simbolos))
        for (origen, destino), simbolos in agrupadas.items()
    )


def nfa_to_graph(nfa: NFA) -> AutomatonGraph:
    """Convierte un AFN en su grafo dibujable."""
    nodos = tuple(
        GraphNode(
            key=estado.label,
            label=estado.label,
            accepting=nfa.is_accepting(estado),
            start=estado == nfa.start,
        )
        for estado in nfa.sorted_states
    )
    pares: list[tuple[str, str, str]] = []
    for origen, simbolo, destinos in nfa.iter_transitions():
        etiqueta = display_symbol(simbolo)
        for destino in sorted(destinos):
            pares.append((origen.label, destino.label, etiqueta))
    return AutomatonGraph(nodes=nodos, edges=_group(pares), start=nfa.start.label)


def dfa_to_graph(dfa: DFA) -> AutomatonGraph:
    """Convierte un AFD en su grafo dibujable."""
    nodos = tuple(
        GraphNode(
            key=estado.label,
            label=estado.label,
            accepting=dfa.is_accepting(estado),
            start=estado == dfa.start,
        )
        for estado in dfa.sorted_states
    )
    pares = [
        (origen.label, destino.label, simbolo)
        for origen, simbolo, destino in dfa.iter_transitions()
    ]
    return AutomatonGraph(nodes=nodos, edges=_group(pares), start=dfa.start.label)
