"""
Universidad Popular del Cesar - Facultad de Ingenierias y Tecnologicas
Ingenieria de Sistemas - Estructura de Datos (Parcial 3)
Programa Estadistico de Rutas de Automoviles (PERA - Colombia) en Python 3
Autores: Kovyn Been Mena Orcasita, Damian Jose Velasquez Gonzalez,
         Sofia Isabel Tovar Rodriguez (KM-DV-ST)
"""

from __future__ import annotations

from dataclasses import dataclass, field
import heapq
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

try:
    import folium
    FOLIUM_DISPONIBLE = True
except ImportError:
    FOLIUM_DISPONIBLE = False


# ============================================================================
# UTILIDADES DE FORMATO
# ============================================================================
def formato_cop(valor: float) -> str:
    return f"${int(round(valor)):,} COP"


def formato_horas(horas: float) -> str:
    h = int(horas)
    m = int(round((horas - h) * 60.0))
    if m == 60:
        h += 1
        m = 0
    return f"{h}h {m:02d}m"


# ============================================================================
# CAPA 1: MODELO DE DATOS (CIUDADES, RUTAS/PEAJES, GRUPOS Y PRODUCTOS)
# ============================================================================
@dataclass
class Ciudad:
    id: int
    nombre: str
    departamento: str
    latitud: float
    longitud: float
    activa: bool = True


@dataclass
class RutaTramo:
    id_ruta: int
    id_origen: int
    id_destino: int
    distancia_km: float
    tiempo_horas: float
    costo_combustible_cop: float
    cantidad_peajes: int
    costo_peajes_cop: float
    categoria_via: str = "Primaria"
    validado: bool = True
    activa: bool = True


@dataclass
class GrupoInvestigacion:
    id_grupo: int
    nombre_grupo: str
    region: str
    investigador_lider: str
    activo: bool = True


@dataclass
class ProductoTecnico:
    id_producto: int
    id_grupo: int
    nombre_producto: str
    categoria: str
    validado: bool = True
    activo: bool = True


@dataclass
class AristaPonderada:
    destino: int
    id_ruta: int
    peso: float


@dataclass
class ResultadoRuta:
    encontrada: bool = False
    criterio: str = ""
    mensaje: str = ""
    camino_ciudades: List[int] = field(default_factory=list)
    rutas_usadas: List[int] = field(default_factory=list)
    distancia_total_km: float = 0.0
    tiempo_total_horas: float = 0.0
    combustible_total_cop: float = 0.0
    total_peajes: int = 0
    peajes_total_cop: float = 0.0
    costo_total_cop: float = 0.0


@dataclass
class EstadisticaVariable:
    n: int = 0
    suma: float = 0.0
    media: float = 0.0
    mediana: float = 0.0
    desv_estandar: float = 0.0
    minimo: float = 0.0
    maximo: float = 0.0


@dataclass
class ResumenEstadisticoPERA:
    total_ciudades: int = 0
    ciudades_activas: int = 0
    ciudades_aisladas: int = 0
    total_rutas: int = 0
    rutas_activas: int = 0
    total_grupos: int = 0
    total_productos: int = 0
    productos_validados: int = 0
    dist_km: EstadisticaVariable = field(default_factory=EstadisticaVariable)
    tiempo_horas: EstadisticaVariable = field(default_factory=EstadisticaVariable)
    combustible_cop: EstadisticaVariable = field(default_factory=EstadisticaVariable)
    peajes_cop: EstadisticaVariable = field(default_factory=EstadisticaVariable)
    top_hubs: List[Tuple[int, int]] = field(default_factory=list)
    top_rutas_peajes: List[Tuple[int, float]] = field(default_factory=list)
    lista_aisladas: List[int] = field(default_factory=list)


# ============================================================================
# CAPA 2: MOTOR DE 3 GRAFOS PONDERADOS Y DIJKSTRA O((V + E) log V)
# ============================================================================
class GrafoPonderado:
    def __init__(self, metrica: str, unidad: str) -> None:
        self.metrica = metrica
        self.unidad = unidad
        self.adyacencia: Dict[int, List[AristaPonderada]] = {}

    def limpiar(self) -> None:
        self.adyacencia.clear()

    def agregar_vertice(self, id_ciudad: int) -> None:
        if id_ciudad not in self.adyacencia:
            self.adyacencia[id_ciudad] = []

    def agregar_arista_no_dirigida(self, u: int, v: int, id_ruta: int, peso: float) -> None:
        self.adyacencia[u].append(AristaPonderada(v, id_ruta, peso))
        self.adyacencia[v].append(AristaPonderada(u, id_ruta, peso))

    def grado(self, id_ciudad: int) -> int:
        return len(self.adyacencia.get(id_ciudad, []))


class SistemaPERA:
    def __init__(self) -> None:
        self.ciudades: Dict[int, Ciudad] = {}
        self.rutas: Dict[int, RutaTramo] = {}
        self.grupos: Dict[int, GrupoInvestigacion] = {}
        self.productos: Dict[int, ProductoTecnico] = {}

        # Tres grafos ponderados independientes y sincronizados
        self.grafo_distancia = GrafoPonderado("Distancia", "km")
        self.grafo_combustible = GrafoPonderado("Combustible", "COP")
        self.grafo_peajes = GrafoPonderado("Peajes", "COP")

    def limpiar_todo(self) -> None:
        self.ciudades.clear()
        self.rutas.clear()
        self.grupos.clear()
        self.productos.clear()
        self.reconstruir_grafos()

    def reconstruir_grafos(self) -> None:
        self.grafo_distancia.limpiar()
        self.grafo_combustible.limpiar()
        self.grafo_peajes.limpiar()

        for cid, ciudad in self.ciudades.items():
            if ciudad.activa:
                self.grafo_distancia.agregar_vertice(cid)
                self.grafo_combustible.agregar_vertice(cid)
                self.grafo_peajes.agregar_vertice(cid)

        for ruta in self.rutas.values():
            if not ruta.activa:
                continue
            c_orig = self.ciudades.get(ruta.id_origen)
            c_dest = self.ciudades.get(ruta.id_destino)
            if not c_orig or not c_dest or not c_orig.activa or not c_dest.activa:
                continue
            self.grafo_distancia.agregar_arista_no_dirigida(
                ruta.id_origen, ruta.id_destino, ruta.id_ruta, ruta.distancia_km
            )
            self.grafo_combustible.agregar_arista_no_dirigida(
                ruta.id_origen, ruta.id_destino, ruta.id_ruta, ruta.costo_combustible_cop
            )
            self.grafo_peajes.agregar_arista_no_dirigida(
                ruta.id_origen, ruta.id_destino, ruta.id_ruta, ruta.costo_peajes_cop
            )

    def nombre_ciudad(self, cid: int) -> str:
        c = self.ciudades.get(cid)
        return c.nombre if c else f"ID_{cid}"

    def siguiente_id_ciudad(self) -> int:
        return (max(self.ciudades.keys()) + 1) if self.ciudades else 1

    def siguiente_id_ruta(self) -> int:
        return (max(self.rutas.keys()) + 1) if self.rutas else 1

    def siguiente_id_grupo(self) -> int:
        return (max(self.grupos.keys()) + 1) if self.grupos else 1

    def siguiente_id_producto(self) -> int:
        return (max(self.productos.keys()) + 1) if self.productos else 1

    # ---- CRUD Ciudades ----
    def agregar_ciudad(self, c: Ciudad) -> bool:
        if c.id in self.ciudades:
            return False
        self.ciudades[c.id] = c
        self.reconstruir_grafos()
        return True

    def modificar_ciudad(self, cid: int, nueva: Ciudad) -> bool:
        if cid not in self.ciudades:
            return False
        nueva.id = cid
        self.ciudades[cid] = nueva
        self.reconstruir_grafos()
        return True

    def cambiar_estado_ciudad(self, cid: int, activa: bool) -> bool:
        if cid not in self.ciudades:
            return False
        self.ciudades[cid].activa = activa
        self.reconstruir_grafos()
        return True

    def eliminar_ciudad(self, cid: int) -> bool:
        if cid not in self.ciudades:
            return False
        del self.ciudades[cid]
        rutas_borrar = [
            rid for rid, r in self.rutas.items() if r.id_origen == cid or r.id_destino == cid
        ]
        for rid in rutas_borrar:
            del self.rutas[rid]
        self.reconstruir_grafos()
        return True

    # ---- CRUD Rutas y Peajes ----
    def agregar_ruta(self, r: RutaTramo) -> bool:
        if r.id_ruta in self.rutas or r.id_origen == r.id_destino:
            return False
        if r.id_origen not in self.ciudades or r.id_destino not in self.ciudades:
            return False
        self.rutas[r.id_ruta] = r
        self.reconstruir_grafos()
        return True

    def modificar_ruta(self, rid: int, nueva: RutaTramo) -> bool:
        if rid not in self.rutas or nueva.id_origen == nueva.id_destino:
            return False
        if nueva.id_origen not in self.ciudades or nueva.id_destino not in self.ciudades:
            return False
        nueva.id_ruta = rid
        self.rutas[rid] = nueva
        self.reconstruir_grafos()
        return True

    def cambiar_estado_ruta(self, rid: int, activa: bool) -> bool:
        if rid not in self.rutas:
            return False
        self.rutas[rid].activa = activa
        self.reconstruir_grafos()
        return True

    def eliminar_ruta(self, rid: int) -> bool:
        if rid not in self.rutas:
            return False
        del self.rutas[rid]
        self.reconstruir_grafos()
        return True

    # ---- CRUD Grupos e Investigadores ----
    def agregar_grupo(self, g: GrupoInvestigacion) -> bool:
        if g.id_grupo in self.grupos:
            return False
        self.grupos[g.id_grupo] = g
        return True

    def modificar_grupo(self, gid: int, nuevo: GrupoInvestigacion) -> bool:
        if gid not in self.grupos:
            return False
        nuevo.id_grupo = gid
        self.grupos[gid] = nuevo
        return True

    def cambiar_estado_grupo(self, gid: int, activo: bool) -> bool:
        if gid not in self.grupos:
            return False
        self.grupos[gid].activo = activo
        return True

    def eliminar_grupo(self, gid: int) -> bool:
        if gid not in self.grupos:
            return False
        del self.grupos[gid]
        prods_borrar = [pid for pid, pr in self.productos.items() if pr.id_grupo == gid]
        for pid in prods_borrar:
            del self.productos[pid]
        return True

    # ---- CRUD Productos Tecnicos ----
    def agregar_producto(self, pr: ProductoTecnico) -> bool:
        if pr.id_producto in self.productos or pr.id_grupo not in self.grupos:
            return False
        self.productos[pr.id_producto] = pr
        return True

    def modificar_producto(self, pid: int, nuevo: ProductoTecnico) -> bool:
        if pid not in self.productos or nuevo.id_grupo not in self.grupos:
            return False
        nuevo.id_producto = pid
        self.productos[pid] = nuevo
        return True

    def cambiar_estado_producto(self, pid: int, activo: bool) -> bool:
        if pid not in self.productos:
            return False
        self.productos[pid].activo = activo
        return True

    def eliminar_producto(self, pid: int) -> bool:
        if pid not in self.productos:
            return False
        del self.productos[pid]
        return True

    # ---- Dijkstra O((V + E) log V) ----
    def calcular_ruta_optima(self, id_origen: int, id_destino: int, criterio: int) -> ResultadoRuta:
        res = ResultadoRuta()
        nombres_crit = {
            1: "Menor Distancia (Grafo 1 - km)",
            2: "Menor Combustible (Grafo 2 - COP)",
            3: "Menor Peajes (Grafo 3 - COP)",
            4: "Menor Costo Total (Combustible + Peajes)",
        }
        res.criterio = nombres_crit.get(criterio, nombres_crit[4])

        c_orig = self.ciudades.get(id_origen)
        c_dest = self.ciudades.get(id_destino)
        if not c_orig or not c_dest:
            res.mensaje = "Una o ambas ciudades no existen en el sistema."
            return res
        if not c_orig.activa or not c_dest.activa:
            res.mensaje = "Origen o destino se encuentra DESACTIVADO."
            return res
        if id_origen == id_destino:
            res.encontrada = True
            res.camino_ciudades = [id_origen]
            res.mensaje = "Origen y destino corresponden a la misma capital."
            return res

        grafo_base = self.grafo_distancia
        if criterio == 2:
            grafo_base = self.grafo_combustible
        elif criterio == 3:
            grafo_base = self.grafo_peajes

        dist: Dict[int, float] = {cid: math.inf for cid in grafo_base.adyacencia}
        padre_ciudad: Dict[int, int] = {}
        padre_ruta: Dict[int, int] = {}
        dist[id_origen] = 0.0
        pq: List[Tuple[float, int]] = [(0.0, id_origen)]

        while pq:
            d_act, u = heapq.heappop(pq)
            if d_act > dist.get(u, math.inf):
                continue
            if u == id_destino:
                break
            for arista in grafo_base.adyacencia.get(u, []):
                peso = arista.peso
                if criterio == 4:
                    tr = self.rutas[arista.id_ruta]
                    peso = tr.costo_combustible_cop + tr.costo_peajes_cop
                nuevo = d_act + peso
                if nuevo < dist.get(arista.destino, math.inf):
                    dist[arista.destino] = nuevo
                    padre_ciudad[arista.destino] = u
                    padre_ruta[arista.destino] = arista.id_ruta
                    heapq.heappush(pq, (nuevo, arista.destino))

        if not math.isfinite(dist.get(id_destino, math.inf)):
            res.encontrada = False
            res.mensaje = (
                f"No existe ruta terrestre activa entre {c_orig.nombre} y {c_dest.nombre} "
                "(componente desconectada o cierres viales)."
            )
            return res

        actual = id_destino
        while actual != id_origen:
            res.camino_ciudades.append(actual)
            rid = padre_ruta[actual]
            res.rutas_usadas.append(rid)
            tramo = self.rutas[rid]
            res.distancia_total_km += tramo.distancia_km
            res.tiempo_total_horas += tramo.tiempo_horas
            res.combustible_total_cop += tramo.costo_combustible_cop
            res.total_peajes += tramo.cantidad_peajes
            res.peajes_total_cop += tramo.costo_peajes_cop
            actual = padre_ciudad[actual]
        res.camino_ciudades.append(id_origen)
        res.camino_ciudades.reverse()
        res.rutas_usadas.reverse()

        res.costo_total_cop = res.combustible_total_cop + res.peajes_total_cop
        res.encontrada = True
        res.mensaje = "Ruta optima calculada satisfactoriamente."
        return res

    @staticmethod
    def _resumir_valores(vals: List[float]) -> EstadisticaVariable:
        if not vals:
            return EstadisticaVariable()
        ordenados = sorted(vals)
        n = len(ordenados)
        suma = sum(ordenados)
        media = suma / n
        mediana = (
            ordenados[n // 2]
            if n % 2 == 1
            else 0.5 * (ordenados[n // 2 - 1] + ordenados[n // 2])
        )
        desv = math.sqrt(sum((v - media) ** 2 for v in ordenados) / n)
        return EstadisticaVariable(
            n=n,
            suma=suma,
            media=media,
            mediana=mediana,
            desv_estandar=desv,
            minimo=ordenados[0],
            maximo=ordenados[-1],
        )

    def calcular_estadisticas(self) -> ResumenEstadisticoPERA:
        st = ResumenEstadisticoPERA(
            total_ciudades=len(self.ciudades),
            total_rutas=len(self.rutas),
            total_grupos=len(self.grupos),
            total_productos=len(self.productos),
            productos_validados=sum(1 for p in self.productos.values() if p.validado and p.activo),
        )

        grados: List[Tuple[int, int]] = []
        for cid, c in self.ciudades.items():
            if c.activa:
                st.ciudades_activas += 1
                g = self.grafo_distancia.grado(cid)
                grados.append((cid, g))
                if g == 0:
                    st.ciudades_aisladas += 1
                    st.lista_aisladas.append(cid)

        grados.sort(key=lambda par: par[1], reverse=True)
        st.top_hubs = grados[:10]

        v_dist, v_tiempo, v_comb, v_peaj = [], [], [], []
        rutas_peaj: List[Tuple[int, float]] = []
        for r in self.rutas.values():
            if not r.activa:
                continue
            st.rutas_activas += 1
            v_dist.append(r.distancia_km)
            v_tiempo.append(r.tiempo_horas)
            v_comb.append(r.costo_combustible_cop)
            v_peaj.append(r.costo_peajes_cop)
            rutas_peaj.append((r.id_ruta, r.costo_peajes_cop))

        st.dist_km = self._resumir_valores(v_dist)
        st.tiempo_horas = self._resumir_valores(v_tiempo)
        st.combustible_cop = self._resumir_valores(v_comb)
        st.peajes_cop = self._resumir_valores(v_peaj)

        rutas_peaj.sort(key=lambda par: par[1], reverse=True)
        st.top_rutas_peajes = rutas_peaj[:10]
        return st


# ============================================================================
# CAPA 3: PERSISTENCIA COMPARTIDA C++ <-> PYTHON (datos_pera.txt)
# ============================================================================
class PersistenciaPERA:
    @staticmethod
    def resolver_ruta(nombre_archivo: str = "datos_pera.txt") -> Path:
        local = Path(nombre_archivo)
        if local.exists():
            return local
        return Path(__file__).resolve().parent / nombre_archivo

    @classmethod
    def cargar(cls, sistema: SistemaPERA, nombre_archivo: str = "datos_pera.txt") -> bool:
        ruta = cls.resolver_ruta(nombre_archivo)
        if not ruta.exists():
            return False

        sistema.limpiar_todo()
        seccion = ""
        with ruta.open("r", encoding="utf-8") as f:
            for linea in f:
                limpia = linea.strip()
                if not limpia or limpia.startswith("#"):
                    continue
                if limpia.startswith("[") and limpia.endswith("]"):
                    seccion = limpia
                    continue
                p = [x.strip() for x in limpia.split(";")]
                try:
                    if seccion == "[CIUDADES]" and len(p) == 6:
                        sistema.agregar_ciudad(
                            Ciudad(int(p[0]), p[1], p[2], float(p[3]), float(p[4]), p[5] != "0")
                        )
                    elif seccion == "[RUTAS]" and len(p) == 11:
                        sistema.agregar_ruta(
                            RutaTramo(
                                int(p[0]), int(p[1]), int(p[2]),
                                float(p[3]), float(p[4]), float(p[5]),
                                int(p[6]), float(p[7]), p[8],
                                p[9] != "0", p[10] != "0",
                            )
                        )
                    elif seccion == "[GRUPOS]" and len(p) == 5:
                        sistema.agregar_grupo(
                            GrupoInvestigacion(int(p[0]), p[1], p[2], p[3], p[4] != "0")
                        )
                    elif seccion == "[PRODUCTOS]" and len(p) == 6:
                        sistema.agregar_producto(
                            ProductoTecnico(
                                int(p[0]), int(p[1]), p[2], p[3], p[4] != "0", p[5] != "0"
                            )
                        )
                except ValueError:
                    continue
        sistema.reconstruir_grafos()
        return True

    @classmethod
    def guardar(cls, sistema: SistemaPERA, nombre_archivo: str = "datos_pera.txt") -> bool:
        ruta = cls.resolver_ruta(nombre_archivo)
        try:
            with ruta.open("w", encoding="utf-8", newline="\n") as f:
                f.write("# Persistencia Parcial 3 - Programa Estadistico de Rutas de Automoviles (PERA - Colombia)\n")
                f.write("# Secciones: [CIUDADES], [RUTAS], [GRUPOS], [PRODUCTOS]\n\n")

                f.write("[CIUDADES]\n# id;nombre;departamento;latitud;longitud;activa\n")
                for cid in sorted(sistema.ciudades):
                    c = sistema.ciudades[cid]
                    f.write(
                        f"{c.id};{c.nombre};{c.departamento};{c.latitud:.4f};{c.longitud:.4f};{1 if c.activa else 0}\n"
                    )

                f.write("\n[RUTAS]\n# idRuta;idOrigen;idDestino;distanciaKm;tiempoHoras;costoCombustibleCOP;cantidadPeajes;costoPeajesCOP;categoriaVia;validado;activa\n")
                for rid in sorted(sistema.rutas):
                    r = sistema.rutas[rid]
                    f.write(
                        f"{r.id_ruta};{r.id_origen};{r.id_destino};{r.distancia_km:.1f};{r.tiempo_horas:.1f};"
                        f"{r.costo_combustible_cop:.0f};{r.cantidad_peajes};{r.costo_peajes_cop:.0f};"
                        f"{r.categoria_via};{1 if r.validado else 0};{1 if r.activa else 0}\n"
                    )

                f.write("\n[GRUPOS]\n# idGrupo;nombreGrupo;region;investigadorLider;activo\n")
                for gid in sorted(sistema.grupos):
                    g = sistema.grupos[gid]
                    f.write(
                        f"{g.id_grupo};{g.nombre_grupo};{g.region};{g.investigador_lider};{1 if g.activo else 0}\n"
                    )

                f.write("\n[PRODUCTOS]\n# idProducto;idGrupo;nombreProducto;categoria;validado;activo\n")
                for pid in sorted(sistema.productos):
                    pr = sistema.productos[pid]
                    f.write(
                        f"{pr.id_producto};{pr.id_grupo};{pr.nombre_producto};{pr.categoria};"
                        f"{1 if pr.validado else 0};{1 if pr.activo else 0}\n"
                    )
            return True
        except OSError:
            return False


# ============================================================================
# CAPA 4: VENTANA DE ACCESO, INTERFAZ TKINTER, DASHBOARD Y BONO FOLIUM
# ============================================================================
USUARIO_PREDEF = "admin"
CLAVE_PREDEF = "pera2026"


class VentanaAccesoPERA:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.autenticado = False
        self.intentos_restantes = 3

        self.win = tk.Toplevel(root)
        self.win.title("Acceso al Sistema PERA - Colombia")
        self.win.geometry("430x340")
        self.win.resizable(False, False)
        self.win.configure(bg="#F8FAFC")
        self.win.protocol("WM_DELETE_WINDOW", self._cancelar)

        enc = tk.Frame(self.win, bg="#0F4C81", height=64)
        enc.pack(fill=tk.X)
        enc.pack_propagate(False)
        tk.Label(
            enc,
            text="MINTRANSPORTE COLOMBIA / UPC\nControl de Acceso - Sistema PERA",
            bg="#0F4C81",
            fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
        ).pack(expand=True)

        cuerpo = tk.Frame(self.win, bg="#F8FAFC", padx=28, pady=12)
        cuerpo.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            cuerpo,
            text=f"(Usuario: {USUARIO_PREDEF}  |  Contrasena: {CLAVE_PREDEF})",
            bg="#E2E8F0",
            fg="#0F4C81",
            font=("Segoe UI", 8, "bold"),
            pady=4,
        ).pack(fill=tk.X, pady=(0, 8))

        self.var_usuario = tk.StringVar()
        self.var_clave = tk.StringVar()
        self.var_mostrar = tk.BooleanVar(value=False)
        self.var_aviso = tk.StringVar(value="Ingrese credenciales sin espacios en blanco.")

        tk.Label(cuerpo, text="Usuario:", bg="#F8FAFC", fg="#1E293B", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.ent_usuario = ttk.Entry(cuerpo, textvariable=self.var_usuario)
        self.ent_usuario.pack(fill=tk.X, pady=(2, 6))

        tk.Label(cuerpo, text="Contrasena:", bg="#F8FAFC", fg="#1E293B", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.ent_clave = ttk.Entry(cuerpo, textvariable=self.var_clave, show="*")
        self.ent_clave.pack(fill=tk.X, pady=(2, 4))

        tk.Checkbutton(
            cuerpo,
            text="Mostrar contrasena",
            variable=self.var_mostrar,
            bg="#F8FAFC",
            fg="#334155",
            activebackground="#F8FAFC",
            font=("Segoe UI", 8),
            command=self._toggle_ver_clave,
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            cuerpo,
            textvariable=self.var_aviso,
            bg="#F8FAFC",
            fg="#B91C1C",
            font=("Segoe UI", 8, "bold"),
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        btns = tk.Frame(cuerpo, bg="#F8FAFC")
        btns.pack(fill=tk.X)
        tk.Button(
            btns,
            text="Ingresar",
            bg="#0F4C81",
            fg="#FFFFFF",
            activebackground="#0C3B66",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._validar,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        tk.Button(
            btns,
            text="Salir",
            bg="#991B1B",
            fg="#FFFFFF",
            activebackground="#7F1D1D",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._cancelar,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))

        self.win.bind("<Return>", lambda _e: self._validar())
        self.ent_usuario.focus_set()
        self.win.grab_set()

    def _toggle_ver_clave(self) -> None:
        self.ent_clave.configure(show="" if self.var_mostrar.get() else "*")

    def _validar(self) -> None:
        usuario_raw = self.var_usuario.get()
        clave_raw = self.var_clave.get()

        # Validacion estricta: prohibe campos vacios, solo espacios o espacios internos
        if not usuario_raw or not clave_raw or not usuario_raw.strip() or not clave_raw.strip():
            self.var_aviso.set("Acceso denegado: no se permiten campos vacios ni espacios.")
            return
        if any(ch.isspace() for ch in usuario_raw) or any(ch.isspace() for ch in clave_raw):
            self.var_aviso.set("Acceso denegado: el usuario y la contrasena no pueden contener espacios.")
            return

        if usuario_raw == USUARIO_PREDEF and clave_raw == CLAVE_PREDEF:
            self.autenticado = True
            self.win.destroy()
            return

        self.intentos_restantes -= 1
        if self.intentos_restantes <= 0:
            messagebox.showerror("Acceso bloqueado", "Se agotaron los 3 intentos de acceso. El programa se cerrara.")
            self.autenticado = False
            self.win.destroy()
            return

        self.var_clave.set("")
        self.var_aviso.set(
            f"Credenciales incorrectas. Intentos restantes: {self.intentos_restantes}."
        )
        self.ent_clave.focus_set()

    def _cancelar(self) -> None:
        self.autenticado = False
        self.win.destroy()

    def solicitar_acceso(self) -> bool:
        self.root.wait_window(self.win)
        return self.autenticado


class InterfazGraficaPERA:
    ARCHIVO_DATOS = "datos_pera.txt"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PERA - Programa Estadistico de Rutas de Automoviles Colombia (KM-DV-ST)")
        self.root.geometry("1180x670")
        self.root.minsize(980, 600)
        self.root.configure(bg="#F1F5F9")

        self.sistema = SistemaPERA()
        self.ultima_ruta: Optional[ResultadoRuta] = None
        self._canvas_dashboard = None

        self._construir_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._accion_salir)
        self.root.after(150, self._preguntar_carga_inicial)

    def _construir_ui(self) -> None:
        # Barra superior
        barra = tk.Frame(self.root, bg="#0F4C81", height=52)
        barra.pack(side=tk.TOP, fill=tk.X)
        barra.pack_propagate(False)

        tk.Label(
            barra,
            text="MINTRANSPORTE COLOMBIA / UPC  |  PERA - 3 GRAFOS DE RUTAS Y PEAJES",
            bg="#0F4C81",
            fg="#FFFFFF",
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT, padx=14)

        cont_der = tk.Frame(barra, bg="#0F4C81")
        cont_der.pack(side=tk.RIGHT, padx=10)

        for texto, color, cmd in [
            ("Cargar", "#00695C", self._accion_cargar),
            ("Guardar", "#2E7D32", self._accion_guardar),
            ("Salir", "#991B1B", self._accion_salir),
        ]:
            tk.Button(
                cont_der,
                text=texto,
                bg=color,
                fg="#FFFFFF",
                activebackground=color,
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                font=("Segoe UI", 9, "bold"),
                padx=10,
                pady=4,
                cursor="hand2",
                command=cmd,
            ).pack(side=tk.LEFT, padx=4, pady=10)

        # Notebook de pestanas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self.tab_rutas = tk.Frame(self.notebook, bg="#F8FAFC")
        self.tab_dashboard = tk.Frame(self.notebook, bg="#F8FAFC")
        self.tab_ciudades = tk.Frame(self.notebook, bg="#F8FAFC")
        self.tab_tramos = tk.Frame(self.notebook, bg="#F8FAFC")
        self.tab_entidades = tk.Frame(self.notebook, bg="#F8FAFC")

        self.notebook.add(self.tab_rutas, text=" 1. Calculadora de Rutas (3 Grafos) ")
        self.notebook.add(self.tab_dashboard, text=" 2. Dashboard Estadistico ")
        self.notebook.add(self.tab_ciudades, text=" 3. Ciudades (Capitales) ")
        self.notebook.add(self.tab_tramos, text=" 4. Rutas y Peajes ")
        self.notebook.add(self.tab_entidades, text=" 5. Grupos y Productos ")

        self._construir_tab_calculadora()
        self._construir_tab_dashboard()
        self._construir_tab_ciudades()
        self._construir_tab_tramos()
        self._construir_tab_entidades()

        # Barra de estado inferior
        self.var_estado = tk.StringVar(value="Listo.")
        tk.Label(
            self.root,
            textvariable=self.var_estado,
            bg="#1E293B",
            fg="#F8FAFC",
            font=("Segoe UI", 9),
            anchor="w",
            padx=12,
            pady=4,
        ).pack(side=tk.BOTTOM, fill=tk.X)

    # ---- TAB 1: CALCULADORA DE RUTAS (DIJKSTRA 4 METRICAS) ----
    def _construir_tab_calculadora(self) -> None:
        controles = tk.Frame(self.tab_rutas, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        controles.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(controles, text="Origen:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=4, sticky="w")
        self.cmb_origen = ttk.Combobox(controles, state="readonly", width=24)
        self.cmb_origen.grid(row=0, column=1, padx=4)

        tk.Label(controles, text="Destino:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, padx=4, sticky="w")
        self.cmb_destino = ttk.Combobox(controles, state="readonly", width=24)
        self.cmb_destino.grid(row=0, column=3, padx=4)

        tk.Label(controles, text="Criterio (Grafo):", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=4, padx=4, sticky="w")
        self.cmb_criterio = ttk.Combobox(
            controles,
            state="readonly",
            width=30,
            values=[
                "1 - Menor Distancia (Grafo 1)",
                "2 - Menor Combustible (Grafo 2)",
                "3 - Menor Peajes (Grafo 3)",
                "4 - Menor Costo Total (Comb + Peajes)",
            ],
        )
        self.cmb_criterio.current(3)
        self.cmb_criterio.grid(row=0, column=5, padx=4)

        fila_btns = tk.Frame(controles, bg="#FFFFFF")
        fila_btns.grid(row=1, column=0, columnspan=6, pady=(8, 0), sticky="w")

        for texto, color, cmd in [
            ("Calcular Ruta Optima", "#0F4C81", self._accion_calcular_ruta),
            ("Comparar los 3 Grafos", "#6A1B9A", self._accion_comparar_grafos),
            ("Abrir Mapa Interactivo Colombia (Folium - Bono)", "#2E7D32", self._accion_abrir_mapa_folium),
        ]:
            tk.Button(
                fila_btns,
                text=texto,
                bg=color,
                fg="#FFFFFF",
                activebackground=color,
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                font=("Segoe UI", 9, "bold"),
                padx=12,
                pady=5,
                cursor="hand2",
                command=cmd,
            ).pack(side=tk.LEFT, padx=4)

        # Tarjetas KPI de los 4 costos obligatorios
        kpi_frame = tk.Frame(self.tab_rutas, bg="#F8FAFC")
        kpi_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.kpi_vars: Dict[str, tk.StringVar] = {}
        kpis = [
            ("distancia", "DISTANCIA TOTAL", "#0284C7"),
            ("tiempo", "TIEMPO ESTIMADO", "#7C3AED"),
            ("combustible", "COSTO COMBUSTIBLE", "#D97706"),
            ("peajes", "COSTO EN PEAJES", "#DC2626"),
            ("total", "COSTO TOTAL VIAJE", "#15803D"),
        ]
        for clave, titulo, color in kpis:
            card = tk.Frame(kpi_frame, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=6)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            tk.Label(card, text=titulo, bg="#FFFFFF", fg="#475569", font=("Segoe UI", 8, "bold")).pack(anchor="w")
            v = tk.StringVar(value="--")
            self.kpi_vars[clave] = v
            tk.Label(card, textvariable=v, bg="#FFFFFF", fg=color, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.var_camino = tk.StringVar(value="Seleccione origen y destino para calcular la ruta optima.")
        tk.Label(
            self.tab_rutas,
            textvariable=self.var_camino,
            bg="#E2E8F0",
            fg="#0F172A",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=10,
            pady=5,
        ).pack(fill=tk.X, padx=8, pady=(0, 6))

        # Tabla de tramos del recorrido + tabla comparativa de los 3 grafos
        paneles = tk.PanedWindow(self.tab_rutas, orient=tk.VERTICAL, bg="#F8FAFC", sashwidth=5)
        paneles.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))

        cols_tr = ("id", "corredor", "km", "tiempo", "comb", "peajes", "cat")
        self.tv_detalle_ruta = ttk.Treeview(paneles, columns=cols_tr, show="headings", height=7)
        for c, t, w in [
            ("id", "Ruta", 55),
            ("corredor", "Corredor Vial", 280),
            ("km", "Distancia (km)", 110),
            ("tiempo", "Tiempo", 90),
            ("comb", "Combustible", 140),
            ("peajes", "Peajes (Cant/COP)", 170),
            ("cat", "Categoria", 130),
        ]:
            self.tv_detalle_ruta.heading(c, text=t)
            self.tv_detalle_ruta.column(c, width=w, anchor="center" if c != "corredor" else "w")
        paneles.add(self.tv_detalle_ruta)

        cols_cmp = ("criterio", "km", "tiempo", "comb", "peajes", "total", "ruta")
        self.tv_comparativa = ttk.Treeview(paneles, columns=cols_cmp, show="headings", height=5)
        for c, t, w in [
            ("criterio", "Criterio / Grafo", 230),
            ("km", "Dist (km)", 80),
            ("tiempo", "Tiempo", 80),
            ("comb", "Combustible", 120),
            ("peajes", "Peajes", 120),
            ("total", "Total", 125),
            ("ruta", "Secuencia de Capitales", 340),
        ]:
            self.tv_comparativa.heading(c, text=t)
            self.tv_comparativa.column(c, width=w, anchor="w" if c in ("criterio", "ruta") else "center")
        paneles.add(self.tv_comparativa)

    # ---- TAB 2: DASHBOARD ESTADISTICO ----
    def _construir_tab_dashboard(self) -> None:
        barra_dash = tk.Frame(self.tab_dashboard, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=6)
        barra_dash.pack(fill=tk.X, padx=8, pady=6)

        self.var_resumen_dash = tk.StringVar(value="Cargue datos para visualizar el Dashboard Estadistico.")
        tk.Label(
            barra_dash,
            textvariable=self.var_resumen_dash,
            bg="#FFFFFF",
            fg="#0F172A",
            font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.LEFT)

        tk.Button(
            barra_dash,
            text="Actualizar Graficas",
            bg="#0F4C81",
            fg="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._renderizar_dashboard,
        ).pack(side=tk.RIGHT)

        self.frame_graficas = tk.Frame(self.tab_dashboard, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        self.frame_graficas.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    # ---- TAB 3: GESTION DE CIUDADES ----
    def _construir_tab_ciudades(self) -> None:
        izq = tk.Frame(self.tab_ciudades, bg="#FFFFFF", width=290, bd=1, relief=tk.SOLID, padx=10, pady=8)
        izq.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        izq.pack_propagate(False)

        tk.Label(izq, text="CRUD de Capitales", bg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        self.v_cid = tk.StringVar()
        self.v_cnom = tk.StringVar()
        self.v_cdep = tk.StringVar()
        self.v_clat = tk.StringVar()
        self.v_clon = tk.StringVar()

        for lbl, var in [
            ("ID (auto al crear):", self.v_cid),
            ("Nombre Capital:", self.v_cnom),
            ("Departamento:", self.v_cdep),
            ("Latitud (WGS-84):", self.v_clat),
            ("Longitud (WGS-84):", self.v_clon),
        ]:
            tk.Label(izq, text=lbl, bg="#FFFFFF", font=("Segoe UI", 8)).pack(anchor="w")
            ttk.Entry(izq, textvariable=var).pack(fill=tk.X, pady=(0, 5))

        for txt, col, cmd in [
            ("Ingresar Capital", "#2E7D32", self._ciudad_agregar),
            ("Modificar Seleccionada", "#1565C0", self._ciudad_modificar),
            ("Desactivar / Reactivar", "#475569", self._ciudad_toggle),
            ("Eliminar Capital", "#B91C1C", self._ciudad_eliminar),
        ]:
            tk.Button(izq, text=txt, bg=col, fg="#FFFFFF", relief=tk.FLAT, font=("Segoe UI", 9, "bold"),
                      pady=4, cursor="hand2", command=cmd).pack(fill=tk.X, pady=2)

        cols = ("id", "nombre", "depto", "lat", "lon", "grado", "estado")
        self.tv_ciudades = ttk.Treeview(self.tab_ciudades, columns=cols, show="headings")
        for c, t, w in [
            ("id", "ID", 45), ("nombre", "Capital", 160), ("depto", "Departamento", 170),
            ("lat", "Latitud", 85), ("lon", "Longitud", 85), ("grado", "Grado", 60), ("estado", "Estado", 95),
        ]:
            self.tv_ciudades.heading(c, text=t)
            self.tv_ciudades.column(c, width=w, anchor="center" if c not in ("nombre", "depto") else "w")
        self.tv_ciudades.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=8)
        self.tv_ciudades.bind("<<TreeviewSelect>>", self._ciudad_seleccionada)

    # ---- TAB 4: GESTION DE RUTAS Y PEAJES ----
    def _construir_tab_tramos(self) -> None:
        izq = tk.Frame(self.tab_tramos, bg="#FFFFFF", width=300, bd=1, relief=tk.SOLID, padx=10, pady=6)
        izq.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        izq.pack_propagate(False)

        tk.Label(izq, text="CRUD de Rutas y Peajes", bg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.v_rid = tk.StringVar()
        self.v_rorig = tk.StringVar()
        self.v_rdest = tk.StringVar()
        self.v_rdist = tk.StringVar()
        self.v_rtiempo = tk.StringVar()
        self.v_rcomb = tk.StringVar()
        self.v_rnpeaj = tk.StringVar()
        self.v_rcpeaj = tk.StringVar()
        self.v_rcat = tk.StringVar(value="Primaria")
        self.v_rval = tk.BooleanVar(value=True)

        campos = [
            ("ID Ruta (auto al crear):", self.v_rid),
            ("ID Origen:", self.v_rorig),
            ("ID Destino:", self.v_rdest),
            ("Distancia (km):", self.v_rdist),
            ("Tiempo (horas):", self.v_rtiempo),
            ("Combustible (COP):", self.v_rcomb),
            ("Cantidad Peajes:", self.v_rnpeaj),
            ("Costo Peajes (COP):", self.v_rcpeaj),
            ("Categoria Via:", self.v_rcat),
        ]
        for lbl, var in campos:
            fila = tk.Frame(izq, bg="#FFFFFF")
            fila.pack(fill=tk.X, pady=1)
            tk.Label(fila, text=lbl, bg="#FFFFFF", font=("Segoe UI", 8), width=19, anchor="w").pack(side=tk.LEFT)
            ttk.Entry(fila, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Checkbutton(izq, text="Tramo / Tarifa Validada (INVIAS/ANI)", variable=self.v_rval, bg="#FFFFFF").pack(anchor="w", pady=3)

        for txt, col, cmd in [
            ("Ingresar Ruta", "#2E7D32", self._ruta_agregar),
            ("Modificar Ruta", "#1565C0", self._ruta_modificar),
            ("Desactivar/Reactivar (Cierre Vial)", "#D97706", self._ruta_toggle),
            ("Eliminar Ruta", "#B91C1C", self._ruta_eliminar),
        ]:
            tk.Button(izq, text=txt, bg=col, fg="#FFFFFF", relief=tk.FLAT, font=("Segoe UI", 8, "bold"),
                      pady=4, cursor="hand2", command=cmd).pack(fill=tk.X, pady=2)

        cols = ("id", "corredor", "km", "hrs", "comb", "peaj", "cat", "val", "est")
        self.tv_rutas = ttk.Treeview(self.tab_tramos, columns=cols, show="headings")
        for c, t, w in [
            ("id", "ID", 40), ("corredor", "Corredor", 210), ("km", "Km", 60), ("hrs", "Hrs", 55),
            ("comb", "Combustible", 110), ("peaj", "Peajes", 110), ("cat", "Categoria", 95),
            ("val", "Val", 45), ("est", "Estado", 75),
        ]:
            self.tv_rutas.heading(c, text=t)
            self.tv_rutas.column(c, width=w, anchor="center" if c != "corredor" else "w")
        self.tv_rutas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=8)
        self.tv_rutas.bind("<<TreeviewSelect>>", self._ruta_seleccionada)

    # ---- TAB 5: GRUPOS, INVESTIGADORES Y PRODUCTOS TECNICOS ----
    def _construir_tab_entidades(self) -> None:
        paned = tk.PanedWindow(self.tab_entidades, orient=tk.HORIZONTAL, bg="#F8FAFC", sashwidth=6)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Panel Grupos
        fr_g = tk.Frame(paned, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=8, pady=8)
        paned.add(fr_g, stretch="always")
        tk.Label(fr_g, text="Grupos e Investigadores Viales", bg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.v_gid = tk.StringVar()
        self.v_gnom = tk.StringVar()
        self.v_greg = tk.StringVar()
        self.v_ginv = tk.StringVar()
        for lbl, var in [("ID Grupo:", self.v_gid), ("Nombre Grupo:", self.v_gnom), ("Region:", self.v_greg), ("Investigador Lider:", self.v_ginv)]:
            f = tk.Frame(fr_g, bg="#FFFFFF")
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=lbl, bg="#FFFFFF", width=16, anchor="w", font=("Segoe UI", 8)).pack(side=tk.LEFT)
            ttk.Entry(f, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        bg_row = tk.Frame(fr_g, bg="#FFFFFF")
        bg_row.pack(fill=tk.X, pady=4)
        for txt, col, cmd in [
            ("Crear", "#2E7D32", self._grupo_agregar),
            ("Editar", "#1565C0", self._grupo_modificar),
            ("Act/Des", "#475569", self._grupo_toggle),
            ("Eliminar", "#B91C1C", self._grupo_eliminar),
        ]:
            tk.Button(bg_row, text=txt, bg=col, fg="#FFFFFF", relief=tk.FLAT, font=("Segoe UI", 8, "bold"),
                      padx=8, pady=3, command=cmd).pack(side=tk.LEFT, padx=2)

        self.tv_grupos = ttk.Treeview(fr_g, columns=("id", "nom", "reg", "inv", "est"), show="headings")
        for c, t, w in [("id", "ID", 35), ("nom", "Grupo", 160), ("reg", "Region", 100), ("inv", "Investigador", 130), ("est", "Estado", 70)]:
            self.tv_grupos.heading(c, text=t)
            self.tv_grupos.column(c, width=w, anchor="w" if c in ("nom", "inv") else "center")
        self.tv_grupos.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.tv_grupos.bind("<<TreeviewSelect>>", self._grupo_seleccionado)

        # Panel Productos
        fr_p = tk.Frame(paned, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=8, pady=8)
        paned.add(fr_p, stretch="always")
        tk.Label(fr_p, text="Productos Tecnicos (Categoria y Validacion)", bg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.v_pid = tk.StringVar()
        self.v_pgid = tk.StringVar()
        self.v_pnom = tk.StringVar()
        self.v_pcat = tk.StringVar()
        self.v_pval = tk.BooleanVar(value=True)
        for lbl, var in [("ID Producto:", self.v_pid), ("ID Grupo:", self.v_pgid), ("Nombre Producto:", self.v_pnom), ("Categoria:", self.v_pcat)]:
            f = tk.Frame(fr_p, bg="#FFFFFF")
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=lbl, bg="#FFFFFF", width=16, anchor="w", font=("Segoe UI", 8)).pack(side=tk.LEFT)
            ttk.Entry(f, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Checkbutton(fr_p, text="Producto Validado", variable=self.v_pval, bg="#FFFFFF").pack(anchor="w")

        bp_row = tk.Frame(fr_p, bg="#FFFFFF")
        bp_row.pack(fill=tk.X, pady=4)
        for txt, col, cmd in [
            ("Crear", "#2E7D32", self._prod_agregar),
            ("Editar", "#1565C0", self._prod_modificar),
            ("Act/Des", "#475569", self._prod_toggle),
            ("Eliminar", "#B91C1C", self._prod_eliminar),
        ]:
            tk.Button(bp_row, text=txt, bg=col, fg="#FFFFFF", relief=tk.FLAT, font=("Segoe UI", 8, "bold"),
                      padx=8, pady=3, command=cmd).pack(side=tk.LEFT, padx=2)

        self.tv_productos = ttk.Treeview(fr_p, columns=("id", "grp", "nom", "cat", "val", "est"), show="headings")
        for c, t, w in [("id", "ID", 35), ("grp", "Grp", 35), ("nom", "Producto", 180), ("cat", "Categoria", 110), ("val", "Val", 50), ("est", "Estado", 70)]:
            self.tv_productos.heading(c, text=t)
            self.tv_productos.column(c, width=w, anchor="w" if c in ("nom", "cat") else "center")
        self.tv_productos.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.tv_productos.bind("<<TreeviewSelect>>", self._prod_seleccionado)

    # ---- PERSISTENCIA Y REFRESCO ----
    def _preguntar_carga_inicial(self) -> None:
        cargar = messagebox.askyesno(
            "Carga Inicial - PERA (Colombia)",
            "Desea cargar los datos reales de Colombia desde 'datos_pera.txt'?\n\n"
            "- Si: Cargar 32 capitales, corredores, peajes y entidades.\n"
            "- No: Ejecutar el sistema sin datos (grafos vacios).",
        )
        if cargar:
            if PersistenciaPERA.cargar(self.sistema, self.ARCHIVO_DATOS):
                self.var_estado.set(
                    f"Cargadas {len(self.sistema.ciudades)} capitales y {len(self.sistema.rutas)} corredores desde '{self.ARCHIVO_DATOS}'."
                )
            else:
                self.var_estado.set(f"No se encontro '{self.ARCHIVO_DATOS}'. Iniciado vacio.")
        else:
            self.sistema.limpiar_todo()
            self.var_estado.set("Sistema iniciado sin datos.")
        self._refrescar_todo()

    def _accion_cargar(self) -> None:
        if PersistenciaPERA.cargar(self.sistema, self.ARCHIVO_DATOS):
            self.var_estado.set(f"Persistencia recargada desde '{self.ARCHIVO_DATOS}'.")
        else:
            messagebox.showwarning("Archivo no encontrado", f"No se encontro '{self.ARCHIVO_DATOS}'.")
        self._refrescar_todo()

    def _accion_guardar(self) -> None:
        if PersistenciaPERA.guardar(self.sistema, self.ARCHIVO_DATOS):
            self.var_estado.set(f"Datos guardados correctamente en '{self.ARCHIVO_DATOS}'.")
        else:
            messagebox.showerror("Error", f"No se pudo guardar en '{self.ARCHIVO_DATOS}'.")

    def _accion_salir(self) -> None:
        resp = messagebox.askyesnocancel(
            "Salir - PERA Colombia",
            "Desea guardar los cambios en 'datos_pera.txt' antes de salir?",
        )
        if resp is None:
            return
        if resp:
            PersistenciaPERA.guardar(self.sistema, self.ARCHIVO_DATOS)
        self.root.destroy()

    def _refrescar_todo(self) -> None:
        opciones = [
            f"{cid} - {c.nombre}{' [INACTIVA]' if not c.activa else ''}"
            for cid, c in sorted(self.sistema.ciudades.items())
        ]
        self.cmb_origen["values"] = opciones
        self.cmb_destino["values"] = opciones
        if opciones and not self.cmb_origen.get():
            idx_val = next((i for i, o in enumerate(opciones) if o.startswith("16 -")), 0)
            idx_bog = next((i for i, o in enumerate(opciones) if o.startswith("1 -")), min(1, len(opciones) - 1))
            self.cmb_origen.current(idx_val)
            self.cmb_destino.current(idx_bog)

        # Tabla Ciudades
        for item in self.tv_ciudades.get_children():
            self.tv_ciudades.delete(item)
        for cid, c in sorted(self.sistema.ciudades.items()):
            self.tv_ciudades.insert(
                "", tk.END,
                values=(cid, c.nombre, c.departamento, f"{c.latitud:.4f}", f"{c.longitud:.4f}",
                        self.sistema.grafo_distancia.grado(cid), "ACTIVA" if c.activa else "DESACTIVADA"),
            )

        # Tabla Rutas
        for item in self.tv_rutas.get_children():
            self.tv_rutas.delete(item)
        for rid, r in sorted(self.sistema.rutas.items()):
            corr = f"{self.sistema.nombre_ciudad(r.id_origen)} <-> {self.sistema.nombre_ciudad(r.id_destino)}"
            self.tv_rutas.insert(
                "", tk.END,
                values=(rid, corr, f"{r.distancia_km:.1f}", f"{r.tiempo_horas:.1f}",
                        formato_cop(r.costo_combustible_cop), f"{r.cantidad_peajes} ({formato_cop(r.costo_peajes_cop)})",
                        r.categoria_via, "SI" if r.validado else "NO", "ACTIVA" if r.activa else "CERRADA"),
            )

        # Tabla Grupos y Productos
        for item in self.tv_grupos.get_children():
            self.tv_grupos.delete(item)
        for gid, g in sorted(self.sistema.grupos.items()):
            self.tv_grupos.insert("", tk.END, values=(gid, g.nombre_grupo, g.region, g.investigador_lider, "ACTIVO" if g.activo else "INACTIVO"))

        for item in self.tv_productos.get_children():
            self.tv_productos.delete(item)
        for pid, p in sorted(self.sistema.productos.items()):
            self.tv_productos.insert("", tk.END, values=(pid, p.id_grupo, p.nombre_producto, p.categoria, "SI" if p.validado else "NO", "ACTIVO" if p.activo else "INACTIVO"))

        self._renderizar_dashboard()

    # ---- ACCIONES CALCULADORA ----
    def _parse_id_combo(self, combo: ttk.Combobox) -> Optional[int]:
        txt = combo.get().strip()
        if not txt or " - " not in txt:
            return None
        try:
            return int(txt.split(" - ")[0])
        except ValueError:
            return None

    def _mostrar_resultado_en_ui(self, res: ResultadoRuta) -> None:
        self.ultima_ruta = res if res.encontrada else None
        for item in self.tv_detalle_ruta.get_children():
            self.tv_detalle_ruta.delete(item)
        if not res.encontrada:
            for v in self.kpi_vars.values():
                v.set("--")
            self.var_camino.set(f"AVISO: {res.mensaje}")
            return

        self.kpi_vars["distancia"].set(f"{res.distancia_total_km:.1f} km")
        self.kpi_vars["tiempo"].set(formato_horas(res.tiempo_total_horas))
        self.kpi_vars["combustible"].set(formato_cop(res.combustible_total_cop))
        self.kpi_vars["peajes"].set(f"{formato_cop(res.peajes_total_cop)} ({res.total_peajes})")
        self.kpi_vars["total"].set(formato_cop(res.costo_total_cop))

        seq = " -> ".join(self.sistema.nombre_ciudad(c) for c in res.camino_ciudades)
        self.var_camino.set(f"[{res.criterio}]  {seq}")

        for i, rid in enumerate(res.rutas_usadas):
            t = self.sistema.rutas[rid]
            corr = f"{self.sistema.nombre_ciudad(res.camino_ciudades[i])} -> {self.sistema.nombre_ciudad(res.camino_ciudades[i + 1])}"
            self.tv_detalle_ruta.insert(
                "", tk.END,
                values=(rid, corr, f"{t.distancia_km:.1f}", formato_horas(t.tiempo_horas),
                        formato_cop(t.costo_combustible_cop), f"{t.cantidad_peajes} | {formato_cop(t.costo_peajes_cop)}",
                        t.categoria_via),
            )

    def _accion_calcular_ruta(self) -> None:
        orig = self._parse_id_combo(self.cmb_origen)
        dest = self._parse_id_combo(self.cmb_destino)
        if orig is None or dest is None:
            messagebox.showwarning("Seleccion", "Seleccione origen y destino.")
            return
        criterio = self.cmb_criterio.current() + 1
        res = self.sistema.calcular_ruta_optima(orig, dest, criterio)
        self._mostrar_resultado_en_ui(res)
        self.var_estado.set(res.mensaje)

    def _accion_comparar_grafos(self) -> None:
        orig = self._parse_id_combo(self.cmb_origen)
        dest = self._parse_id_combo(self.cmb_destino)
        if orig is None or dest is None:
            messagebox.showwarning("Seleccion", "Seleccione origen y destino.")
            return
        for item in self.tv_comparativa.get_children():
            self.tv_comparativa.delete(item)
        ultimo_ok = None
        for crit in (1, 2, 3, 4):
            r = self.sistema.calcular_ruta_optima(orig, dest, crit)
            if r.encontrada:
                ultimo_ok = r
                seq = " -> ".join(self.sistema.nombre_ciudad(c) for c in r.camino_ciudades)
                self.tv_comparativa.insert(
                    "", tk.END,
                    values=(r.criterio, f"{r.distancia_total_km:.1f}", formato_horas(r.tiempo_total_horas),
                            formato_cop(r.combustible_total_cop), formato_cop(r.peajes_total_cop),
                            formato_cop(r.costo_total_cop), seq),
                )
            else:
                self._mostrar_resultado_en_ui(r)
                return
        if ultimo_ok:
            self._mostrar_resultado_en_ui(ultimo_ok)
            self.var_estado.set("Comparativa de los 3 grafos y costo total generada.")

    # ---- CRUD CALLBACKS CIUDADES ----
    def _ciudad_seleccionada(self, _e=None) -> None:
        sel = self.tv_ciudades.selection()
        if not sel:
            return
        cid = int(self.tv_ciudades.item(sel[0])["values"][0])
        c = self.sistema.ciudades[cid]
        self.v_cid.set(str(c.id))
        self.v_cnom.set(c.nombre)
        self.v_cdep.set(c.departamento)
        self.v_clat.set(str(c.latitud))
        self.v_clon.set(str(c.longitud))

    def _ciudad_agregar(self) -> None:
        try:
            c = Ciudad(
                self.sistema.siguiente_id_ciudad(),
                self.v_cnom.get().strip(),
                self.v_cdep.get().strip(),
                float(self.v_clat.get().strip()),
                float(self.v_clon.get().strip()),
                True,
            )
            if not c.nombre or not c.departamento:
                raise ValueError("Nombre y departamento obligatorios")
            self.sistema.agregar_ciudad(c)
            self.var_estado.set(f"Capital '{c.nombre}' agregada con ID {c.id}.")
            self._refrescar_todo()
        except ValueError as err:
            messagebox.showerror("Datos invalidos", f"Verifique los campos de la ciudad: {err}")

    def _ciudad_modificar(self) -> None:
        try:
            cid = int(self.v_cid.get().strip())
            prev = self.sistema.ciudades[cid]
            nueva = Ciudad(
                cid, self.v_cnom.get().strip(), self.v_cdep.get().strip(),
                float(self.v_clat.get().strip()), float(self.v_clon.get().strip()), prev.activa,
            )
            self.sistema.modificar_ciudad(cid, nueva)
            self.var_estado.set(f"Capital ID {cid} actualizada.")
            self._refrescar_todo()
        except Exception:
            messagebox.showerror("Error", "Seleccione una ciudad valida para modificar.")

    def _ciudad_toggle(self) -> None:
        try:
            cid = int(self.v_cid.get().strip())
            nuevo = not self.sistema.ciudades[cid].activa
            self.sistema.cambiar_estado_ciudad(cid, nuevo)
            self.var_estado.set(f"Capital ID {cid} marcada como {'ACTIVA' if nuevo else 'DESACTIVADA'}.")
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione una ciudad primero.")

    def _ciudad_eliminar(self) -> None:
        try:
            cid = int(self.v_cid.get().strip())
            if self.sistema.eliminar_ciudad(cid):
                self.var_estado.set(f"Capital ID {cid} y sus rutas incidentes eliminadas.")
                self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione una ciudad para eliminar.")

    # ---- CRUD CALLBACKS RUTAS ----
    def _ruta_seleccionada(self, _e=None) -> None:
        sel = self.tv_rutas.selection()
        if not sel:
            return
        rid = int(self.tv_rutas.item(sel[0])["values"][0])
        r = self.sistema.rutas[rid]
        self.v_rid.set(str(r.id_ruta))
        self.v_rorig.set(str(r.id_origen))
        self.v_rdest.set(str(r.id_destino))
        self.v_rdist.set(str(r.distancia_km))
        self.v_rtiempo.set(str(r.tiempo_horas))
        self.v_rcomb.set(str(int(r.costo_combustible_cop)))
        self.v_rnpeaj.set(str(r.cantidad_peajes))
        self.v_rcpeaj.set(str(int(r.costo_peajes_cop)))
        self.v_rcat.set(r.categoria_via)
        self.v_rval.set(r.validado)

    def _ruta_agregar(self) -> None:
        try:
            r = RutaTramo(
                self.sistema.siguiente_id_ruta(),
                int(self.v_rorig.get()), int(self.v_rdest.get()),
                float(self.v_rdist.get()), float(self.v_rtiempo.get()),
                float(self.v_rcomb.get()), int(self.v_rnpeaj.get()),
                float(self.v_rcpeaj.get()), self.v_rcat.get().strip() or "Primaria",
                self.v_rval.get(), True,
            )
            if not self.sistema.agregar_ruta(r):
                raise ValueError("Ciudades inexistentes o iguales")
            self.var_estado.set(f"Ruta #{r.id_ruta} agregada a los 3 grafos.")
            self._refrescar_todo()
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo agregar la ruta: {err}")

    def _ruta_modificar(self) -> None:
        try:
            rid = int(self.v_rid.get())
            prev = self.sistema.rutas[rid]
            r = RutaTramo(
                rid, int(self.v_rorig.get()), int(self.v_rdest.get()),
                float(self.v_rdist.get()), float(self.v_rtiempo.get()),
                float(self.v_rcomb.get()), int(self.v_rnpeaj.get()),
                float(self.v_rcpeaj.get()), self.v_rcat.get().strip() or prev.categoria_via,
                self.v_rval.get(), prev.activa,
            )
            if not self.sistema.modificar_ruta(rid, r):
                raise ValueError("Datos de ruta invalidos")
            self.var_estado.set(f"Ruta #{rid} actualizada y sincronizada en los 3 grafos.")
            self._refrescar_todo()
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo modificar la ruta: {err}")

    def _ruta_toggle(self) -> None:
        try:
            rid = int(self.v_rid.get())
            nuevo = not self.sistema.rutas[rid].activa
            self.sistema.cambiar_estado_ruta(rid, nuevo)
            self.var_estado.set(f"Ruta #{rid} {'HABILITADA' if nuevo else 'DESACTIVADA (cierre vial)'}.")
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione una ruta primero.")

    def _ruta_eliminar(self) -> None:
        try:
            rid = int(self.v_rid.get())
            if self.sistema.eliminar_ruta(rid):
                self.var_estado.set(f"Ruta #{rid} eliminada de los 3 grafos.")
                self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione una ruta para eliminar.")

    # ---- CRUD CALLBACKS GRUPOS Y PRODUCTOS ----
    def _grupo_seleccionado(self, _e=None) -> None:
        sel = self.tv_grupos.selection()
        if not sel:
            return
        gid = int(self.tv_grupos.item(sel[0])["values"][0])
        g = self.sistema.grupos[gid]
        self.v_gid.set(str(g.id_grupo))
        self.v_gnom.set(g.nombre_grupo)
        self.v_greg.set(g.region)
        self.v_ginv.set(g.investigador_lider)

    def _grupo_agregar(self) -> None:
        nom = self.v_gnom.get().strip()
        if not nom:
            messagebox.showwarning("Dato", "Ingrese nombre del grupo.")
            return
        g = GrupoInvestigacion(self.sistema.siguiente_id_grupo(), nom, self.v_greg.get().strip(), self.v_ginv.get().strip(), True)
        self.sistema.agregar_grupo(g)
        self._refrescar_todo()

    def _grupo_modificar(self) -> None:
        try:
            gid = int(self.v_gid.get())
            prev = self.sistema.grupos[gid]
            self.sistema.modificar_grupo(gid, GrupoInvestigacion(gid, self.v_gnom.get().strip(), self.v_greg.get().strip(), self.v_ginv.get().strip(), prev.activo))
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione un grupo valido.")

    def _grupo_toggle(self) -> None:
        try:
            gid = int(self.v_gid.get())
            self.sistema.cambiar_estado_grupo(gid, not self.sistema.grupos[gid].activo)
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione un grupo.")

    def _grupo_eliminar(self) -> None:
        try:
            gid = int(self.v_gid.get())
            self.sistema.eliminar_grupo(gid)
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione un grupo.")

    def _prod_seleccionado(self, _e=None) -> None:
        sel = self.tv_productos.selection()
        if not sel:
            return
        pid = int(self.tv_productos.item(sel[0])["values"][0])
        p = self.sistema.productos[pid]
        self.v_pid.set(str(p.id_producto))
        self.v_pgid.set(str(p.id_grupo))
        self.v_pnom.set(p.nombre_producto)
        self.v_pcat.set(p.categoria)
        self.v_pval.set(p.validado)

    def _prod_agregar(self) -> None:
        try:
            p = ProductoTecnico(
                self.sistema.siguiente_id_producto(), int(self.v_pgid.get()),
                self.v_pnom.get().strip(), self.v_pcat.get().strip(), self.v_pval.get(), True,
            )
            if not p.nombre_producto or not self.sistema.agregar_producto(p):
                raise ValueError("Verifique ID de grupo existente y nombre.")
            self._refrescar_todo()
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _prod_modificar(self) -> None:
        try:
            pid = int(self.v_pid.get())
            prev = self.sistema.productos[pid]
            p = ProductoTecnico(pid, int(self.v_pgid.get()), self.v_pnom.get().strip(), self.v_pcat.get().strip(), self.v_pval.get(), prev.activo)
            self.sistema.modificar_producto(pid, p)
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione un producto valido.")

    def _prod_toggle(self) -> None:
        try:
            pid = int(self.v_pid.get())
            self.sistema.cambiar_estado_producto(pid, not self.sistema.productos[pid].activo)
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione un producto.")

    def _prod_eliminar(self) -> None:
        try:
            pid = int(self.v_pid.get())
            self.sistema.eliminar_producto(pid)
            self._refrescar_todo()
        except Exception:
            messagebox.showwarning("Seleccion", "Seleccione un producto.")

    # ---- DASHBOARD ESTADISTICO (MATPLOTLIB) Y MAPA INTERACTIVO (FOLIUM) ----
    @staticmethod
    def construir_figura_dashboard(sistema: SistemaPERA) -> "Figure":
        fig = Figure(figsize=(10.8, 5.2), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")

        st = sistema.calcular_estadisticas()
        rutas_activas = [r for r in sistema.rutas.values() if r.activa]

        # 1. Histograma de Distancias (km)
        ax1 = fig.add_subplot(2, 2, 1)
        dists = [r.distancia_km for r in rutas_activas]
        if dists:
            ax1.hist(dists, bins=10, color="#0284C7", edgecolor="#FFFFFF", alpha=0.9)
            ax1.axvline(st.dist_km.media, color="#DC2626", linestyle="--", linewidth=1.4,
                        label=f"Media: {st.dist_km.media:.1f} km")
            ax1.legend(fontsize=8)
        ax1.set_title("Histograma: Distancias por Corredor (km)", fontsize=9.5, fontweight="bold", color="#0F172A")
        ax1.set_xlabel("Distancia (km)", fontsize=8)
        ax1.set_ylabel("Frecuencia", fontsize=8)
        ax1.tick_params(labelsize=8)
        ax1.grid(axis="y", linestyle=":", alpha=0.5)

        # 2. Histograma de Costos en Peajes (miles de COP)
        ax2 = fig.add_subplot(2, 2, 2)
        peajes_k = [r.costo_peajes_cop / 1000.0 for r in rutas_activas]
        if peajes_k:
            ax2.hist(peajes_k, bins=10, color="#D97706", edgecolor="#FFFFFF", alpha=0.9)
            ax2.axvline(st.peajes_cop.media / 1000.0, color="#0F4C81", linestyle="--", linewidth=1.4,
                        label=f"Media: ${st.peajes_cop.media / 1000.0:.1f}k")
            ax2.legend(fontsize=8)
        ax2.set_title("Histograma: Costos en Peajes (miles COP)", fontsize=9.5, fontweight="bold", color="#0F172A")
        ax2.set_xlabel("Costo en Peajes (miles de COP)", fontsize=8)
        ax2.set_ylabel("Frecuencia", fontsize=8)
        ax2.tick_params(labelsize=8)
        ax2.grid(axis="y", linestyle=":", alpha=0.5)

        # 3. Diagrama de Barras: Top 8 Capitales por Conectividad (Grado)
        ax3 = fig.add_subplot(2, 2, 3)
        top_hubs = [par for par in st.top_hubs[:8] if par[1] > 0]
        if top_hubs:
            nombres = [sistema.nombre_ciudad(cid) for cid, _ in reversed(top_hubs)]
            grados = [g for _, g in reversed(top_hubs)]
            ax3.barh(nombres, grados, color="#15803D", alpha=0.9)
            for idx, val in enumerate(grados):
                ax3.text(val + 0.12, idx, str(val), va="center", fontsize=8, fontweight="bold")
        ax3.set_title("Barras: Top 8 Capitales por Conectividad (Grado)", fontsize=9.5, fontweight="bold", color="#0F172A")
        ax3.set_xlabel("Corredores Directos", fontsize=8)
        ax3.tick_params(labelsize=8)
        ax3.grid(axis="x", linestyle=":", alpha=0.5)

        # 4. Diagrama de Barras Agrupadas: Combustible vs Peajes (Top 6 corredores)
        ax4 = fig.add_subplot(2, 2, 4)
        top_corr = sorted(
            rutas_activas,
            key=lambda r: r.costo_combustible_cop + r.costo_peajes_cop,
            reverse=True,
        )[:6]
        if top_corr:
            etqs = [
                f"{sistema.nombre_ciudad(r.id_origen)[:6]}-{sistema.nombre_ciudad(r.id_destino)[:6]}"
                for r in top_corr
            ]
            comb_k = [r.costo_combustible_cop / 1000.0 for r in top_corr]
            peaj_k = [r.costo_peajes_cop / 1000.0 for r in top_corr]
            pos = list(range(len(etqs)))
            ancho = 0.36
            ax4.bar([p - ancho / 2 for p in pos], comb_k, width=ancho, label="Combustible", color="#0F4C81")
            ax4.bar([p + ancho / 2 for p in pos], peaj_k, width=ancho, label="Peajes", color="#DC2626")
            ax4.set_xticks(pos)
            ax4.set_xticklabels(etqs, rotation=18, ha="right", fontsize=7.5)
            ax4.legend(fontsize=8)
        ax4.set_title("Barras: Combustible vs Peajes (Top 6 Corredores)", fontsize=9.5, fontweight="bold", color="#0F172A")
        ax4.set_ylabel("Miles de COP", fontsize=8)
        ax4.tick_params(axis="y", labelsize=8)
        ax4.grid(axis="y", linestyle=":", alpha=0.5)

        fig.tight_layout(pad=1.6)
        return fig

    @staticmethod
    def generar_mapa_folium(
        sistema: SistemaPERA,
        ultima_ruta: Optional[ResultadoRuta],
        ruta_html: Path,
    ) -> Path:
        mapa = folium.Map(location=[4.5709, -74.2973], zoom_start=6, tiles=None)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Street Map",
            name="Esri Calles Colombia",
            control=True,
        ).add_to(mapa)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Topo Map",
            name="Esri Topografico",
            control=True,
        ).add_to(mapa)

        rutas_destacadas = set(ultima_ruta.rutas_usadas) if (ultima_ruta and ultima_ruta.encontrada) else set()

        # Dibujar corredores viales
        for r in sistema.rutas.values():
            c1 = sistema.ciudades.get(r.id_origen)
            c2 = sistema.ciudades.get(r.id_destino)
            if not c1 or not c2:
                continue
            es_optima = r.id_ruta in rutas_destacadas
            if es_optima:
                color, grosor, opacidad, dash = "#DC2626", 6, 0.95, None
            elif not r.activa:
                color, grosor, opacidad, dash = "#94A3B8", 2, 0.6, "6, 6"
            else:
                color, grosor, opacidad, dash = "#1D4ED8", 2.5, 0.65, None

            popup_txt = (
                f"<b>{c1.nombre} &harr; {c2.nombre}</b><br>"
                f"Distancia: {r.distancia_km:.1f} km<br>"
                f"Tiempo: {formato_horas(r.tiempo_horas)}<br>"
                f"Combustible: {formato_cop(r.costo_combustible_cop)}<br>"
                f"Peajes ({r.cantidad_peajes}): {formato_cop(r.costo_peajes_cop)}<br>"
                f"Categoria: {r.categoria_via} | Estado: {'ACTIVA' if r.activa else 'CERRADA'}"
            )
            kwargs_linea = dict(
                locations=[(c1.latitud, c1.longitud), (c2.latitud, c2.longitud)],
                color=color,
                weight=grosor,
                opacity=opacidad,
                popup=folium.Popup(popup_txt, max_width=260),
                tooltip=f"{c1.nombre} - {c2.nombre} ({r.distancia_km:.0f} km)",
            )
            if dash:
                kwargs_linea["dash_array"] = dash
            folium.PolyLine(**kwargs_linea).add_to(mapa)

        # Dibujar marcadores de las 32 capitales
        camino_set = set(ultima_ruta.camino_ciudades) if (ultima_ruta and ultima_ruta.encontrada) else set()
        for cid, c in sistema.ciudades.items():
            grado = sistema.grafo_distancia.grado(cid)
            if cid in camino_set:
                color_ic = "red"
            elif not c.activa or grado == 0:
                color_ic = "gray"
            else:
                color_ic = "green"
            popup_c = (
                f"<b>{c.nombre}</b> ({c.departamento})<br>"
                f"ID: {cid} | Grado vial: {grado}<br>"
                f"Estado: {'ACTIVA' if c.activa else 'DESACTIVADA'}"
            )
            folium.CircleMarker(
                location=[c.latitud, c.longitud],
                radius=7 if cid in camino_set else 5,
                color="#0F172A",
                weight=1.2,
                fill=True,
                fill_color=color_ic,
                fill_opacity=0.9,
                popup=folium.Popup(popup_c, max_width=230),
                tooltip=f"{c.nombre} (Grado: {grado})",
            ).add_to(mapa)

        # Leyenda flotante con resumen de la ruta optima
        resumen_html = "Sin ruta seleccionada (calcule una ruta en PERA para resaltarla)."
        if ultima_ruta and ultima_ruta.encontrada:
            seq = " &rarr; ".join(sistema.nombre_ciudad(c) for c in ultima_ruta.camino_ciudades)
            resumen_html = (
                f"<b>{ultima_ruta.criterio}</b><br>"
                f"{seq}<br>"
                f"Dist: <b>{ultima_ruta.distancia_total_km:.1f} km</b> | "
                f"Tiempo: <b>{formato_horas(ultima_ruta.tiempo_total_horas)}</b><br>"
                f"Combustible: <b>{formato_cop(ultima_ruta.combustible_total_cop)}</b> | "
                f"Peajes ({ultima_ruta.total_peajes}): <b>{formato_cop(ultima_ruta.peajes_total_cop)}</b><br>"
                f"Total viaje: <b>{formato_cop(ultima_ruta.costo_total_cop)}</b>"
            )
        leyenda = f"""
        <div style="position:fixed; bottom:24px; left:24px; z-index:9999; background:white;
                    padding:10px 14px; border:2px solid #0F4C81; border-radius:6px;
                    font-family:Arial,sans-serif; font-size:12px; max-width:390px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.2);">
            <div style="font-weight:bold; color:#0F4C81; margin-bottom:4px;">
                PERA Colombia - Red Vial Nacional (32 Capitales)
            </div>
            {resumen_html}
        </div>
        """
        mapa.get_root().html.add_child(folium.Element(leyenda))
        folium.LayerControl().add_to(mapa)
        mapa.save(str(ruta_html))
        return ruta_html

    def _renderizar_dashboard(self) -> None:
        st = self.sistema.calcular_estadisticas()
        self.var_resumen_dash.set(
            f"Capitales: {st.ciudades_activas}/{st.total_ciudades} (Aisladas: {st.ciudades_aisladas})  |  "
            f"Corredores activos: {st.rutas_activas}  |  Media Dist: {st.dist_km.media:.1f} km  |  "
            f"Mediana Peajes: {formato_cop(st.peajes_cop.mediana)}  |  Desv.Est Dist: {st.dist_km.desv_estandar:.1f} km"
        )

        for widget in self.frame_graficas.winfo_children():
            widget.destroy()

        if not MATPLOTLIB_DISPONIBLE:
            tk.Label(
                self.frame_graficas,
                text="Para visualizar el Dashboard grafico instale matplotlib:\n\npip install matplotlib",
                bg="#FFFFFF",
                fg="#B91C1C",
                font=("Segoe UI", 11, "bold"),
            ).pack(expand=True)
            return

        fig = self.construir_figura_dashboard(self.sistema)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas_dashboard = canvas

    def _accion_abrir_mapa_folium(self) -> None:
        if not FOLIUM_DISPONIBLE:
            messagebox.showwarning(
                "Folium no instalado",
                "Instale folium para abrir el mapa interactivo de Colombia:\n\npip install folium",
            )
            return
        if not self.sistema.ciudades:
            messagebox.showinfo("Sin datos", "Cargue datos o ingrese capitales antes de generar el mapa.")
            return
        ruta_html = Path(__file__).resolve().parent / "mapa_pera_colombia.html"
        self.generar_mapa_folium(self.sistema, self.ultima_ruta, ruta_html)
        webbrowser.open(ruta_html.as_uri())
        self.var_estado.set(f"Mapa interactivo generado y abierto: {ruta_html.name}")


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    acceso = VentanaAccesoPERA(root)
    if not acceso.solicitar_acceso():
        root.destroy()
        return
    root.deiconify()
    InterfazGraficaPERA(root)
    root.mainloop()


if __name__ == "__main__":
    main()
