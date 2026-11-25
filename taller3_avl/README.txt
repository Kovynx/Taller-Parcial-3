======================================================================
TALLER 3 - PROGRAMA DE APRENDIZAJE DE ARBOLES (PAA - ARBOLES AVL)
Universidad Popular del Cesar - Ingenieria de Sistemas (2026-2)
Autores: Kovyn Mena, Damian Velasquez, Sofia Tovar (KM-DV-ST)
======================================================================

1. CONTENIDO DEL PAQUETE
   - Taller_3_KM-DV-ST.cpp   : Aplicacion en C++11/17 con GotoXY() y ASCII puro.
   - Taller_3_KM-DV-ST.py    : Aplicacion grafica en Python 3 (tkinter nativo).
   - datos_avl.txt           : Archivo de persistencia compartido (carga opcional).
   - Especificacion_Tecnica_Taller_3.docx : Informe IEEE 830 con 3 diagramas UML.
   - Identificacion_Estudiantes.txt       : Datos del grupo y enlace del video.
   - docs/                   : Diagramas UML en formato PNG (220 DPI).

2. EJECUCION EN WINDOWS (10 / 11)
   [C++]
   - Opcion A (Dev-C++): Abrir Taller_3_KM-DV-ST.cpp, verificar en
     Herramientas -> Opciones del Compilador el flag "-std=c++11" (o c++17)
     y presionar F11 (Compilar y Ejecutar).
   - Opcion B (Consola MinGW / CMD):
       g++ -std=c++17 -static Taller_3_KM-DV-ST.cpp -o Taller_3.exe
       Taller_3.exe

   [Python 3] (No requiere instalar librerias externas)
   - En CMD o PowerShell dentro de esta carpeta:
       python Taller_3_KM-DV-ST.py

3. EJECUCION EN LINUX
   [C++]
       g++ -std=c++17 Taller_3_KM-DV-ST.cpp -o Taller_3 && ./Taller_3

   [Python 3] (Requiere soporte tkinter del sistema, ej. python3-tk / tk)
       python3 Taller_3_KM-DV-ST.py

4. NOTAS DE USO
   - Al iniciar, ambos programas preguntan si desea cargar datos_avl.txt
     o iniciar con el arbol vacio.
   - Los recorridos Pre-orden, In-orden y Post-orden permanecen siempre visibles.
   - La opcion "Demo Pedagogico" ejecuta la secuencia 10, 20, 30, 5, 3, 8, 25
     demostrando las 4 rotaciones AVL (RR, LL, LR, RL) y permite restaurar
     el arbol previo al finalizar.
======================================================================
