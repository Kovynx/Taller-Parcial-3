---
tipo: nodo
proyecto: Taller 3 (PAA - Árboles AVL)
estado: pendiente
archivos: []
dependencias:
  - "[[Taller-3-PAA-AVL]]"
  - "[[Nodo-Persistencia-AVL]]"
ultima_actualizacion: 2026-11-25
---

# Nodo — AVL en C/C++

## Propósito
Implementación en C/C++ del Programa de Aprendizaje de Árboles (PAA) para enseñar árboles binarios AVL de forma visual (incluyendo `GotoXY()` en consola), con recorridos siempre visibles.

## Archivos Exactos (Actualizar al crear)
- `tests_compatibilidad/prueba_win_linux.cpp` — Base validada de `Consola::GotoXY()`, `Consola::limpiarPantalla()`, `rutaJuntoAlEjecutable()` y lectura `CRLF`-safe (compilada limpio en `g++` Linux y `x86_64-w64-mingw32-g++ -static` Windows PE32+ `1.1 MB` sin DLLs externas).
- `taller3_avl/Taller_3_KM-DV-ST.cpp` — Implementación principal C++17 (pendiente de creación).

## Símbolos / Estructuras Clave
- *(Pendiente de definición en etapa de desarrollo)*

## Entradas y Salidas
- **Entradas:** Opción de carga inicial (con/sin archivo), claves/datos del nodo a insertar, eliminar, desactivar, buscar o modificar.
- **Salidas:** Representación visual del árbol AVL antes/después de rotaciones, factor de equilibrio, y recorridos Pre-orden, In-orden y Post-orden siempre visibles.

## Modo Demo Pedagógico (Opción del Menú)
Incluir una opción `D) Demo pedagógico` en el menú principal que ejecuta automáticamente la secuencia exacta `10, 20, 30, 5, 3, 8, 25` (7 pasos) con pausa de ~1.5 s entre cada inserción, garantizando cubrir **las 4 rotaciones reales del árbol AVL (`RR`, `LL`, `LR`, `RL`)** y terminar en un árbol completo simétrico.

**Comportamiento matemático exacto por paso:**
1. Insertar `10` → raíz inicial `10`, FE = 0.
2. Insertar `20` → hijo derecho de `10`, FE(10) = -1.
3. Insertar `30` → desbalance en `10` (`FE = -2`, hijo `20` con `FE = -1`) → **Rotación Simple Izquierda [RR]**; raíz pasa a `20(10, 30)`. Mostrar ANTES/DESPUÉS.
4. Insertar `5`  → hijo izquierdo de `10`, árbol balanceado.
5. Insertar `3`  → desbalance en `10` (`FE = +2`, hijo `5` con `FE = +1`) → **Rotación Simple Derecha [LL]**; subárbol izquierdo pasa a `5(3, 10)`. Mostrar ANTES/DESPUÉS.
6. Insertar `8`  → entra a la izquierda de `10`; desbalance en raíz `20` (`FE = +2`, hijo `5` con `FE = -1`) → **Rotación Doble Izquierda-Derecha [LR]**; nueva raíz global `10(5(3, 8), 20(null, 30))`. Mostrar ANTES/DESPUÉS.
7. Insertar `25` → entra a la izquierda de `30`; desbalance en `20` (`FE = -2`, hijo `30` con `FE = +1`) → **Rotación Doble Derecha-Izquierda [RL]**; subárbol derecho pasa a `25(20, 30)`. Árbol final perfecto: `10(5(3, 8), 25(20, 30))` con `FE = 0` en todos los nodos.

**Implementación en C++:**
- Usar `std::this_thread::sleep_for(std::chrono::milliseconds(1500))` (cabecera `<chrono>` + `<thread>`, disponibles en C++17/STL, sin dependencias externas).
- Antes de cada paso, limpiar la zona del árbol (re-dibujar con `GotoXY`) y mostrar en la **Zona Inferior** el texto: `[DEMO] Paso N/7: Insertando XX -> <nombre rotación o "Sin rotación">`.
- Al terminar la secuencia, pausar con `Presiona ENTER para continuar...` y volver al menú.

**Valor en el video:** cubre las **4 rotaciones reales (`RR`, `LL`, `LR`, `RL`)** en ~60 segundos de forma 100% matemática, guionizada y reproducible.

## Conexiones con Otros Nodos
- Depende de: [[Taller-3-PAA-AVL]], [[Nodo-Persistencia-AVL]]
- Relacionado con: [[Nodo-AVL-Python]], [[Nodo-Docs-UML-Taller-3]]
