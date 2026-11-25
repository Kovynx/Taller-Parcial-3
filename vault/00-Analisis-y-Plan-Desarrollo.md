---
tipo: plan-desarrollo
proyecto: Taller 3 (AVL) + Parcial 3 (Grafos PERA)
fecha_creacion: 2026-11-25
fecha_limite: 2026-12-01T11:59:00-05:00
estado: aprobado-en-ejecucion
---

# Análisis Riguroso y Plan Maestro de Desarrollo (Taller 3 & Parcial 3)

> **Propósito de este documento:** Servir como especificación de arquitectura y plan de ejecución para revisión cruzada entre **Carbon, Kiro y Claude**, maximizando eficiencia algorítmica, claridad para el video de 10 minutos y compatibilidad 100% libre de fallos en **Windows (OptiOS 10 22H2 y PC del docente)**.

---

## 1. Diagnóstico Crítico de los Enunciados (Hallazgos y Trampas Detectadas)

Al inspeccionar a bajo nivel `Taller 3 EdD (2026-11-17).pdf` y `Parcial 3 EdD (2026-11-17).pdf` (incluyendo metadatos y URIs incrustadas), se identificaron **6 puntos críticos** que definen el éxito de la entrega:

### 1.1 Análisis de `plantilla_formato.doc` (Estándar IEEE Std 830-1998)
Ya se descargó y analizó a nivel binario `plantilla_formato.doc` en la raíz del proyecto:
- **Formato real:** Documento binario Word 97-2003 (`.doc` OLE2 CFBF, no `.docx`), basado en el estándar **IEEE Std 830-1998 (Especificación de Requisitos de Software - SRS)**.
- **Reglas internas de la plantilla:**
  1. Eliminar todos los textos guía en **color azul** y sustituir todos los campos `MACROBUTTON NoMacro [...]`.
  2. Mantener la numeración automática `Titulo1..Titulo3` (`1. Introducción`, `2. Descripción general`, `3. Requisitos específicos`, `4. Apéndices`) y actualizar la Tabla de Contenido al cerrar en Word.
  3. **Mapeo directo con la rúbrica de ambos PDFs:**
     - `3.1 Requisitos comunes de los interfaces` pide textualmente *"Descripción detallada de todas las entradas y salidas del sistema"* -> **resuelve ahí mismo las variables de entrada y salida del modelo**.
     - `3.2 Requisitos funcionales` exige para cada requisito la tabla oficial (`Número | Nombre | Tipo [Requisito/Restricción] | Fuente | Prioridad [Alta/Media/Baja]`).
     - `4. Apéndices` alojará el **Diseño detallado de la Estructura de Datos (AVL / 3 Grafos)**, **Estrategia de Solución**, los **3 Diagramas UML obligatorios (Casos de Uso, Secuencia y Estados)** y capturas de ejecución en Windows.
  4. **Flujo técnico de generación:** Convertimos `plantilla_formato.doc` a `.docx` (LibreOffice headless o Word) y/o generamos los dos `.docx` completos mediante script `python-docx` con esa estructura IEEE 830 exacta para que el compañero en Windows solo revise formato, inserte capturas finales y actualice el índice.

### 1.2 Tensión entre "Programa bien modulado" vs "Entregar los 2 archivos fuente (`<Iniciales>.cpp`, `<Iniciales>.py`)"
- **Riesgo real en calificación C++ en Windows:** Los docentes de Estructura de Datos suelen abrir `<Iniciales>.cpp` en **Embarcadero Dev-C++ / Code::Blocks** o compilar con `g++ <Iniciales>.cpp -o app.exe`. Si se entregan múltiples `.cpp` sueltos sin proyecto/Makefile, el compilador lanza `undefined reference` y el programa "no compila".
- **Solución óptima (Modularidad por Capas en Unidad Única o Bundler Automático):**
  - Estructurar cada programa en **4 capas desacopladas** (`Modelo`, `EstructuraDeDatos`, `Persistencia`, `VistaControlador`) usando `namespace` / `class` bien delimitadas.
  - **En desarrollo:** Podemos trabajar en módulos limpios (`src/...`) si se desea, o directamente en secciones modulares claramente encabezadas, pero **el entregable dentro de cada `.zip` debe ser 1 solo `.cpp` y 1 solo `.py` autocontenidos** (~450–650 líneas bien comentadas) que compilen y corran con un solo comando o tecla `F11`.
  - **Ventaja en el video (10 min):** Los 3 integrantes dividen la explicación exactamente por capas (Integrante 1: Modelo + Estructura AVL/Grafos; Integrante 2: Algoritmos de balanceo / Dijkstra + Persistencia; Integrante 3: Interfaz `GotoXY` / Dashboard Python + Demostración en vivo).

### 1.3 Cláusula heredada en Parcial 3 (Punto 5 textual del PDF)
En `Parcial 3 EdD`, el numeral 5 dice textualmente:
> *"5. La estructura de datos debe permitir ingresar, eliminar, desactivar, y modificar los datos de un producto incluyendo su categoría y su validación; y los datos correspondientes a los grupos e investigadores."*
- **Diagnóstico:** Es un texto arrastrado por el docente de una rúbrica previa (proyectos/productos de investigación MinCiencias), mezclado con el problema del Ministerio de Transporte (PERA).
- **Estrategia de blindaje (Cero pérdida de puntos bajo cualquier criterio):**
  1. En las **Rutas/Peajes** del grafo incluimos explícitamente los atributos `categoria` (ej. *Vía 4G / Primaria / Secundaria* o *Categoría Peaje I–V*) y `validado` (`bool`: tramo/tarifa verificada INVIAS/ANI), cubriendo *"categoría y validación"* de forma natural en el dominio vial.
  2. Incluimos un submódulo ligero de **Grupos de Estudio Vial / Investigadores y Productos Técnicos del MinTransporte** vinculado a los corredores (con CRUD + desactivación + categoría + validación) o lo asociamos como metadato opcional del sistema PERA. Ocupa <80 líneas y blinda el 100% de la rúbrica literal si el profesor revisa ese ítem con lista de chequeo.

### 1.4 Conectividad terrestre real de las capitales de Colombia (Parcial 3)
- Colombia tiene **32 capitales departamentales** (Bogotá D.C. es capital de Cundinamarca y Distrito Capital).
- **Realidad geográfica:** **27 capitales** están conectadas por la red vial nacional terrestre (incluyendo **Valledupar** como nodo clave de la región Caribe/Cesar), mientras que **5 capitales** carecen de conexión vial terrestre integrada al resto del país (**San Andrés** insular; **Leticia**, **Mitú**, **Inírida** amazónicas/fluviales; y **Puerto Carreño** con conexión estacional/aislada, o conectada vía ruta llanera estacional según criterio).
- **Valor académico enorme:** Cargar las **32 capitales reales** como vértices (con latitud/longitud reales) y las **~48–55 aristas reales** de corredores troncales INVIAS/ANI demuestra en vivo **componentes conexas vs vértices aislados** en teoría de grafos (ej. consultar `Valledupar -> San Andrés` responde limpiamente *"Sin ruta terrestre disponible"*).

### 1.5 Persistencia compartida C++ <-> Python sin librerías externas
- **Formato elegido:** Archivo de texto estructurado UTF-8 delimitado por `;` (`datos_avl.txt` en Taller 3 y `datos_pera.txt` en Parcial 3), cumpliendo *"un archivo de su preferencia donde se consigne la persistencia"* (singular) y *"el usuario puede decidir si cargar los datos del archivo o ejecutar sin datos"*.
- **Por qué `;` y no JSON en C++:** C++ estándar lee/escribe campos separados por `;` en ~25 líneas con `<fstream>` y `<sstream>`, sin depender de `nlohmann/json.hpp`. Tanto el ejecutable C++ como el script Python leen y actualizan **exactamente el mismo archivo**.
- **Blindaje Windows/Linux (`CRLF`):** En C++, toda lectura `std::getline` limpiará `\r` final (`if (!s.empty() && s.back() == '\r') s.pop_back();`) para que un archivo guardado en Windows funcione idéntico en Linux y viceversa.

### 1.6 Dos entregas `.zip` completamente independientes
1. **ZIP Taller 3** (`Estructura de datos Taller 3 Grupo # 2026-2`): `<Iniciales>.cpp`, `<Iniciales>.py`, `datos_avl.txt`, `Especificacion_Tecnica_Taller_3.docx`, `Identificacion_Estudiantes.txt` (+ enlace YouTube ~10 min).
2. **ZIP Parcial 3** (`Estructura de datos Parcial 3 Grupo # 2026-2`): `<Iniciales>.cpp`, `<Iniciales>.py`, `datos_pera.txt`, `Especificacion_Tecnica_Parcial_3.docx`, `Identificacion_Estudiantes.txt` (+ enlace YouTube ~10 min).

---

## 2. Arquitectura Técnica — Taller 3: PAA (Árboles Binarios AVL)

### 2.1 Modelo de Datos y Complejidad
Cada nodo del árbol AVL modela un registro académico/didáctico compacto (rápido de digitar en el video):

| Campo | Tipo | Rol |
| :--- | :--- | :--- |
| `clave` (`id`) | `int` | Clave primaria de ordenamiento BST/AVL (ej. `10, 20, 30, 25`). |
| `etiqueta` | `string` | Nombre o concepto asociado (ej. `"Estructura"`, `"Nodo_25"`). |
| `altura` | `int` | Altura del subárbol ($h(\text{hoja}) = 1$, $h(\text{null}) = 0$). |
| `activo` | `bool` | Estado lógico (`true` = activo, `false` = desactivado). |
| `izq`, `der` | Puntero / Ref | Hijos izquierdo y derecho. |

- **Factor de Equilibrio:** $FE(n) = \text{altura}(n.\text{izq}) - \text{altura}(n.\text{der}) \in \{-1, 0, +1\}$.
- **Complejidades garantizadas:**
  - Inserción, Eliminación física, Búsqueda, Desactivación/Reactivación: $O(\log n)$ peor caso.
  - Modificación de `etiqueta`: $O(\log n)$ in-situ. Modificación de `clave`: Eliminación $O(\log n)$ + Inserción $O(\log n)$ con rebalanceo visual.
  - Recorridos Pre-orden, In-orden, Post-orden: $O(n)$.

### 2.2 Visualización Pedagógica del Ordenamiento y Balanceo
Para cumplir estrictamente *"enseñar cómo funcionan los árboles binarios AVL de una manera visual"*:
1. **Bitácora paso a paso por operación:** Cada inserción o eliminación registra la traza pedagógica:
   - Comparaciones realizadas desde la raíz (`25 < 30 [Izq] -> 25 > 20 [Der]`).
   - Recálculo de alturas y $FE$ en el retorno recursivo.
   - Si $|FE| = 2$: Identificación explícita del caso (**Rotación Simple Derecha [LL]**, **Simple Izquierda [RR]**, **Doble Izquierda-Derecha [LR]**, **Doble Derecha-Izquierda [RL]**), mostrando instantánea **ANTES** y **DESPUÉS** del giro.
2. **En C++ (`GotoXY` multiplataforma):**
   - Layout fijo en consola (120x32):
     - **Zona Superior (Filas 1–16):** Lienzo 2D posicionado con `GotoXY(x, y)` dibujando cada nodo como `[25|0]` (o `(25*)` si está desactivado) y ramas ASCII `/` `\`.
     - **Zona Media Fija (Filas 17–20 — SIEMPRE VISIBLE):** Panel permanente con **Pre-orden**, **In-orden** y **Post-orden** actualizados en tiempo real.
     - **Zona Inferior (Filas 21–30):** Última rotación/explicación pedagógica + Menú de operaciones.
3. **En Python (`tkinter` estándar — CERO dependencias externas):**
   - Ventana gráfica dividida en:
     - **Canvas Central:** Dibujo vectorial del árbol AVL con nodos circulares coloreados según $FE$ (`0` verde, `±1` azul, desactivado gris punteado), animación/comparación **Antes vs Después** cuando ocurre una rotación.
     - **Panel Fijo Inferior:** **Pre-orden, In-orden y Post-orden siempre visibles**.
     - **Panel Lateral:** Botones para Crear/Vaciar, Insertar, Eliminar, Desactivar/Reactivar, Consultar, Modificar, Guardar/Cargar y **Modo Demo Pedagógico** (inserta la secuencia matemática `10, 20, 30, 5, 3, 8, 25` de 7 pasos que ejecuta **las 4 rotaciones reales: RR -> LL -> LR -> RL** y termina en un árbol simétrico perfecto durante el video).

---

## 3. Arquitectura Técnica — Parcial 3: PERA (Grafos de Rutas en Colombia)

### 3.1 Diseño de los "Tres Grafos" sin Redundancia
El enunciado recomienda *"hacer tres grafos"* y pide *"calcular los costos en tiempo, distancia, combustible y peajes entre dos ciudades dadas"*.

- **Estructura base reutilizable (`class GrafoPonderado`):**
  - Lista de adyacencia: `vector<vector<Arista>>` en C++ y `dict[int, list[Arista]]` en Python.
  - Cada vértice (`Ciudad`) almacena: `id`, `nombre`, `departamento`, `lat`, `lon`, `activa`.
  - Cada corredor (`RutaTramo`) almacena: `idRuta`, `origen`, `destino`, `distanciaKm`, `tiempoHoras`, `costoCombustibleCOP`, `cantidadPeajes`, `costoPeajesCOP`, `categoriaVia`, `validado`, `activa`.
- **Los 3 Grafos coordinados por `GestorPERA`:**
  1. **`GrafoDistancia` ($G_1$):** Peso de arista $w_1 = \text{distanciaKm}$ (optimiza ruta más corta / rápida).
  2. **`GrafoCombustible` ($G_2$):** Peso de arista $w_2 = \text{costoCombustibleCOP}$ (modelando distancia + factor topográfico montaña/llano).
  3. **`GrafoPeajes` ($G_3$):** Peso de arista $w_3 = \text{costoPeajesCOP}$ (optimiza ruta con menor pago de peajes).
- **Algoritmo de Ruta Óptima (Dijkstra con Cola de Prioridad):**
  - Complejidad: $O((V + E) \log V)$ usando `std::priority_queue` (C++) y `heapq` (Python).
  - Ignora automáticamente ciudades o tramos con `activa == false` (permite simular en el video un **cierre vial por derrumbe** desactivando una arista y viendo cómo el algoritmo recalcula ruta alterna en vivo).
  - Al consultar entre Ciudad A y Ciudad B (eligiendo criterio: menor distancia, menor peaje, menor combustible o menor costo total = combustible + peajes), reconstruye la secuencia exacta de capitales intermedias y entrega el **desglose completo de las 4 métricas: Tiempo (h/min), Distancia (km), Combustible (COP) y Peajes (COP)**.

### 3.2 Esquema Estadístico Descriptivo (C++ vs Python)
- **En C++ (Resumen Estadístico en Consola):**
  - Conteo de capitales activas/inactivas/aisladas y tramos viales.
  - Estadísticos descriptivos ($n$, media, mediana, desviación estándar, mínimo, máximo, suma) para **Distancia**, **Tiempo**, **Combustible** y **Peajes**.
  - Top 5 nodos con mayor grado (hubs viales de Colombia) y Top 5 corredores más costosos.
- **En Python (`tkinter` + `matplotlib` + `folium`):**
  - Se ejecuta directamente con `python <Iniciales>.py` (sin requerir comandos externos tipo servidor).
  - **Pestaña 1 — Gestión y Calculadora de Rutas (Dijkstra en los 3 Grafos):** Selector de ciudad origen/destino, criterio de optimización, tabla de ruta paso a paso y CRUD completo (Ciudades, Rutas/Peajes, Grupos/Productos viales).
  - **Pestaña 2 — DASHBOARD Estadístico (`matplotlib` embebido):**
    - Tarjetas KPI (Total km red nacional, promedio peajes, capital más conectada, costo promedio por km).
    - **Histogramas:** Distribución de distancias entre capitales y distribución de costos de peajes por tramo.
    - **Diagramas de barras:** Top 10 capitales por conectividad (grado del vértice) y comparativa de costos Combustible vs Peajes por corredor principal.
  - **Botón Bono — Mapa Interactivo de Colombia (`folium`):**
    - Genera `mapa_pera_colombia.html` y lo abre en el navegador (`webbrowser.open`): pinta las 32 capitales sobre el mapa real de Colombia, dibuja todos los corredores activos/inactivos con popups de peajes/distancias, y **resalta en color destacado la ruta óptima calculada entre las dos ciudades seleccionadas**.

---

## 4. Guía de Compatibilidad Total: Linux + Dual Boot OptiOS 10 22H2

Para garantizar **cero retrasos y cero fallos de ejecución en Windows**:

### 4.1 Reglas de Oro en C++ (Portabilidad Garantizada)
1. **Estándar C++17 puro (`-std=c++17`) solo con STL:** Compatible con GCC en Linux, MinGW-w64 moderno y Embarcadero Dev-C++ 6.3.
2. **Capa `Console` aislada con `#ifdef _WIN32` (30 líneas):**
   - En Windows (`_WIN32`): incluye `<windows.h>`, define `GotoXY(int x, int y)` usando `SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord)` y activa UTF-8 con `SetConsoleOutputCP(65001); SetConsoleCP(65001);`. Esto funciona nativamente en el `cmd.exe` clásico (`conhost.exe`) de **OptiOS 10 22H2** (que no trae Windows Terminal por ser recortado).
   - En Linux: usa secuencias ANSI `\033[y;xH`.
3. **Bordes y árboles 100% ASCII de 7 bits (`+`, `-`, `|`, `/`, `\`):** Evita por completo caracteres Unicode `┌─┐` que se rompen en consolas `cmd.exe` con fuente Raster/Consolas mal configurada.
4. **Entrada estándar segura:** Usar `std::getline(std::cin, linea)` con conversión segura (`std::stoi` / `std::stod` en `try/catch`) en vez de `cin >>` mezclado o `getch()` de `<conio.h>`. Así un error de dedo en pleno video nunca mete al programa en un bucle infinito.
5. **Compilación estática del `.exe` de prueba:** Al compilar en Windows/MinGW usar `-static -static-libgcc -static-libstdc++` para no depender jamás de `libstdc++-6.dll` ni `libwinpthread-1.dll`.

### 4.2 Flujo Recomendado entre Linux y OptiOS 10 22H2 (85% / 15%)
- **En Linux (85% del tiempo — Desarrollo rápido y pruebas):**
  - Desarrollamos y depuramos toda la lógica, persistencia, documentos `.docx` y diagramas UML aquí mismo con acceso rápido a la Vault y agentes.
  - *(Opcional en Linux)*: Si instalas `mingw-w64-gcc` (`sudo pacman -S mingw-w64-gcc`), podemos cruzar-compilar el `.exe` de Windows desde Linux en cada cambio para verificar que el bloque `#ifdef _WIN32` compila sin un solo warning antes siquiera de reiniciar.
- **En OptiOS 10 22H2 (15% del tiempo — Validación final, capturas y grabación de video):**
  - **Checklist de entorno en OptiOS 10 22H2 (15 minutos una sola vez):**
    1. Verificar/instalar **Microsoft Visual C++ Redistributable 2015–2022 (x64)** *(clave en OptiOS porque las ISOs optimizadas a veces lo omiten y Python/`matplotlib` lo requieren por `vcruntime140.dll`)*.
    2. Instalar **Python 3.12 (x64)** marcando `Add python.exe to PATH` y verificando que `tcl/tk` (`tkinter`) esté marcado. Ejecutar:
       `pip install matplotlib folium python-docx`
    3. Instalar **Embarcadero Dev-C++ 6.3** o **WinLibs MinGW-w64** para probar que abrir `<Iniciales>.cpp` y compilar/ejecutar abre `cmd.exe` perfecto a la primera.
    4. Tomar las capturas en Windows para el Word y grabar los 2 videos en OBS Studio.

---

## 5. Estructura de Carpetas del Repositorio y Empaquetado Final

```text
Taller-Parcial 3/
├── vault/                             # Bóveda Obsidian (NO entra en los .zip)
├── .agents/skills/                    # Skills de contexto (NO entra en los .zip)
├── tests_compatibilidad/              # Pruebas de humo Win/Linux (NO entra en los .zip)
├── taller3_avl/                       # Trabajo del Taller 3 -> Taller_3_Grupo_05.zip
│   ├── Taller_3_KM-DV-ST.cpp          # C++17 AVL visual con GotoXY() (120x34 seguro)
│   ├── Taller_3_KM-DV-ST.py           # Python tkinter AVL visual interactivo
│   ├── datos_avl.txt                  # Persistencia compartida (; CRLF-safe)
│   ├── Identificacion_Estudiantes.txt
│   └── docs/                          # Especificacion_Tecnica_Taller_3.docx + 3 UML PNG
├── parcial3_pera/                     # Trabajo del Parcial 3 -> Parcial_3_Grupo_05.zip
│   ├── Parcial_3_KM-DV-ST.cpp         # C++17 3 Grafos Colombia + Dijkstra + Resumen
│   ├── Parcial_3_KM-DV-ST.py          # Python 3 Grafos + Dashboard Matplotlib + Bono Folium
│   ├── datos_pera.txt                 # Persistencia real Colombia (32 capitales + peajes)
│   ├── Identificacion_Estudiantes.txt
│   └── docs/                          # Especificacion_Tecnica_Parcial_3.docx + 3 UML PNG
└── scripts/
    └── empaquetar_entregas.py         # Compila Linux+Win, audita limpieza anti-IA y crea los 2 .zip
```

### 5.1 Lógica de Validación y Auditoría Industrial en `empaquetar_entregas.py`

Antes de empaquetar cada `.zip`, el script ejecuta las validaciones en orden y **aborta** si cualquiera falla:

1. **`validar_compilacion_cpp(ruta_cpp)` (Doble compilación real):**
   - Compila con `g++ -std=c++17 -Wall -Wextra -Werror` (Linux).
   - Si `x86_64-w64-mingw32-g++` está instalado, compila también con `-std=c++17 -Wall -Wextra -Werror -static -static-libgcc -static-libstdc++` hacia un `.exe` temporal (verificando el bloque `#ifdef _WIN32` y `<windows.h>` sin incluir binarios en el `.zip`).
2. **`validar_sintaxis_python(ruta_py)`:**
   - Ejecuta `py_compile` para garantizar 0 errores de sintaxis en los `.py`.
3. **`auditar_limpieza_industrial(archivos_entregables)`:**
   - Escanea todos los `.cpp`, `.py`, `.txt` y el XML de los `.docx` para confirmar **cero rastros de IA ni plantillas** (`TODO`, `FIXME`, `MACROBUTTON`, `Inserte aquí`, `pon esto`, `acá haremos`, `Sugerencia`, nombres de modelos/agentes o placeholders `<...>`).
4. **Checklist de completitud y aislamiento:**
   - Verifica existencia y tamaño válido de `.cpp`, `.py`, `datos_*.txt`, `Identificacion_Estudiantes.txt` y `Especificacion_Tecnica_*.docx` (> 50 KB con diagramas UML).
   - Empaqueta **solo los entregables limpios** (excluyendo `vault/`, `.agents/`, `AGENTS.md`, `tests_compatibilidad/`, `.git/` y binarios compilados).

---

## 6. Plan de Ejecución Continuo por Fases y Subfases Atómicas

> **Regla de ritmo continuo:** Las fases **NO están atadas a días calendario**. En cuanto se completa, verifica y commitea una subfase, se avanza inmediatamente a la siguiente. La fecha límite absoluta sigue siendo **Martes 1 de Diciembre de 2026 — 11:59 AM**.
> **Regla Git:** Cada subfase cierra con su propio **commit pequeño y atómico** + actualización del nodo afectado en `vault/` y `Registro-Cambios.md`.

### Fase 0 — Preparación de Entorno, Validación Temprana y Esquemas de Datos
- **0A — Entorno CachyOS y Smoke-Test Windows:**
  - Verificar en CachyOS `tk`, `libreoffice-fresh` y `.venv` (`matplotlib`, `folium`, `python-docx`, `pillow`).
  - Confirmar en Windows real (OptiOS 10 o PC de compañero) la ejecución de `tests_compatibilidad/prueba_win.exe` + `datos_prueba.txt`.
  - *Responsable:* Tú (CachyOS) + Damian/Sofia (prueba rápida en Windows).
- **0B — Esquemas de Persistencia y Dataset Base:**
  - Crear `taller3_avl/datos_avl.txt` (dataset pedagógico de ~10 nodos en formato `clave;etiqueta;activo`).
  - Crear `parcial3_pera/datos_pera.txt` con las **32 capitales de Colombia** (lat/lon reales) + **~50 corredores troncales reales** (distancia km, tiempo h, combustible COP, cantidad/costo de peajes COP, categoría vial, validado, activo) y bloque de grupos/investigadores viales.
  - *Commit:* `data(persistencia): crear archivos base datos_avl.txt y datos_pera.txt Colombia`
  - *En paralelo (Damian / Sofia):* Auditar distancias y peajes de `datos_pera.txt` con INVIAS/ANI y consolidar cédulas/códigos/correos para `Identificacion_Estudiantes.txt`.

### Fase 1 — Taller 3 (PAA): Implementación C++17 (`taller3_avl/Taller_3_KM-DV-ST.cpp`)
- **1A — Capa Modelo, Motor AVL y Persistencia:**
  - Implementar `NodoAVL`, alturas, factor de equilibrio $FE$, 4 rotaciones (`LL`, `RR`, `LR`, `RL`) con bitácora de traza pedagógica (comparaciones + estado antes/después), CRUD completo (crear, insertar, eliminar 0/1/2 hijos, desactivar/reactivar, consultar, modificar etiqueta o clave con rebalanceo), recorridos Pre/In/Post-orden y carga/guardado `;` (`CRLF`-safe, opción inicial cargar o iniciar vacío).
  - *Commit:* `feat(taller3-cpp): implementar motor AVL, operaciones CRUD y persistencia`
- **1B — Capa Vista `GotoXY()` Segura (`120x34`) y Recorridos Fijos:**
  - Integrar la capa `Consola` validada con redimensionamiento seguro en `_WIN32` (`SetConsoleScreenBufferSize` / `SetConsoleWindowInfo` a `120x34` para evitar desbordes en `cmd.exe` de 80 columnas) y tope limpio de profundidad visual 2D (niveles 0–4 + resumen si supera).
  - Franja central fija con **Pre-orden, In-orden y Post-orden siempre visibles** + panel de traza de rotaciones.
  - *Commit:* `feat(taller3-cpp): agregar interfaz GotoXY 120x34 y panel fijo de recorridos`
- **1C — Modo Demo Pedagógico (7 pasos) y Verificación Dual Linux/Windows:**
  - Implementar opción `D) Demo pedagogico` con la secuencia exacta `10, 20, 30, 5, 3, 8, 25` (`RR → LL → LR → RL` terminando en árbol simétrico perfecto).
  - Compilar y validar en `g++` (Linux) + `x86_64-w64-mingw32-g++ -static` (Windows PE32+ sin warnings).
  - *Commit:* `feat(taller3-cpp): agregar demo pedagogico de 4 rotaciones y validar compilacion dual`

### Fase 2 — Taller 3 (PAA): Python Visual y Cierre Documental Taller 3
- **2A — Motor AVL y Persistencia Compartida en Python (`taller3_avl/Taller_3_KM-DV-ST.py`):**
  - Implementar exactamente el mismo modelo AVL, operaciones CRUD + desactivación, traza de rotaciones y persistencia compartida `datos_avl.txt` (con selector inicial cargar/vacío).
  - *Commit:* `feat(taller3-py): implementar motor AVL y persistencia compartida`
- **2B — Interfaz Visual `tkinter` + Demo Animado:**
  - Canvas 2D vectorial coloreado por $FE$, panel fijo inferior con **Pre-orden, In-orden y Post-orden siempre visibles**, panel de operaciones y botón `Demo Pedagogico` (`10, 20, 30, 5, 3, 8, 25`) animado con `root.after()` sin bloquear la UI. Cero dependencias externas.
  - *Commit:* `feat(taller3-py): agregar interfaz grafica tkinter y demo animado de rotaciones`
- **2C — Documentación IEEE 830 + 3 Diagramas UML del Taller 3 (Adelantada para evitar cuello de botella):**
  - Generar los 3 diagramas UML en PNG alta resolución (Casos de Uso, Secuencia de inserción/rebalanceo, Estados del nodo AVL).
  - Generar `taller3_avl/Especificacion_Tecnica_Taller_3.docx` basado en la estructura de `plantilla_formato.doc` (sin textos guía azules ni `MACROBUTTON`, con variables de entrada/salida en `3.1` y fichas `RF` en `3.2`) + `Identificacion_Estudiantes.txt`.
  - *Commit:* `docs(taller3): generar informe IEEE 830, 3 diagramas UML e identificacion`
  - *En paralelo (Damian / Sofia en Windows):* Probar `Taller_3_KM-DV-ST.cpp` en Dev-C++ (`F11`) y `.py` en Windows, tomar capturas reales, insertarlas en el `.docx` en MS Word y actualizar la Tabla de Contenido.

### Fase 3 — Parcial 3 (PERA): Implementación C++17 (`parcial3_pera/Parcial_3_KM-DV-ST.cpp`)
- **3A — Modelo, 3 Grafos Ponderados y Persistencia Real de Colombia:**
  - Implementar `GrafoPonderado` reutilizable (lista de adyacencia) instanciado en **3 grafos sincronizados**: `GrafoDistancia`, `GrafoCombustible` y `GrafoPeajes`, bajo `GestorPERA`.
  - Carga opcional al inicio desde `datos_pera.txt` (`CRLF`-safe).
  - *Commit:* `feat(parcial3-cpp): implementar 3 grafos ponderados sincronizados y persistencia`
- **3B — CRUD Completo, Desactivación y Cobertura del Punto 5:**
  - Ingresar, eliminar, desactivar/reactivar y modificar cualquier ciudad, tramo/peaje (incluyendo `categoria` y `validado`) y el submódulo de grupos/investigadores y productos técnicos viales.
  - *Commit:* `feat(parcial3-cpp): agregar CRUD completo, desactivacion y gestion de entidades viales`
- **3C — Motor Dijkstra (4 Métricas), Resumen Descriptivo y Compilación Dual:**
  - Dijkstra con `std::priority_queue` $O((V+E)\log V)$ seleccionando criterio (distancia, combustible, peajes o costo total), ignorando nodos/tramos desactivados (simulación de cierre vial) y mostrando desglose completo: **tiempo, distancia, combustible y peajes** + detección de capitales aisladas (San Andrés, Leticia, Mitú, Inírida).
  - Módulo de estadísticas descriptivas en consola ($n$, media, mediana, desv. estándar, mín, máx, grados/hubs).
  - Validar compilación dual `g++` + `x86_64-w64-mingw32-g++ -static`.
  - *Commit:* `feat(parcial3-cpp): agregar Dijkstra 4 metricas, estadisticas descriptivas y validacion dual`

### Fase 4 — Parcial 3 (PERA): Python Dashboard y Bono Mapa Folium (`parcial3_pera/Parcial_3_KM-DV-ST.py`)
- **4A — Motor de 3 Grafos, Dijkstra y Persistencia Compartida:**
  - Implementar los 3 grafos, Dijkstra 4 métricas, CRUD completo + desactivación y carga/guardado de `datos_pera.txt` (compatible 100% con C++).
  - *Commit:* `feat(parcial3-py): implementar motor de 3 grafos, Dijkstra y persistencia compartida`
- **4B — Interfaz `tkinter` (Calculadora de Rutas y Gestión CRUD):**
  - Ventana principal con pestañas para consulta de rutas óptimas entre 2 ciudades, gestión CRUD de ciudades/tramos/peajes/entidades y carga opcional al inicio.
  - *Commit:* `feat(parcial3-py): construir interfaz tkinter de calculadora de rutas y gestion CRUD`
- **4C — Dashboard Estadístico (`matplotlib`) + Bono Mapa Interactivo (`folium`):**
  - Pestaña Dashboard con KPIs, **histogramas** (distancias y peajes) y **diagramas de barras** (top capitales por grado y comparativa combustible vs peajes) embebidos en `tkinter` con protección `try/except ImportError` amigable.
  - Botón Bono que genera `mapa_pera_colombia.html` con `folium` (32 capitales, tramos activos/inactivos con popups y ruta óptima resaltada) y lo abre en el navegador.
  - *Commit:* `feat(parcial3-py): agregar dashboard matplotlib y bono de mapa interactivo folium`

### Fase 5 — Cierre Documental Parcial 3, Empaquetador Automático y QA Windows
- **5A — Documentación IEEE 830 + 3 Diagramas UML del Parcial 3:**
  - Generar los 3 diagramas UML en PNG alta resolución (Casos de Uso, Secuencia de cálculo Dijkstra/Dashboard, Estado de tramos/sistema PERA).
  - Generar `parcial3_pera/Especificacion_Tecnica_Parcial_3.docx` bajo estándar IEEE 830 (`plantilla_formato.doc`) + `Identificacion_Estudiantes.txt`.
  - *Commit:* `docs(parcial3): generar informe IEEE 830, 3 diagramas UML e identificacion`
- **5B — Script de Validación, Auditoría Anti-IA y Empaquetado (`scripts/empaquetar_entregas.py`):**
  - Implementar doble compilación C++, validación Python, auditoría anti-rastros de IA/plantillas y generación de los **2 `.zip` independientes** (`Taller_3_Grupo_#.zip` y `Parcial_3_Grupo_#.zip`).
  - *Commit:* `chore(entrega): crear script de validacion, auditoria industrial y empaquetado zip`
- **5C — QA Nativo en OptiOS 10 22H2 / Windows de Compañeros:**
  - Compilar y ejecutar ambos `.cpp` con `F11` en Dev-C++ y correr ambos `.py` en Windows real.
  - Insertar capturas finales en ambos `.docx` en MS Word y actualizar sus Tablas de Contenido.
  - *Commit:* `docs(entrega): incorporar capturas reales de Windows y cerrar documentos finales`

### Fase 6 — Grabación de Videos y Envío Oficial
- **6A — Grabación y Subida de Videos (~10 min c/u en YouTube):**
  - Reparto por capas entre Kovyn, Damian y Sofia, identidad institucional UPC y **los 3 visibles en cámara todo el tiempo**.
  - Registrar enlaces finales de YouTube en `Identificacion_Estudiantes.txt` de cada entrega.
  - *Commit:* `docs(entrega): registrar enlaces de videos YouTube y verificar paquetes zip`
- **6B — Envío por Correo a `adithperez@unicesar.edu.co` (antes del Mar 1 Dic 11:59 AM):**
  - Correo 1 (Asunto: `Estructura de datos Taller 3 Grupo 05 2026-2`) + `Taller_3_Grupo_05.zip`.
  - Correo 2 (Asunto: `Estructura de datos Parcial 3 Grupo 05 2026-2`) + `Parcial_3_Grupo_05.zip`.

---

## 7. Estado de Decisiones del Proyecto

### Resueltas
1. **Integrantes, Curso e Iniciales Oficiales (`KM-DV-ST` | `Grupo 05`):** Kovyn Been Mena Orcasita (`KM`), Damian Jose Velasquez Gonzalez (`DV`), Sofia Isabel Tovar Rodriguez (`ST`). Archivos: `Taller_3_KM-DV-ST.cpp/.py` y `Parcial_3_KM-DV-ST.cpp/.py`.
2. **Plantilla Oficial Word:** `plantilla_formato.doc` descargada y analizada (IEEE Std 830-1998).
3. **Arquitectura de Entrega:** 1 archivo `.cpp` y 1 archivo `.py` por proyecto en 4 capas internas desacopladas + `README.txt` + commits pequeños por subfase + cero rastros de IA/plantillas.
4. **Cobertura del Punto 5 de Parcial 3 y Acceso:** Blindaje híbrido (`categoria` + `validado` en tramos/peajes + submódulo de grupos/investigadores/productos) y pantalla previa de acceso (`admin` / `pera2026`, visible en pantalla y en `README.txt`).

### Pendientes para cierre final
1. **QA visual del Parcial 3 en Windows 10** (Taller 3 ya aprobado con capturas reales).
2. **Grabación de los 2 videos (~10 min c/u)** y pegado de los enlaces YouTube en ambos `Identificacion_Estudiantes.txt`.
