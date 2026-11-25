---
name: obsidian-vault-navigator
description: >-
  Use this skill before exploring or modifying any file in the project.
  Guides agents to navigate the Obsidian vault by exact nodes instead of
  scanning the whole repository, and enforces updating node notes and the
  changelog after every change.
---

# Navegador de Obsidian Vault (Acceso por Nodo Exacto)

## Regla Principal
Nunca recorras todo el repositorio para entender o editar el proyecto. La bóveda en `vault/` es el índice vivo del proyecto.

## Flujo de Lectura (Antes de Editar)
1. Lee `vault/00-MOC-Principal.md` si no sabes en qué subproyecto estás.
2. Abre únicamente el MOC del subproyecto (`vault/02-Nodos-Taller-3/MOC-Taller-3.md` o `vault/03-Nodos-Parcial-3/MOC-Parcial-3.md`).
3. Abre el **Nodo exacto** relacionado con tu tarea (ej. `Nodo-AVL-CPP.md`).
4. Lee únicamente los archivos listados en la sección `Archivos Exactos` del nodo y sus dependencias directas si es necesario.

## Flujo de Sincronización (Después de Editar)
Cada vez que crees, modifiques o elimines código, datos o documentación:
1. Actualiza el nodo correspondiente en `vault/`:
   - `estado` en frontmatter (`pendiente` -> `en-progreso` -> `completado`).
   - `archivos` en frontmatter y sección `Archivos Exactos`.
   - `Símbolos / Estructuras Clave` modificados o añadidos.
   - `ultima_actualizacion` con la fecha actual.
2. Si creas un módulo nuevo que no encaja en los nodos existentes, crea una nota usando `vault/_templates/Template-Nodo.md` y enlázala en su MOC.
3. Agrega una fila en `vault/04-Bitacora/Registro-Cambios.md` indicando fecha, agente/modelo, nodo afectado y resumen breve.
4. Cierra cada fase o nodo con un **commit pequeño y atómico en Git** siguiendo `vault/00-Reglas-Git-y-Calidad.md` (sin commitear binarios compilados ni `.venv/`).
