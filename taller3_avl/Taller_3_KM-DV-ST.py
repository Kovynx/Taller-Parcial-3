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
from typing import Dict, List, Optional, Set, Tuple
import tkinter as tk
from tkinter import messagebox, ttk


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


# ============================================================================
# CAPA 4: INTERFAZ GRAFICA VISUAL EN TKINTER (RECORRIDOS SIEMPRE VISIBLES)
# ============================================================================
class InterfazGraficaPAA:
    ARCHIVO_DATOS = "datos_avl.txt"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PAA - Programa de Aprendizaje de Arboles AVL (UPC | KM-DV-ST)")
        self.root.geometry("1220x740")
        self.root.minsize(980, 620)
        self.root.configure(bg="#F4F6F8")

        self.arbol = ArbolAVL()
        self.nodos_resaltados: Set[int] = set()
        self.botones_accion: List[tk.Button] = []
        self.demo_en_curso = False

        self._construir_ui()
        self.root.after(150, self._preguntar_carga_inicial)

    def _construir_ui(self) -> None:
        # Barra superior institucional
        barra_sup = tk.Frame(self.root, bg="#1B5E20", height=54)
        barra_sup.pack(side=tk.TOP, fill=tk.X)
        barra_sup.pack_propagate(False)

        tk.Label(
            barra_sup,
            text="UNIVERSIDAD POPULAR DEL CESAR  |  PAA - ARBOL BINARIO AVL",
            bg="#1B5E20",
            fg="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
        ).pack(side=tk.LEFT, padx=16)

        self.lbl_resumen = tk.Label(
            barra_sup,
            text="Nodos: 0 | Activos: 0 | Altura: 0",
            bg="#2E7D32",
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=4,
        )
        self.lbl_resumen.pack(side=tk.RIGHT, padx=16, pady=10)

        # Franja inferior fija: Recorridos SIEMPRE VISIBLES
        panel_recorridos = tk.Frame(self.root, bg="#1E293B", padx=14, pady=8)
        panel_recorridos.pack(side=tk.BOTTOM, fill=tk.X)

        self.var_pre = tk.StringVar(value="(vacio)")
        self.var_in = tk.StringVar(value="(vacio)")
        self.var_post = tk.StringVar(value="(vacio)")

        for titulo, var, color in [
            ("PRE-ORDEN :", self.var_pre, "#38BDF8"),
            ("IN-ORDEN  :", self.var_in, "#4ADE80"),
            ("POST-ORDEN:", self.var_post, "#FBBF24"),
        ]:
            fila = tk.Frame(panel_recorridos, bg="#1E293B")
            fila.pack(fill=tk.X, pady=1)
            tk.Label(
                fila,
                text=titulo,
                bg="#1E293B",
                fg=color,
                font=("Consolas", 10, "bold"),
                width=12,
                anchor="w",
            ).pack(side=tk.LEFT)
            tk.Label(
                fila,
                textvariable=var,
                bg="#1E293B",
                fg="#F8FAFC",
                font=("Consolas", 10),
                anchor="w",
                justify="left",
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Cuerpo central dividido: Panel de control izquierdo + Lienzo derecho
        cuerpo = tk.Frame(self.root, bg="#F4F6F8")
        cuerpo.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=8)

        panel_izq = tk.Frame(cuerpo, bg="#FFFFFF", width=320, bd=1, relief=tk.SOLID)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        panel_izq.pack_propagate(False)

        tk.Label(
            panel_izq,
            text="Gestion de Nodos AVL",
            bg="#FFFFFF",
            fg="#1E293B",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 6))

        form = tk.Frame(panel_izq, bg="#FFFFFF")
        form.pack(fill=tk.X, padx=12)

        self.var_clave = tk.StringVar()
        self.var_etiqueta = tk.StringVar()
        self.var_nueva_clave = tk.StringVar()

        for lbl, var in [
            ("Clave (entero):", self.var_clave),
            ("Etiqueta (opcional):", self.var_etiqueta),
            ("Nueva clave (solo modificar):", self.var_nueva_clave),
        ]:
            tk.Label(form, text=lbl, bg="#FFFFFF", fg="#334155", font=("Segoe UI", 9)).pack(
                anchor="w", pady=(4, 1)
            )
            ttk.Entry(form, textvariable=var).pack(fill=tk.X, pady=(0, 2))

        grid_btns = tk.Frame(panel_izq, bg="#FFFFFF")
        grid_btns.pack(fill=tk.X, padx=12, pady=8)
        grid_btns.columnconfigure(0, weight=1)
        grid_btns.columnconfigure(1, weight=1)

        especificacion_botones = [
            ("Insertar", "#2E7D32", self._accion_insertar, 0, 0),
            ("Eliminar", "#C62828", self._accion_eliminar, 0, 1),
            ("Desactivar/Activar", "#455A64", self._accion_toggle_activo, 1, 0),
            ("Consultar", "#1565C0", self._accion_consultar, 1, 1),
            ("Modificar", "#6A1B9A", self._accion_modificar, 2, 0),
            ("Crear Vacio", "#546E7A", self._accion_vaciar, 2, 1),
            ("Cargar Archivo", "#00695C", self._accion_cargar, 3, 0),
            ("Guardar Archivo", "#0277BD", self._accion_guardar, 3, 1),
        ]

        for texto, color, cmd, r, c in especificacion_botones:
            btn = tk.Button(
                grid_btns,
                text=texto,
                bg=color,
                fg="#FFFFFF",
                activebackground=color,
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
                pady=5,
                command=cmd,
            )
            btn.grid(row=r, column=c, sticky="ew", padx=3, pady=3)
            self.botones_accion.append(btn)

        btn_demo = tk.Button(
            panel_izq,
            text="> Demo Pedagogico (4 Rotaciones)",
            bg="#EF6C00",
            fg="#FFFFFF",
            activebackground="#E65100",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            pady=7,
            command=self._iniciar_demo,
        )
        btn_demo.pack(fill=tk.X, padx=15, pady=(4, 4))
        self.botones_accion.append(btn_demo)

        btn_vars = tk.Button(
            panel_izq,
            text="Variables de Entrada / Salida",
            bg="#334155",
            fg="#FFFFFF",
            activebackground="#1E293B",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 9),
            cursor="hand2",
            pady=5,
            command=self._mostrar_variables_modelo,
        )
        btn_vars.pack(fill=tk.X, padx=15, pady=(0, 8))
        self.botones_accion.append(btn_vars)

        # Bitacora pedagogica de balanceo y comparaciones
        tk.Label(
            panel_izq,
            text="Traza de Ordenamiento y Balanceo",
            bg="#FFFFFF",
            fg="#1E293B",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=12, pady=(2, 4))

        self.txt_traza = tk.Text(
            panel_izq,
            height=11,
            bg="#F8FAFC",
            fg="#0F172A",
            font=("Consolas", 9),
            wrap=tk.WORD,
            bd=1,
            relief=tk.SOLID,
            state=tk.DISABLED,
        )
        self.txt_traza.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        # Panel derecho: Estado actual + Lienzo grafico del arbol AVL
        panel_der = tk.Frame(cuerpo, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        panel_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        barra_estado = tk.Frame(panel_der, bg="#E2E8F0", height=36)
        barra_estado.pack(side=tk.TOP, fill=tk.X)
        barra_estado.pack_propagate(False)

        self.var_estado = tk.StringVar(value="Listo. Seleccione una operacion en el panel izquierdo.")
        tk.Label(
            barra_estado,
            textvariable=self.var_estado,
            bg="#E2E8F0",
            fg="#0F172A",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        tk.Label(
            barra_estado,
            text="Verde: FE=0 | Azul: FE=+-1 | Naranja: Rotacion/Paso | Gris*: Desactivado",
            bg="#E2E8F0",
            fg="#475569",
            font=("Segoe UI", 8),
        ).pack(side=tk.RIGHT, padx=10)

        self.canvas = tk.Canvas(panel_der, bg="#FFFFFF", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self._dibujar_arbol())

    def _preguntar_carga_inicial(self) -> None:
        cargar = messagebox.askyesno(
            "Carga Inicial - PAA (AVL)",
            "Desea cargar los datos iniciales desde 'datos_avl.txt'?\n\n"
            "- Si: Cargar nodos almacenados.\n"
            "- No: Iniciar el programa sin datos (arbol vacio).",
        )
        if cargar:
            ok, cant = PersistenciaAVL.cargar(self.arbol, self.ARCHIVO_DATOS)
            if ok:
                self.var_estado.set(f"Cargados {cant} nodos desde '{self.ARCHIVO_DATOS}'.")
            else:
                self.var_estado.set(
                    f"No se encontro '{self.ARCHIVO_DATOS}'. Sesion iniciada sin datos."
                )
        else:
            self.arbol.crear_vacio()
            self.var_estado.set("Sesion iniciada sin datos (arbol vacio).")
        self._refrescar_vista()

    def _leer_clave(self, var: tk.StringVar, nombre_campo: str) -> Optional[int]:
        texto = var.get().strip()
        if not texto:
            messagebox.showwarning("Dato requerido", f"Debe ingresar un entero en '{nombre_campo}'.")
            return None
        try:
            return int(texto)
        except ValueError:
            messagebox.showerror("Dato invalido", f"'{nombre_campo}' debe ser un numero entero.")
            return None

    def _establecer_botones_habilitados(self, habilitado: bool) -> None:
        estado = tk.NORMAL if habilitado else tk.DISABLED
        for btn in self.botones_accion:
            btn.configure(state=estado)

    def _resaltar_temporalmente(self, claves: Set[int], duracion_ms: int = 850) -> None:
        self.nodos_resaltados = set(claves)
        self._dibujar_arbol()
        if claves:
            self.root.after(duracion_ms, self._limpiar_resaltado)

    def _limpiar_resaltado(self) -> None:
        self.nodos_resaltados.clear()
        self._dibujar_arbol()

    def _accion_insertar(self) -> None:
        clave = self._leer_clave(self.var_clave, "Clave")
        if clave is None:
            return
        etq = self.var_etiqueta.get().strip()
        insertado = self.arbol.insertar(clave, etq, True)
        destacados = {clave}
        for rot in self.arbol.ultima_traza.rotaciones:
            destacados.add(rot.clave_pivote)
        self.var_estado.set(self.arbol.ultima_traza.mensaje_final)
        self._refrescar_vista()
        if insertado:
            self._resaltar_temporalmente(destacados)
            self.var_clave.set("")
            self.var_etiqueta.set("")

    def _accion_eliminar(self) -> None:
        clave = self._leer_clave(self.var_clave, "Clave")
        if clave is None:
            return
        self.arbol.eliminar(clave)
        destacados = {rot.clave_pivote for rot in self.arbol.ultima_traza.rotaciones}
        self.var_estado.set(self.arbol.ultima_traza.mensaje_final)
        self._refrescar_vista()
        if destacados:
            self._resaltar_temporalmente(destacados)

    def _accion_toggle_activo(self) -> None:
        clave = self._leer_clave(self.var_clave, "Clave")
        if clave is None:
            return
        nodo = self.arbol.buscar(clave)
        if nodo is None:
            self.var_estado.set(self.arbol.ultima_traza.mensaje_final)
            self._refrescar_vista()
            return
        self.arbol.cambiar_estado_activo(clave, not nodo.activo)
        self.var_estado.set(self.arbol.ultima_traza.mensaje_final)
        self._refrescar_vista()
        self._resaltar_temporalmente({clave})

    def _accion_consultar(self) -> None:
        clave = self._leer_clave(self.var_clave, "Clave")
        if clave is None:
            return
        nodo = self.arbol.buscar(clave)
        self.var_estado.set(self.arbol.ultima_traza.mensaje_final)
        self._refrescar_vista()
        if nodo is not None:
            self._resaltar_temporalmente({clave}, 1200)

    def _accion_modificar(self) -> None:
        clave_actual = self._leer_clave(self.var_clave, "Clave")
        if clave_actual is None:
            return
        nueva_txt = self.var_nueva_clave.get().strip()
        if nueva_txt:
            nueva_clave = self._leer_clave(self.var_nueva_clave, "Nueva clave")
            if nueva_clave is None:
                return
        else:
            nueva_clave = clave_actual
        nueva_etq = self.var_etiqueta.get().strip()
        ok = self.arbol.modificar(clave_actual, nueva_clave, nueva_etq)
        self.var_estado.set(self.arbol.ultima_traza.mensaje_final)
        self._refrescar_vista()
        if ok:
            self._resaltar_temporalmente({nueva_clave})
            self.var_nueva_clave.set("")

    def _accion_vaciar(self) -> None:
        self.arbol.crear_vacio()
        self.var_estado.set(self.arbol.ultima_traza.mensaje_final)
        self._refrescar_vista()

    def _accion_cargar(self) -> None:
        ok, cant = PersistenciaAVL.cargar(self.arbol, self.ARCHIVO_DATOS)
        if ok:
            self.var_estado.set(f"Recargados {cant} nodos desde '{self.ARCHIVO_DATOS}'.")
        else:
            self.var_estado.set(f"No se encontro '{self.ARCHIVO_DATOS}'.")
        self._refrescar_vista()

    def _accion_guardar(self) -> None:
        if PersistenciaAVL.guardar(self.arbol, self.ARCHIVO_DATOS):
            self.var_estado.set(f"Datos guardados correctamente en '{self.ARCHIVO_DATOS}'.")
        else:
            messagebox.showerror("Error", f"No se pudo guardar en '{self.ARCHIVO_DATOS}'.")

    def _mostrar_variables_modelo(self) -> None:
        texto = (
            "VARIABLES DE ENTRADA DEL MODELO AVL:\n"
            "  1. opcionCargaInicial (bool): Cargar archivo o iniciar vacio.\n"
            "  2. clave (int): Clave numerica unica de ordenamiento.\n"
            "  3. etiqueta (str): Nombre o concepto asociado al nodo.\n"
            "  4. activo (bool): Estado logico (Activo / Desactivado).\n\n"
            "VARIABLES DE SALIDA DEL MODELO AVL:\n"
            "  1. altura (int) y Factor de Equilibrio FE = h(izq) - h(der).\n"
            "  2. rotacionAplicada (LL, RR, LR, RL) y traza de comparaciones.\n"
            "  3. Recorridos Pre-orden, In-orden y Post-orden siempre visibles.\n"
            "  4. Representacion grafica 2D del arbol balanceado."
        )
        messagebox.showinfo("Variables de Entrada y Salida - PAA", texto)

    def _iniciar_demo(self) -> None:
        if self.demo_en_curso:
            return
        self.demo_en_curso = True
        self._establecer_botones_habilitados(False)
        self.arbol.crear_vacio()
        self._refrescar_vista()

        secuencia = [
            (10, "Demo_10"),
            (20, "Demo_20"),
            (30, "Demo_30_RR"),
            (5, "Demo_5"),
            (3, "Demo_3_LL"),
            (8, "Demo_8_LR"),
            (25, "Demo_25_RL"),
        ]
        self.root.after(400, lambda: self._ejecutar_paso_demo(secuencia, 0))

    def _ejecutar_paso_demo(self, secuencia: List[Tuple[int, str]], indice: int) -> None:
        if indice >= len(secuencia):
            self.demo_en_curso = False
            self._establecer_botones_habilitados(True)
            self.nodos_resaltados.clear()
            self.var_estado.set(
                "Demo completado: se ejecutaron las 4 rotaciones AVL (RR -> LL -> LR -> RL)."
            )
            self._dibujar_arbol()
            return

        clave, etq = secuencia[indice]
        self.arbol.insertar(clave, etq, True)
        traza = self.arbol.ultima_traza
        rot_txt = traza.rotaciones[-1].detalle if traza.rotaciones else "Sin rotacion"
        self.var_estado.set(
            f"Demo - Paso {indice + 1}/{len(secuencia)}: Insertando {clave} -> {rot_txt}"
        )

        destacados = {clave}
        for rot in traza.rotaciones:
            destacados.add(rot.clave_pivote)
        self.nodos_resaltados = destacados
        self._refrescar_vista()

        self.root.after(800, self._limpiar_resaltado)
        self.root.after(1400, lambda: self._ejecutar_paso_demo(secuencia, indice + 1))

    def _refrescar_vista(self) -> None:
        self.lbl_resumen.configure(
            text=(
                f"Nodos: {self.arbol.total_nodos()}  |  "
                f"Activos: {self.arbol.total_activos()}  |  "
                f"Altura: {self.arbol.altura_total()}"
            )
        )
        self.var_pre.set(self.arbol.formatear_recorrido(self.arbol.pre_orden()))
        self.var_in.set(self.arbol.formatear_recorrido(self.arbol.in_orden()))
        self.var_post.set(self.arbol.formatear_recorrido(self.arbol.post_orden()))

        traza = self.arbol.ultima_traza
        lineas = [
            f"Operacion: {traza.operacion}",
            f"Resultado: {traza.mensaje_final}",
            "",
            "Comparaciones:",
        ]
        if traza.pasos:
            lineas.extend(f"  - {p}" for p in traza.pasos)
        else:
            lineas.append("  (sin pasos)")

        lineas.append("")
        lineas.append("Rotaciones AVL:")
        if traza.rotaciones:
            lineas.extend(f"  * {r.detalle}" for r in traza.rotaciones)
        else:
            lineas.append("  Ninguna (|FE| <= 1)")

        self.txt_traza.configure(state=tk.NORMAL)
        self.txt_traza.delete("1.0", tk.END)
        self.txt_traza.insert(tk.END, "\n".join(lineas))
        self.txt_traza.configure(state=tk.DISABLED)

        self._dibujar_arbol()

    def _calcular_posiciones(self) -> Dict[int, Tuple[float, float]]:
        posiciones: Dict[int, Tuple[float, float]] = {}
        if self.arbol.raiz is None:
            return posiciones

        ancho = max(self.canvas.winfo_width(), 720)
        alto = max(self.canvas.winfo_height(), 460)
        altura_arbol = max(self.arbol.altura_total(), 1)
        paso_y = min(92.0, (alto - 90.0) / max(altura_arbol, 1))

        def _asignar(nodo: Optional[NodoAVL], x_min: float, x_max: float, nivel: int) -> None:
            if nodo is None:
                return
            cx = (x_min + x_max) / 2.0
            cy = 48.0 + nivel * paso_y
            posiciones[nodo.clave] = (cx, cy)
            _asignar(nodo.izq, x_min, cx, nivel + 1)
            _asignar(nodo.der, cx, x_max, nivel + 1)

        _asignar(self.arbol.raiz, 24.0, float(ancho - 24), 0)
        return posiciones

    def _dibujar_arbol(self) -> None:
        self.canvas.delete("all")
        if self.arbol.raiz is None:
            ancho = max(self.canvas.winfo_width(), 720)
            alto = max(self.canvas.winfo_height(), 460)
            self.canvas.create_text(
                ancho / 2,
                alto / 2,
                text="Arbol AVL vacio.\nInserte un nodo, cargue 'datos_avl.txt' o ejecute el Demo Pedagogico.",
                fill="#64748B",
                font=("Segoe UI", 12),
                justify=tk.CENTER,
            )
            return

        posiciones = self._calcular_posiciones()
        radio = 24 if self.arbol.altura_total() <= 4 else 19

        # Dibujar aristas primero
        def _dibujar_aristas(nodo: Optional[NodoAVL]) -> None:
            if nodo is None:
                return
            x1, y1 = posiciones[nodo.clave]
            for hijo in (nodo.izq, nodo.der):
                if hijo is not None:
                    x2, y2 = posiciones[hijo.clave]
                    self.canvas.create_line(x1, y1, x2, y2, fill="#94A3B8", width=2)
                    _dibujar_aristas(hijo)

        _dibujar_aristas(self.arbol.raiz)

        # Dibujar nodos encima
        def _dibujar_nodos(nodo: Optional[NodoAVL]) -> None:
            if nodo is None:
                return
            cx, cy = posiciones[nodo.clave]
            fe = self.arbol.factor_equilibrio(nodo)

            if nodo.clave in self.nodos_resaltados:
                relleno, borde, dash = "#EF6C00", "#BF360C", ()
            elif not nodo.activo:
                relleno, borde, dash = "#90A4AE", "#455A64", (4, 2)
            elif fe == 0:
                relleno, borde, dash = "#2E7D32", "#1B5E20", ()
            else:
                relleno, borde, dash = "#1565C0", "#0D47A1", ()

            self.canvas.create_oval(
                cx - radio,
                cy - radio,
                cx + radio,
                cy + radio,
                fill=relleno,
                outline=borde,
                width=2,
                dash=dash,
            )
            texto_clave = f"{nodo.clave}" if nodo.activo else f"{nodo.clave}*"
            self.canvas.create_text(
                cx, cy - 3, text=texto_clave, fill="#FFFFFF", font=("Segoe UI", 10, "bold")
            )
            fe_str = f"FE:{'+' if fe > 0 else ''}{fe}"
            self.canvas.create_text(
                cx, cy + 10, text=fe_str, fill="#E2E8F0", font=("Segoe UI", 7, "bold")
            )

            etq_corta = nodo.etiqueta if len(nodo.etiqueta) <= 13 else nodo.etiqueta[:11] + ".."
            self.canvas.create_text(
                cx, cy + radio + 11, text=etq_corta, fill="#334155", font=("Segoe UI", 8)
            )
            _dibujar_nodos(nodo.izq)
            _dibujar_nodos(nodo.der)

        _dibujar_nodos(self.arbol.raiz)


def main() -> None:
    root = tk.Tk()
    InterfazGraficaPAA(root)
    root.mainloop()


if __name__ == "__main__":
    main()
