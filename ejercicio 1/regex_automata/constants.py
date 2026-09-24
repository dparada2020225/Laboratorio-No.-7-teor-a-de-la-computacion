"""Constantes compartidas por todo el proyecto.

Reune la sintaxis aceptada de expresiones regulares: operadores, precedencias,
caracteres reservados y la representacion interna de epsilon.
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------- #
# Epsilon
# --------------------------------------------------------------------------- #

#: Caracter principal con el que el usuario escribe epsilon (el que usa el enunciado).
EPSILON_INPUT: Final[str] = "\u03b5"  # ε

#: Alternativa ASCII para epsilon, facil de teclear. No aparece en ninguna de las
#: expresiones de prueba (a diferencia de ``~``, que es un caracter valido de URL).
EPSILON_ASCII: Final[str] = "^"

#: Todas las formas aceptadas de escribir epsilon en expresiones y en cadenas.
EPSILON_INPUTS: Final[frozenset[str]] = frozenset({EPSILON_INPUT, EPSILON_ASCII})

#: Etiqueta visible de epsilon en trazas, resumenes e imagenes.
EPSILON_LABEL: Final[str] = "ε"

#: Representacion interna de epsilon como simbolo de transicion.
#:
#: Es una constante de varios caracteres y por lo tanto no puede colisionar con
#: ningun simbolo del alfabeto, ya que todo simbolo ordinario ocupa exactamente
#: un caracter. Nunca debe compararse contra un simbolo escrito por el usuario.
EPSILON: Final[str] = "\x00epsilon"

# --------------------------------------------------------------------------- #
# Operadores
# --------------------------------------------------------------------------- #

KLEENE_STAR: Final[str] = "*"
PLUS: Final[str] = "+"
OPTIONAL: Final[str] = "?"
#: Operador interno de concatenacion. El usuario ya no lo escribe: la
#: concatenacion es siempre implicita y ``.`` es un simbolo literal mas. Se usa
#: el punto medio para que en las salidas no se confunda con un ``.`` literal.
CONCATENATION: Final[str] = "\u00b7"  # ·
UNION: Final[str] = "|"
LEFT_PAREN: Final[str] = "("
RIGHT_PAREN: Final[str] = ")"
LEFT_BRACKET: Final[str] = "["
RIGHT_BRACKET: Final[str] = "]"
RANGE: Final[str] = "-"
ESCAPE: Final[str] = "\\"

#: Operadores unarios que se escriben despues de su operando.
POSTFIX_OPERATORS: Final[frozenset[str]] = frozenset({KLEENE_STAR, PLUS, OPTIONAL})

#: Operadores binarios.
BINARY_OPERATORS: Final[frozenset[str]] = frozenset({CONCATENATION, UNION})

OPERATORS: Final[frozenset[str]] = POSTFIX_OPERATORS | BINARY_OPERATORS

#: Operadores que el usuario puede escribir. La concatenacion no esta: es
#: implicita, y el tokenizador la inserta despues.
INPUT_OPERATORS: Final[frozenset[str]] = POSTFIX_OPERATORS | {UNION}

#: Precedencia de los operadores. A mayor numero, mayor prioridad.
PRECEDENCE: Final[dict[str, int]] = {
    UNION: 1,
    CONCATENATION: 2,
    KLEENE_STAR: 3,
    PLUS: 3,
    OPTIONAL: 3,
}

#: Los dos operadores binarios son asociativos por la izquierda.
LEFT_ASSOCIATIVE: Final[frozenset[str]] = frozenset({UNION, CONCATENATION})

#: Caracteres que tienen significado especial y que deben escaparse con ``\``
#: para usarse como simbolos literales fuera de una clase ``[...]``. Dentro de
#: una clase todo es literal salvo ``]``, ``-`` (rango) y ``\``.
RESERVED_CHARACTERS: Final[frozenset[str]] = frozenset(
    {
        KLEENE_STAR,
        PLUS,
        OPTIONAL,
        UNION,
        LEFT_PAREN,
        RIGHT_PAREN,
        LEFT_BRACKET,
        RIGHT_BRACKET,
        ESCAPE,
    }
    | EPSILON_INPUTS
)

# --------------------------------------------------------------------------- #
# Archivos de entrada
# --------------------------------------------------------------------------- #

#: Prefijo que marca una linea de comentario dentro del archivo de expresiones.
COMMENT_PREFIX: Final[str] = "#"

#: Nombre del estado pozo que se agrega al completar un AFD.
TRAP_STATE_LABEL: Final[str] = "TRAMPA"


def is_epsilon(symbol: str) -> bool:
    """Indica si ``symbol`` es la transicion epsilon interna."""
    return symbol == EPSILON


def display_symbol(symbol: str) -> str:
    """Devuelve la representacion legible de un simbolo de transicion."""
    return EPSILON_LABEL if is_epsilon(symbol) else symbol
