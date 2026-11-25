---
tipo: nodo
proyecto: Parcial 3 (PERA - Grafos Colombia)
estado: completado
archivos:
  - parcial3_pera/datos_pera.txt
dependencias:
  - "[[Parcial-3-PERA-Grafos]]"
  - "[[Nodo-Datos-Colombia-Peajes]]"
ultima_actualizacion: 2026-11-25
---

# Nodo — Persistencia Grafos (PERA)

## Propósito
Archivo único multi-sección (`[CIUDADES]`, `[RUTAS]`, `[GRUPOS]`, `[PRODUCTOS]`) delimitado por `;` y seguro ante `CRLF`, compartido entre C++17 y Python, con carga opcional al iniciar.

## Archivos Exactos
- `parcial3_pera/datos_pera.txt`

## Conexiones con Otros Nodos
- Depende de: [[Nodo-Datos-Colombia-Peajes]]
- Alimenta a: [[Nodo-Grafos-CPP]], [[Nodo-Grafos-Python-Dashboard]]
