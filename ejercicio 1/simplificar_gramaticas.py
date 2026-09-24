#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratorio 7 - Teoría de la computación
Ejercicio 1: simplificación de gramáticas (eliminación de producciones-ε)

Uso:
    python simplificar_gramaticas.py gramatica1.txt
    python simplificar_gramaticas.py            (pregunta el nombre del archivo)

Formato del archivo (una producción por línea, se pueden separar cuerpos con |):
    S -> 0A0 | 1B1 | BB
    A -> C
    C -> S | ε

  * Letra mayúscula individual  = no terminal
  * Letra minúscula o dígito    = terminal
  * ε                           = cadena vacía
  * La flecha puede ser -> o →
  * El símbolo inicial es el lado izquierdo de la primera línea.

La validación de cada línea NO usa la librería `re` de Python: usa el motor de
expresiones regulares del Proyecto 1 (carpeta regex_automata), que convierte la
regex a postfix con Shunting Yard, la pasa a AFN con Thompson, a AFD por
subconjuntos y la minimiza, y luego simula cada línea en esos autómatas.
"""

import sys
from itertools import product
from pathlib import Path

# Motor del Proyecto 1 (Shunting Yard, Thompson, subconjuntos, minimización y
# simulación). Está copiado en la carpeta regex_automata, junto a este archivo.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from regex_automata.services import analyze_expression, simulate_all  # noqa: E402
from regex_automata.simulation import simulate_dfa  # noqa: E402

EPS = "ε"

# ---------------------------------------------------------------------------
# 1. Validación con el motor de expresiones regulares del Proyecto 1
# ---------------------------------------------------------------------------
# Sintaxis del Proyecto 1: "\ " es un espacio literal, "\|" sería una barra
# literal, "\ε" es el símbolo ε como carácter, y "|" sin escapar es unión.
#
#   línea  = NoTerminal  flecha  cuerpo ( "|" cuerpo )*
#   flecha = "->" | "→"
#   cuerpo = letras/dígitos (una o más)  |  ε
_CUERPO = r"([a-zA-Z0-9]+|\ε)"
REGEX_PRODUCCION = rf"[A-Z]\ *(->|→)\ *{_CUERPO}(\ *\|\ *{_CUERPO})*"


def construir_validador():
    """
    Construye con el Proyecto 1 los autómatas de REGEX_PRODUCCION:
    infix -> postfix (Shunting Yard) -> AFN (Thompson) -> AFD (subconjuntos)
    -> AFD mínimo. Se hace una sola vez y se reutiliza para cada línea.
    """
    analisis = analyze_expression(REGEX_PRODUCCION)
    print("Validador de producciones (motor del Proyecto 1)")
    print(f"  Regex:   {REGEX_PRODUCCION}")
    print(f"  Postfix: {analisis.postfix_expression}")
    print(
        f"  AFN (Thompson): {analisis.nfa.state_count} estados | "
        f"AFD (subconjuntos): {analisis.subset.dfa.state_count} estados | "
        f"AFD mínimo: {analisis.partition.dfa.state_count} estados\n"
    )
    return analisis


def _si_no(aceptada):
    return "sí" if aceptada else "no"


def validar_linea(analisis, linea):
    """
    Simula la línea en el AFN y en los AFD del Proyecto 1.
    Devuelve (es_valida, detalle, posicion_error, mensaje_error).
    """
    resultado = simulate_all(analisis, linea)
    detalle = (
        f"AFN: {_si_no(resultado.nfa.accepted)} | "
        f"AFD: {_si_no(resultado.dfa.accepted)} | "
        f"AFD mín.: {_si_no(resultado.partition.accepted)}"
    )
    if resultado.accepted:
        return True, detalle, None, None

    # Para ubicar el error se usa el AFD por subconjuntos, que es parcial:
    # la primera transición que no existe marca el símbolo inesperado.
    sim = simulate_dfa(analisis.subset.dfa, linea, name="AFD")
    if sim.rejected_symbol is not None:
        pos = len(sim.trace)
        return False, detalle, pos, f"símbolo inesperado '{sim.rejected_symbol}'"
    return False, detalle, len(linea), "la producción está incompleta"


def cargar_gramatica(ruta, analisis):
    """
    Lee el archivo y valida cada línea con el motor del Proyecto 1.
    Si alguna línea es inválida, muestra el error y detiene la ejecución.
    Devuelve (gramática, símbolo_inicial); la gramática es un dict
    {no_terminal: [cuerpos]} donde la cadena vacía "" representa a ε.
    """
    try:
        with open(ruta, encoding="utf-8-sig") as f:
            lineas = f.read().splitlines()
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{ruta}'.")
        sys.exit(1)

    gramatica = {}
    inicial = None
    errores = 0

    print(f"Validando '{ruta}' ...")
    for n, linea in enumerate(lineas, start=1):
        linea = linea.strip()
        if linea == "":
            continue  # las líneas en blanco se ignoran
        valida, detalle, pos, mensaje = validar_linea(analisis, linea)
        if not valida:
            print(f"  [ERROR] línea {n}: {mensaje}")
            print(f"          {linea}")
            print(f"          {' ' * pos}^")
            print(f"          ({detalle})")
            errores += 1
            continue

        cabeza, cuerpos = linea.replace("→", "->").split("->", 1)
        cabeza = cabeza.strip()
        if inicial is None:
            inicial = cabeza
        lista = gramatica.setdefault(cabeza, [])
        for c in cuerpos.split("|"):
            c = c.strip()
            c = "" if c == EPS else c
            if c not in lista:
                lista.append(c)
        print(f"  [OK]    línea {n}: {linea}   ({detalle})")

    if errores:
        print(f"\nSe encontraron {errores} error(es). Se detiene la ejecución.")
        sys.exit(1)
    if not gramatica:
        print("Error: el archivo no contiene producciones.")
        sys.exit(1)

    print("Todas las líneas son válidas.\n")
    return gramatica, inicial


# ---------------------------------------------------------------------------
# Utilidades de impresión
# ---------------------------------------------------------------------------
def txt(cuerpo):
    return cuerpo if cuerpo else EPS


def mostrar(gramatica, inicial, titulo):
    print(titulo)
    orden = [inicial] + [a for a in gramatica if a != inicial]
    for a in orden:
        if a in gramatica:
            print(f"  {a} → " + " | ".join(txt(c) for c in gramatica[a]))
    print()


# ---------------------------------------------------------------------------
# 2. Eliminación de producciones-ε
# ---------------------------------------------------------------------------
def encontrar_anulables(gramatica):
    """
    Paso 1: símbolos anulables (los que derivan ε).
      - Si A → ε, A es anulable.
      - Si A → X1 X2 ... Xk y todos los Xi son anulables, A es anulable.
    Se repite hasta que no aparezcan más.
    """
    print("PASO 1: encontrar símbolos anulables")
    anulables = set()
    ronda = 0
    while True:
        ronda += 1
        nuevos = []
        for a, cuerpos in gramatica.items():
            if a in anulables:
                continue
            for c in cuerpos:
                if all(s in anulables for s in c):
                    nuevos.append((a, f"{a} → {txt(c)}"))
                    break
        if not nuevos:
            break
        for a, razon in nuevos:
            anulables.add(a)
        detalle = ", ".join(f"{a} (por {r})" for a, r in nuevos)
        print(f"  Ronda {ronda}: se agregan {detalle}")
    print(f"  Símbolos anulables = {{{', '.join(sorted(anulables)) or '∅'}}}\n")
    return anulables


def generar_variantes(cuerpo, anulables):
    """
    Dado un cuerpo con m símbolos anulables, genera los 2^m cuerpos
    resultantes de quitar o conservar cada símbolo anulable.
    Devuelve una lista de (cuerpo_resultante, quitados).
    """
    posiciones = [i for i, s in enumerate(cuerpo) if s in anulables]
    variantes = []
    for mascara in product([False, True], repeat=len(posiciones)):
        quitar = {p for p, q in zip(posiciones, mascara) if q}
        nuevo = "".join(s for i, s in enumerate(cuerpo) if i not in quitar)
        variantes.append((nuevo, sorted(quitar)))
    return posiciones, variantes


def eliminar_epsilon(gramatica, inicial):
    print("=" * 60)
    print("ELIMINACIÓN DE PRODUCCIONES-ε")
    print("=" * 60 + "\n")
    mostrar(gramatica, inicial, "Gramática original:")

    anulables = encontrar_anulables(gramatica)

    print("PASO 2: nuevas producciones (2^m combinaciones por producción)")
    nueva = {}
    for a, cuerpos in gramatica.items():
        for c in cuerpos:
            if c == "":
                print(f"  {a} → ε   (producción-ε: se elimina)")
                continue
            posiciones, variantes = generar_variantes(c, anulables)
            m = len(posiciones)
            print(f"  {a} → {c}   (m = {m} anulable(s) → 2^{m} = {2 ** m} casos)")
            for nuevo, quitados in variantes:
                if quitados:
                    marca = "quitando " + ", ".join(f"{c[i]}(pos {i + 1})" for i in quitados)
                else:
                    marca = "sin quitar nada"
                if nuevo == "":
                    print(f"       {marca:<32} → ε   [se descarta]")
                    continue
                lista = nueva.setdefault(a, [])
                if nuevo in lista:
                    print(f"       {marca:<32} → {nuevo}   [repetida]")
                else:
                    lista.append(nuevo)
                    print(f"       {marca:<32} → {nuevo}")
    print()

    # No terminales que se quedaron sin producciones
    for a in list(gramatica):
        if a not in nueva:
            print(f"  Nota: {a} se quedó sin producciones y se elimina de la gramática.")
    if inicial in anulables:
        print(f"  Nota: el símbolo inicial {inicial} es anulable, por lo que ε ∈ L(G).")
        print("        La gramática sin producciones-ε genera L(G) − {ε}.")
    print()

    # Mantener el orden original de los no terminales
    resultado = {a: nueva[a] for a in gramatica if a in nueva}
    mostrar(resultado, inicial, "RESULTADO: gramática sin producciones-ε")
    return resultado


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    # Para que ε y → se impriman bien en la consola de Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        ruta = input("Archivo de la gramática: ").strip().strip('"')

    analisis = construir_validador()
    gramatica, inicial = cargar_gramatica(ruta, analisis)
    eliminar_epsilon(gramatica, inicial)


if __name__ == "__main__":
    main()
