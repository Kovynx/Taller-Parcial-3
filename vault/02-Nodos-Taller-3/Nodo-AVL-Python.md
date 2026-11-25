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

# Nodo — AVL en Python

## Propósito
Implementación en Python del Programa de Aprendizaje de Árboles (PAA) para enseñar árboles binarios AVL de forma visual, mostrando ordenamiento, balanceo (rotaciones LL, RR, LR, RL) y recorridos siempre visibles.

## Archivos Exactos (Actualizar al crear)
- *(Pendiente: definir ruta exacta con iniciales de los estudiantes, ej. `taller3/python/<Iniciales>.py`)*

## Símbolos / Estructuras Clave
- *(Pendiente de definición en etapa de desarrollo)*

## Entradas y Salidas
- **Entradas:** Decisión de cargar persistencia o iniciar vacío; datos para crear, insertar, eliminar, desactivar, consultar y modificar nodos.
- **Salidas:** Visualización gráfica del árbol AVL y sus rotaciones/balanceo + recorridos Pre-orden, In-orden y Post-orden siempre visibles.

## Modo Demo Pedagógico (Botón en la UI)
Incluir un botón `▶ Demo Pedagógico` en el panel lateral que ejecuta automáticamente la secuencia exacta `10, 20, 30, 5, 3, 8, 25` (7 pasos) con pausa de ~1.2 s entre cada inserción usando `canvas.after()` (sin bloquear el event loop de tkinter), demostrando **las 4 rotaciones reales (`RR`, `LL`, `LR`, `RL`)**.

**Comportamiento matemático exacto por paso:**
1. Insertar `10` → raíz inicial `10`, FE = 0.
2. Insertar `20` → cadena derecha, FE(10) = -1.
3. Insertar `30` → desbalance en `10` (`FE = -2`, hijo `20` con `FE = -1`) → **Rotación Simple Izquierda [RR]**, raíz pasa a `20(10, 30)`. Animar ANTES/DESPUÉS en naranja durante 800 ms.
4. Insertar `5`  → inserción izquierda en `10`, árbol balanceado.
5. Insertar `3`  → desbalance en `10` (`FE = +2`, hijo `5` con `FE = +1`) → **Rotación Simple Derecha [LL]**, subárbol izquierdo pasa a `5(3, 10)`. Animar ANTES/DESPUÉS.
6. Insertar `8`  → desbalance en raíz `20` (`FE = +2`, hijo `5` con `FE = -1`) → **Rotación Doble Izquierda-Derecha [LR]**, nueva raíz `10(5(3, 8), 20(null, 30))`. Animar ANTES/DESPUÉS.
7. Insertar `25` → desbalance en `20` (`FE = -2`, hijo `30` con `FE = +1`) → **Rotación Doble Derecha-Izquierda [RL]**, árbol final simétrico perfecto `10(5(3, 8), 25(20, 30))` con `FE = 0` en todos los nodos.

**Implementación en Python/tkinter:**
- Encadenar los pasos con `root.after(delay_ms, siguiente_paso)` para no congelar la ventana.
- Deshabilitar todos los botones durante el demo (`state=tk.DISABLED`) y rehabilitarlos al terminar.
- Mostrar en un label de estado: `Demo — Paso N/7: Insertando XX → <nombre rotación>`.
- El nodo que provoca una rotación se pinta en naranja temporalmente; los nodos afectados por el rebalanceo parpadean una vez.
- Pre/in/post-orden se actualizan en tiempo real en el panel fijo inferior en cada paso.

**Valor en el video:** cubre las **4 rotaciones reales (`RR`, `LL`, `LR`, `RL`)** en ~60 segundos de forma guionizada, visualmente clara y reproducible.

## Conexiones con Otros Nodos
- Depende de: [[Taller-3-PAA-AVL]], [[Nodo-Persistencia-AVL]]
- Relacionado con: [[Nodo-AVL-CPP]], [[Nodo-Docs-UML-Taller-3]]
