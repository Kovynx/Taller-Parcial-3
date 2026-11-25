---
tipo: nodo
proyecto: Parcial 3 (PERA - Grafos Colombia)
estado: completado-pendiente-video
archivos:
  - parcial3_pera/docs/uml_casos_uso_parcial3.png
  - parcial3_pera/docs/uml_secuencia_parcial3.png
  - parcial3_pera/docs/uml_estados_parcial3.png
  - parcial3_pera/Especificacion_Tecnica_Parcial_3.docx
  - parcial3_pera/Identificacion_Estudiantes.txt
dependencias:
  - "[[Parcial-3-PERA-Grafos]]"
  - "[[Entregables-y-Fechas]]"
ultima_actualizacion: 2026-11-25
---

# Nodo — Documentación y UML Parcial 3

## Propósito
Centralizar el documento técnico Word (`.docx`), la plantilla de requerimientos, los diagramas UML (Casos de Uso, Secuencia, Estado), el archivo de identificación de estudiantes y los insumos del video de 10 minutos.

## Archivos Exactos
- `plantilla_formato.doc` — Plantilla oficial **IEEE Std 830-1998 (SRS)** de referencia.
- `parcial3_pera/Especificacion_Tecnica_Parcial_3.docx` — Informe IEEE 830 completo (`649 KB`) con los 3 diagramas UML embebidos y 0 rastros de IA/plantillas.
- `parcial3_pera/docs/uml_casos_uso_parcial3.png`, `uml_secuencia_parcial3.png`, `uml_estados_parcial3.png` — Diagramas UML a 220 DPI verificados visualmente.
- `parcial3_pera/Identificacion_Estudiantes.txt`, `parcial3_pera/README.txt`, `parcial3_pera/requirements.txt`.
- `scripts/generar_docs_parcial3.py` — Script generador interno (excluido del `.zip`).

## Estructura Exacta Exigida por `plantilla_formato.doc` (IEEE 830)
> **Nota técnica:** Convertir `plantilla_formato.doc` -> `.docx` o autogenerar con `python-docx` conservando la jerarquía IEEE 830-1998 exacta, tablas de ficha `RF-XX` y eliminando todas las notas guía en color azul y `MACROBUTTON NoMacro [...]`.

1. **Portada + Ficha del documento:** Cliente: Ministerio de Transporte de Colombia (simulado UPC) / Suministrador: Grupo de 3 estudiantes.
2. **1. Introducción:** `1.1 Propósito`, `1.2 Alcance` (PERA en C++ y Python), `1.3 Personal involucrado` (tabla), `1.4 Definiciones y acrónimos` (PERA, Grafo Ponderado, Lista de Adyacencia, Dijkstra, INVIAS, ANI), `1.5 Referencias`, `1.6 Resumen`.
3. **2. Descripción general:** `2.1 Perspectiva del producto` (3 Grafos sincronizados: Distancia, Combustible, Peajes), `2.2 Funcionalidad del producto` (**incluye Diagrama de Casos de Uso UML**), `2.3 Características de usuarios`, `2.4 Restricciones`, `2.5 Suposiciones`, `2.6 Evolución`.
4. **3. Requisitos específicos:**
   - `3.1 Interfaces` (Entradas/salidas del cálculo de 4 costos entre dos ciudades, `3.1.1 UI` capturas Resumen C++, Dashboard `matplotlib` y Mapa `folium`, `3.1.3 Software` formato `datos_pera.txt`, `3.1.4 Comunicación` tiles OSM para bono Folium).
   - `3.2 Requisitos funcionales` (fichas individuales `RF-01..RF-10` con tabla oficial de prioridad/fuente, incluyendo CRUD de ciudades/rutas/peajes, desactivación, categoría/validación y Dijkstra 4 métricas).
   - `3.3 Requisitos no funcionales` (`3.3.1 Rendimiento` Dijkstra $O((V+E)\log V)$, `3.3.2..3.3.6`).
5. **4. Apéndices (Diseño Técnico y UML):**
   - `4.1 Diseño de los 3 Grafos Ponderados y Estrategia Algorítmica (Dijkstra)`
   - `4.2 Diagrama de Casos de Uso (UML)`
   - `4.3 Diagramas de Secuencia (UML)` (Cálculo de ruta óptima en los 3 grafos y renderizado de Dashboard/Folium)
   - `4.4 Diagrama de Estado (UML)` (Estados de tramos viales Activo/Desactivado/Validado y flujo del motor PERA)

## Checklist de Contenido Obligatorio
- [x] Diseño de la estructura de datos basada en grafos y estrategia de solución
- [x] Diagrama de Casos de Uso (UML)
- [x] Diagrama de Secuencia (UML)
- [x] Diagrama de Estado (UML)
- [x] Archivo texto con identificación de los 3 estudiantes (`GRUPO: 05`, falta solo pegar URL YouTube)
- [ ] Video ~10 min en YouTube (identidad UPC, estudiantes visibles todo el tiempo)
