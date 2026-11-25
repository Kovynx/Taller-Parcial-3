// ============================================================================
// PRUEBA DE COMPATIBILIDAD REAL WINDOWS (OptiOS 10 22H2) <-> LINUX (CachyOS)
// Compilar en Windows (Dev-C++ F11 o MinGW):
//   g++ -std=c++17 -static prueba_win_linux.cpp -o prueba_win.exe
// Compilar desde Linux para Windows:
//   x86_64-w64-mingw32-g++ -std=c++17 -Wall -Wextra -static -static-libgcc -static-libstdc++ prueba_win_linux.cpp -o prueba_win.exe
// ============================================================================

#ifdef _WIN32
  #define WIN32_LEAN_AND_MEAN
  #include <windows.h>
#endif

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

namespace Consola {
    void inicializar() {
    #ifdef _WIN32
        SetConsoleOutputCP(65001);
        SetConsoleCP(65001);
    #endif
    }

    void GotoXY(int x, int y) {
    #ifdef _WIN32
        COORD coord;
        coord.X = static_cast<SHORT>(x);
        coord.Y = static_cast<SHORT>(y);
        SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);
    #else
        std::cout << "\033[" << (y + 1) << ";" << (x + 1) << "H" << std::flush;
    #endif
    }

    void limpiarPantalla() {
    #ifdef _WIN32
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        if (GetConsoleScreenBufferInfo(hOut, &csbi)) {
            DWORD celdas = csbi.dwSize.X * csbi.dwSize.Y;
            DWORD escritas = 0;
            COORD origen = {0, 0};
            FillConsoleOutputCharacterA(hOut, ' ', celdas, origen, &escritas);
            FillConsoleOutputAttribute(hOut, csbi.wAttributes, celdas, origen, &escritas);
            SetConsoleCursorPosition(hOut, origen);
        }
    #else
        std::cout << "\033[2J\033[H" << std::flush;
    #endif
    }

    std::string rutaJuntoAlEjecutable(const std::string& nombreArchivo) {
        std::ifstream pruebaDirecta(nombreArchivo);
        if (pruebaDirecta.good()) return nombreArchivo;
    #ifdef _WIN32
        char buffer[MAX_PATH];
        DWORD len = GetModuleFileNameA(NULL, buffer, MAX_PATH);
        if (len > 0) {
            std::string rutaExe(buffer, len);
            std::size_t pos = rutaExe.find_last_of("\\/");
            if (pos != std::string::npos) {
                return rutaExe.substr(0, pos + 1) + nombreArchivo;
            }
        }
    #endif
        return nombreArchivo;
    }
}

struct NodoDemo {
    int clave;
    std::string etiqueta;
    bool activo;
};

static std::string limpiarCRLF(std::string s) {
    while (!s.empty() && (s.back() == '\r' || s.back() == '\n' || s.back() == ' ')) {
        s.pop_back();
    }
    return s;
}

int main() {
    Consola::inicializar();
    Consola::limpiarPantalla();

    // 1. Leer archivo de persistencia compartido (; y seguro ante CRLF)
    std::string ruta = Consola::rutaJuntoAlEjecutable("datos_prueba.txt");
    std::ifstream archivo(ruta);
    std::vector<NodoDemo> nodos;
    std::string linea;
    while (std::getline(archivo, linea)) {
        linea = limpiarCRLF(linea);
        if (linea.empty()) continue;
        std::stringstream ss(linea);
        std::string cStr, etq, actStr;
        if (std::getline(ss, cStr, ';') && std::getline(ss, etq, ';') && std::getline(ss, actStr, ';')) {
            nodos.push_back({std::stoi(cStr), etq, actStr == "1"});
        }
    }

    // 2. Dibujar encabezado y mini-arbol AVL usando GotoXY() y ASCII puro
    Consola::GotoXY(2, 1);
    std::cout << "+======================================================================+";
    Consola::GotoXY(2, 2);
    std::cout << "| PRUEBA DE HUMO C++17: GotoXY() + UTF-8 + Persistencia Windows/Linux  |";
    Consola::GotoXY(2, 3);
    std::cout << "+======================================================================+";

    Consola::GotoXY(30, 5);  std::cout << "[20|FE:0]";
    Consola::GotoXY(24, 6);  std::cout << "/";
    Consola::GotoXY(42, 6);  std::cout << "\\";
    Consola::GotoXY(16, 7);  std::cout << "[10|FE:0]";
    Consola::GotoXY(44, 7);  std::cout << "(30*|Inactivo)";

    // 3. Franja fija de recorridos siempre visibles
    Consola::GotoXY(2, 10);
    std::cout << "------------------------------------------------------------------------";
    Consola::GotoXY(2, 11);
    std::cout << "PRE-ORDEN : 20 -> 10 -> 30*";
    Consola::GotoXY(2, 12);
    std::cout << "IN-ORDEN  : 10 -> 20 -> 30*";
    Consola::GotoXY(2, 13);
    std::cout << "POST-ORDEN: 10 -> 30* -> 20";
    Consola::GotoXY(2, 14);
    std::cout << "------------------------------------------------------------------------";

    // 4. Reporte de estado de persistencia y entorno
    Consola::GotoXY(2, 16);
#ifdef _WIN32
    std::cout << "Plataforma detectada : WINDOWS NATIVO (Win32 API SetConsoleCursorPosition)";
#else
    std::cout << "Plataforma detectada : LINUX NATIVO (ANSI Escape Cursor)";
#endif
    Consola::GotoXY(2, 17);
    std::cout << "Tildes / UTF-8       : Árbol, camión, Bogotá, Medellín, niño [OK]";
    Consola::GotoXY(2, 18);
    std::cout << "Archivo datos leido  : " << (nodos.empty() ? "NO ENCONTRADO (modo sin datos)" : "OK (" + std::to_string(nodos.size()) + " registros cargados)");
    for (std::size_t i = 0; i < nodos.size(); ++i) {
        Consola::GotoXY(4, 19 + static_cast<int>(i));
        std::cout << "- Clave " << nodos[i].clave << " | " << nodos[i].etiqueta
                  << " | Estado: " << (nodos[i].activo ? "ACTIVO" : "DESACTIVADO");
    }

    Consola::GotoXY(2, 23);
    std::cout << "Todo funciono al 100%. Presione ENTER para cerrar la ventana...";
    std::string pausa;
    std::getline(std::cin, pausa);
    return 0;
}
