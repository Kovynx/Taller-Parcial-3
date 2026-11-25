// ============================================================================
// Universidad Popular del Cesar - Facultad de Ingenierias y Tecnologicas
// Ingenieria de Sistemas - Estructura de Datos (Parcial 3)
// Programa Estadistico de Rutas de Automoviles (PERA - Colombia) en C++17
// Autores: Kovyn Been Mena Orcasita, Damian Jose Velasquez Gonzalez,
//          Sofia Isabel Tovar Rodriguez (KM-DV-ST)
// ============================================================================

#ifdef _WIN32
  #define WIN32_LEAN_AND_MEAN
  #include <windows.h>
#endif

#include <algorithm>
#include <cmath>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <sstream>
#include <string>
#include <vector>

// ============================================================================
// CAPA 0: UTILIDADES MULTIPLATAFORMA (WINDOWS Win32 / LINUX)
// ============================================================================
namespace Consola {

    void inicializar() {
    #ifdef _WIN32
        SetConsoleOutputCP(65001);
        SetConsoleCP(65001);
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        if (hOut != INVALID_HANDLE_VALUE) {
            COORD tamBuffer = {120, 40};
            SetConsoleScreenBufferSize(hOut, tamBuffer);
            SMALL_RECT ventana = {0, 0, 119, 34};
            SetConsoleWindowInfo(hOut, TRUE, &ventana);
        }
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
            int val = std::stoi(entrada, &idx);
            if (idx != entrada.size()) return false;
            destino = val;
            return true;
        } catch (...) {
            return false;
        }
    }

    bool leerDecimal(const std::string& mensaje, double& destino) {
        std::string entrada = leerLinea(mensaje);
        if (entrada.empty()) return false;
        std::replace(entrada.begin(), entrada.end(), ',', '.');
        try {
            std::size_t idx = 0;
            double val = std::stod(entrada, &idx);
            if (idx != entrada.size()) return false;
            destino = val;
            return true;
        } catch (...) {
            return false;
        }
    }

    std::string formatoCOP(double valor) {
        long long entero = static_cast<long long>(std::llround(valor));
        bool neg = entero < 0;
        std::string s = std::to_string(neg ? -entero : entero);
        std::string res;
        int cont = 0;
        for (int i = static_cast<int>(s.size()) - 1; i >= 0; --i) {
            if (cont > 0 && cont % 3 == 0) res.push_back(',');
            res.push_back(s[static_cast<std::size_t>(i)]);
            ++cont;
        }
        std::reverse(res.begin(), res.end());
        return (neg ? "-$" : "$") + res + " COP";
    }

    std::string formatoHoras(double horas) {
        int h = static_cast<int>(horas);
        int m = static_cast<int>(std::llround((horas - h) * 60.0));
        if (m == 60) {
            ++h;
            m = 0;
        }
        std::ostringstream oss;
        oss << h << "h " << std::setw(2) << std::setfill('0') << m << "m";
        return oss.str();
    }

    void pausar() {
        std::cout << "\n";
        leerLinea("Presione ENTER para continuar...");
    }

} // namespace Consola

// ============================================================================
// CAPA 1: MODELO DE DATOS (CIUDADES, RUTAS/PEAJES, GRUPOS Y PRODUCTOS)
// ============================================================================
struct Ciudad {
    int id;
    std::string nombre;
    std::string departamento;
    double latitud;
    double longitud;
    bool activa;
};

struct RutaTramo {
    int idRuta;
    int idOrigen;
    int idDestino;
    double distanciaKm;
    double tiempoHoras;
    double costoCombustibleCOP;
    int cantidadPeajes;
    double costoPeajesCOP;
    std::string categoriaVia;
    bool validado;
    bool activa;
};

struct GrupoInvestigacion {
    int idGrupo;
    std::string nombreGrupo;
    std::string region;
    std::string investigadorLider;
    bool activo;
};

struct ProductoTecnico {
    int idProducto;
    int idGrupo;
    std::string nombreProducto;
    std::string categoria;
    bool validado;
    bool activo;
};

struct EstadisticaVariable {
    int n = 0;
    double suma = 0.0;
    double media = 0.0;
    double mediana = 0.0;
    double desvEstandar = 0.0;
    double minimo = 0.0;
    double maximo = 0.0;
};

struct ResumenEstadisticoPERA {
    int totalCiudades = 0;
    int ciudadesActivas = 0;
    int ciudadesAisladas = 0;
    int totalRutas = 0;
    int rutasActivas = 0;
    int totalGrupos = 0;
    int totalProductos = 0;
    int productosValidados = 0;
    EstadisticaVariable distKm;
    EstadisticaVariable tiempoHoras;
    EstadisticaVariable combustibleCOP;
    EstadisticaVariable peajesCOP;
    std::vector<std::pair<int, int>> topHubs;            // (idCiudad, grado)
    std::vector<std::pair<int, double>> topRutasPeajes;  // (idRuta, costoPeajesCOP)
    std::vector<int> listaAisladas;
};

struct AristaPonderada {
    int destino;
    int idRuta;
    double peso;
};

struct ResultadoRuta {
    bool encontrada = false;
    std::string criterio;
    std::string mensaje;
    std::vector<int> caminoCiudades;
    std::vector<int> rutasUsadas;
    double distanciaTotalKm = 0.0;
    double tiempoTotalHoras = 0.0;
    double combustibleTotalCOP = 0.0;
    int totalPeajes = 0;
    double peajesTotalCOP = 0.0;
    double costoTotalCOP = 0.0;
};

// ============================================================================
// CAPA 2: ESTRUCTURA DE GRAFOS PONDERADOS (3 GRAFOS SINCRONIZADOS)
// Complejidad Dijkstra con Min-Heap: O((V + E) log V)
// ============================================================================
class GrafoPonderado {
private:
    std::string nombreMetrica;
    std::string unidad;
    std::map<int, std::vector<AristaPonderada>> adyacencia;

public:
    GrafoPonderado(const std::string& metrica, const std::string& u)
        : nombreMetrica(metrica), unidad(u) {}

    void limpiar() { adyacencia.clear(); }

    void agregarVertice(int idCiudad) {
        if (adyacencia.find(idCiudad) == adyacencia.end()) {
            adyacencia[idCiudad] = std::vector<AristaPonderada>();
        }
    }

    void agregarAristaNoDirigida(int u, int v, int idRuta, double peso) {
        adyacencia[u].push_back({v, idRuta, peso});
        adyacencia[v].push_back({u, idRuta, peso});
    }

    const std::string& obtenerMetrica() const { return nombreMetrica; }
    const std::string& obtenerUnidad() const { return unidad; }

    const std::map<int, std::vector<AristaPonderada>>& obtenerAdyacencia() const {
        return adyacencia;
    }

    int grado(int idCiudad) const {
        auto it = adyacencia.find(idCiudad);
        return (it != adyacencia.end()) ? static_cast<int>(it->second.size()) : 0;
    }
};

class SistemaPERA {
private:
    std::map<int, Ciudad> ciudades;
    std::map<int, RutaTramo> rutas;
    std::map<int, GrupoInvestigacion> grupos;
    std::map<int, ProductoTecnico> productos;

    // Tres grafos ponderados independientes y sincronizados
    GrafoPonderado grafoDistancia;
    GrafoPonderado grafoCombustible;
    GrafoPonderado grafoPeajes;

public:
    SistemaPERA()
        : grafoDistancia("Distancia", "km"),
          grafoCombustible("Combustible", "COP"),
          grafoPeajes("Peajes", "COP") {}

    void limpiarTodo() {
        ciudades.clear();
        rutas.clear();
        grupos.clear();
        productos.clear();
        reconstruirGrafos();
    }

    void reconstruirGrafos() {
        grafoDistancia.limpiar();
        grafoCombustible.limpiar();
        grafoPeajes.limpiar();

        for (const auto& par : ciudades) {
            if (par.second.activa) {
                grafoDistancia.agregarVertice(par.first);
                grafoCombustible.agregarVertice(par.first);
                grafoPeajes.agregarVertice(par.first);
            }
        }

        for (const auto& par : rutas) {
            const RutaTramo& r = par.second;
            if (!r.activa) continue;
            auto itU = ciudades.find(r.idOrigen);
            auto itV = ciudades.find(r.idDestino);
            if (itU == ciudades.end() || itV == ciudades.end()) continue;
            if (!itU->second.activa || !itV->second.activa) continue;

            grafoDistancia.agregarAristaNoDirigida(r.idOrigen, r.idDestino, r.idRuta, r.distanciaKm);
            grafoCombustible.agregarAristaNoDirigida(r.idOrigen, r.idDestino, r.idRuta, r.costoCombustibleCOP);
            grafoPeajes.agregarAristaNoDirigida(r.idOrigen, r.idDestino, r.idRuta, r.costoPeajesCOP);
        }
    }

    // Accesores de solo lectura
    const std::map<int, Ciudad>& obtenerCiudades() const { return ciudades; }
    const std::map<int, RutaTramo>& obtenerRutas() const { return rutas; }
    const std::map<int, GrupoInvestigacion>& obtenerGrupos() const { return grupos; }
    const std::map<int, ProductoTecnico>& obtenerProductos() const { return productos; }

    const GrafoPonderado& obtenerGrafoDistancia() const { return grafoDistancia; }
    const GrafoPonderado& obtenerGrafoCombustible() const { return grafoCombustible; }
    const GrafoPonderado& obtenerGrafoPeajes() const { return grafoPeajes; }

    // Insercion directa (usada por persistencia y CRUD)
    bool agregarCiudad(const Ciudad& c) {
        if (ciudades.find(c.id) != ciudades.end()) return false;
        ciudades[c.id] = c;
        reconstruirGrafos();
        return true;
    }

    bool agregarRuta(const RutaTramo& r) {
        if (rutas.find(r.idRuta) != rutas.end()) return false;
        if (ciudades.find(r.idOrigen) == ciudades.end() || ciudades.find(r.idDestino) == ciudades.end()) return false;
        if (r.idOrigen == r.idDestino) return false;
        rutas[r.idRuta] = r;
        reconstruirGrafos();
        return true;
    }

    bool agregarGrupo(const GrupoInvestigacion& g) {
        if (grupos.find(g.idGrupo) != grupos.end()) return false;
        grupos[g.idGrupo] = g;
        return true;
    }

    bool agregarProducto(const ProductoTecnico& p) {
        if (productos.find(p.idProducto) != productos.end()) return false;
        if (grupos.find(p.idGrupo) == grupos.end()) return false;
        productos[p.idProducto] = p;
        return true;
    }

    int siguienteIdCiudad() const { return ciudades.empty() ? 1 : (ciudades.rbegin()->first + 1); }
    int siguienteIdRuta() const { return rutas.empty() ? 1 : (rutas.rbegin()->first + 1); }
    int siguienteIdGrupo() const { return grupos.empty() ? 1 : (grupos.rbegin()->first + 1); }
    int siguienteIdProducto() const { return productos.empty() ? 1 : (productos.rbegin()->first + 1); }

    std::string nombreCiudad(int id) const {
        auto it = ciudades.find(id);
        return (it != ciudades.end()) ? it->second.nombre : ("ID_" + std::to_string(id));
    }

    // ---- CRUD completo y desactivacion: Ciudades ----
    bool modificarCiudad(int id, const Ciudad& nueva) {
        auto it = ciudades.find(id);
        if (it == ciudades.end()) return false;
        it->second = nueva;
        it->second.id = id;
        reconstruirGrafos();
        return true;
    }

    bool cambiarEstadoCiudad(int id, bool activa) {
        auto it = ciudades.find(id);
        if (it == ciudades.end()) return false;
        it->second.activa = activa;
        reconstruirGrafos();
        return true;
    }

    bool eliminarCiudad(int id) {
        if (ciudades.erase(id) == 0) return false;
        for (auto it = rutas.begin(); it != rutas.end();) {
            if (it->second.idOrigen == id || it->second.idDestino == id) {
                it = rutas.erase(it);
            } else {
                ++it;
            }
        }
        reconstruirGrafos();
        return true;
    }

    // ---- CRUD completo y desactivacion: Rutas y Peajes ----
    bool modificarRuta(int idRuta, const RutaTramo& nueva) {
        auto it = rutas.find(idRuta);
        if (it == rutas.end()) return false;
        if (ciudades.find(nueva.idOrigen) == ciudades.end() ||
            ciudades.find(nueva.idDestino) == ciudades.end() ||
            nueva.idOrigen == nueva.idDestino) {
            return false;
        }
        it->second = nueva;
        it->second.idRuta = idRuta;
        reconstruirGrafos();
        return true;
    }

    bool cambiarEstadoRuta(int idRuta, bool activa) {
        auto it = rutas.find(idRuta);
        if (it == rutas.end()) return false;
        it->second.activa = activa;
        reconstruirGrafos();
        return true;
    }

    bool eliminarRuta(int idRuta) {
        if (rutas.erase(idRuta) == 0) return false;
        reconstruirGrafos();
        return true;
    }

    // ---- CRUD completo y desactivacion: Grupos e Investigadores ----
    bool modificarGrupo(int idGrupo, const GrupoInvestigacion& nuevo) {
        auto it = grupos.find(idGrupo);
        if (it == grupos.end()) return false;
        it->second = nuevo;
        it->second.idGrupo = idGrupo;
        return true;
    }

    bool cambiarEstadoGrupo(int idGrupo, bool activo) {
        auto it = grupos.find(idGrupo);
        if (it == grupos.end()) return false;
        it->second.activo = activo;
        return true;
    }

    bool eliminarGrupo(int idGrupo) {
        if (grupos.erase(idGrupo) == 0) return false;
        for (auto it = productos.begin(); it != productos.end();) {
            if (it->second.idGrupo == idGrupo) {
                it = productos.erase(it);
            } else {
                ++it;
            }
        }
        return true;
    }

    // ---- CRUD completo y desactivacion: Productos Tecnicos ----
    bool modificarProducto(int idProducto, const ProductoTecnico& nuevo) {
        auto it = productos.find(idProducto);
        if (it == productos.end()) return false;
        if (grupos.find(nuevo.idGrupo) == grupos.end()) return false;
        it->second = nuevo;
        it->second.idProducto = idProducto;
        return true;
    }

    bool cambiarEstadoProducto(int idProducto, bool activo) {
        auto it = productos.find(idProducto);
        if (it == productos.end()) return false;
        it->second.activo = activo;
        return true;
    }

    bool eliminarProducto(int idProducto) {
        return productos.erase(idProducto) > 0;
    }

    // ---- Algoritmo de Dijkstra O((V + E) log V) sobre los 3 Grafos ----
    // criterio: 1 = Distancia (Grafo 1), 2 = Combustible (Grafo 2),
    //           3 = Peajes (Grafo 3),    4 = Costo Total (Combustible + Peajes)
    ResultadoRuta calcularRutaOptima(int idOrigen, int idDestino, int criterio) const {
        ResultadoRuta res;
        if (criterio == 1) res.criterio = "Menor Distancia (Grafo 1 - km)";
        else if (criterio == 2) res.criterio = "Menor Combustible (Grafo 2 - COP)";
        else if (criterio == 3) res.criterio = "Menor Peajes (Grafo 3 - COP)";
        else res.criterio = "Menor Costo Total (Combustible + Peajes)";

        auto itO = ciudades.find(idOrigen);
        auto itD = ciudades.find(idDestino);
        if (itO == ciudades.end() || itD == ciudades.end()) {
            res.mensaje = "Una o ambas ciudades no existen en el sistema.";
            return res;
        }
        if (!itO->second.activa || !itD->second.activa) {
            res.mensaje = "Origen o destino se encuentra DESACTIVADO.";
            return res;
        }
        if (idOrigen == idDestino) {
            res.encontrada = true;
            res.caminoCiudades.push_back(idOrigen);
            res.mensaje = "Origen y destino corresponden a la misma capital.";
            return res;
        }

        const GrafoPonderado* grafoBase = &grafoDistancia;
        if (criterio == 2) grafoBase = &grafoCombustible;
        else if (criterio == 3) grafoBase = &grafoPeajes;

        const auto& adj = grafoBase->obtenerAdyacencia();
        const double INF = std::numeric_limits<double>::infinity();
        std::map<int, double> dist;
        std::map<int, int> padreCiudad;
        std::map<int, int> padreRuta;

        for (const auto& par : adj) {
            dist[par.first] = INF;
        }

        using ParCola = std::pair<double, int>;
        std::priority_queue<ParCola, std::vector<ParCola>, std::greater<ParCola>> pq;
        dist[idOrigen] = 0.0;
        pq.push({0.0, idOrigen});

        while (!pq.empty()) {
            double dActual = pq.top().first;
            int u = pq.top().second;
            pq.pop();

            if (dActual > dist[u]) continue;
            if (u == idDestino) break;

            auto itAdj = adj.find(u);
            if (itAdj == adj.end()) continue;

            for (const AristaPonderada& arista : itAdj->second) {
                double peso = arista.peso;
                if (criterio == 4) {
                    const RutaTramo& r = rutas.at(arista.idRuta);
                    peso = r.costoCombustibleCOP + r.costoPeajesCOP;
                }
                double nuevoCosto = dActual + peso;
                if (nuevoCosto < dist[arista.destino]) {
                    dist[arista.destino] = nuevoCosto;
                    padreCiudad[arista.destino] = u;
                    padreRuta[arista.destino] = arista.idRuta;
                    pq.push({nuevoCosto, arista.destino});
                }
            }
        }

        if (dist.find(idDestino) == dist.end() || !std::isfinite(dist[idDestino])) {
            res.encontrada = false;
            res.mensaje = "No existe ruta terrestre activa entre " + itO->second.nombre +
                          " y " + itD->second.nombre + " (componente desconectada o cierres viales).";
            return res;
        }

        // Reconstruccion del camino optimo y acumulacion de las 4 metricas
        int actual = idDestino;
        while (actual != idOrigen) {
            res.caminoCiudades.push_back(actual);
            int idR = padreRuta[actual];
            res.rutasUsadas.push_back(idR);
            const RutaTramo& tramo = rutas.at(idR);
            res.distanciaTotalKm += tramo.distanciaKm;
            res.tiempoTotalHoras += tramo.tiempoHoras;
            res.combustibleTotalCOP += tramo.costoCombustibleCOP;
            res.totalPeajes += tramo.cantidadPeajes;
            res.peajesTotalCOP += tramo.costoPeajesCOP;
            actual = padreCiudad[actual];
        }
        res.caminoCiudades.push_back(idOrigen);
        std::reverse(res.caminoCiudades.begin(), res.caminoCiudades.end());
        std::reverse(res.rutasUsadas.begin(), res.rutasUsadas.end());

        res.costoTotalCOP = res.combustibleTotalCOP + res.peajesTotalCOP;
        res.encontrada = true;
        res.mensaje = "Ruta optima calculada satisfactoriamente.";
        return res;
    }

    // ---- Estadisticas Descriptivas sobre los 3 Grafos ----
    static EstadisticaVariable resumirVector(std::vector<double> vals) {
        EstadisticaVariable st;
        if (vals.empty()) return st;
        std::sort(vals.begin(), vals.end());
        st.n = static_cast<int>(vals.size());
        st.minimo = vals.front();
        st.maximo = vals.back();
        for (double v : vals) st.suma += v;
        st.media = st.suma / st.n;
        if (st.n % 2 == 1) {
            st.mediana = vals[static_cast<std::size_t>(st.n / 2)];
        } else {
            st.mediana = 0.5 * (vals[static_cast<std::size_t>(st.n / 2 - 1)] +
                                vals[static_cast<std::size_t>(st.n / 2)]);
        }
        double var = 0.0;
        for (double v : vals) {
            double diff = v - st.media;
            var += diff * diff;
        }
        st.desvEstandar = std::sqrt(var / st.n);
        return st;
    }

    ResumenEstadisticoPERA calcularEstadisticas() const {
        ResumenEstadisticoPERA res;
        res.totalCiudades = static_cast<int>(ciudades.size());
        res.totalRutas = static_cast<int>(rutas.size());
        res.totalGrupos = static_cast<int>(grupos.size());
        res.totalProductos = static_cast<int>(productos.size());

        for (const auto& par : productos) {
            if (par.second.validado && par.second.activo) ++res.productosValidados;
        }

        std::vector<std::pair<int, int>> grados;
        for (const auto& par : ciudades) {
            if (par.second.activa) {
                ++res.ciudadesActivas;
                int g = grafoDistancia.grado(par.first);
                grados.push_back({par.first, g});
                if (g == 0) {
                    ++res.ciudadesAisladas;
                    res.listaAisladas.push_back(par.first);
                }
            }
        }
        std::sort(grados.begin(), grados.end(),
                  [](const std::pair<int, int>& a, const std::pair<int, int>& b) {
                      return a.second > b.second;
                  });
        for (std::size_t i = 0; i < std::min<std::size_t>(5, grados.size()); ++i) {
            res.topHubs.push_back(grados[i]);
        }

        std::vector<double> vDist, vTiempo, vComb, vPeaj;
        std::vector<std::pair<int, double>> rutasCosto;
        for (const auto& par : rutas) {
            const RutaTramo& r = par.second;
            if (!r.activa) continue;
            ++res.rutasActivas;
            vDist.push_back(r.distanciaKm);
            vTiempo.push_back(r.tiempoHoras);
            vComb.push_back(r.costoCombustibleCOP);
            vPeaj.push_back(r.costoPeajesCOP);
            rutasCosto.push_back({r.idRuta, r.costoPeajesCOP});
        }

        res.distKm = resumirVector(vDist);
        res.tiempoHoras = resumirVector(vTiempo);
        res.combustibleCOP = resumirVector(vComb);
        res.peajesCOP = resumirVector(vPeaj);

        std::sort(rutasCosto.begin(), rutasCosto.end(),
                  [](const std::pair<int, double>& a, const std::pair<int, double>& b) {
                      return a.second > b.second;
                  });
        for (std::size_t i = 0; i < std::min<std::size_t>(5, rutasCosto.size()); ++i) {
            res.topRutasPeajes.push_back(rutasCosto[i]);
        }
        return res;
    }
};

// ============================================================================
// CAPA 3: PERSISTENCIA COMPARTIDA C++ <-> PYTHON (datos_pera.txt)
// ============================================================================
namespace PersistenciaPERA {

    std::vector<std::string> dividir(const std::string& linea, char delim) {
        std::vector<std::string> partes;
        std::stringstream ss(linea);
        std::string item;
        while (std::getline(ss, item, delim)) {
            partes.push_back(Consola::limpiarTexto(item));
        }
        return partes;
    }

    bool cargarArchivo(SistemaPERA& sistema, const std::string& nombreArchivo) {
        std::string ruta = Consola::rutaJuntoAlEjecutable(nombreArchivo);
        std::ifstream archivo(ruta);
        if (!archivo.is_open()) return false;

        sistema.limpiarTodo();
        std::string seccion;
        std::string linea;

        while (std::getline(archivo, linea)) {
            linea = Consola::limpiarTexto(linea);
            if (linea.empty() || linea[0] == '#') continue;
            if (linea.front() == '[' && linea.back() == ']') {
                seccion = linea;
                continue;
            }

            auto p = dividir(linea, ';');
            try {
                if (seccion == "[CIUDADES]" && p.size() == 6) {
                    sistema.agregarCiudad({
                        std::stoi(p[0]), p[1], p[2],
                        std::stod(p[3]), std::stod(p[4]), p[5] != "0"
                    });
                } else if (seccion == "[RUTAS]" && p.size() == 11) {
                    sistema.agregarRuta({
                        std::stoi(p[0]), std::stoi(p[1]), std::stoi(p[2]),
                        std::stod(p[3]), std::stod(p[4]), std::stod(p[5]),
                        std::stoi(p[6]), std::stod(p[7]), p[8],
                        p[9] != "0", p[10] != "0"
                    });
                } else if (seccion == "[GRUPOS]" && p.size() == 5) {
                    sistema.agregarGrupo({
                        std::stoi(p[0]), p[1], p[2], p[3], p[4] != "0"
                    });
                } else if (seccion == "[PRODUCTOS]" && p.size() == 6) {
                    sistema.agregarProducto({
                        std::stoi(p[0]), std::stoi(p[1]), p[2], p[3],
                        p[4] != "0", p[5] != "0"
                    });
                }
            } catch (...) {
                // Omite registros corruptos preservando estabilidad de carga
            }
        }
        sistema.reconstruirGrafos();
        return true;
    }

    bool guardarArchivo(const SistemaPERA& sistema, const std::string& nombreArchivo) {
        std::string ruta = Consola::rutaJuntoAlEjecutable(nombreArchivo);
        std::ofstream archivo(ruta, std::ios::trunc);
        if (!archivo.is_open()) return false;

        archivo << "# Persistencia Parcial 3 - Programa Estadistico de Rutas de Automoviles (PERA - Colombia)\n";
        archivo << "# Secciones: [CIUDADES], [RUTAS], [GRUPOS], [PRODUCTOS]\n\n";

        archivo << "[CIUDADES]\n# id;nombre;departamento;latitud;longitud;activa\n";
        for (const auto& par : sistema.obtenerCiudades()) {
            const Ciudad& c = par.second;
            archivo << c.id << ";" << c.nombre << ";" << c.departamento << ";"
                    << std::fixed << std::setprecision(4) << c.latitud << ";" << c.longitud << ";"
                    << (c.activa ? 1 : 0) << "\n";
        }

        archivo << "\n[RUTAS]\n# idRuta;idOrigen;idDestino;distanciaKm;tiempoHoras;costoCombustibleCOP;cantidadPeajes;costoPeajesCOP;categoriaVia;validado;activa\n";
        for (const auto& par : sistema.obtenerRutas()) {
            const RutaTramo& r = par.second;
            archivo << r.idRuta << ";" << r.idOrigen << ";" << r.idDestino << ";"
                    << std::fixed << std::setprecision(1) << r.distanciaKm << ";"
                    << r.tiempoHoras << ";"
                    << std::setprecision(0) << r.costoCombustibleCOP << ";"
                    << r.cantidadPeajes << ";" << r.costoPeajesCOP << ";"
                    << r.categoriaVia << ";" << (r.validado ? 1 : 0) << ";" << (r.activa ? 1 : 0) << "\n";
        }

        archivo << "\n[GRUPOS]\n# idGrupo;nombreGrupo;region;investigadorLider;activo\n";
        for (const auto& par : sistema.obtenerGrupos()) {
            const GrupoInvestigacion& g = par.second;
            archivo << g.idGrupo << ";" << g.nombreGrupo << ";" << g.region << ";"
                    << g.investigadorLider << ";" << (g.activo ? 1 : 0) << "\n";
        }

        archivo << "\n[PRODUCTOS]\n# idProducto;idGrupo;nombreProducto;categoria;validado;activo\n";
        for (const auto& par : sistema.obtenerProductos()) {
            const ProductoTecnico& pr = par.second;
            archivo << pr.idProducto << ";" << pr.idGrupo << ";" << pr.nombreProducto << ";"
                    << pr.categoria << ";" << (pr.validado ? 1 : 0) << ";" << (pr.activo ? 1 : 0) << "\n";
        }

        return archivo.good();
    }

} // namespace PersistenciaPERA

// ============================================================================
// CAPA 4: INTERFAZ DE CONSOLA INTERACTIVA (CRUD, DIJKSTRA Y RESUMEN)
// ============================================================================
class InterfazPERA {
private:
    SistemaPERA& sistema;
    const std::string archivoDatos = "datos_pera.txt";

    void mostrarEncabezado(const std::string& subtitulo) const {
        Consola::limpiarPantalla();
        std::cout << "+============================================================================================================+\n";
        std::cout << "|   MINISTERIO DE TRANSPORTE DE COLOMBIA - PROGRAMA ESTADISTICO DE RUTAS DE AUTOMOVILES (PERA | KM-DV-ST)   |\n";
        std::cout << "+============================================================================================================+\n";
        std::cout << "  " << subtitulo << "\n";
        std::cout << "--------------------------------------------------------------------------------------------------------------\n";
    }

    void listarCiudadesCompacto() const {
        const auto& ciudades = sistema.obtenerCiudades();
        if (ciudades.empty()) {
            std::cout << "  (No hay ciudades registradas)\n";
            return;
        }
        int col = 0;
        for (const auto& par : ciudades) {
            const Ciudad& c = par.second;
            std::ostringstream celda;
            celda << std::setw(2) << c.id << ") " << c.nombre << (c.activa ? "" : " [INACTIVA]");
            std::cout << "  " << std::left << std::setw(34) << celda.str();
            if (++col % 3 == 0) std::cout << "\n";
        }
        if (col % 3 != 0) std::cout << "\n";
    }

    void imprimirDetalleRuta(const ResultadoRuta& res) const {
        std::cout << "\n+------------------------------------------------------------------------------------------------------------+\n";
        std::cout << "| CRITERIO: " << std::left << std::setw(96) << res.criterio << " |\n";
        std::cout << "+------------------------------------------------------------------------------------------------------------+\n";
        if (!res.encontrada) {
            std::cout << "  [AVISO] " << res.mensaje << "\n";
            return;
        }
        std::cout << "  RECORRIDO : ";
        for (std::size_t i = 0; i < res.caminoCiudades.size(); ++i) {
            if (i > 0) std::cout << " -> ";
            std::cout << sistema.nombreCiudad(res.caminoCiudades[i]);
        }
        std::cout << "\n\n";
        std::cout << "  1. DISTANCIA TOTAL   : " << std::fixed << std::setprecision(1) << res.distanciaTotalKm << " km\n";
        std::cout << "  2. TIEMPO ESTIMADO   : " << Consola::formatoHoras(res.tiempoTotalHoras) << "\n";
        std::cout << "  3. COSTO COMBUSTIBLE : " << Consola::formatoCOP(res.combustibleTotalCOP) << "\n";
        std::cout << "  4. COSTO EN PEAJES   : " << Consola::formatoCOP(res.peajesTotalCOP)
                  << " (" << res.totalPeajes << " estaciones)\n";
        std::cout << "  => COSTO TOTAL VIAJE : " << Consola::formatoCOP(res.costoTotalCOP) << "\n";

        if (!res.rutasUsadas.empty()) {
            std::cout << "\n  Desglose por tramo vial:\n";
            std::cout << "  " << std::left << std::setw(6) << "ID"
                      << std::setw(36) << "CORREDOR"
                      << std::setw(10) << "DIST(km)"
                      << std::setw(10) << "TIEMPO"
                      << std::setw(18) << "COMBUSTIBLE"
                      << std::setw(18) << "PEAJES"
                      << "CATEGORIA\n";
            std::cout << "  ----------------------------------------------------------------------------------------------------------\n";
            const auto& mapaRutas = sistema.obtenerRutas();
            for (std::size_t i = 0; i < res.rutasUsadas.size(); ++i) {
                const RutaTramo& t = mapaRutas.at(res.rutasUsadas[i]);
                std::string corredor = sistema.nombreCiudad(res.caminoCiudades[i]) + " -> " +
                                       sistema.nombreCiudad(res.caminoCiudades[i + 1]);
                std::cout << "  " << std::left << std::setw(6) << t.idRuta
                          << std::setw(36) << corredor
                          << std::setw(10) << std::fixed << std::setprecision(1) << t.distanciaKm
                          << std::setw(10) << Consola::formatoHoras(t.tiempoHoras)
                          << std::setw(18) << Consola::formatoCOP(t.costoCombustibleCOP)
                          << std::setw(18) << Consola::formatoCOP(t.costoPeajesCOP)
                          << t.categoriaVia << "\n";
            }
        }
    }

    void menuCalcularRuta() const {
        mostrarEncabezado("CALCULO DE COSTOS ENTRE DOS CIUDADES (TIEMPO, DISTANCIA, COMBUSTIBLE Y PEAJES)");
        listarCiudadesCompacto();
        std::cout << "--------------------------------------------------------------------------------------------------------------\n";

        int idOrig = 0, idDest = 0, criterio = 0;
        if (!Consola::leerEntero("ID ciudad de ORIGEN : ", idOrig) ||
            !Consola::leerEntero("ID ciudad de DESTINO: ", idDest)) {
            std::cout << "Entrada invalida.\n";
            Consola::pausar();
            return;
        }

        std::cout << "\nCriterio de optimizacion sobre los 3 grafos:\n";
        std::cout << "  1) Menor Distancia (Grafo 1 - km)\n";
        std::cout << "  2) Menor Combustible (Grafo 2 - COP)\n";
        std::cout << "  3) Menor Costo en Peajes (Grafo 3 - COP)\n";
        std::cout << "  4) Menor Costo Total (Combustible + Peajes)\n";
        std::cout << "  5) Comparar los 3 Grafos + Costo Total lado a lado\n";
        if (!Consola::leerEntero("Seleccione criterio [1-5]: ", criterio) || criterio < 1 || criterio > 5) {
            std::cout << "Criterio fuera de rango.\n";
            Consola::pausar();
            return;
        }

        if (criterio == 5) {
            std::cout << "\n" << std::left << std::setw(42) << "CRITERIO"
                      << std::setw(11) << "DIST(km)"
                      << std::setw(10) << "TIEMPO"
                      << std::setw(17) << "COMBUSTIBLE"
                      << std::setw(17) << "PEAJES"
                      << "TOTAL\n";
            std::cout << "--------------------------------------------------------------------------------------------------------------\n";
            for (int c = 1; c <= 4; ++c) {
                ResultadoRuta r = sistema.calcularRutaOptima(idOrig, idDest, c);
                if (!r.encontrada) {
                    std::cout << "  " << r.mensaje << "\n";
                    break;
                }
                std::cout << std::left << std::setw(42) << r.criterio
                          << std::setw(11) << std::fixed << std::setprecision(1) << r.distanciaTotalKm
                          << std::setw(10) << Consola::formatoHoras(r.tiempoTotalHoras)
                          << std::setw(17) << Consola::formatoCOP(r.combustibleTotalCOP)
                          << std::setw(17) << Consola::formatoCOP(r.peajesTotalCOP)
                          << Consola::formatoCOP(r.costoTotalCOP) << "\n";
            }
            ResultadoRuta detalle = sistema.calcularRutaOptima(idOrig, idDest, 4);
            imprimirDetalleRuta(detalle);
        } else {
            ResultadoRuta r = sistema.calcularRutaOptima(idOrig, idDest, criterio);
            imprimirDetalleRuta(r);
        }
        Consola::pausar();
    }

    void menuGestionCiudades() {
        bool volver = false;
        while (!volver) {
            mostrarEncabezado("GESTION DE CIUDADES / CAPITALES (VERTICES DE LOS 3 GRAFOS)");
            std::cout << std::left << std::setw(6) << "ID" << std::setw(24) << "CAPITAL"
                      << std::setw(26) << "DEPARTAMENTO" << std::setw(11) << "LATITUD"
                      << std::setw(11) << "LONGITUD" << std::setw(8) << "GRADO" << "ESTADO\n";
            std::cout << "--------------------------------------------------------------------------------------------------------------\n";
            for (const auto& par : sistema.obtenerCiudades()) {
                const Ciudad& c = par.second;
                std::cout << std::left << std::setw(6) << c.id
                          << std::setw(24) << c.nombre
                          << std::setw(26) << c.departamento
                          << std::setw(11) << std::fixed << std::setprecision(4) << c.latitud
                          << std::setw(11) << c.longitud
                          << std::setw(8) << sistema.obtenerGrafoDistancia().grado(c.id)
                          << (c.activa ? "ACTIVA" : "DESACTIVADA") << "\n";
            }
            std::cout << "\n  1) Ingresar ciudad   2) Modificar ciudad   3) Desactivar/Reactivar   4) Eliminar ciudad   0) Volver\n";
            std::string op = Consola::leerLinea("Opcion: ");

            if (op == "1") {
                Ciudad c;
                c.id = sistema.siguienteIdCiudad();
                c.nombre = Consola::leerLinea("Nombre de la capital: ");
                c.departamento = Consola::leerLinea("Departamento: ");
                if (!Consola::leerDecimal("Latitud (ej. 10.4631): ", c.latitud) ||
                    !Consola::leerDecimal("Longitud (ej. -73.2532): ", c.longitud)) {
                    std::cout << "Coordenadas invalidas.\n";
                } else {
                    c.activa = true;
                    std::cout << (sistema.agregarCiudad(c) ? "Ciudad agregada con ID " + std::to_string(c.id) + ".\n"
                                                           : "No se pudo agregar.\n");
                }
                Consola::pausar();
            } else if (op == "2") {
                int id = 0;
                if (!Consola::leerEntero("ID de ciudad a modificar: ", id) ||
                    sistema.obtenerCiudades().find(id) == sistema.obtenerCiudades().end()) {
                    std::cout << "Ciudad no encontrada.\n";
                    Consola::pausar();
                    continue;
                }
                Ciudad c = sistema.obtenerCiudades().at(id);
                std::string s = Consola::leerLinea("Nuevo nombre (ENTER para '" + c.nombre + "'): ");
                if (!s.empty()) c.nombre = s;
                s = Consola::leerLinea("Nuevo departamento (ENTER para '" + c.departamento + "'): ");
                if (!s.empty()) c.departamento = s;
                double d = 0.0;
                if (Consola::leerDecimal("Nueva latitud (ENTER para mantener): ", d)) c.latitud = d;
                if (Consola::leerDecimal("Nueva longitud (ENTER para mantener): ", d)) c.longitud = d;
                sistema.modificarCiudad(id, c);
                std::cout << "Ciudad actualizada correctamente.\n";
                Consola::pausar();
            } else if (op == "3") {
                int id = 0;
                if (Consola::leerEntero("ID de ciudad a desactivar/reactivar: ", id) &&
                    sistema.obtenerCiudades().find(id) != sistema.obtenerCiudades().end()) {
                    bool nuevo = !sistema.obtenerCiudades().at(id).activa;
                    sistema.cambiarEstadoCiudad(id, nuevo);
                    std::cout << "Ciudad marcada como " << (nuevo ? "ACTIVA.\n" : "DESACTIVADA.\n");
                } else {
                    std::cout << "Ciudad no encontrada.\n";
                }
                Consola::pausar();
            } else if (op == "4") {
                int id = 0;
                if (Consola::leerEntero("ID de ciudad a eliminar (borra rutas incidentes): ", id) &&
                    sistema.eliminarCiudad(id)) {
                    std::cout << "Ciudad y sus rutas incidentes eliminadas.\n";
                } else {
                    std::cout << "Ciudad no encontrada.\n";
                }
                Consola::pausar();
            } else if (op == "0") {
                volver = true;
            }
        }
    }

    void menuGestionRutas() {
        bool volver = false;
        while (!volver) {
            mostrarEncabezado("GESTION DE RUTAS Y PEAJES (ARISTAS DE LOS 3 GRAFOS)");
            std::cout << std::left << std::setw(5) << "ID" << std::setw(34) << "CORREDOR"
                      << std::setw(9) << "KM" << std::setw(8) << "HORAS"
                      << std::setw(16) << "COMBUSTIBLE" << std::setw(16) << "PEAJES"
                      << std::setw(13) << "CATEGORIA" << "VAL/EST\n";
            std::cout << "--------------------------------------------------------------------------------------------------------------\n";
            for (const auto& par : sistema.obtenerRutas()) {
                const RutaTramo& r = par.second;
                std::string corr = sistema.nombreCiudad(r.idOrigen) + " <-> " + sistema.nombreCiudad(r.idDestino);
                if (corr.size() > 32) corr = corr.substr(0, 30) + "..";
                std::cout << std::left << std::setw(5) << r.idRuta
                          << std::setw(34) << corr
                          << std::setw(9) << std::fixed << std::setprecision(1) << r.distanciaKm
                          << std::setw(8) << r.tiempoHoras
                          << std::setw(16) << Consola::formatoCOP(r.costoCombustibleCOP)
                          << std::setw(16) << Consola::formatoCOP(r.costoPeajesCOP)
                          << std::setw(13) << r.categoriaVia
                          << (r.validado ? "SI/" : "NO/") << (r.activa ? "ACT" : "INA") << "\n";
            }
            std::cout << "\n  1) Ingresar ruta   2) Modificar ruta/peajes   3) Desactivar/Reactivar (Cierre vial)   4) Eliminar   0) Volver\n";
            std::string op = Consola::leerLinea("Opcion: ");

            if (op == "1") {
                listarCiudadesCompacto();
                RutaTramo r;
                r.idRuta = sistema.siguienteIdRuta();
                if (!Consola::leerEntero("ID ciudad origen : ", r.idOrigen) ||
                    !Consola::leerEntero("ID ciudad destino: ", r.idDestino) ||
                    !Consola::leerDecimal("Distancia (km): ", r.distanciaKm) ||
                    !Consola::leerDecimal("Tiempo estimado (horas): ", r.tiempoHoras) ||
                    !Consola::leerDecimal("Costo combustible (COP): ", r.costoCombustibleCOP) ||
                    !Consola::leerEntero("Cantidad de peajes: ", r.cantidadPeajes) ||
                    !Consola::leerDecimal("Costo total peajes (COP): ", r.costoPeajesCOP)) {
                    std::cout << "Datos numericos invalidos.\n";
                } else {
                    r.categoriaVia = Consola::leerLinea("Categoria vial (Concesion 4G / Primaria / Secundaria): ");
                    if (r.categoriaVia.empty()) r.categoriaVia = "Primaria";
                    r.validado = (Consola::leerLinea("Tramo validado? (1=Si, 0=No): ") != "0");
                    r.activa = true;
                    std::cout << (sistema.agregarRuta(r) ? "Ruta agregada con ID " + std::to_string(r.idRuta) + ".\n"
                                                         : "Error: verifique que las ciudades existan y sean distintas.\n");
                }
                Consola::pausar();
            } else if (op == "2") {
                int idR = 0;
                if (!Consola::leerEntero("ID de ruta a modificar: ", idR) ||
                    sistema.obtenerRutas().find(idR) == sistema.obtenerRutas().end()) {
                    std::cout << "Ruta no encontrada.\n";
                    Consola::pausar();
                    continue;
                }
                RutaTramo r = sistema.obtenerRutas().at(idR);
                double d = 0.0;
                int ent = 0;
                if (Consola::leerDecimal("Nueva distancia km (ENTER mantener " + std::to_string(static_cast<int>(r.distanciaKm)) + "): ", d)) r.distanciaKm = d;
                if (Consola::leerDecimal("Nuevo tiempo horas (ENTER mantener): ", d)) r.tiempoHoras = d;
                if (Consola::leerDecimal("Nuevo combustible COP (ENTER mantener): ", d)) r.costoCombustibleCOP = d;
                if (Consola::leerEntero("Nueva cantidad peajes (ENTER mantener): ", ent)) r.cantidadPeajes = ent;
                if (Consola::leerDecimal("Nuevo costo peajes COP (ENTER mantener): ", d)) r.costoPeajesCOP = d;
                std::string s = Consola::leerLinea("Nueva categoria (ENTER mantener '" + r.categoriaVia + "'): ");
                if (!s.empty()) r.categoriaVia = s;
                s = Consola::leerLinea("Validado? 1=Si / 0=No (ENTER mantener): ");
                if (s == "1" || s == "0") r.validado = (s == "1");
                sistema.modificarRuta(idR, r);
                std::cout << "Ruta actualizada y los 3 grafos fueron sincronizados.\n";
                Consola::pausar();
            } else if (op == "3") {
                int idR = 0;
                if (Consola::leerEntero("ID de ruta para activar/desactivar (simular cierre vial): ", idR) &&
                    sistema.obtenerRutas().find(idR) != sistema.obtenerRutas().end()) {
                    bool nuevo = !sistema.obtenerRutas().at(idR).activa;
                    sistema.cambiarEstadoRuta(idR, nuevo);
                    std::cout << "Ruta " << idR << " marcada como " << (nuevo ? "ACTIVA.\n" : "DESACTIVADA (cerrada).\n");
                } else {
                    std::cout << "Ruta no encontrada.\n";
                }
                Consola::pausar();
            } else if (op == "4") {
                int idR = 0;
                if (Consola::leerEntero("ID de ruta a eliminar: ", idR) && sistema.eliminarRuta(idR)) {
                    std::cout << "Ruta eliminada de los 3 grafos.\n";
                } else {
                    std::cout << "Ruta no encontrada.\n";
                }
                Consola::pausar();
            } else if (op == "0") {
                volver = true;
            }
        }
    }

    void menuEntidadesInvestigacion() {
        bool volver = false;
        while (!volver) {
            mostrarEncabezado("GESTION DE GRUPOS, INVESTIGADORES Y PRODUCTOS TECNICOS VIALES");
            std::cout << "[GRUPOS E INVESTIGADORES]\n";
            std::cout << std::left << std::setw(5) << "ID" << std::setw(32) << "GRUPO"
                      << std::setw(22) << "REGION" << std::setw(26) << "INVESTIGADOR LIDER" << "ESTADO\n";
            std::cout << "--------------------------------------------------------------------------------------------------------------\n";
            for (const auto& par : sistema.obtenerGrupos()) {
                const GrupoInvestigacion& g = par.second;
                std::cout << std::left << std::setw(5) << g.idGrupo << std::setw(32) << g.nombreGrupo
                          << std::setw(22) << g.region << std::setw(26) << g.investigadorLider
                          << (g.activo ? "ACTIVO" : "DESACTIVADO") << "\n";
            }

            std::cout << "\n[PRODUCTOS TECNICOS (CATEGORIA Y VALIDACION)]\n";
            std::cout << std::left << std::setw(5) << "ID" << std::setw(8) << "GRUPO"
                      << std::setw(40) << "NOMBRE DEL PRODUCTO" << std::setw(24) << "CATEGORIA"
                      << std::setw(12) << "VALIDADO" << "ESTADO\n";
            std::cout << "--------------------------------------------------------------------------------------------------------------\n";
            for (const auto& par : sistema.obtenerProductos()) {
                const ProductoTecnico& pr = par.second;
                std::cout << std::left << std::setw(5) << pr.idProducto << std::setw(8) << pr.idGrupo
                          << std::setw(40) << pr.nombreProducto << std::setw(24) << pr.categoria
                          << std::setw(12) << (pr.validado ? "VALIDADO" : "PENDIENTE")
                          << (pr.activo ? "ACTIVO" : "DESACTIVADO") << "\n";
            }

            std::cout << "\n  GRUPOS   : 1) Ingresar   2) Modificar   3) Desactivar/Reactivar   4) Eliminar\n";
            std::cout << "  PRODUCTOS: 5) Ingresar   6) Modificar   7) Desactivar/Reactivar   8) Eliminar   0) Volver\n";
            std::string op = Consola::leerLinea("Opcion: ");

            if (op == "1") {
                GrupoInvestigacion g;
                g.idGrupo = sistema.siguienteIdGrupo();
                g.nombreGrupo = Consola::leerLinea("Nombre del grupo: ");
                g.region = Consola::leerLinea("Region de cobertura: ");
                g.investigadorLider = Consola::leerLinea("Nombre del investigador lider: ");
                g.activo = true;
                sistema.agregarGrupo(g);
                std::cout << "Grupo creado con ID " << g.idGrupo << ".\n";
                Consola::pausar();
            } else if (op == "2") {
                int id = 0;
                if (Consola::leerEntero("ID de grupo a modificar: ", id) &&
                    sistema.obtenerGrupos().find(id) != sistema.obtenerGrupos().end()) {
                    GrupoInvestigacion g = sistema.obtenerGrupos().at(id);
                    std::string s = Consola::leerLinea("Nuevo nombre (ENTER mantener): ");
                    if (!s.empty()) g.nombreGrupo = s;
                    s = Consola::leerLinea("Nueva region (ENTER mantener): ");
                    if (!s.empty()) g.region = s;
                    s = Consola::leerLinea("Nuevo investigador lider (ENTER mantener): ");
                    if (!s.empty()) g.investigadorLider = s;
                    sistema.modificarGrupo(id, g);
                    std::cout << "Grupo actualizado.\n";
                } else {
                    std::cout << "Grupo no encontrado.\n";
                }
                Consola::pausar();
            } else if (op == "3") {
                int id = 0;
                if (Consola::leerEntero("ID de grupo: ", id) &&
                    sistema.obtenerGrupos().find(id) != sistema.obtenerGrupos().end()) {
                    bool nuevo = !sistema.obtenerGrupos().at(id).activo;
                    sistema.cambiarEstadoGrupo(id, nuevo);
                    std::cout << "Estado actualizado.\n";
                }
                Consola::pausar();
            } else if (op == "4") {
                int id = 0;
                if (Consola::leerEntero("ID de grupo a eliminar: ", id) && sistema.eliminarGrupo(id)) {
                    std::cout << "Grupo eliminado.\n";
                }
                Consola::pausar();
            } else if (op == "5") {
                ProductoTecnico pr;
                pr.idProducto = sistema.siguienteIdProducto();
                if (!Consola::leerEntero("ID de grupo responsable: ", pr.idGrupo) ||
                    sistema.obtenerGrupos().find(pr.idGrupo) == sistema.obtenerGrupos().end()) {
                    std::cout << "Grupo inexistente.\n";
                } else {
                    pr.nombreProducto = Consola::leerLinea("Nombre del producto: ");
                    pr.categoria = Consola::leerLinea("Categoria: ");
                    pr.validado = (Consola::leerLinea("Validado? (1=Si, 0=No): ") != "0");
                    pr.activo = true;
                    sistema.agregarProducto(pr);
                    std::cout << "Producto agregado con ID " << pr.idProducto << ".\n";
                }
                Consola::pausar();
            } else if (op == "6") {
                int id = 0;
                if (Consola::leerEntero("ID de producto a modificar: ", id) &&
                    sistema.obtenerProductos().find(id) != sistema.obtenerProductos().end()) {
                    ProductoTecnico pr = sistema.obtenerProductos().at(id);
                    std::string s = Consola::leerLinea("Nuevo nombre (ENTER mantener): ");
                    if (!s.empty()) pr.nombreProducto = s;
                    s = Consola::leerLinea("Nueva categoria (ENTER mantener): ");
                    if (!s.empty()) pr.categoria = s;
                    s = Consola::leerLinea("Validado? 1=Si / 0=No (ENTER mantener): ");
                    if (s == "1" || s == "0") pr.validado = (s == "1");
                    sistema.modificarProducto(id, pr);
                    std::cout << "Producto actualizado.\n";
                } else {
                    std::cout << "Producto no encontrado.\n";
                }
                Consola::pausar();
            } else if (op == "7") {
                int id = 0;
                if (Consola::leerEntero("ID de producto: ", id) &&
                    sistema.obtenerProductos().find(id) != sistema.obtenerProductos().end()) {
                    bool nuevo = !sistema.obtenerProductos().at(id).activo;
                    sistema.cambiarEstadoProducto(id, nuevo);
                    std::cout << "Estado del producto actualizado.\n";
                }
                Consola::pausar();
            } else if (op == "8") {
                int id = 0;
                if (Consola::leerEntero("ID de producto a eliminar: ", id) && sistema.eliminarProducto(id)) {
                    std::cout << "Producto eliminado.\n";
                }
                Consola::pausar();
            } else if (op == "0") {
                volver = true;
            }
        }
    }

    void mostrarResumenEstadistico() const {
        mostrarEncabezado("RESUMEN ESTADISTICO DESCRIPTIVO - RED VIAL DE COLOMBIA (PERA)");
        ResumenEstadisticoPERA st = sistema.calcularEstadisticas();

        std::cout << "  Capitales totales     : " << st.totalCiudades
                  << " (Activas: " << st.ciudadesActivas
                  << " | Conectadas: " << (st.ciudadesActivas - st.ciudadesAisladas)
                  << " | Aisladas terrestres: " << st.ciudadesAisladas << ")\n";
        std::cout << "  Corredores viales     : " << st.totalRutas
                  << " (Activos en grafos: " << st.rutasActivas << ")\n";
        std::cout << "  Grupos / Productos    : " << st.totalGrupos << " grupos | "
                  << st.totalProductos << " productos (" << st.productosValidados << " validados)\n\n";

        auto filaStat = [](const std::string& nom, const EstadisticaVariable& v, bool esCOP) {
            auto fmt = [esCOP](double x) -> std::string {
                if (esCOP) return Consola::formatoCOP(x);
                std::ostringstream o;
                o << std::fixed << std::setprecision(1) << x;
                return o.str();
            };
            std::cout << "  " << std::left << std::setw(18) << nom
                      << std::setw(15) << fmt(v.media)
                      << std::setw(15) << fmt(v.mediana)
                      << std::setw(15) << fmt(v.desvEstandar)
                      << std::setw(15) << fmt(v.minimo)
                      << std::setw(15) << fmt(v.maximo)
                      << fmt(v.suma) << "\n";
        };

        std::cout << "  " << std::left << std::setw(18) << "VARIABLE"
                  << std::setw(15) << "MEDIA"
                  << std::setw(15) << "MEDIANA"
                  << std::setw(15) << "DESV.EST."
                  << std::setw(15) << "MINIMO"
                  << std::setw(15) << "MAXIMO"
                  << "SUMA TOTAL\n";
        std::cout << "  ----------------------------------------------------------------------------------------------------------\n";
        filaStat("Distancia (km)", st.distKm, false);
        filaStat("Tiempo (horas)", st.tiempoHoras, false);
        filaStat("Combustible", st.combustibleCOP, true);
        filaStat("Peajes", st.peajesCOP, true);

        std::cout << "\n  [TOP 5 CAPITALES CON MAYOR CONECTIVIDAD (GRADO DEL VERTICE)]\n";
        for (const auto& hub : st.topHubs) {
            std::cout << "    - " << std::left << std::setw(24) << sistema.nombreCiudad(hub.first)
                      << ": " << hub.second << " corredores directos\n";
        }

        std::cout << "\n  [TOP 5 CORREDORES CON MAYOR COSTO EN PEAJES]\n";
        const auto& rMap = sistema.obtenerRutas();
        for (const auto& par : st.topRutasPeajes) {
            const RutaTramo& r = rMap.at(par.first);
            std::cout << "    - " << sistema.nombreCiudad(r.idOrigen) << " <-> "
                      << sistema.nombreCiudad(r.idDestino) << " (" << r.cantidadPeajes
                      << " peajes): " << Consola::formatoCOP(r.costoPeajesCOP) << "\n";
        }

        std::cout << "\n  [CAPITALES SIN CONEXION TERRESTRE INTEGRADA (GRADO 0)]\n    ";
        if (st.listaAisladas.empty()) {
            std::cout << "(Ninguna)";
        } else {
            for (std::size_t i = 0; i < st.listaAisladas.size(); ++i) {
                if (i > 0) std::cout << ", ";
                std::cout << sistema.nombreCiudad(st.listaAisladas[i]);
            }
        }
        std::cout << "\n";
        Consola::pausar();
    }

    void inspeccionarTresGrafos() const {
        mostrarEncabezado("INSPECCION DE LOS 3 GRAFOS PONDERADOS (LISTAS DE ADYACENCIA)");
        listarCiudadesCompacto();
        int id = 0;
        if (!Consola::leerEntero("\nIngrese ID de capital a inspeccionar en los 3 grafos: ", id) ||
            sistema.obtenerCiudades().find(id) == sistema.obtenerCiudades().end()) {
            std::cout << "Capital no encontrada.\n";
            Consola::pausar();
            return;
        }

        std::cout << "\nCapital seleccionada: " << sistema.nombreCiudad(id) << "\n";
        auto mostrarGrafo = [&](const GrafoPonderado& g, bool esCOP) {
            std::cout << "\n  [" << g.obtenerMetrica() << " (" << g.obtenerUnidad() << ")]\n";
            const auto& adj = g.obtenerAdyacencia();
            auto it = adj.find(id);
            if (it == adj.end() || it->second.empty()) {
                std::cout << "    (Sin aristas activas - vertice aislado o desactivado)\n";
                return;
            }
            for (const AristaPonderada& a : it->second) {
                std::cout << "    --> " << std::left << std::setw(24) << sistema.nombreCiudad(a.destino)
                          << " | Peso: " << (esCOP ? Consola::formatoCOP(a.peso)
                                                   : (std::to_string(static_cast<int>(a.peso)) + " km"))
                          << " (Ruta #" << a.idRuta << ")\n";
            }
        };

        mostrarGrafo(sistema.obtenerGrafoDistancia(), false);
        mostrarGrafo(sistema.obtenerGrafoCombustible(), true);
        mostrarGrafo(sistema.obtenerGrafoPeajes(), true);
        Consola::pausar();
    }

    bool autenticarUsuario() const {
        const std::string usuarioValido = "admin";
        const std::string claveValida = "pera2026";

        auto contieneEspacio = [](const std::string& s) {
            for (char ch : s) {
                if (ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n') return true;
            }
            return false;
        };

        int intentos = 3;
        while (intentos > 0) {
            mostrarEncabezado("CONTROL DE ACCESO - SISTEMA PERA (Intentos restantes: " + std::to_string(intentos) + ")");
            std::cout << "  Credenciales predeterminadas: (Usuario: admin | Contrasena: pera2026)\n";
            std::cout << "  No se permiten campos vacios ni espacios en blanco.\n\n";
            std::string usr, pwd;
            std::cout << "  Usuario    : ";
            std::getline(std::cin, usr);
            if (!usr.empty() && usr.back() == '\r') usr.pop_back();
            std::cout << "  Contrasena : ";
            std::getline(std::cin, pwd);
            if (!pwd.empty() && pwd.back() == '\r') pwd.pop_back();

            if (usr.empty() || pwd.empty() || contieneEspacio(usr) || contieneEspacio(pwd)) {
                std::cout << "\n  [DENEGADO] No se permiten entradas vacias ni espacios en blanco.\n";
                Consola::pausar();
                continue;
            }
            if (usr == usuarioValido && pwd == claveValida) {
                std::cout << "\n  [OK] Acceso concedido. Bienvenido al sistema PERA.\n";
                Consola::pausar();
                return true;
            }
            --intentos;
            std::cout << "\n  [DENEGADO] Credenciales incorrectas.\n";
            Consola::pausar();
        }
        std::cout << "\n  Se agotaron los 3 intentos de acceso. El programa se cerrara.\n";
        Consola::pausar();
        return false;
    }

    void mostrarInicioPersistencia() {
        mostrarEncabezado("INICIALIZACION DE PERSISTENCIA");
        std::cout << "  1) Cargar datos reales de Colombia desde '" << archivoDatos << "'\n";
        std::cout << "  2) Ejecutar programa sin datos (grafos vacios)\n\n";
        std::string op = Consola::leerLinea("Seleccione opcion [1-2]: ");
        if (op == "1") {
            if (PersistenciaPERA::cargarArchivo(sistema, archivoDatos)) {
                std::cout << "\nCargados " << sistema.obtenerCiudades().size() << " capitales y "
                          << sistema.obtenerRutas().size() << " corredores en los 3 grafos.\n";
            } else {
                std::cout << "\nNo se encontro '" << archivoDatos << "'. Se inicio sin datos.\n";
            }
        } else {
            sistema.limpiarTodo();
            std::cout << "\nSistema iniciado vacio.\n";
        }
        Consola::pausar();
    }

public:
    explicit InterfazPERA(SistemaPERA& s) : sistema(s) {}

    void ejecutar() {
        if (!autenticarUsuario()) return;
        mostrarInicioPersistencia();
        bool ejecutando = true;

        while (ejecutando) {
            mostrarEncabezado("MENU PRINCIPAL | Capitales: " +
                              std::to_string(sistema.obtenerCiudades().size()) +
                              " | Corredores: " + std::to_string(sistema.obtenerRutas().size()) +
                              " | 3 Grafos Sincronizados: Distancia, Combustible, Peajes");
            std::cout << "  1) Calcular costos entre 2 ciudades (Tiempo, Distancia, Combustible, Peajes)\n";
            std::cout << "  2) Gestionar Ciudades / Capitales (CRUD + Desactivar)\n";
            std::cout << "  3) Gestionar Rutas y Peajes (CRUD + Cierre Vial + Validacion)\n";
            std::cout << "  4) Gestionar Grupos, Investigadores y Productos Tecnicos\n";
            std::cout << "  5) Ver Resumen Estadistico Descriptivo\n";
            std::cout << "  6) Inspeccionar Listas de Adyacencia de los 3 Grafos\n";
            std::cout << "  7) Recargar archivo de persistencia ('" << archivoDatos << "')\n";
            std::cout << "  8) Guardar cambios en persistencia ('" << archivoDatos << "')\n";
            std::cout << "  0) Salir del programa\n\n";

            std::string op = Consola::leerLinea("Seleccione una opcion [0-8]: ");
            if (op == "1") {
                menuCalcularRuta();
            } else if (op == "2") {
                menuGestionCiudades();
            } else if (op == "3") {
                menuGestionRutas();
            } else if (op == "4") {
                menuEntidadesInvestigacion();
            } else if (op == "5") {
                mostrarResumenEstadistico();
            } else if (op == "6") {
                inspeccionarTresGrafos();
            } else if (op == "7") {
                if (PersistenciaPERA::cargarArchivo(sistema, archivoDatos)) {
                    std::cout << "Persistencia recargada exitosamente.\n";
                } else {
                    std::cout << "No se pudo abrir '" << archivoDatos << "'.\n";
                }
                Consola::pausar();
            } else if (op == "8") {
                if (PersistenciaPERA::guardarArchivo(sistema, archivoDatos)) {
                    std::cout << "Datos guardados correctamente en '" << archivoDatos << "'.\n";
                } else {
                    std::cout << "Error al guardar '" << archivoDatos << "'.\n";
                }
                Consola::pausar();
            } else if (op == "0") {
                std::string g = Consola::leerLinea("Desea guardar cambios en '" + archivoDatos + "' antes de salir? (s/n): ");
                if (g == "s" || g == "S") {
                    PersistenciaPERA::guardarArchivo(sistema, archivoDatos);
                }
                ejecutando = false;
            }
        }

        Consola::limpiarPantalla();
        std::cout << "Sesion PERA finalizada. Presione ENTER para cerrar...\n";
        Consola::leerLinea("");
    }
};

// ============================================================================
// PUNTO DE ENTRADA PRINCIPAL
// ============================================================================
int main() {
    Consola::inicializar();
    SistemaPERA pera;
    InterfazPERA interfaz(pera);
    interfaz.ejecutar();
    return 0;
}
