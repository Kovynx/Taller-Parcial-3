---
tipo: bitacora
---

# Registro de Cambios

> Cada agente debe agregar una línea al inicio o al final cuando modifique cualquier nodo, código o documento.

| Fecha | Agente / Modelo | Nodo Afectado | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| 2026-11-25 | Hydrogen | [[00-MOC-Principal]] | Inicialización de la Obsidian Vault por nodos, `AGENTS.md` y skills base en `.agents/skills/`. |
| 2026-11-25 | Carbon | [[00-Analisis-y-Plan-Desarrollo]], [[Entregables-y-Fechas]] | Análisis riguroso de ambos PDFs (incluyendo URL SharePoint incrustada y cláusula punto 5 de Parcial 3), arquitectura por capas C++/Python, guía de compatibilidad Windows OptiOS 10 22H2 y plan táctico de 6 días. |
| 2026-11-25 | Kiro | [[Nodo-AVL-CPP]], [[Nodo-AVL-Python]] | Sugerencia C: especificación del Modo Demo Pedagógico (secuencia `10,20,30,25,28,5`, ~90 s, cubre rotaciones RR y RL). C++: `sleep_for` + redespliegue `GotoXY`. Python: `canvas.after()` + animación de nodos rotados en naranja. |
| 2026-11-25 | Kiro | [[00-Analisis-y-Plan-Desarrollo]] | Sugerencia E: nueva sección 5.1 en el plan con lógica de `validar_compilacion_cpp()` para `empaquetar_entregas.py` — compila con `g++ -std=c++17 -Wall -Wextra` antes de crear el `.zip`, aborta si hay errores. |
| 2026-11-25 | Carbon | [[Nodo-AVL-CPP]], [[Nodo-AVL-Python]], [[Nodo-Docs-UML-Taller-3]], [[Nodo-Docs-UML-Parcial-3]], [[00-Analisis-y-Plan-Desarrollo]] | Corrección matemática de secuencia Demo AVL (`10,20,30,5,3,8,25` cubre las 4 rotaciones reales `RR,LL,LR,RL`) y análisis binario de `plantilla_formato.doc` (IEEE Std 830-1998) integrado en los nodos de documentación. |
| 2026-11-25 | Carbon | `AGENTS.md` | Blindaje obligatorio anti-fallos Linux/Windows (prohibición de binarios ELF en entregas/scripts, compilación cruzada estática `mingw-w64-gcc -static`, cero POSIX/`conio.h`, cero `.bat` con LF y protocolo de prueba temprana en Windows/Wine). |
| 2026-11-25 | Carbon | [[Nodo-AVL-CPP]] | Creación y doble compilación real de `tests_compatibilidad/prueba_win_linux.cpp` (`prueba_linux` ELF + `prueba_win.exe` PE32+ 1.1 MB 100% estático sin `libstdc++-6.dll`). |
| 2026-11-25 | Neon | [[00-Reglas-Git-y-Calidad]], [[Entregables-y-Fechas]], `AGENTS.md` | Inicialización del repositorio Git en rama `main` con `.gitignore` (sin binarios), regla obligatoria de commits pequeños por fase y estándar industrial de cero rastros de IA/plantillas en entregables. |
