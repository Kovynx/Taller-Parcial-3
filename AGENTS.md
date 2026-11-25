# Instrucciones del Proyecto (Taller 3 & Parcial 3 - Estructura de Datos)

> **Fecha límite de entrega:** Martes 1 de Diciembre de 2026 a las 11:59 AM (`adithperez@unicesar.edu.co`).
> **Fuente de verdad:** La bóveda de Obsidian en [`vault/`](./vault/00-MOC-Principal.md).

## Regla de Navegación por Nodos (Obligatoria)

Para evitar recorrer todo el proyecto en cada cambio y ahorrar contexto/tiempo:

1. **Punto de entrada único:** Empieza siempre leyendo [`vault/00-MOC-Principal.md`](./vault/00-MOC-Principal.md) o el MOC específico (`MOC-Taller-3.md` / `MOC-Parcial-3.md`).
2. **Solo el nodo exacto:** Sigue los `[[wikilinks]]` hasta el nodo correspondiente a la tarea. Cada nodo indica las rutas exactas de archivos, símbolos clave y dependencias. **No hagas búsquedas globales innecesarias** si el nodo ya te da la ruta.
3. **Sincronización obligatoria:** Cada vez que crees, edites o elimines código, datos o documentación:
   - Actualiza la nota del nodo afectado en `vault/` (rutas, estado, símbolos, notas técnicas).
   - Agrega una entrada breve en [`vault/04-Bitacora/Registro-Cambios.md`](./vault/04-Bitacora/Registro-Cambios.md).
4. **Skills disponibles (`.agents/skills/`):**
   - `obsidian-vault-navigator`: Protocolo para navegar y mantener la vault.
   - `taller3-avl-context`: Requerimientos exactos del Taller 3 (PAA - Árboles AVL).
   - `parcial3-grafos-context`: Requerimientos exactos del Parcial 3 (PERA - Grafos Colombia).
   - `entrega-upc-checklist`: Reglas de entrega, nombrado de archivos, UML, video y correo.

## Reglas Inquebrantables de Compatibilidad Linux <-> Windows (C++ y Python)

1. **Prohibido mezclar binarios de Linux con Windows:** Un binario compilado con `g++` en Linux (ELF) **jamás** corre en Windows ni debe meterse en un `.zip` o `.bat`. Para generar `.exe` desde Linux es **obligatorio** usar `x86_64-w64-mingw32-g++ -std=c++17 -Wall -Wextra -static -static-libgcc -static-libstdc++` (el flag `-static` evita el fallo de `libstdc++-6.dll` faltante en Windows).
2. **Prohibido cabeceras POSIX o `<conio.h>`:** Nunca usar `<unistd.h>`, `<termios.h>`, `<sys/ioctl.h>` ni `<conio.h>`. Todo código dependiente del SO va aislado en un único bloque `#ifdef _WIN32` (`<windows.h>`, `SetConsoleCursorPosition` para `GotoXY`, `SetConsoleOutputCP(65001)`) / `#else` ANSI estándar, y el resto es **100% C++17 STL puro**.
3. **Cero scripts `.bat` frágiles:** Entregar únicamente el `.cpp` y `.py` autocontenidos (que compilen directo con `F11` en Dev-C++ o un clic). Si se crea algún `.bat` auxiliar para pruebas locales en Windows, debe guardarse con saltos de línea **`CRLF` (`\r\n`)** y finalizar con `pause`.
4. **ASCII puro y limpieza `CRLF`:** En C++ usar solo ASCII de 7 bits (`+ - | / \`) para ramas/tablas, `std::getline` para toda entrada, y recortar siempre `\r` al leer archivos `.txt` para que funcionen idéntico entre Windows y Linux.
5. **Verificación real antes de dar por terminado un `.cpp`:** Ningún agente puede afirmar que un `.cpp` "ya funciona en Windows" sin haberlo compilado exitosamente tanto con `g++` (Linux) como con `x86_64-w64-mingw32-g++ -static` (PE32+ Windows `.exe`) y verificado con `wine` o en Windows real.

## Reglas de Git (Commits Pequeños) y Estándar Profesional (Cero Rastros de IA)

1. **Commits pequeños y atómicos por fase:** Cada fase o nodo completado debe quedar en su propio commit pequeño y claro (ver [`vault/00-Reglas-Git-y-Calidad.md`](./vault/00-Reglas-Git-y-Calidad.md)), dejando el repo siempre listo para `git push origin main`.
2. **Cero rastros de IA ni plantillas en los entregables:** En todo archivo destinado a los `.zip` (`.cpp`, `.py`, `.docx`, `.txt`, UML) está estrictamente prohibido dejar frases de plantilla o asistente (`"pon esto acá"`, `"aquí haremos..."`, `"este modelo hizo..."`, `TODO`, `FIXME`, `Sugerencia C/E`, nombres de agentes/LLMs, `MACROBUTTON`, textos azules guía o placeholders `<...>`). El código y la documentación deben reflejar acabado profesional de industria.
3. **Aislamiento de herramientas internas:** `vault/`, `.agents/`, `AGENTS.md`, `tests_compatibilidad/` y `.git/` son infraestructura de trabajo y **nunca** se empaquetan en los `.zip` de entrega.
