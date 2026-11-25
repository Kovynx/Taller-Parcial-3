---
tipo: plan-desarrollo
proyecto: Taller 3 (AVL) + Parcial 3 (Grafos PERA)
fecha_creacion: 2026-11-25
fecha_limite: 2026-12-01T11:59:00-05:00
estado: en-revision-arquitectura
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
├── vault/                          # Bóveda Obsidian (Nodos + MOCs + Bitácora)
├── .agents/skills/                 # Skills de contexto y navegación
├── taller3_avl/                    # Trabajo del Taller 3 -> genera Taller_3_Grupo_X.zip
│   ├── <Iniciales>.cpp             # C++17 AVL visual con GotoXY()
│   ├── <Iniciales>.py              # Python tkinter AVL visual interactivo
│   ├── datos_avl.txt               # Persistencia compartida (carga opcional al inicio)
│   ├── Identificacion_Estudiantes.txt
│   └── docs/                       # Generador + Especificacion_Tecnica_Taller_3.docx + UML
├── parcial3_pera/                  # Trabajo del Parcial 3 -> genera Parcial_3_Grupo_X.zip
│   ├── <Iniciales>.cpp             # C++17 3 Grafos Colombia + Dijkstra + Resumen
│   ├── <Iniciales>.py              # Python 3 Grafos + Dashboard Matplotlib + Bono Folium
│   ├── datos_pera.txt              # Persistencia real Colombia (32 capitales + peajes)
│   ├── Identificacion_Estudiantes.txt
│   └── docs/                       # Generador + Especificacion_Tecnica_Parcial_3.docx + UML
└── scripts/
    └── empaquetar_entregas.py      # Valida checklist, compila los .cpp con g++ y crea los 2 .zip limpios
```

### 5.1 Lógica de Validación en `empaquetar_entregas.py`

Antes de empaquetar cada `.zip`, el script ejecuta los pasos siguientes en orden. Si cualquier paso falla, aborta con un mensaje claro e indica qué corregir.

```python
import subprocess, zipfile, os, sys

def validar_compilacion_cpp(ruta_cpp: str) -> None:
    """Compila el .cpp con g++ -std=c++17 -Wall -Wextra.
    Aborta el empaquetado si hay errores de compilación."""
    resultado = subprocess.run(
        ["g++", "-std=c++17", "-Wall", "-Wextra", "-o", os.devnull, ruta_cpp],
        capture_output=True, text=True
    )
    if resultado.returncode != 0:
        print(f"\n❌ ERROR DE COMPILACIÓN en {ruta_cpp}:\n{resultado.stderr}")
        sys.exit(1)
    if resultado.stderr:          # Warnings no bloquean, pero se muestran
        print(f"⚠️  Warnings en {ruta_cpp}:\n{resultado.stderr}")
    print(f"✅ Compilación OK: {ruta_cpp}")

# Checklist completo por proyecto antes de crear el .zip:
# 1. validar_compilacion_cpp("<Iniciales>.cpp")     ← NUEVO (sugerencia E)
# 2. Verificar existencia de: .cpp, .py, datos_*.txt,
#    Identificacion_Estudiantes.txt, Especificacion_Tecnica_*.docx
# 3. Verificar que el .docx contiene los diagramas UML (tamaño > 50 KB)
# 4. Verificar que el .txt de identificación no está vacío
# 5. Crear el .zip con nombre exacto del asunto del correo
```

**Notas de implementación:**
- `g++` debe estar en el `PATH` (en Linux siempre lo está; en Windows usar el MinGW-w64 instalado en el Paso 3 del checklist OptiOS).
- Compilar contra `/dev/null` (`os.devnull`) en Linux o `NUL` en Windows: `subprocess` en Python resuelve `os.devnull` correctamente en ambos SO.
- Si se quiere cruzar-compilar desde Linux para verificar el `.exe` de Windows, reemplazar `g++` por `x86_64-w64-mingw32-g++` como paso adicional opcional.

---

## 6. Cronograma Táctico de 6 Días (25 Nov -> 1 Dic 11:59 AM)

| Día | Fecha | Meta Concreta | Nodos de la Vault |
| :--- | :--- | :--- | :--- |
| **Día 1** | Mié 25 Nov | Cierre de arquitectura (Carbon + Kiro + Claude) + Dataset real de Colombia (32 capitales, corredores y peajes) + Persistencia base. | `Nodo-Datos-Colombia-Peajes`, `Nodo-Persistencia-*` |
| **Día 2** | Jue 26 Nov | **Taller 3 completo en código:** `<Iniciales>.cpp` (`GotoXY` + rotaciones AVL + recorridos fijos) y `<Iniciales>.py` (`tkinter` visual). | `Nodo-AVL-CPP`, `Nodo-AVL-Python` |
| **Día 3** | Vie 27 Nov | **Parcial 3 en C++:** 3 grafos, CRUD + desactivación, Dijkstra 4 métricas y resumen estadístico descriptivo. | `Nodo-Grafos-CPP` |
| **Día 4** | Sáb 28 Nov | **Parcial 3 en Python:** 3 grafos + Dashboard (`matplotlib` histogramas/barras) + **Bono Mapa Folium** interactivo. | `Nodo-Grafos-Python-Dashboard` |
| **Día 5** | Dom 29 Nov | **Prueba real en OptiOS 10 22H2** + Generación de los 2 `.docx` con Plantilla UPC y diagramas UML (Casos de Uso, Secuencia, Estados). | `Nodo-Docs-UML-Taller-3`, `Nodo-Docs-UML-Parcial-3` |
| **Día 6** | Lun 30 Nov | **Grabación y subida a YouTube de los 2 videos (~10 min c/u)** + Empaquetado de los 2 `.zip` (dejando margen de seguridad antes del Mar 1 Dic 11:59 AM). | `Entregables-y-Fechas` |

---

## 7. Decisiones Abiertas para Alinear con Kiro / Claude y el Equipo

1. **Iniciales y Datos del Grupo:** ¿Cuáles son los nombres completos, cédulas/códigos, iniciales exactas para nombrar los archivos (ej. `ABC-DEF-GHI.cpp` o `AP-KL-MR.cpp`) y el número de `Grupo #` del asunto del correo?
2. **Plantilla Word del Profesor:** ¿Puedes descargar el archivo de la URL de SharePoint extraída del PDF y dejarlo en el proyecto para clonar su estructura exacta con `python-docx`?
3. **Modularidad de Entrega (Un solo archivo vs Múltiples archivos + Bundler):** ¿Preferimos escribir cada programa directamente en **un único archivo modularizado por clases/secciones (~500 líneas)** (más directo de leer y depurar), o desarrollar en múltiples archivos `src/` y generar automáticamente el archivo único de entrega para el `.zip`? *(Recomendación: **archivo único limpio por capas de clases**, porque lo que explican en el video es exactamente el mismo archivo que recibe y compila el profesor).*
4. **Cobertura del Punto 5 de Parcial 3:** ¿Confirmamos incluir `categoria` + `validado` en Rutas/Peajes + registro ligero de `Grupos/Investigadores Viales` para cubrir al 100% la redacción literal del PDF sin ensuciar la interfaz principal?
