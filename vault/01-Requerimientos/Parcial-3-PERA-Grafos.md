---
tipo: requerimiento
fuente: ../Parcial 3 EdD (2026-11-17).pdf
fecha_entrega: 2026-12-01T11:59:00-05:00
---

# Parcial 3 — Programa Estadístico de Rutas de Automóviles (PERA) — Grafos

- **Fuente:** `Parcial 3 EdD (2026-11-17).pdf`
- **Universidad:** Universidad Popular del Cesar (UPC) — Ingeniería de Sistemas — Estructura de Datos
- **Modalidad:** Grupos de 3 estudiantes.
- **MOC relacionado:** [[MOC-Parcial-3]] | **Entrega:** [[Entregables-y-Fechas]]

## Objetivo del Sistema
Contratado por el Ministerio de Transporte de Colombia para realizar un **Programa Estadístico de Rutas de Automóviles (PERA)** que modele las rutas entre las **capitales de los departamentos de Colombia**, indicando distancias, costos en combustible y costos en peajes.
- **Recomendación del enunciado:** Hacer **tres grafos**.

## Requerimientos Funcionales Obligatorios
1. **Lenguajes:** Dos programas independientes para gestionar viajes terrestres en Colombia:
   - **C / C++** -> [[Nodo-Grafos-CPP]]
   - **Python** -> [[Nodo-Grafos-Python-Dashboard]]
2. **Gestión de Rutas, Peajes y Datos Reales:**
   - Gestionar información de **rutas** y **peajes**.
   - Para cada grafo gestionar datos de **distancias** y **costos** (combustible y peajes).
   - Utilizar **datos reales del país** (capitales departamentales de Colombia, distancias, peajes). -> [[Nodo-Datos-Colombia-Peajes]]
3. **Operaciones sobre la Estructura de Datos (Grafos):**
   - Diseñar estructura de datos basada en grafos que modele el problema.
   - Permitir **ingresar, eliminar, desactivar y modificar** los datos (el PDF menciona también: datos de un producto incluyendo su categoría y validación; y datos correspondientes a los grupos e investigadores — tener en cuenta este punto textual del enunciado al diseñar/documentar).
   - Permitir **editar y modificar cualquier dato**.
4. **Cálculo Principal (PARCIAL):**
   - Calcular los costos en **tiempo**, **distancia**, **combustible** y **peajes** entre **dos ciudades dadas**.
5. **Estadísticas (Esquema Descriptivo):**
   - **En C/C++:** Presentar la información en tipo **resumen de datos**.
   - **En Python:** Mostrar un **DASHBOARD** con información estadística, **histogramas** y **diagramas de barras** (**Bono:** Mapa, se sugiere usar **Folium**).
6. **Persistencia al inicio:** -> [[Nodo-Persistencia-Grafos]]
   - Archivo de persistencia suministrado por los estudiantes.
   - El usuario puede decidir si **cargar los datos del archivo** o **ejecutar sin datos**.

## Documentación Técnica Requerida
- Archivo Word (texto) de especificación técnica (diseño de estructura de datos, estrategia de solución, imágenes y diagramas, plantilla de requerimientos) -> [[Nodo-Docs-UML-Parcial-3]]
- Diagramas UML obligatorios:
  - Diagramas de **Casos de Uso** (UML)
  - Diagramas de **Secuencia** (UML)
  - Diagramas de **Estado** (UML)
