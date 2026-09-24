"""Division de una expresion regular en tokens.

Reglas aplicadas:

* ``ε`` es epsilon. Como alternativa facil de teclear tambien se acepta ``^``.
* ``\\x`` produce el simbolo literal ``x`` (sirve para ``\\*``, ``\\|``, ``\\^``...).
* ``[...]`` es una clase de caracteres: acepta un solo simbolo de los que
  enumera. Admite rangos (``a-z``, ``0-9``) y escapes (``\\]``). Dentro de la
  clase todos los demas caracteres son literales, incluidos ``. * + ? | ( ) ~``.
* ``.`` es un simbolo literal. La concatenacion siempre es implicita.
* Los caracteres reservados sin escapar son operadores o parentesis.
* Cualquier otro caracter es un simbolo del alfabeto.
* Los espacios exteriores se ignoran; para un espacio literal se usa ``\\ ``.
"""

from __future__ import annotations

from ..constants import (
    EPSILON_INPUT,
    EPSILON_INPUTS,
    ESCAPE,
    INPUT_OPERATORS,
    LEFT_BRACKET,
    LEFT_PAREN,
    RANGE,
    RIGHT_BRACKET,
    RIGHT_PAREN,
)
from ..errors import TokenizationError
from ..models.token import Token, TokenType


def tokenize(expression: str, *, line_number: int | None = None) -> list[Token]:
    """Convierte ``expression`` en una lista de tokens.

    Args:
        expression: Expresion regular escrita por el usuario.
        line_number: Numero de linea del archivo de origen, si aplica.

    Returns:
        Lista de tokens en el mismo orden en que aparecen.

    Raises:
        TokenizationError: Si la expresion esta vacia, hay un escape incompleto
            o una clase de caracteres mal formada.
    """
    if not expression.strip():
        raise TokenizationError(
            "la expresion esta vacia",
            expression=expression,
            position=0,
            line_number=line_number,
        )

    def fallar(mensaje: str, posicion: int) -> TokenizationError:
        return TokenizationError(
            mensaje, expression=expression, position=posicion, line_number=line_number
        )

    tokens: list[Token] = []
    indice = 0
    longitud = len(expression)

    while indice < longitud:
        caracter = expression[indice]

        if caracter.isspace():
            indice += 1
            continue

        if caracter == ESCAPE:
            if indice + 1 >= longitud:
                raise fallar(
                    "escape incompleto: falta el caracter despues de la barra invertida",
                    indice,
                )
            literal = expression[indice + 1]
            tokens.append(Token(TokenType.SYMBOL, literal, indice, escaped=True))
            indice += 2
            continue

        if caracter == LEFT_BRACKET:
            token, indice = _read_class(expression, indice, fallar)
            tokens.append(token)
            continue

        if caracter in EPSILON_INPUTS:
            tokens.append(Token(TokenType.EPSILON, EPSILON_INPUT, indice))
        elif caracter == LEFT_PAREN:
            tokens.append(Token(TokenType.LEFT_PAREN, LEFT_PAREN, indice))
        elif caracter == RIGHT_PAREN:
            tokens.append(Token(TokenType.RIGHT_PAREN, RIGHT_PAREN, indice))
        elif caracter == RIGHT_BRACKET:
            raise fallar(
                "corchete de cierre ']' sin su '[' de apertura (use '\\]' para el simbolo)",
                indice,
            )
        elif caracter in INPUT_OPERATORS:
            tokens.append(Token(TokenType.OPERATOR, caracter, indice))
        else:
            tokens.append(Token(TokenType.SYMBOL, caracter, indice))

        indice += 1

    if not tokens:
        raise fallar("la expresion no contiene ningun simbolo", 0)

    return tokens


def _read_class(expression: str, inicio: int, fallar) -> tuple[Token, int]:
    """Lee una clase ``[...]`` que empieza en ``inicio``.

    Returns:
        El token de la clase y el indice siguiente al ``]`` de cierre.
    """
    longitud = len(expression)
    indice = inicio + 1

    # Cada elemento es (caracter, posicion). Se leen primero todos los
    # caracteres literales, resolviendo escapes, y luego se arman los rangos.
    elementos: list[tuple[str, int, bool]] = []  # (caracter, posicion, es_guion_rango)
    cerrado = False
    while indice < longitud:
        caracter = expression[indice]
        if caracter == ESCAPE:
            if indice + 1 >= longitud:
                raise fallar(
                    "escape incompleto dentro de la clase de caracteres", indice
                )
            elementos.append((expression[indice + 1], indice, False))
            indice += 2
            continue
        # Un ']' justo despues de '[' es literal, como en POSIX: '[]a]'.
        if caracter == RIGHT_BRACKET and elementos:
            cerrado = True
            indice += 1
            break
        elementos.append((caracter, indice, caracter == RANGE))
        indice += 1

    if not cerrado:
        raise fallar("clase de caracteres '[' sin su ']' de cierre", inicio)

    simbolos: set[str] = set()
    posicion = 0
    while posicion < len(elementos):
        caracter, pos_caracter, _ = elementos[posicion]
        hay_rango = (
            posicion + 2 < len(elementos)
            and elementos[posicion + 1][2]  # '-' sin escapar
        )
        if hay_rango:
            final, pos_final, _ = elementos[posicion + 2]
            if ord(final) < ord(caracter):
                raise fallar(
                    f"rango invalido '{caracter}-{final}': el inicio es mayor que el final",
                    pos_caracter,
                )
            simbolos.update(chr(codigo) for codigo in range(ord(caracter), ord(final) + 1))
            posicion += 3
        else:
            # Un '-' al inicio o al final de la clase es literal.
            simbolos.add(caracter)
            posicion += 1

    texto = expression[inicio:indice]
    token = Token(
        TokenType.CLASS,
        texto,
        inicio,
        symbols=tuple(sorted(simbolos)),
    )
    return token, indice
