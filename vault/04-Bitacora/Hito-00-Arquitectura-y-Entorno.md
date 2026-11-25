---
tipo: hito
fase: Fase 0
estado: completado
fecha: 2026-11-25
---

# Hito 00 — Arquitectura, Compatibilidad y Entorno Base

> Enlace estructural: [[00-Analisis-y-Plan-Desarrollo]] | [[00-Reglas-Git-y-Calidad]]

## Cambios Agrupados (Inicialización → Plan → Fase 0)
1. **Bóveda Obsidian, Skills y Reglas:** Creación de `vault/` por nodos, `AGENTS.md` y `.agents/skills/` (`obsidian-vault-navigator`, `taller3-avl-context`, `parcial3-grafos-context`, `entrega-upc-checklist`).
2. **Análisis de Enunciados y Plan Continuo:** Inspección de ambos PDFs y de `plantilla_formato.doc` (IEEE Std 830-1998); reestructuración en fases y subfases atómicas continuas (`0A..6B`), registro oficial del equipo `KM-DV-ST` y regla de cero rastros de IA en entregables.
3. **Blindaje Linux ↔ Windows y Git:** Repositorio Git en `main` con `.gitignore` sin binarios, compilación dual `g++` + `x86_64-w64-mingw32-g++ -static` validada con `tests_compatibilidad/prueba_win_linux.cpp`.
4. **Entorno y Persistencia Base (Fase 0):** `.venv` en CachyOS (`tkinter`, `matplotlib`, `folium`, `python-docx`, `PIL`) y creación/validación BFS+Dijkstra de `taller3_avl/datos_avl.txt` y `parcial3_pera/datos_pera.txt` (32 capitales de Colombia, 48 corredores, 5 capitales aisladas).
