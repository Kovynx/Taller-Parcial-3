---
tipo: hito
fase: Fases 1 y 2
estado: completado-pendiente-video
fecha: 2026-11-25
---

# Hito 01 — Taller 3 Completo (PAA - Árboles Binarios AVL)

> Enlace estructural: [[MOC-Taller-3]]

## Cambios Agrupados (Implementación → Documentación → QA Windows 10)
1. **Implementación C++17 (`Taller_3_KM-DV-ST.cpp` — Fase 1A..1C + QA):**
   - Motor AVL en 4 capas (`Consola`, `Modelo`, `ArbolAVL`, `PersistenciaAVL`, `InterfazPAA`), CRUD completo + desactivación lógica, `GotoXY()` en cuadrícula `120x34`, recorridos Pre/In/Post-orden siempre visibles y Demo de 4 rotaciones (`10,20,30,5,3,8,25` → `RR, LL, LR, RL`).
   - **Correcciones integradas tras QA en Windows 10:** `Sleep()` nativo de `<windows.h>` (compatible con Dev-C++ C++11/C++17 sin `<thread>`), Demo no destructivo con respaldo y opción de restaurar árbol previo.
2. **Implementación Python 3 (`Taller_3_KM-DV-ST.py` — Fase 2A..2B + QA):**
   - Interfaz gráfica `tkinter` (cero dependencias externas) con paridad exacta de persistencia `datos_avl.txt`, lienzo vectorial coloreado por `FE`, panel fijo de recorridos y Demo animado con `root.after()`.
   - **Correcciones integradas tras QA en Windows 10:** Botón `Salir del Programa` con guardado opcional, ventana `1180x670` (barra de recorridos 100% visible en 1366x768) y Demo no destructivo con restauración.
3. **Documentación IEEE 830 y UML (`Especificacion_Tecnica_Taller_3.docx` — Fase 2C):**
   - Informe completo bajo estándar IEEE Std 830-1998 (0 rastros de IA/plantillas) con **3 diagramas UML a 220 DPI** (Casos de Uso, Secuencia, Estados) y **3 capturas reales de ejecución en Windows 10** incrustadas en `3.1.1`.
   - Archivo `Identificacion_Estudiantes.txt` listo para completar cédulas, `Grupo #` y URL de YouTube.
