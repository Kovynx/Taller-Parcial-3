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


if __name__ == "__main__":
    s = SistemaPERA()
    assert PersistenciaPERA.cargar(s)
    for c in (1, 2, 3, 4):
        r = s.calcular_ruta_optima(16, 1, c)
        print(
            f"{r.criterio} -> {r.distancia_total_km:.1f} km | {formato_horas(r.tiempo_total_horas)} | "
            f"Comb: {formato_cop(r.combustible_total_cop)} | Peajes: {formato_cop(r.peajes_total_cop)}"
        )
