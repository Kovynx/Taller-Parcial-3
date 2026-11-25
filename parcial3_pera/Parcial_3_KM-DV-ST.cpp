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

int main() {
    Consola::inicializar();
    SistemaPERA pera;
    if (PersistenciaPERA::cargarArchivo(pera, "datos_pera.txt")) {
        for (int c = 1; c <= 4; ++c) {
            auto r = pera.calcularRutaOptima(16, 1, c);
            std::cout << r.criterio << " -> Dist: " << r.distanciaTotalKm
                      << " km | Tiempo: " << Consola::formatoHoras(r.tiempoTotalHoras)
                      << " | Comb: " << Consola::formatoCOP(r.combustibleTotalCOP)
                      << " | Peajes (" << r.totalPeajes << "): " << Consola::formatoCOP(r.peajesTotalCOP) << "\n";
        }
        auto iso = pera.calcularRutaOptima(16, 28, 1);
        std::cout << "Valledupar -> San Andres: " << iso.mensaje << "\n";
        auto st = pera.calcularEstadisticas();
        std::cout << "Stats OK: activas=" << st.ciudadesActivas << ", aisladas=" << st.ciudadesAisladas
                  << ", mediaDist=" << st.distKm.media << " km\n";
    }
    return 0;
}
