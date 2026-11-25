---
tipo: nodo
proyecto: Parcial 3 (PERA - Grafos Colombia)
estado: completado
archivos:
  - parcial3_pera/datos_pera.txt
dependencias:
  - "[[Parcial-3-PERA-Grafos]]"
ultima_actualizacion: 2026-11-25
---

# Nodo — Datos Reales de Colombia y Peajes

## Propósito
Dataset real de las **32 capitales departamentales de Colombia** (coordenadas WGS-84 reales), **48 corredores terrestres troncales** (distancia km, tiempo h, combustible COP, cantidad y costo de peajes COP, categoría vial, validado, activo), **3 grupos de estudio vial** y **4 productos técnicos**.

## Archivos Exactos
- `parcial3_pera/datos_pera.txt` — Verificado con BFS/Dijkstra: 27 capitales en 1 componente conexa terrestre + 5 capitales aisladas (`San Andres`, `Leticia`, `Mitu`, `Inirida`, `Puerto Carreno`).

## Conexiones con Otros Nodos
- Alimenta a: [[Nodo-Grafos-CPP]], [[Nodo-Grafos-Python-Dashboard]], [[Nodo-Persistencia-Grafos]]
