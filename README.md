# Taller 3 & Parcial 3 — Estructura de Datos (UPC 2026-2 | Grupo 05)

Repositorio de desarrollo y empaquetado para los entregables finales de **Estructura de Datos** — **Universidad Popular del Cesar (Ingeniería de Sistemas)**.

- **Equipo (`KM-DV-ST`):** Kovyn Been Mena Orcasita, Damian Jose Velasquez Gonzalez y Sofia Isabel Tovar Rodriguez.
- **Curso:** Grupo 05 (`2026-2`) | **Entrega:** Martes 1 de Diciembre de 2026 — 11:59 AM (`adithperez@unicesar.edu.co`).

---

## Estructura del Repositorio

```text
Taller-Parcial 3/
├── taller3_avl/                    # Entregable Taller 3 (PAA - Árboles Binarios AVL)
│   ├── Taller_3_KM-DV-ST.cpp       # C++11/17 con GotoXY() y Demo de 4 rotaciones
│   ├── Taller_3_KM-DV-ST.py        # Python 3 (tkinter nativo, cero dependencias)
│   ├── datos_avl.txt               # Persistencia compartida C++ <-> Python
│   ├── Especificacion_Tecnica_Taller_3.docx  # Informe IEEE 830 + 3 UML + capturas Windows
│   ├── Identificacion_Estudiantes.txt
│   ├── README.txt                  # Guía de ejecución incluida en el .zip
│   └── docs/                       # Diagramas UML (PNG 220 DPI) y capturas
├── parcial3_pera/                  # Entregable Parcial 3 (PERA - Grafos de Colombia)
│   ├── Parcial_3_KM-DV-ST.cpp      # C++11/17 (3 grafos, Dijkstra 4 métricas, resumen)
│   ├── Parcial_3_KM-DV-ST.py       # Python 3 (tkinter, Dashboard matplotlib, Mapa Folium)
│   ├── datos_pera.txt              # 32 capitales reales, 48 corredores, peajes, grupos/productos
│   ├── requirements.txt            # matplotlib y folium
│   ├── Especificacion_Tecnica_Parcial_3.docx # Informe IEEE 830 + 3 UML
│   ├── Identificacion_Estudiantes.txt
│   ├── README.txt                  # Guía de ejecución incluida en el .zip
│   └── docs/                       # Diagramas UML (PNG 220 DPI)
├── scripts/
│   ├── generar_docs_taller3.py     # Generador UML + .docx Taller 3
│   ├── generar_docs_parcial3.py    # Generador UML + .docx Parcial 3
│   └── empaquetar_entregas.py      # Compila, audita y genera los 2 .zip limpios
├── vault/                          # Bóveda de Obsidian por nodos (no entra en los .zip)
├── .agents/                        # Skills para agentes IA (no entra en los .zip)
├── tests_compatibilidad/           # Pruebas de humo Windows/Linux (no entra en los .zip)
└── AGENTS.md                       # Reglas del proyecto para colaboradores y agentes
```

---

## Ejecución Rápida

### Taller 3 — PAA (Árboles AVL)
- **Windows (C++ en Dev-C++ / VS Code):** Abrir `taller3_avl/Taller_3_KM-DV-ST.cpp` (con `-std=c++11` o `-std=c++17`) y presionar `F11` / Run.
- **Windows (Python):** `python taller3_avl/Taller_3_KM-DV-ST.py` *(no requiere librerías externas)*.
- **Linux:**
  ```bash
  g++ -std=c++17 taller3_avl/Taller_3_KM-DV-ST.cpp -o /tmp/paa && /tmp/paa
  python3 taller3_avl/Taller_3_KM-DV-ST.py
  ```

### Parcial 3 — PERA (Grafos de Colombia)
> **Credenciales de acceso inicial (C++ y Python):** Usuario `admin` | Contraseña `pera2026`

- **Windows (C++ en Dev-C++ / VS Code):** Abrir `parcial3_pera/Parcial_3_KM-DV-ST.cpp` (`-std=c++11` o `-std=c++17`) y ejecutar.
- **Windows (Python):**
  ```powershell
  pip install -r parcial3_pera/requirements.txt
  python parcial3_pera/Parcial_3_KM-DV-ST.py
  ```
- **Linux:**
  ```bash
  g++ -std=c++17 parcial3_pera/Parcial_3_KM-DV-ST.cpp -o /tmp/pera && /tmp/pera
  python3 -m venv .venv && .venv/bin/pip install -r parcial3_pera/requirements.txt
  .venv/bin/python parcial3_pera/Parcial_3_KM-DV-ST.py
  ```

---

## Flujo de Trabajo para Colaboradores y Agentes

1. **Rama de trabajo para QA en Windows:**
   ```bash
   git checkout -b qa-windows-damian
   ```
   *(No trabajar directo sobre `main`; subir cambios a la rama y revisar antes de hacer merge).*
2. **Navegación por nodos:** Abrir [`vault/00-MOC-Principal.md`](./vault/00-MOC-Principal.md) o [`AGENTS.md`](./AGENTS.md) para ir directo al nodo del archivo a modificar.
3. **Empaquetado y auditoría automática:**
   ```bash
   python scripts/empaquetar_entregas.py
   ```
   Valida compilación C++11/C++17 (`g++` y `mingw-w64` si está disponible), sintaxis Python, ausencia de rastros de plantilla/IA y genera los 2 archivos finales listos para enviar por separado:
   - `Taller_3_KM-DV-ST.zip` → Asunto: `Estructura de datos Taller 3 Grupo 05 2026-2`
   - `Parcial_3_KM-DV-ST.zip` → Asunto: `Estructura de datos Parcial 3 Grupo 05 2026-2`
