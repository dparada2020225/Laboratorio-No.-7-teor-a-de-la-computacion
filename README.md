# Laboratorio 7 — Teoría de la computación

Universidad del Valle de Guatemala · Teoría de la computación

**Autor:** Denil José Parada Cabrera

Simplificación de gramáticas libres de contexto (CFG): un programa que elimina
producciones-ε mostrando el procedimiento paso a paso (Problema 1) y la resolución
a mano de tres CFGs (Problema 2).

## Video de demostración

> **Pendiente:** aquí va el enlace al video de YouTube (no listado, máximo 10 minutos)
> donde se muestra la ejecución del programa del Ejercicio 1.
>
> `https://youtu.be/PEGAR-AQUI-EL-ENLACE`

## Estructura del repositorio

```text
.
├── README.md
├── ejercicio 1/
│   ├── simplificar_gramaticas.py     Programa principal
│   ├── gramatica1.txt                CFG 1 del Ejercicio 2
│   ├── gramatica2.txt                CFG 2 del Ejercicio 2
│   ├── gramatica3.txt                CFG 3 del Ejercicio 2
│   ├── gramatica_con_error.txt       Gramática con errores, para probar la validación
│   └── regex_automata/               Motor de regex del Proyecto 1
└── ejercicio 2/
    ├── ejercicio_2.pdf               Respuestas del Problema 2
    └── ejercicio_2.tex               Código fuente LaTeX del PDF
```

## Ejercicio 1: eliminación de producciones-ε

El lenguaje elegido es **Python 3.10 o superior**. No requiere instalar ninguna
dependencia.

### Ejecución

Desde la carpeta `ejercicio 1`:

```bash
python simplificar_gramaticas.py gramatica1.txt
python simplificar_gramaticas.py gramatica2.txt
python simplificar_gramaticas.py gramatica3.txt
python simplificar_gramaticas.py gramatica_con_error.txt
```

Si no se pasa ningún archivo, el programa pregunta el nombre.

### Formato de los archivos de gramática

Una producción por línea. Varias producciones del mismo no terminal pueden ir en
una sola línea separadas por `|`.

```text
S -> 0A0 | 1B1 | BB
A -> C
B -> S | A
C -> S | ε
```

- Una letra mayúscula individual es un **no terminal**.
- Una letra minúscula o un dígito es un **terminal**.
- `ε` representa la cadena vacía.
- La flecha puede escribirse `->` o `→`.
- El símbolo inicial es el lado izquierdo de la primera línea.
- Las líneas en blanco se ignoran.

### Qué hace el programa

1. **Carga y valida** cada línea del archivo. La validación no usa la librería `re`
   de Python: usa el motor de expresiones regulares construido en el
   Proyecto 1 del curso (carpeta `regex_automata`). La regex de las producciones se convierte a postfix con
   Shunting Yard, luego a AFN con Thompson, a AFD por subconjuntos y se minimiza.
   Cada línea se simula en esos autómatas. Si alguna línea es inválida, el programa
   indica la línea y el símbolo donde falla y **detiene la ejecución**.

   La regex usada (sintaxis del Proyecto 1) es:

   ```text
   [A-Z]\ *(->|→)\ *([a-zA-Z0-9]+|\ε)(\ *\|\ *([a-zA-Z0-9]+|\ε))*
   ```

2. **Elimina las producciones-ε**, mostrando en pantalla cada paso:
   - Encuentra los símbolos anulables, ronda por ronda.
   - Para cada producción con `m` símbolos anulables, genera los **2^m casos**
     posibles (quitar o conservar cada anulable), descartando el cuerpo vacío y
     los repetidos.
   - Muestra la gramática resultante sin producciones-ε.

### Ejemplo de salida

```text
$ python simplificar_gramaticas.py gramatica_con_error.txt
  [OK]    línea 1: S -> 0A0 | 1B1 | BB   (AFN: sí | AFD: sí | AFD mín.: sí)
  [OK]    línea 2: A -> C   (AFN: sí | AFD: sí | AFD mín.: sí)
  [ERROR] línea 3: símbolo inesperado '='
          B => S | A
            ^
          (AFN: no | AFD: no | AFD mín.: no)
  ...
Se encontraron 2 error(es). Se detiene la ejecución.
```

### Nota sobre el resultado

Se eliminan **todas** las producciones-ε. Si el símbolo inicial es anulable (como en
las gramáticas 1 y 2), la gramática resultante genera `L(G) − {ε}`, y el programa lo
avisa.

## Ejercicio 2: CFGs a mano

Carpeta `ejercicio 2/`. El PDF contiene, para cada una de las tres gramáticas, el
procedimiento completo de:

- a) eliminar producciones-ε,
- b) eliminar producciones unitarias,
- c) eliminar símbolos inútiles (que no producen y no alcanzables),
- d) pasar a Forma Normal de Chomsky.

En la gramática 2, el símbolo `E` de `C → CDE` no tiene producciones; se trata como
un no terminal sin producciones, por lo que `C` y `E` se eliminan como símbolos que
no producen.

## Créditos

El paquete `regex_automata` (Shunting Yard, Thompson, subconjuntos, minimización y
simulación) proviene del Proyecto 1 del curso.
