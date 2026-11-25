// ============================================================================
// Universidad Popular del Cesar - Facultad de Ingenieria y Tecnologicas
// Ingenieria de Sistemas - Estructura de Datos (Taller 3)
// Programa de Aprendizaje de Arboles (PAA) - Arbol Binario AVL en C++17
// Autores: Kovyn Been Mena Orcasita, Damian Jose Velasquez Gonzalez,
//          Sofia Isabel Tovar Rodriguez (KM-DV-ST)
// ============================================================================

#ifdef _WIN32
  #define WIN32_LEAN_AND_MEAN
  #include <windows.h>
#endif

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

// ============================================================================
// CAPA 0: UTILIDADES DE CONSOLA MULTIPLATAFORMA (WINDOWS Win32 / LINUX ANSI)
// ============================================================================
namespace Consola {

    void inicializar() {
    #ifdef _WIN32
        SetConsoleOutputCP(65001);
        SetConsoleCP(65001);
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        if (hOut != INVALID_HANDLE_VALUE) {
            COORD tamBuffer = {120, 36};
            SetConsoleScreenBufferSize(hOut, tamBuffer);
            SMALL_RECT ventana = {0, 0, 119, 34};
            SetConsoleWindowInfo(hOut, TRUE, &ventana);
        }
    #endif
    }

    void GotoXY(int x, int y) {
    #ifdef _WIN32
        COORD coord;
        coord.X = static_cast<SHORT>(std::max(0, x));
        coord.Y = static_cast<SHORT>(std::max(0, y));
        SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);
    #else
        std::cout << "\033[" << (std::max(0, y) + 1) << ";"
                  << (std::max(0, x) + 1) << "H" << std::flush;
    #endif
    }

    void limpiarPantalla() {
    #ifdef _WIN32
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        if (GetConsoleScreenBufferInfo(hOut, &csbi)) {
            DWORD celdas = static_cast<DWORD>(csbi.dwSize.X) * static_cast<DWORD>(csbi.dwSize.Y);
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

    std::string limpiarTexto(std::string s) {
        while (!s.empty() && (s.back() == '\r' || s.back() == '\n' || s.back() == ' ' || s.back() == '\t')) {
            s.pop_back();
        }
        std::size_t ini = 0;
        while (ini < s.size() && (s[ini] == ' ' || s[ini] == '\t')) ++ini;
        return s.substr(ini);
    }

    std::string leerLinea(const std::string& mensaje) {
        if (!mensaje.empty()) std::cout << mensaje;
        std::string linea;
        std::getline(std::cin, linea);
        return limpiarTexto(linea);
    }

    bool leerEntero(const std::string& mensaje, int& destino) {
        std::string entrada = leerLinea(mensaje);
        if (entrada.empty()) return false;
        try {
            std::size_t idx = 0;
            int valor = std::stoi(entrada, &idx);
            if (idx != entrada.size()) return false;
            destino = valor;
            return true;
        } catch (...) {
            return false;
        }
    }

} // namespace Consola

// ============================================================================
// CAPA 1: MODELO DE DATOS DEL ARBOL AVL
// ============================================================================
struct NodoAVL {
    int clave;
    std::string etiqueta;
    int altura;
    bool activo;
    NodoAVL* izq;
    NodoAVL* der;

    NodoAVL(int c, const std::string& etq, bool act = true)
        : clave(c), etiqueta(etq), altura(1), activo(act), izq(nullptr), der(nullptr) {}
};

struct EventoBalanceo {
    std::string tipoRotacion; // "LL", "RR", "LR", "RL"
    int clavePivote;
    int feAntes;
    std::string detalle;
};

struct RegistroTraza {
    std::string operacion;
    std::vector<std::string> pasos;
    std::vector<EventoBalanceo> rotaciones;
    bool exito = false;
    std::string mensajeFinal;

    void reiniciar(const std::string& op) {
        operacion = op;
        pasos.clear();
        rotaciones.clear();
        exito = false;
        mensajeFinal.clear();
    }
};

// ============================================================================
// CAPA 2: MOTOR DE ESTRUCTURA DE DATOS - ARBOL BINARIO AVL
// Complejidad: Insercion, Eliminacion, Busqueda, Desactivacion -> O(log n)
//              Recorridos Pre-orden, In-orden, Post-orden      -> O(n)
// ============================================================================
class ArbolAVL {
private:
    NodoAVL* raiz;
    RegistroTraza ultimaTraza;

    int obtenerAltura(const NodoAVL* n) const {
        return n ? n->altura : 0;
    }

    void actualizarAltura(NodoAVL* n) {
        if (n) {
            n->altura = 1 + std::max(obtenerAltura(n->izq), obtenerAltura(n->der));
        }
    }

    int factorEquilibrio(const NodoAVL* n) const {
        return n ? (obtenerAltura(n->izq) - obtenerAltura(n->der)) : 0;
    }

    // Rotacion Simple a la Derecha (Caso LL)
    NodoAVL* rotarDerecha(NodoAVL* y) {
        NodoAVL* x = y->izq;
        NodoAVL* t2 = x->der;
        x->der = y;
        y->izq = t2;
        actualizarAltura(y);
        actualizarAltura(x);
        return x;
    }

    // Rotacion Simple a la Izquierda (Caso RR)
    NodoAVL* rotarIzquierda(NodoAVL* x) {
        NodoAVL* y = x->der;
        NodoAVL* t2 = y->izq;
        y->izq = x;
        x->der = t2;
        actualizarAltura(x);
        actualizarAltura(y);
        return y;
    }

    NodoAVL* balancear(NodoAVL* nodo) {
        if (!nodo) return nullptr;
        actualizarAltura(nodo);
        int fe = factorEquilibrio(nodo);

        // Desbalance Izquierdo (FE > +1)
        if (fe > 1) {
            int feIzq = factorEquilibrio(nodo->izq);
            if (feIzq >= 0) {
                ultimaTraza.rotaciones.push_back({
                    "LL", nodo->clave, fe,
                    "Rotacion Simple Derecha (LL) en pivote " + std::to_string(nodo->clave) +
                    " (FE=" + std::to_string(fe) + ")"
                });
                return rotarDerecha(nodo);
            } else {
                ultimaTraza.rotaciones.push_back({
                    "LR", nodo->clave, fe,
                    "Rotacion Doble Izquierda-Derecha (LR) en pivote " + std::to_string(nodo->clave) +
                    " (FE=" + std::to_string(fe) + ", FE_izq=" + std::to_string(feIzq) + ")"
                });
                nodo->izq = rotarIzquierda(nodo->izq);
                return rotarDerecha(nodo);
            }
        }

        // Desbalance Derecho (FE < -1)
        if (fe < -1) {
            int feDer = factorEquilibrio(nodo->der);
            if (feDer <= 0) {
                ultimaTraza.rotaciones.push_back({
                    "RR", nodo->clave, fe,
                    "Rotacion Simple Izquierda (RR) en pivote " + std::to_string(nodo->clave) +
                    " (FE=" + std::to_string(fe) + ")"
                });
                return rotarIzquierda(nodo);
            } else {
                ultimaTraza.rotaciones.push_back({
                    "RL", nodo->clave, fe,
                    "Rotacion Doble Derecha-Izquierda (RL) en pivote " + std::to_string(nodo->clave) +
                    " (FE=" + std::to_string(fe) + ", FE_der=" + std::to_string(feDer) + ")"
                });
                nodo->der = rotarDerecha(nodo->der);
                return rotarIzquierda(nodo);
            }
        }

        return nodo;
    }

    NodoAVL* insertarRec(NodoAVL* nodo, int clave, const std::string& etiqueta, bool activo, bool& insertado) {
        if (!nodo) {
            insertado = true;
            ultimaTraza.pasos.push_back("Insertado nodo [" + std::to_string(clave) + "]");
            return new NodoAVL(clave, etiqueta, activo);
        }
        if (clave < nodo->clave) {
            ultimaTraza.pasos.push_back(std::to_string(clave) + " < " + std::to_string(nodo->clave) + " -> Izq");
            nodo->izq = insertarRec(nodo->izq, clave, etiqueta, activo, insertado);
        } else if (clave > nodo->clave) {
            ultimaTraza.pasos.push_back(std::to_string(clave) + " > " + std::to_string(nodo->clave) + " -> Der");
            nodo->der = insertarRec(nodo->der, clave, etiqueta, activo, insertado);
        } else {
            insertado = false;
            return nodo;
        }
        return balancear(nodo);
    }

    NodoAVL* minimoNodo(NodoAVL* nodo) const {
        NodoAVL* actual = nodo;
        while (actual && actual->izq) actual = actual->izq;
        return actual;
    }

    NodoAVL* eliminarRec(NodoAVL* nodo, int clave, bool& eliminado) {
        if (!nodo) return nullptr;

        if (clave < nodo->clave) {
            ultimaTraza.pasos.push_back(std::to_string(clave) + " < " + std::to_string(nodo->clave) + " -> Izq");
            nodo->izq = eliminarRec(nodo->izq, clave, eliminado);
        } else if (clave > nodo->clave) {
            ultimaTraza.pasos.push_back(std::to_string(clave) + " > " + std::to_string(nodo->clave) + " -> Der");
            nodo->der = eliminarRec(nodo->der, clave, eliminado);
        } else {
            eliminado = true;
            if (!nodo->izq || !nodo->der) {
                NodoAVL* hijo = nodo->izq ? nodo->izq : nodo->der;
                ultimaTraza.pasos.push_back("Eliminado nodo [" + std::to_string(clave) + "] (0 o 1 hijo)");
                delete nodo;
                return hijo;
            } else {
                NodoAVL* sucesor = minimoNodo(nodo->der);
                ultimaTraza.pasos.push_back("Nodo [" + std::to_string(clave) + "] reemplazado por sucesor in-orden [" +
                                            std::to_string(sucesor->clave) + "]");
                nodo->clave = sucesor->clave;
                nodo->etiqueta = sucesor->etiqueta;
                nodo->activo = sucesor->activo;
                bool dummy = false;
                nodo->der = eliminarRec(nodo->der, sucesor->clave, dummy);
            }
        }
        return balancear(nodo);
    }

    void liberarRec(NodoAVL* nodo) {
        if (!nodo) return;
        liberarRec(nodo->izq);
        liberarRec(nodo->der);
        delete nodo;
    }

    void preOrdenRec(const NodoAVL* n, std::vector<const NodoAVL*>& out) const {
        if (!n) return;
        out.push_back(n);
        preOrdenRec(n->izq, out);
        preOrdenRec(n->der, out);
    }

    void inOrdenRec(const NodoAVL* n, std::vector<const NodoAVL*>& out) const {
        if (!n) return;
        inOrdenRec(n->izq, out);
        out.push_back(n);
        inOrdenRec(n->der, out);
    }

    void postOrdenRec(const NodoAVL* n, std::vector<const NodoAVL*>& out) const {
        if (!n) return;
        postOrdenRec(n->izq, out);
        postOrdenRec(n->der, out);
        out.push_back(n);
    }

    int contarNodosRec(const NodoAVL* n, bool soloActivos) const {
        if (!n) return 0;
        int suma = (!soloActivos || n->activo) ? 1 : 0;
        return suma + contarNodosRec(n->izq, soloActivos) + contarNodosRec(n->der, soloActivos);
    }

public:
    ArbolAVL() : raiz(nullptr) {}
    ~ArbolAVL() { crearVacio(); }

    ArbolAVL(const ArbolAVL&) = delete;
    ArbolAVL& operator=(const ArbolAVL&) = delete;

    void crearVacio() {
        liberarRec(raiz);
        raiz = nullptr;
        ultimaTraza.reiniciar("Crear / Vaciar");
        ultimaTraza.exito = true;
        ultimaTraza.mensajeFinal = "Arbol AVL inicializado vacio.";
    }

    const NodoAVL* obtenerRaiz() const { return raiz; }
    int alturaTotal() const { return obtenerAltura(raiz); }
    int totalNodos() const { return contarNodosRec(raiz, false); }
    int totalActivos() const { return contarNodosRec(raiz, true); }
    int obtenerFE(const NodoAVL* n) const { return factorEquilibrio(n); }
    const RegistroTraza& obtenerUltimaTraza() const { return ultimaTraza; }

    bool insertar(int clave, const std::string& etiqueta, bool activo = true) {
        ultimaTraza.reiniciar("Insertar " + std::to_string(clave));
        bool insertado = false;
        std::string etq = etiqueta.empty() ? ("Nodo_" + std::to_string(clave)) : etiqueta;
        raiz = insertarRec(raiz, clave, etq, activo, insertado);
        ultimaTraza.exito = insertado;
        if (!insertado) {
            ultimaTraza.mensajeFinal = "La clave " + std::to_string(clave) + " ya existe en el arbol AVL.";
        } else if (ultimaTraza.rotaciones.empty()) {
            ultimaTraza.mensajeFinal = "Clave " + std::to_string(clave) + " insertada. Arbol balanceado (sin rotaciones).";
        } else {
            ultimaTraza.mensajeFinal = "Clave " + std::to_string(clave) + " insertada -> " +
                                       ultimaTraza.rotaciones.back().detalle;
        }
        return insertado;
    }

    bool eliminar(int clave) {
        ultimaTraza.reiniciar("Eliminar " + std::to_string(clave));
        bool eliminado = false;
        raiz = eliminarRec(raiz, clave, eliminado);
        ultimaTraza.exito = eliminado;
        if (!eliminado) {
            ultimaTraza.mensajeFinal = "Clave " + std::to_string(clave) + " no encontrada para eliminar.";
        } else if (ultimaTraza.rotaciones.empty()) {
            ultimaTraza.mensajeFinal = "Clave " + std::to_string(clave) + " eliminada. Arbol permanece balanceado.";
        } else {
            ultimaTraza.mensajeFinal = "Clave " + std::to_string(clave) + " eliminada -> " +
                                       ultimaTraza.rotaciones.back().detalle;
        }
        return eliminado;
    }

    NodoAVL* buscar(int clave) {
        ultimaTraza.reiniciar("Consultar " + std::to_string(clave));
        NodoAVL* actual = raiz;
        while (actual) {
            if (clave == actual->clave) {
                ultimaTraza.pasos.push_back("Encontrado [" + std::to_string(clave) + "]");
                ultimaTraza.exito = true;
                ultimaTraza.mensajeFinal = "Encontrado: Clave=" + std::to_string(actual->clave) +
                    " | Etiqueta=" + actual->etiqueta +
                    " | Altura=" + std::to_string(actual->altura) +
                    " | FE=" + std::to_string(factorEquilibrio(actual)) +
                    " | Estado=" + (actual->activo ? "ACTIVO" : "DESACTIVADO");
                return actual;
            }
            if (clave < actual->clave) {
                ultimaTraza.pasos.push_back(std::to_string(clave) + " < " + std::to_string(actual->clave) + " -> Izq");
                actual = actual->izq;
            } else {
                ultimaTraza.pasos.push_back(std::to_string(clave) + " > " + std::to_string(actual->clave) + " -> Der");
                actual = actual->der;
            }
        }
        ultimaTraza.exito = false;
        ultimaTraza.mensajeFinal = "Clave " + std::to_string(clave) + " no existe en el arbol.";
        return nullptr;
    }

    bool cambiarEstadoActivo(int clave, bool nuevoEstado) {
        NodoAVL* nodo = buscar(clave);
        ultimaTraza.operacion = (nuevoEstado ? "Reactivar " : "Desactivar ") + std::to_string(clave);
        if (!nodo) {
            ultimaTraza.exito = false;
            ultimaTraza.mensajeFinal = "Clave " + std::to_string(clave) + " no encontrada.";
            return false;
        }
        nodo->activo = nuevoEstado;
        ultimaTraza.exito = true;
        ultimaTraza.mensajeFinal = "Nodo " + std::to_string(clave) + " marcado como " +
                                   (nuevoEstado ? "ACTIVO." : "DESACTIVADO (estructura AVL intacta).");
        return true;
    }

    bool modificar(int claveActual, int nuevaClave, const std::string& nuevaEtiqueta) {
        NodoAVL* nodo = buscar(claveActual);
        if (!nodo) {
            ultimaTraza.operacion = "Modificar " + std::to_string(claveActual);
            ultimaTraza.exito = false;
            ultimaTraza.mensajeFinal = "Clave " + std::to_string(claveActual) + " no encontrada.";
            return false;
        }
        std::string etqFinal = nuevaEtiqueta.empty() ? nodo->etiqueta : nuevaEtiqueta;
        if (nuevaClave == claveActual) {
            nodo->etiqueta = etqFinal;
            ultimaTraza.reiniciar("Modificar " + std::to_string(claveActual));
            ultimaTraza.exito = true;
            ultimaTraza.mensajeFinal = "Etiqueta del nodo " + std::to_string(claveActual) +
                                       " actualizada a '" + etqFinal + "'.";
            return true;
        }
        if (buscar(nuevaClave) != nullptr) {
            ultimaTraza.reiniciar("Modificar " + std::to_string(claveActual));
            ultimaTraza.exito = false;
            ultimaTraza.mensajeFinal = "No se puede cambiar clave: ya existe el nodo " +
                                       std::to_string(nuevaClave) + ".";
            return false;
        }
        bool estadoPrevio = nodo->activo;
        eliminar(claveActual);
        insertar(nuevaClave, etqFinal, estadoPrevio);
        ultimaTraza.operacion = "Modificar clave " + std::to_string(claveActual) + " -> " + std::to_string(nuevaClave);
        ultimaTraza.mensajeFinal = "Clave reubicada de " + std::to_string(claveActual) + " a " +
                                   std::to_string(nuevaClave) + " con rebalanceo AVL.";
        return true;
    }

    std::vector<const NodoAVL*> preOrden() const {
        std::vector<const NodoAVL*> out;
        preOrdenRec(raiz, out);
        return out;
    }

    std::vector<const NodoAVL*> inOrden() const {
        std::vector<const NodoAVL*> out;
        inOrdenRec(raiz, out);
        return out;
    }

    std::vector<const NodoAVL*> postOrden() const {
        std::vector<const NodoAVL*> out;
        postOrdenRec(raiz, out);
        return out;
    }

    std::string formatearRecorrido(const std::vector<const NodoAVL*>& lista) const {
        if (lista.empty()) return "(vacio)";
        std::ostringstream oss;
        for (std::size_t i = 0; i < lista.size(); ++i) {
            if (i > 0) oss << " -> ";
            oss << lista[i]->clave;
            if (!lista[i]->activo) oss << "*";
        }
        return oss.str();
    }
};

// ============================================================================
// CAPA 3: PERSISTENCIA COMPARTIDA C++ <-> PYTHON (datos_avl.txt)
// ============================================================================
namespace PersistenciaAVL {

    bool cargarArchivo(ArbolAVL& arbol, const std::string& nombreArchivo, int& cargados) {
        cargados = 0;
        std::string ruta = Consola::rutaJuntoAlEjecutable(nombreArchivo);
        std::ifstream archivo(ruta);
        if (!archivo.is_open()) return false;

        arbol.crearVacio();
        std::string linea;
        while (std::getline(archivo, linea)) {
            linea = Consola::limpiarTexto(linea);
            if (linea.empty() || linea[0] == '#') continue;

            std::stringstream ss(linea);
            std::string cStr, etq, actStr;
            if (std::getline(ss, cStr, ';') && std::getline(ss, etq, ';') && std::getline(ss, actStr, ';')) {
                try {
                    int clave = std::stoi(Consola::limpiarTexto(cStr));
                    bool activo = (Consola::limpiarTexto(actStr) != "0");
                    if (arbol.insertar(clave, Consola::limpiarTexto(etq), activo)) {
                        ++cargados;
                    }
                } catch (...) {
                    // Ignora lineas mal formadas sin interrumpir la carga
                }
            }
        }
        return true;
    }

    bool guardarArchivo(const ArbolAVL& arbol, const std::string& nombreArchivo) {
        std::string ruta = Consola::rutaJuntoAlEjecutable(nombreArchivo);
        std::ofstream archivo(ruta, std::ios::trunc);
        if (!archivo.is_open()) return false;

        archivo << "# Persistencia Taller 3 - Programa de Aprendizaje de Arboles (AVL)\n";
        archivo << "# Formato: clave;etiqueta;activo (1=Activo, 0=Desactivado)\n";
        for (const NodoAVL* n : arbol.preOrden()) {
            archivo << n->clave << ";" << n->etiqueta << ";" << (n->activo ? 1 : 0) << "\n";
        }
        return archivo.good();
    }

} // namespace PersistenciaAVL

// ============================================================================
// CAPA 4: INTERFAZ VISUAL CON GotoXY() Y RECORRIDOS SIEMPRE VISIBLES
// ============================================================================
class InterfazPAA {
private:
    ArbolAVL& arbol;
    const std::string archivoDatos = "datos_avl.txt";
    std::string estadoBanner;

    static std::string recortarAncho(const std::string& texto, std::size_t maxLen) {
        if (texto.size() <= maxLen) return texto;
        if (maxLen <= 3) return texto.substr(0, maxLen);
        return texto.substr(0, maxLen - 3) + "...";
    }

    static std::string formatoNodo(const NodoAVL* n, int fe) {
        std::ostringstream oss;
        if (n->activo) {
            oss << "[" << n->clave << "|" << (fe > 0 ? "+" : "") << fe << "]";
        } else {
            oss << "(" << n->clave << "*)";
        }
        return oss.str();
    }

    void dibujarNodoRec(const NodoAVL* n, int x, int y, int offset, int nivel) const {
        if (!n || nivel > 4) return;

        std::string etiqueta = formatoNodo(n, arbol.obtenerFE(n));
        int xInicio = std::max(1, std::min(118 - static_cast<int>(etiqueta.size()),
                                           x - static_cast<int>(etiqueta.size()) / 2));
        Consola::GotoXY(xInicio, y);
        std::cout << etiqueta;

        if (nivel == 4) return;

        int nextOffset = std::max(3, offset / 2);
        if (n->izq) {
            int xHijo = std::max(3, x - offset);
            int xRama = (x + xHijo) / 2;
            Consola::GotoXY(xRama, y + 1);
            std::cout << "/";
            dibujarNodoRec(n->izq, xHijo, y + 2, nextOffset, nivel + 1);
        }
        if (n->der) {
            int xHijo = std::min(115, x + offset);
            int xRama = (x + xHijo) / 2;
            Consola::GotoXY(xRama, y + 1);
            std::cout << "\\";
            dibujarNodoRec(n->der, xHijo, y + 2, nextOffset, nivel + 1);
        }
    }

    void dibujarPantallaPrincipal(const std::string& avisoSuperior = "") const {
        Consola::limpiarPantalla();

        // Encabezado (Filas 0-2)
        Consola::GotoXY(1, 0);
        std::cout << "+====================================================================================================================+";
        Consola::GotoXY(1, 1);
        std::ostringstream titulo;
        titulo << "| PAA - ARBOL BINARIO AVL (UPC) | Nodos: " << arbol.totalNodos()
               << " (Activos: " << arbol.totalActivos() << ") | Altura: " << arbol.alturaTotal()
               << " | Leyenda: [clave|FE] (inactivo*)";
        std::string linTitulo = recortarAncho(titulo.str(), 116);
        std::cout << linTitulo << std::string(117 - linTitulo.size(), ' ') << "|";
        Consola::GotoXY(1, 2);
        std::cout << "+====================================================================================================================+";

        // Lienzo 2D del Arbol AVL (Filas 3-15)
        if (!arbol.obtenerRaiz()) {
            Consola::GotoXY(42, 8);
            std::cout << "[ Arbol AVL vacio - Inserte o cargue nodos ]";
        } else {
            dibujarNodoRec(arbol.obtenerRaiz(), 59, 4, 28, 0);
            if (arbol.alturaTotal() > 5) {
                Consola::GotoXY(2, 15);
                std::cout << "[Nota: Mostrando niveles 1-5 en lienzo 2D; use opcion 9 para ver el listado completo.]";
            }
        }

        // Franja Media Fija: Recorridos SIEMPRE VISIBLES (Filas 16-20)
        Consola::GotoXY(1, 16);
        std::cout << "+--------------------------------------------------------------------------------------------------------------------+";
        Consola::GotoXY(2, 17);
        std::cout << "PRE-ORDEN : " << recortarAncho(arbol.formatearRecorrido(arbol.preOrden()), 103);
        Consola::GotoXY(2, 18);
        std::cout << "IN-ORDEN  : " << recortarAncho(arbol.formatearRecorrido(arbol.inOrden()), 103);
        Consola::GotoXY(2, 19);
        std::cout << "POST-ORDEN: " << recortarAncho(arbol.formatearRecorrido(arbol.postOrden()), 103);
        Consola::GotoXY(1, 20);
        std::cout << "+--------------------------------------------------------------------------------------------------------------------+";

        // Panel de Traza Pedagogica de Ordenamiento y Balanceo (Filas 21-24)
        const RegistroTraza& traza = arbol.obtenerUltimaTraza();
        Consola::GotoXY(2, 21);
        std::string cabeceraTraza = avisoSuperior.empty() ? ("ULTIMA OPERACION (" + traza.operacion + "): " + traza.mensajeFinal) : avisoSuperior;
        std::cout << recortarAncho(cabeceraTraza, 115);

        std::ostringstream rutaStr;
        rutaStr << "TRAZA DE COMPARACION: ";
        if (traza.pasos.empty()) {
            rutaStr << "(sin pasos registrados)";
        } else {
            for (std::size_t i = 0; i < traza.pasos.size(); ++i) {
                if (i > 0) rutaStr << " | ";
                rutaStr << traza.pasos[i];
            }
        }
        Consola::GotoXY(2, 22);
        std::cout << recortarAncho(rutaStr.str(), 115);

        Consola::GotoXY(2, 23);
        if (!traza.rotaciones.empty()) {
            std::cout << recortarAncho("BALANCEO APLICADO   : " + traza.rotaciones.back().detalle, 115);
        } else if (!estadoBanner.empty()) {
            std::cout << recortarAncho("ESTADO              : " + estadoBanner, 115);
        } else {
            std::cout << "BALANCEO APLICADO   : Sin rotaciones requeridas (|FE| <= 1 en todo el arbol).";
        }
        Consola::GotoXY(1, 24);
        std::cout << "----------------------------------------------------------------------------------------------------------------------";
    }

    void dibujarMenu() const {
        Consola::GotoXY(2, 25);
        std::cout << "1) Insertar nodo      2) Eliminar nodo      3) Desactivar/Reactivar   4) Consultar (Buscar)   5) Modificar nodo";
        Consola::GotoXY(2, 26);
        std::cout << "6) Crear vacio        7) Cargar archivo     8) Guardar archivo        9) Detalle y Vars E/S   D) Demo 4 Rotaciones";
        Consola::GotoXY(2, 27);
        std::cout << "0) Salir";
        Consola::GotoXY(2, 28);
        std::cout << "Seleccione una opcion: ";
    }

    void ejecutarDemoPedagogico() {
        const std::vector<std::pair<int, std::string>> secuencia = {
            {10, "Demo_10"},
            {20, "Demo_20"},
            {30, "Demo_30_RR"},
            {5,  "Demo_5"},
            {3,  "Demo_3_LL"},
            {8,  "Demo_8_LR"},
            {25, "Demo_25_RL"}
        };

        arbol.crearVacio();
        for (std::size_t i = 0; i < secuencia.size(); ++i) {
            int clave = secuencia[i].first;
            arbol.insertar(clave, secuencia[i].second, true);
            const RegistroTraza& traza = arbol.obtenerUltimaTraza();
            std::string rotInfo = traza.rotaciones.empty()
                ? "Sin rotacion"
                : traza.rotaciones.back().detalle;

            std::string aviso = "[DEMO] Paso " + std::to_string(i + 1) + "/" +
                                std::to_string(secuencia.size()) +
                                ": Insertando " + std::to_string(clave) + " -> " + rotInfo;
            dibujarPantallaPrincipal(aviso);
            Consola::GotoXY(2, 26);
            std::cout << "Ejecutando secuencia pedagogica AVL (RR -> LL -> LR -> RL)...";
            std::cout << std::flush;
            std::this_thread::sleep_for(std::chrono::milliseconds(1500));
        }
        estadoBanner = "Demo completado: 4 rotaciones AVL (RR, LL, LR, RL) ejecutadas.";
        pausarEn(28);
    }

    void pausarEn(int fila) const {
        Consola::GotoXY(2, fila);
        Consola::leerLinea("Presione ENTER para continuar...");
    }

    void mostrarDetalleYVariables() const {
        Consola::limpiarPantalla();
        std::cout << "======================================================================================\n";
        std::cout << "  DETALLE DE NODOS DEL ARBOL AVL Y VARIABLES DE ENTRADA / SALIDA DEL MODELO\n";
        std::cout << "======================================================================================\n\n";
        std::cout << "[VARIABLES DE ENTRADA]\n";
        std::cout << "  - opcionCargaInicial : Decision de cargar 'datos_avl.txt' o iniciar vacio.\n";
        std::cout << "  - clave (int)        : Clave numerica unica de ordenamiento BST/AVL.\n";
        std::cout << "  - etiqueta (string)  : Nombre o concepto asociado al nodo.\n";
        std::cout << "  - activo (bool)      : Estado logico del registro (1=Activo, 0=Desactivado).\n\n";
        std::cout << "[VARIABLES DE SALIDA]\n";
        std::cout << "  - altura, FE         : Altura del subarbol y Factor de Equilibrio (h_izq - h_der).\n";
        std::cout << "  - tipoRotacion       : Rotacion ejecutada (LL, RR, LR, RL) y traza de comparaciones.\n";
        std::cout << "  - recorridos         : Pre-orden, In-orden y Post-orden visibles permanentemente.\n\n";
        std::cout << "[LISTADO DE NODOS EN IN-ORDEN]\n";
        std::cout << std::left << std::setw(10) << "CLAVE" << std::setw(26) << "ETIQUETA"
                  << std::setw(10) << "ALTURA" << std::setw(8) << "FE" << "ESTADO\n";
        std::cout << "----------------------------------------------------------------------\n";
        auto lista = arbol.inOrden();
        if (lista.empty()) {
            std::cout << "(Arbol vacio)\n";
        } else {
            for (const NodoAVL* n : lista) {
                std::cout << std::left << std::setw(10) << n->clave
                          << std::setw(26) << n->etiqueta
                          << std::setw(10) << n->altura
                          << std::setw(8) << arbol.obtenerFE(n)
                          << (n->activo ? "ACTIVO" : "DESACTIVADO") << "\n";
            }
        }
        std::cout << "\n";
        Consola::leerLinea("Presione ENTER para volver al arbol...");
    }

    void mostrarInicioPersistencia() {
        Consola::limpiarPantalla();
        std::cout << "+======================================================================+\n";
        std::cout << "|   UNIVERSIDAD POPULAR DEL CESAR - PROGRAMA DE APRENDIZAJE DE ARBOLES |\n";
        std::cout << "|                 ARBOL BINARIO AVL (C++17) - KM-DV-ST                 |\n";
        std::cout << "+======================================================================+\n\n";
        std::cout << "  1) Cargar datos iniciales desde '" << archivoDatos << "'\n";
        std::cout << "  2) Ejecutar programa sin datos (arbol vacio)\n\n";
        std::string op = Consola::leerLinea("Seleccione una opcion [1-2]: ");
        if (op == "1") {
            int cargados = 0;
            if (PersistenciaAVL::cargarArchivo(arbol, archivoDatos, cargados)) {
                estadoBanner = "Cargados " + std::to_string(cargados) + " nodos desde " + archivoDatos + ".";
            } else {
                estadoBanner = "No se encontro '" + archivoDatos + "'. Se inicio con arbol vacio.";
            }
        } else {
            arbol.crearVacio();
            estadoBanner = "Sesion iniciada sin datos (arbol vacio).";
        }
    }

public:
    explicit InterfazPAA(ArbolAVL& a) : arbol(a) {}

    void ejecutar() {
        mostrarInicioPersistencia();
        bool ejecutando = true;

        while (ejecutando) {
            dibujarPantallaPrincipal();
            dibujarMenu();

            std::string opcion = Consola::leerLinea("");
            estadoBanner.clear();

            if (opcion == "1") {
                int clave = 0;
                Consola::GotoXY(2, 30);
                if (!Consola::leerEntero("Ingrese clave numerica (entero): ", clave)) {
                    estadoBanner = "Entrada invalida: debe digitar un numero entero.";
                    continue;
                }
                Consola::GotoXY(2, 31);
                std::string etq = Consola::leerLinea("Ingrese etiqueta (ENTER para 'Nodo_" + std::to_string(clave) + "'): ");
                arbol.insertar(clave, etq, true);
            } else if (opcion == "2") {
                int clave = 0;
                Consola::GotoXY(2, 30);
                if (!Consola::leerEntero("Clave a eliminar fisicamente: ", clave)) {
                    estadoBanner = "Entrada invalida: debe digitar un numero entero.";
                    continue;
                }
                arbol.eliminar(clave);
            } else if (opcion == "3") {
                int clave = 0;
                Consola::GotoXY(2, 30);
                if (!Consola::leerEntero("Clave a desactivar o reactivar: ", clave)) {
                    estadoBanner = "Entrada invalida.";
                    continue;
                }
                NodoAVL* encontrado = arbol.buscar(clave);
                if (encontrado) {
                    arbol.cambiarEstadoActivo(clave, !encontrado->activo);
                }
            } else if (opcion == "4") {
                int clave = 0;
                Consola::GotoXY(2, 30);
                if (!Consola::leerEntero("Clave a consultar: ", clave)) {
                    estadoBanner = "Entrada invalida.";
                    continue;
                }
                arbol.buscar(clave);
            } else if (opcion == "5") {
                int claveActual = 0;
                Consola::GotoXY(2, 30);
                if (!Consola::leerEntero("Clave actual a modificar: ", claveActual)) {
                    estadoBanner = "Entrada invalida.";
                    continue;
                }
                NodoAVL* nodo = arbol.buscar(claveActual);
                if (!nodo) continue;

                Consola::GotoXY(2, 31);
                std::string nuevaClaveStr = Consola::leerLinea(
                    "Nueva clave (ENTER para mantener " + std::to_string(claveActual) + "): ");
                int nuevaClave = claveActual;
                if (!nuevaClaveStr.empty()) {
                    try {
                        nuevaClave = std::stoi(nuevaClaveStr);
                    } catch (...) {
                        estadoBanner = "Nueva clave invalida.";
                        continue;
                    }
                }
                Consola::GotoXY(2, 32);
                std::string nuevaEtq = Consola::leerLinea("Nueva etiqueta (ENTER para mantener '" + nodo->etiqueta + "'): ");
                arbol.modificar(claveActual, nuevaClave, nuevaEtq);
            } else if (opcion == "6") {
                arbol.crearVacio();
            } else if (opcion == "7") {
                int cargados = 0;
                if (PersistenciaAVL::cargarArchivo(arbol, archivoDatos, cargados)) {
                    estadoBanner = "Recargados " + std::to_string(cargados) + " nodos desde " + archivoDatos + ".";
                } else {
                    estadoBanner = "No se pudo abrir '" + archivoDatos + "'.";
                }
            } else if (opcion == "8") {
                if (PersistenciaAVL::guardarArchivo(arbol, archivoDatos)) {
                    estadoBanner = "Arbol guardado correctamente en '" + archivoDatos + "'.";
                } else {
                    estadoBanner = "Error al guardar en '" + archivoDatos + "'.";
                }
            } else if (opcion == "9") {
                mostrarDetalleYVariables();
            } else if (opcion == "d" || opcion == "D") {
                ejecutarDemoPedagogico();
            } else if (opcion == "0") {
                Consola::GotoXY(2, 30);
                std::string resp = Consola::leerLinea("Desea guardar los cambios antes de salir? (s/n): ");
                if (resp == "s" || resp == "S") {
                    PersistenciaAVL::guardarArchivo(arbol, archivoDatos);
                }
                ejecutando = false;
            } else {
                estadoBanner = "Opcion no reconocida. Seleccione 0-9 o D.";
            }
        }

        Consola::limpiarPantalla();
        std::cout << "Sesion finalizada. Gracias por usar el Programa de Aprendizaje de Arboles (PAA).\n";
        Consola::leerLinea("Presione ENTER para cerrar...");
    }
};

// ============================================================================
// PUNTO DE ENTRADA PRINCIPAL
// ============================================================================
int main() {
    Consola::inicializar();
    ArbolAVL arbol;
    InterfazPAA interfaz(arbol);
    interfaz.ejecutar();
    return 0;
}
