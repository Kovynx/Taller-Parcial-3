======================================================================
PARCIAL 3 - PROGRAMA ESTADISTICO DE RUTAS DE AUTOMOVILES (PERA)
Universidad Popular del Cesar - Ingenieria de Sistemas (2026-2)
Autores: Kovyn Mena, Damian Velasquez, Sofia Tovar (KM-DV-ST)
======================================================================

1. CONTENIDO DEL PAQUETE
   - Parcial_3_KM-DV-ST.cpp  : Aplicacion C++11/17 (3 grafos, Dijkstra, resumen).
   - Parcial_3_KM-DV-ST.py   : Aplicacion Python 3 (GUI, Dashboard, Mapa Folium).
   - datos_pera.txt          : Persistencia real de Colombia (32 capitales,
                               48 corredores, peajes, grupos y productos).
   - requirements.txt        : Dependencias opcionales para Dashboard y Mapa.
   - Especificacion_Tecnica_Parcial_3.docx : Informe IEEE 830 con 3 diagramas UML.
   - Identificacion_Estudiantes.txt        : Datos del grupo y enlace del video.
   - docs/                   : Diagramas UML en formato PNG (220 DPI).

2. CREDENCIALES DE ACCESO INICIAL (C++ Y PYTHON)
   - Usuario    : admin
   - Contrasena : pera2026
   (Validacion estricta: no permite campos vacios ni espacios en blanco).

3. EJECUCION EN WINDOWS (10 / 11)
   [C++]
   - Opcion A (Dev-C++): Abrir Parcial_3_KM-DV-ST.cpp, verificar en
     Herramientas -> Opciones del Compilador el flag "-std=c++11" (o c++17)
     y presionar F11 (Compilar y Ejecutar).
   - Opcion B (Consola MinGW / CMD):
       g++ -std=c++17 -static Parcial_3_KM-DV-ST.cpp -o Parcial_3.exe
       Parcial_3.exe

   [Python 3]
   - Instalar dependencias del Dashboard y Mapa interactivo (una sola vez):
       pip install -r requirements.txt
   - Ejecutar:
       python Parcial_3_KM-DV-ST.py

4. EJECUCION EN LINUX
   [C++]
       g++ -std=c++17 Parcial_3_KM-DV-ST.cpp -o Parcial_3 && ./Parcial_3

   [Python 3]
       python3 -m venv .venv
       .venv/bin/pip install -r requirements.txt
       .venv/bin/python Parcial_3_KM-DV-ST.py

5. NOTAS DE USO
   - Al iniciar tras el acceso, puede cargar datos_pera.txt o iniciar vacio.
   - En la pestana 1 (Python) u opcion 1 (C++) se calculan tiempo, distancia,
     combustible y peajes entre dos ciudades comparando los 3 grafos.
   - El boton "Abrir Mapa Interactivo Colombia (Folium)" genera y abre
     mapa_pera_colombia.html en el navegador con la ruta optima resaltada.
======================================================================
