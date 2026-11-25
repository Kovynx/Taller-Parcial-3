---
tipo: nodo
proyecto: Taller 3 (PAA - Árboles AVL)
estado: en-qa-windows
archivos:
  - taller3_avl/Especificacion_Tecnica_Taller_3.docx
  - taller3_avl/Identificacion_Estudiantes.txt
  - taller3_avl/docs/uml_casos_uso_taller3.png
  - taller3_avl/docs/uml_secuencia_taller3.png
  - taller3_avl/docs/uml_estados_taller3.png
  - scripts/generar_docs_taller3.py
dependencias:
  - "[[Taller-3-PAA-AVL]]"
  - "[[Entregables-y-Fechas]]"
ultima_actualizacion: 2026-11-25
---

# Nodo — Documentación y UML Taller 3

## Propósito
Centralizar el documento técnico Word (`.docx`), la plantilla de requerimientos, las variables de entrada/salida, los diagramas UML (Casos de Uso, Secuencia, Estados), el archivo de identificación de estudiantes y los insumos del video de 10 minutos.

## Archivos Exactos
- `plantilla_formato.doc` — Plantilla oficial **IEEE Std 830-1998 (SRS)** de referencia.
- `taller3_avl/Especificacion_Tecnica_Taller_3.docx` — Informe IEEE 830 completo (`602 KB`) con los 3 diagramas UML embebidos y 0 rastros de IA/plantillas.
- `taller3_avl/docs/uml_casos_uso_taller3.png`, `uml_secuencia_taller3.png`, `uml_estados_taller3.png` — Diagramas UML a 220 DPI verificados visualmente.
- `taller3_avl/Identificacion_Estudiantes.txt` — Datos del grupo `KM-DV-ST` (falta completar cédulas, correos faltantes, `Grupo #` y URL de YouTube).
- `scripts/generar_docs_taller3.py` — Script generador interno (excluido del `.zip`).

## Estructura Exacta Exigida por `plantilla_formato.doc` (IEEE 830)
> **Nota técnica:** `plantilla_formato.doc` es OLE2 `.doc` (no `.docx`). Se convierte a `.docx` con LibreOffice (`soffice --headless --convert-to docx plantilla_formato.doc`) o se genera con `python-docx` respetando fielmente todas sus secciones y eliminando los textos guía en color azul y los `MACROBUTTON NoMacro [...]`.

1. **Portada + Ficha del documento:** Tabla de revisiones y validación (Cliente: Ingeniería de Sistemas UPC / Suministrador: Grupo de 3 estudiantes).
2. **1. Introducción:** `1.1 Propósito`, `1.2 Alcance` (PAA - AVL en C++ y Python), `1.3 Personal involucrado` (tabla con los 3 estudiantes + docente), `1.4 Definiciones y acrónimos` (AVL, BST, FE, Rotaciones LL/RR/LR/RL), `1.5 Referencias`, `1.6 Resumen`.
3. **2. Descripción general:** `2.1 Perspectiva del producto` (arquitectura en 4 capas), `2.2 Funcionalidad del producto` (**incluye Diagrama de Casos de Uso UML**), `2.3 Características de usuarios` (tabla), `2.4 Restricciones`, `2.5 Suposiciones y dependencias`, `2.6 Evolución previsible`.
4. **3. Requisitos específicos:**
   - `3.1 Interfaces` (**`3.1` detalla explícitamente todas las variables de entrada y salida del modelo**, `3.1.1 UI` con capturas C++ `GotoXY` y Python `Tkinter`, `3.1.2 Hardware`, `3.1.3 Software` formato `datos_avl.txt`, `3.1.4 Comunicación: NA`).
   - `3.2 Requisitos funcionales` (fichas individuales `RF-01..RF-09` con la tabla oficial: Número, Nombre, Tipo `[X] Requisito`, Fuente, Prioridad `[X] Alta/Esencial`).
   - `3.3 Requisitos no funcionales` (`3.3.1 Rendimiento` $O(\log n)$, `3.3.2 Seguridad`, `3.3.3 Fiabilidad`, `3.3.4 Disponibilidad`, `3.3.5 Mantenibilidad`, `3.3.6 Portabilidad` Windows/Linux).
5. **4. Apéndices (Diseño Técnico y UML):**
   - `4.1 Diseño de la Estructura de Datos AVL y Estrategia de Solución`
   - `4.2 Diagrama de Casos de Uso (UML)`
   - `4.3 Diagramas de Secuencia (UML)` (Inserción/Eliminación con rebalanceo y persistencia)
   - `4.4 Diagrama de Estados (UML)` (Ciclo de vida del nodo y árbol AVL)

## Checklist de Contenido Obligatorio
- [x] Diseño de la estructura de datos AVL y estrategia de solución
- [x] Variables de entrada y salida del modelo
- [x] Diagrama de Casos de Uso (UML)
- [x] Diagrama de Secuencia (UML)
- [x] Diagrama de Estados (UML)
- [ ] Completar cédulas, correos faltantes, `Grupo #` y URL YouTube en `Identificacion_Estudiantes.txt`
- [x] Insertar 3 capturas reales de Windows 10 en `Especificacion_Tecnica_Taller_3.docx` (`3.1.1`)
- [ ] Video ~10 min en YouTube (identidad UPC, estudiantes visibles todo el tiempo)
