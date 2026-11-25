"""
Universidad Popular del Cesar - Facultad de Ingenieria y Tecnologicas
Ingenieria de Sistemas - Estructura de Datos (Taller 3)
Programa de Aprendizaje de Arboles (PAA) - Arbol Binario AVL en Python 3
Autores: Kovyn Been Mena Orcasita, Damian Jose Velasquez Gonzalez,
         Sofia Isabel Tovar Rodriguez (KM-DV-ST)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ============================================================================
# CAPA 1: MODELO DE DATOS DEL ARBOL AVL
# ============================================================================
@dataclass
class NodoAVL:
    clave: int
    etiqueta: str
    altura: int = 1
    activo: bool = True
    izq: Optional["NodoAVL"] = None
    der: Optional["NodoAVL"] = None


@dataclass
class EventoBalanceo:
    tipo_rotacion: str  # "LL", "RR", "LR", "RL"
    clave_pivote: int
    fe_antes: int
    detalle: str


@dataclass
class RegistroTraza:
    operacion: str = "Inicio"
    pasos: List[str] = field(default_factory=list)
    rotaciones: List[EventoBalanceo] = field(default_factory=list)
    exito: bool = True
    mensaje_final: str = "Sistema listo."

    def reiniciar(self, operacion: str) -> None:
        self.operacion = operacion
        self.pasos.clear()
        self.rotaciones.clear()
        self.exito = False
        self.mensaje_final = ""


# ============================================================================
# CAPA 2: MOTOR DE ESTRUCTURA DE DATOS - ARBOL BINARIO AVL
# Complejidad: Insercion, Eliminacion, Busqueda, Desactivacion -> O(log n)
#              Recorridos Pre-orden, In-orden, Post-orden      -> O(n)
# ============================================================================
class ArbolAVL:
    def __init__(self) -> None:
        self.raiz: Optional[NodoAVL] = None
        self.ultima_traza = RegistroTraza()

    @staticmethod
    def obtener_altura(nodo: Optional[NodoAVL]) -> int:
        return nodo.altura if nodo else 0

    def actualizar_altura(self, nodo: Optional[NodoAVL]) -> None:
        if nodo:
            nodo.altura = 1 + max(self.obtener_altura(nodo.izq), self.obtener_altura(nodo.der))

    def factor_equilibrio(self, nodo: Optional[NodoAVL]) -> int:
        if not nodo:
            return 0
        return self.obtener_altura(nodo.izq) - self.obtener_altura(nodo.der)

    def _rotar_derecha(self, y: NodoAVL) -> NodoAVL:
        x = y.izq
        assert x is not None
        t2 = x.der
        x.der = y
        y.izq = t2
        self.actualizar_altura(y)
        self.actualizar_altura(x)
        return x

    def _rotar_izquierda(self, x: NodoAVL) -> NodoAVL:
        y = x.der
        assert y is not None
        t2 = y.izq
        y.izq = x
        x.der = t2
        self.actualizar_altura(x)
        self.actualizar_altura(y)
        return y

    def _balancear(self, nodo: Optional[NodoAVL]) -> Optional[NodoAVL]:
        if not nodo:
            return None
        self.actualizar_altura(nodo)
        fe = self.factor_equilibrio(nodo)

        if fe > 1:
            fe_izq = self.factor_equilibrio(nodo.izq)
            if fe_izq >= 0:
                self.ultima_traza.rotaciones.append(
                    EventoBalanceo(
                        "LL",
                        nodo.clave,
                        fe,
                        f"Rotacion Simple Derecha (LL) en pivote {nodo.clave} (FE=+{fe})",
                    )
                )
                return self._rotar_derecha(nodo)
            self.ultima_traza.rotaciones.append(
                EventoBalanceo(
                    "LR",
                    nodo.clave,
                    fe,
                    f"Rotacion Doble Izquierda-Derecha (LR) en pivote {nodo.clave} (FE=+{fe}, FE_izq={fe_izq})",
                )
            )
            assert nodo.izq is not None
            nodo.izq = self._rotar_izquierda(nodo.izq)
            return self._rotar_derecha(nodo)

        if fe < -1:
            fe_der = self.factor_equilibrio(nodo.der)
            if fe_der <= 0:
                self.ultima_traza.rotaciones.append(
                    EventoBalanceo(
                        "RR",
                        nodo.clave,
                        fe,
                        f"Rotacion Simple Izquierda (RR) en pivote {nodo.clave} (FE={fe})",
                    )
                )
                return self._rotar_izquierda(nodo)
            self.ultima_traza.rotaciones.append(
                EventoBalanceo(
                    "RL",
                    nodo.clave,
                    fe,
                    f"Rotacion Doble Derecha-Izquierda (RL) en pivote {nodo.clave} (FE={fe}, FE_der=+{fe_der})",
                )
            )
            assert nodo.der is not None
            nodo.der = self._rotar_derecha(nodo.der)
            return self._rotar_izquierda(nodo)

        return nodo

    def _insertar_rec(
        self, nodo: Optional[NodoAVL], clave: int, etiqueta: str, activo: bool
    ) -> Tuple[Optional[NodoAVL], bool]:
        if nodo is None:
            self.ultima_traza.pasos.append(f"Insertado nodo [{clave}]")
            return NodoAVL(clave=clave, etiqueta=etiqueta, activo=activo), True

        if clave < nodo.clave:
            self.ultima_traza.pasos.append(f"{clave} < {nodo.clave} -> Izq")
            nodo.izq, ok = self._insertar_rec(nodo.izq, clave, etiqueta, activo)
        elif clave > nodo.clave:
            self.ultima_traza.pasos.append(f"{clave} > {nodo.clave} -> Der")
            nodo.der, ok = self._insertar_rec(nodo.der, clave, etiqueta, activo)
        else:
            return nodo, False

        return self._balancear(nodo), ok

    @staticmethod
    def _minimo_nodo(nodo: NodoAVL) -> NodoAVL:
        actual = nodo
        while actual.izq is not None:
            actual = actual.izq
        return actual

    def _eliminar_rec(self, nodo: Optional[NodoAVL], clave: int) -> Tuple[Optional[NodoAVL], bool]:
        if nodo is None:
            return None, False

        if clave < nodo.clave:
            self.ultima_traza.pasos.append(f"{clave} < {nodo.clave} -> Izq")
            nodo.izq, ok = self._eliminar_rec(nodo.izq, clave)
        elif clave > nodo.clave:
            self.ultima_traza.pasos.append(f"{clave} > {nodo.clave} -> Der")
            nodo.der, ok = self._eliminar_rec(nodo.der, clave)
        else:
            ok = True
            if nodo.izq is None or nodo.der is None:
                self.ultima_traza.pasos.append(f"Eliminado nodo [{clave}] (0 o 1 hijo)")
                return (nodo.izq if nodo.izq is not None else nodo.der), True
            sucesor = self._minimo_nodo(nodo.der)
            self.ultima_traza.pasos.append(
                f"Nodo [{clave}] reemplazado por sucesor in-orden [{sucesor.clave}]"
            )
            nodo.clave = sucesor.clave
            nodo.etiqueta = sucesor.etiqueta
            nodo.activo = sucesor.activo
            nodo.der, _ = self._eliminar_rec(nodo.der, sucesor.clave)

        return self._balancear(nodo), ok

    def crear_vacio(self) -> None:
        self.raiz = None
        self.ultima_traza.reiniciar("Crear / Vaciar")
        self.ultima_traza.exito = True
        self.ultima_traza.mensaje_final = "Arbol AVL inicializado vacio."

    def insertar(self, clave: int, etiqueta: str = "", activo: bool = True) -> bool:
        self.ultima_traza.reiniciar(f"Insertar {clave}")
        etq = etiqueta.strip() if etiqueta.strip() else f"Nodo_{clave}"
        self.raiz, insertado = self._insertar_rec(self.raiz, clave, etq, activo)
        self.ultima_traza.exito = insertado
        if not insertado:
            self.ultima_traza.mensaje_final = f"La clave {clave} ya existe en el arbol AVL."
        elif not self.ultima_traza.rotaciones:
            self.ultima_traza.mensaje_final = (
                f"Clave {clave} insertada. Arbol balanceado (sin rotaciones)."
            )
        else:
            self.ultima_traza.mensaje_final = (
                f"Clave {clave} insertada -> {self.ultima_traza.rotaciones[-1].detalle}"
            )
        return insertado

    def eliminar(self, clave: int) -> bool:
        self.ultima_traza.reiniciar(f"Eliminar {clave}")
        self.raiz, eliminado = self._eliminar_rec(self.raiz, clave)
        self.ultima_traza.exito = eliminado
        if not eliminado:
            self.ultima_traza.mensaje_final = f"Clave {clave} no encontrada para eliminar."
        elif not self.ultima_traza.rotaciones:
            self.ultima_traza.mensaje_final = f"Clave {clave} eliminada. Arbol permanece balanceado."
        else:
            self.ultima_traza.mensaje_final = (
                f"Clave {clave} eliminada -> {self.ultima_traza.rotaciones[-1].detalle}"
            )
        return eliminado

    def buscar(self, clave: int) -> Optional[NodoAVL]:
        self.ultima_traza.reiniciar(f"Consultar {clave}")
        actual = self.raiz
        while actual is not None:
            if clave == actual.clave:
                self.ultima_traza.pasos.append(f"Encontrado [{clave}]")
                self.ultima_traza.exito = True
                estado = "ACTIVO" if actual.activo else "DESACTIVADO"
                self.ultima_traza.mensaje_final = (
                    f"Encontrado: Clave={actual.clave} | Etiqueta={actual.etiqueta} | "
                    f"Altura={actual.altura} | FE={self.factor_equilibrio(actual)} | Estado={estado}"
                )
                return actual
            if clave < actual.clave:
                self.ultima_traza.pasos.append(f"{clave} < {actual.clave} -> Izq")
                actual = actual.izq
            else:
                self.ultima_traza.pasos.append(f"{clave} > {actual.clave} -> Der")
                actual = actual.der
        self.ultima_traza.exito = False
        self.ultima_traza.mensaje_final = f"Clave {clave} no existe en el arbol."
        return None

    def cambiar_estado_activo(self, clave: int, nuevo_estado: bool) -> bool:
        nodo = self.buscar(clave)
        accion = "Reactivar" if nuevo_estado else "Desactivar"
        self.ultima_traza.operacion = f"{accion} {clave}"
        if nodo is None:
            self.ultima_traza.exito = False
            self.ultima_traza.mensaje_final = f"Clave {clave} no encontrada."
            return False
        nodo.activo = nuevo_estado
        self.ultima_traza.exito = True
        estado_txt = "ACTIVO." if nuevo_estado else "DESACTIVADO (estructura AVL intacta)."
        self.ultima_traza.mensaje_final = f"Nodo {clave} marcado como {estado_txt}"
        return True

    def modificar(self, clave_actual: int, nueva_clave: int, nueva_etiqueta: str) -> bool:
        nodo = self.buscar(clave_actual)
        if nodo is None:
            self.ultima_traza.operacion = f"Modificar {clave_actual}"
            self.ultima_traza.exito = False
            self.ultima_traza.mensaje_final = f"Clave {clave_actual} no encontrada."
            return False

        etq_final = nueva_etiqueta.strip() if nueva_etiqueta.strip() else nodo.etiqueta
        if nueva_clave == clave_actual:
            nodo.etiqueta = etq_final
            self.ultima_traza.reiniciar(f"Modificar {clave_actual}")
            self.ultima_traza.exito = True
            self.ultima_traza.mensaje_final = (
                f"Etiqueta del nodo {clave_actual} actualizada a '{etq_final}'."
            )
            return True

        if self.buscar(nueva_clave) is not None:
            self.ultima_traza.reiniciar(f"Modificar {clave_actual}")
            self.ultima_traza.exito = False
            self.ultima_traza.mensaje_final = (
                f"No se puede cambiar clave: ya existe el nodo {nueva_clave}."
            )
            return False

        estado_previo = nodo.activo
        self.eliminar(clave_actual)
        self.insertar(nueva_clave, etq_final, estado_previo)
        self.ultima_traza.operacion = f"Modificar clave {clave_actual} -> {nueva_clave}"
        self.ultima_traza.mensaje_final = (
            f"Clave reubicada de {clave_actual} a {nueva_clave} con rebalanceo AVL."
        )
        return True

    def pre_orden(self) -> List[NodoAVL]:
        res: List[NodoAVL] = []

        def _rec(n: Optional[NodoAVL]) -> None:
            if n is None:
                return
            res.append(n)
            _rec(n.izq)
            _rec(n.der)

        _rec(self.raiz)
        return res

    def in_orden(self) -> List[NodoAVL]:
        res: List[NodoAVL] = []

        def _rec(n: Optional[NodoAVL]) -> None:
            if n is None:
                return
            _rec(n.izq)
            res.append(n)
            _rec(n.der)

        _rec(self.raiz)
        return res

    def post_orden(self) -> List[NodoAVL]:
        res: List[NodoAVL] = []

        def _rec(n: Optional[NodoAVL]) -> None:
            if n is None:
                return
            _rec(n.izq)
            _rec(n.der)
            res.append(n)

        _rec(self.raiz)
        return res

    def total_nodos(self) -> int:
        return len(self.in_orden())

    def total_activos(self) -> int:
        return sum(1 for n in self.in_orden() if n.activo)

    def altura_total(self) -> int:
        return self.obtener_altura(self.raiz)

    @staticmethod
    def formatear_recorrido(lista: List[NodoAVL]) -> str:
        if not lista:
            return "(vacio)"
        return " -> ".join(f"{n.clave}{'' if n.activo else '*'}" for n in lista)


# ============================================================================
# CAPA 3: PERSISTENCIA COMPARTIDA C++ <-> PYTHON (datos_avl.txt)
# ============================================================================
class PersistenciaAVL:
    @staticmethod
    def resolver_ruta(nombre_archivo: str = "datos_avl.txt") -> Path:
        local = Path(nombre_archivo)
        if local.exists():
            return local
        return Path(__file__).resolve().parent / nombre_archivo

    @classmethod
    def cargar(cls, arbol: ArbolAVL, nombre_archivo: str = "datos_avl.txt") -> Tuple[bool, int]:
        ruta = cls.resolver_ruta(nombre_archivo)
        if not ruta.exists():
            return False, 0

        arbol.crear_vacio()
        cargados = 0
        with ruta.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                limpia = linea.strip()
                if not limpia or limpia.startswith("#"):
                    continue
                partes = limpia.split(";")
                if len(partes) != 3:
                    continue
                try:
                    clave = int(partes[0].strip())
                    etiqueta = partes[1].strip()
                    activo = partes[2].strip() != "0"
                    if arbol.insertar(clave, etiqueta, activo):
                        cargados += 1
                except ValueError:
                    continue
        return True, cargados

    @classmethod
    def guardar(cls, arbol: ArbolAVL, nombre_archivo: str = "datos_avl.txt") -> bool:
        ruta = cls.resolver_ruta(nombre_archivo)
        try:
            with ruta.open("w", encoding="utf-8", newline="\n") as archivo:
                archivo.write("# Persistencia Taller 3 - Programa de Aprendizaje de Arboles (AVL)\n")
                archivo.write("# Formato: clave;etiqueta;activo (1=Activo, 0=Desactivado)\n")
                for nodo in arbol.pre_orden():
                    estado = 1 if nodo.activo else 0
                    archivo.write(f"{nodo.clave};{nodo.etiqueta};{estado}\n")
            return True
        except OSError:
            return False


if __name__ == "__main__":
    arbol_prueba = ArbolAVL()
    ok, cant = PersistenciaAVL.cargar(arbol_prueba)
    print(f"Carga datos_avl.txt: ok={ok}, nodos={cant}")
    print("Pre-orden :", arbol_prueba.formatear_recorrido(arbol_prueba.pre_orden()))
    print("In-orden  :", arbol_prueba.formatear_recorrido(arbol_prueba.in_orden()))
    print("Post-orden:", arbol_prueba.formatear_recorrido(arbol_prueba.post_orden()))
