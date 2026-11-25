---
tipo: regla-memoria
proyecto: Taller 3 y Parcial 3 (UPC 2026-2)
ultima_actualizacion: 2026-11-25
---

# 00 — Reglas de Git (Commits Pequeños) y Estándar Industrial (Cero Rastros de IA)

> Esta nota forma parte de la memoria obligatoria de la bóveda para todos los agentes y colaboradores.

## 1. Flujo Git y Commits Pequeños por Fase
- **Rama principal:** `main`.
- **Commits atómicos y pequeños:** Cada sub-fase o nodo completado debe cerrarse con su propio commit pequeño y descriptivo antes de pasar al siguiente bloque (nunca acumular todo un taller en un solo commit gigante).
- **Convención sugerida de mensajes:**
  - `chore(repo): ...` — Configuración de repositorio, `.gitignore`, scripts.
  - `docs(vault): ...` — Actualizaciones de nodos Obsidian, requerimientos, bitácora.
  - `feat(taller3-cpp): ...` / `feat(taller3-py): ...` — Fases del Taller 3 (AVL).
  - `feat(parcial3-cpp): ...` / `feat(parcial3-py): ...` — Fases del Parcial 3 (Grafos PERA).
  - `data(colombia): ...` — Dataset real de capitales y peajes.
  - `docs(entrega): ...` — Informes IEEE 830 `.docx` y diagramas UML.
  - `fix(...): ...` — Correcciones puntuales.
- **Sincronización entre CachyOS, OptiOS 10 y compañero:** Solo `git push origin main` desde CachyOS y `git pull origin main` desde Windows.
- **Binarios fuera de Git:** `.gitignore` excluye ejecutables ELF de Linux, `.exe` temporales y `.venv/`.

## 2. Estándar Industrial — Cero Rastros de IA ni Plantillas en Entregables
Aunque el docente permite el uso de LLMs/agentes, evalúa rigor profesional acorde a la industria actual. **Todo archivo que entre en los `.zip` de entrega (`.cpp`, `.py`, `.docx`, `.txt`, diagramas UML) debe estar 100% limpio:**

1. **Cero comentarios de plantilla o narrativa de asistente:**
   - Prohibido dejar frases como `"// Aquí implementaremos..."`, `"// Pon esto acá"`, `"// TODO"`, `"// FIXME"`, `"// Placeholder"`, `"// Generado por..."`, `"// Sugerencia C/E"`, o nombres de modelos/agentes (`Claude`, `Kiro`, `Carbon`, `Hydrogen`, `Neon`, `ChatGPT`, `OpenCode`, `Antigravity`).
   - Los comentarios en código deben ser breves, naturales y técnicos (invariantes, rotaciones AVL, complejidad $O(\log n)$ / $O((V+E)\log V)$, unidades de medida), escritos como código de ingeniería del grupo.
2. **Cero textos guía ni marcadores en los documentos Word (`.docx`):**
   - Eliminar el 100% de textos instructivos en color azul y campos `MACROBUTTON NoMacro [...]` de `plantilla_formato.doc`.
   - Reemplazar cualquier `<Iniciales>`, `Grupo #` o `[Inserte aquí el texto]`.
3. **Aislamiento total de archivos internos:**
   - Jamás incluir `vault/`, `.agents/`, `AGENTS.md`, `tests_compatibilidad/`, `.git/` ni scripts internos dentro de los `.zip` de entrega.
4. **Auditoría automática previa al `.zip`:**
   - `scripts/empaquetar_entregas.py` debe escanear automáticamente todos los archivos entregables antes de comprimir y **abortar** si detecta palabras/marcadores prohibidos (`TODO`, `FIXME`, `MACROBUTTON`, `Inserte aquí`, `pon esto`, `acá haremos`, `Sugerencia`, nombres de modelos/agentes o placeholders `<...>`).
