---
tipo: requerimiento
fuente: ../Taller 3 EdD (2026-11-17).pdf
fecha_entrega: 2026-12-01T11:59:00-05:00
---

# Taller 3 — Programa de Aprendizaje de Árboles (PAA) — Árboles AVL

- **Fuente:** `Taller 3 EdD (2026-11-17).pdf`
- **Universidad:** Universidad Popular del Cesar (UPC) — Ingeniería de Sistemas — Estructura de Datos
- **Modalidad:** Grupos de 3 estudiantes.
- **MOC relacionado:** [[MOC-Taller-3]] | **Entrega:** [[Entregables-y-Fechas]]

## Objetivo del Sistema
Realizar un **Programa de Aprendizaje de Árboles (PAA)** para enseñar cómo funcionan los **árboles binarios AVL** de manera visual: al ingresar o eliminar un dato, debe mostrarse visualmente el comportamiento de ordenamiento y balanceo (rotaciones / factores de equilibrio).

## Requerimientos Funcionales Obligatorios
1. **Lenguajes:** Dos programas independientes que gestionen la enseñanza del árbol AVL:
   - **C / C++** (puede usar `GotoXY()` para visualización en consola). -> [[Nodo-AVL-CPP]]
   - **Python** (visualización clara del ordenamiento y balanceo). -> [[Nodo-AVL-Python]]
2. **Operaciones sobre la estructura AVL:**
   - Creación
   - Inclusión (insertar)
   - Eliminación
   - Desactivación (borrado lógico / estado activo-inactivo)
   - Consulta (buscar)
   - Modificación
   - Persistencia de los datos -> [[Nodo-Persistencia-AVL]]
3. **Visualización y Recorridos:**
   - Mostrar visualmente el ordenamiento y balanceo al insertar o eliminar.
   - Los recorridos **Pre-orden**, **In-orden** y **Post-orden** deben ser **siempre visibles**.
4. **Modelo:**
   - Identificar claramente las **variables de entrada y salida** del modelo.
   - Diseñar una estructura de datos de árboles AVL que modele el problema.
5. **Persistencia al inicio:**
   - Archivo de persistencia suministrado por los estudiantes.
   - El usuario puede decidir si **cargar los datos del archivo** o **ejecutar sin datos**.

## Documentación Técnica Requerida
- Archivo Word (texto) de especificación técnica (diseño de estructura de datos, estrategia de solución, imágenes y diagramas, plantilla de requerimientos) -> [[Nodo-Docs-UML-Taller-3]]
- Diagramas UML obligatorios:
  - Diagramas de **Casos de Uso** (UML)
  - Diagramas de **Secuencia** (UML)
  - Diagramas de **Estados** (UML)
