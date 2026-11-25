---
tipo: nodo
proyecto: Parcial 3 (PERA - Grafos Colombia)
estado: completado
archivos:
  - parcial3_pera/Parcial_3_KM-DV-ST.cpp
dependencias:
  - "[[Parcial-3-PERA-Grafos]]"
  - "[[Nodo-Datos-Colombia-Peajes]]"
  - "[[Nodo-Persistencia-Grafos]]"
ultima_actualizacion: 2026-11-25
---

# Nodo — Grafos en C/C++ (PERA)

## Propósito
Implementación en C++11/17 del Programa Estadístico de Rutas de Automóviles (PERA) con **3 grafos ponderados sincronizados** (`GrafoDistancia`, `GrafoCombustible`, `GrafoPeajes`), cálculo de costos (tiempo, distancia, combustible, peajes) entre dos ciudades por Dijkstra $O((V+E)\log V)$, CRUD completo + desactivación (incluyendo categoría, validación y grupos/investigadores/productos) y estadísticas en **resumen descriptivo**.

## Archivos Exactos
- `parcial3_pera/Parcial_3_KM-DV-ST.cpp` — Autocontenido en 4 capas, verificado con `-Werror` en C++11 y C++17 (Linux `g++` y Windows `x86_64-w64-mingw32-g++ -static` sin DLLs externas).

## Símbolos / Estructuras Clave
- `Consola`: `inicializar`, `limpiarPantalla`, `rutaJuntoAlEjecutable`, `formatoCOP`, `formatoHoras`
- `Ciudad`, `RutaTramo`, `GrupoInvestigacion`, `ProductoTecnico`, `ResultadoRuta`, `ResumenEstadisticoPERA`
- `GrafoPonderado`: `agregarVertice`, `agregarAristaNoDirigida`, `grado`
- `SistemaPERA`: `reconstruirGrafos`, `calcularRutaOptima` (Dijkstra 4 criterios), `calcularEstadisticas`, CRUD completo para ciudades/rutas/grupos/productos
- `PersistenciaPERA`: `cargarArchivo`, `guardarArchivo`
- `InterfazPERA`: `menuCalcularRuta`, `menuGestionCiudades`, `menuGestionRutas`, `menuEntidadesInvestigacion`, `mostrarResumenEstadistico`, `inspeccionarTresGrafos`

## Conexiones con Otros Nodos
- Depende de: [[Parcial-3-PERA-Grafos]], [[Nodo-Datos-Colombia-Peajes]], [[Nodo-Persistencia-Grafos]]
- Relacionado con: [[Nodo-Grafos-Python-Dashboard]], [[Nodo-Docs-UML-Parcial-3]]
