---
tipo: nodo
proyecto: Parcial 3 (PERA - Grafos Colombia)
estado: completado
archivos:
  - parcial3_pera/Parcial_3_KM-DV-ST.py
dependencias:
  - "[[Parcial-3-PERA-Grafos]]"
  - "[[Nodo-Datos-Colombia-Peajes]]"
  - "[[Nodo-Persistencia-Grafos]]"
ultima_actualizacion: 2026-11-25
---

# Nodo — Grafos en Python y Dashboard (PERA)

## Propósito
Implementación en Python 3 (`tkinter` + `matplotlib` + `folium`) del Programa Estadístico de Rutas de Automóviles (PERA): 3 grafos ponderados sincronizados, calculadora Dijkstra 4 métricas con comparativa lado a lado, CRUD completo + desactivación, **DASHBOARD** con histogramas y diagramas de barras y **bono de mapa interactivo en Folium**.

## Archivos Exactos
- `parcial3_pera/Parcial_3_KM-DV-ST.py` — Autocontenido en 4 capas, paridad numérica exacta con C++, ventana `1180x670`, botón `Salir` con guardado opcional y protección `try/except ImportError` para `matplotlib`/`folium`.

## Símbolos / Estructuras Clave
- `Ciudad`, `RutaTramo`, `GrupoInvestigacion`, `ProductoTecnico`, `ResultadoRuta`, `ResumenEstadisticoPERA`
- `GrafoPonderado`, `SistemaPERA` (`reconstruir_grafos`, `calcular_ruta_optima`, `calcular_estadisticas`, CRUD completo)
- `PersistenciaPERA` (`cargar`, `guardar`)
- `VentanaAccesoPERA`: control de acceso previo modal con credenciales visibles en pantalla y en `README.txt` (`admin` / `pera2026`), casilla `Mostrar contrasena` y bloqueo estricto ante vacíos o espacios.
- `InterfazGraficaPERA` (`construir_figura_dashboard`, `generar_mapa_folium` con Esri sin 403, `_accion_comparar_grafos`, `_accion_salir`)

## Conexiones con Otros Nodos
- Depende de: [[Parcial-3-PERA-Grafos]], [[Nodo-Datos-Colombia-Peajes]], [[Nodo-Persistencia-Grafos]]
- Relacionado con: [[Nodo-Grafos-CPP]], [[Nodo-Docs-UML-Parcial-3]]
