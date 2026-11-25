---
tipo: hito
fase: Fases 3, 4 y 5
estado: en-progreso
fecha: 2026-11-25
---

# Hito 02 — Parcial 3 (PERA - Grafos de Rutas en Colombia)

> Enlace estructural: [[MOC-Parcial-3]]

## Cambios Agrupados
- [x] **Calibración Real Colombia (`datos_pera.txt`):** Tarifas y distancias ajustadas a referencias reales CREG (~$16,200 COP/gal) e INVIAS/ANI Cat. I vigentes (32 capitales, 48 corredores, 5 capitales aisladas).
- [x] **Fase 3 (`Parcial_3_KM-DV-ST.cpp` — 3A..3C):** 3 grafos ponderados sincronizados (`Distancia`, `Combustible`, `Peajes`), CRUD completo + desactivación (cierres viales, categoría, validación, grupos/investigadores/productos), Dijkstra 4 métricas con comparativa lado a lado, resumen estadístico descriptivo y validación dual C++11/C++17 Linux + Windows PE32+ estático.
- [x] **Fase 4 (`Parcial_3_KM-DV-ST.py` — 4A..4C + Login + CartoDB):** Ventana previa de acceso (`admin` / `pera2026`, validación estricta sin vacíos ni espacios en C++ y Python), 3 grafos, Dashboard `matplotlib` y mapa interactivo `folium` sobre tiles `CartoDB voyager` / `Esri` (sin bloqueo 403 en `file://`).
- [x] **Fase 5A:** Informe IEEE 830 + 3 diagramas UML Parcial 3 + Identificacion_Estudiantes.txt generados con scripts/generar_docs_parcial3.py.
- [ ] **Fase 5B:** Script empaquetar_entregas.py y QA final en Windows 10.
