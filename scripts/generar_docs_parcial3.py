"""
Generador de diagramas UML (PNG 220 DPI) y especificacion tecnica IEEE 830 (.docx)
para el Parcial 3 - Programa Estadistico de Rutas de Automoviles (PERA - Colombia).
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Circle

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent.parent
PERA_DIR = ROOT / "parcial3_pera"
DOCS_DIR = PERA_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def _dibujar_actor(ax, x: float, y: float, etiqueta: str) -> None:
    ax.add_patch(Circle((x, y + 0.45), 0.16, fill=False, ec="#1B5E20", lw=2))
    ax.plot([x, x], [y + 0.29, y - 0.18], color="#1B5E20", lw=2)
    ax.plot([x - 0.25, x + 0.25], [y + 0.12, y + 0.12], color="#1B5E20", lw=2)
    ax.plot([x, x - 0.22], [y - 0.18, y - 0.55], color="#1B5E20", lw=2)
    ax.plot([x, x + 0.22], [y - 0.18, y - 0.55], color="#1B5E20", lw=2)
    ax.text(x, y - 0.85, etiqueta, ha="center", va="top", fontsize=9, fontweight="bold", color="#0F172A")


def generar_uml_casos_uso(ruta_salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.0, 7.4), dpi=220)
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 8.2)
    ax.axis("off")

    sistema = FancyBboxPatch((2.6, 0.4), 9.6, 7.4, boxstyle="round,pad=0.12", fc="#F8FAFC", ec="#1B5E20", lw=2)
    ax.add_patch(sistema)
    ax.text(7.4, 7.55, "Sistema PERA - Programa Estadistico de Rutas de Automoviles (Colombia)", ha="center", va="center", fontsize=11, fontweight="bold", color="#1B5E20")

    _dibujar_actor(ax, 1.1, 4.6, "Analista /\nUsuario")

    casos_izq = [
        (5.0, 7.0, "Cargar datos_pera.txt\n(32 capitales, 48 corredores)"),
        (5.0, 6.0, "CRUD de ciudades\n(alta, baja, modificacion)"),
        (5.0, 5.0, "CRUD de rutas y peajes\n(alta, baja, modificacion)"),
        (5.0, 4.0, "Desactivar / Reactivar\ntramo vial"),
        (5.0, 3.0, "Consultar y validar\ntramos (categoria)"),
        (5.0, 2.0, "Calcular ruta optima\n(Dijkstra 4 metricas)"),
    ]

    casos_der = [
        (9.9, 7.0, "Guardar / Cargar\npersistencia compartida"),
        (9.9, 5.0, "Sincronizar 3 grafos\n(Distancia, Combustible, Peajes)"),
        (9.9, 3.0, "Generar Dashboard\nmatplotlib (4 graficos)"),
        (9.9, 1.5, "Generar mapa interactivo\nFolium (bono)"),
    ]

    for cx, cy, txt in casos_izq:
        ax.add_patch(Ellipse((cx, cy), 3.4, 0.74, fc="#E8F5E9", ec="#2E7D32", lw=1.6))
        ax.text(cx, cy, txt, ha="center", va="center", fontsize=8.2, color="#0F172A", fontweight="bold")
        ax.plot([1.45, cx - 1.70], [4.65, cy], color="#334155", lw=1.3)

    for cx, cy, txt in casos_der:
        ax.add_patch(Ellipse((cx, cy), 3.4, 0.82, fc="#E3F2FD", ec="#1565C0", lw=1.6))
        ax.text(cx, cy, txt, ha="center", va="center", fontsize=8.2, color="#0F172A", fontweight="bold")

    inclusiones = [
        ((6.70, 7.00), (8.20, 7.00), "<<extend>>", 0.0, 0.16),
        ((6.70, 6.00), (8.20, 5.30), "<<include>>", 0.05, 0.18),
        ((6.70, 5.00), (8.20, 5.00), "<<include>>", 0.0, 0.16),
        ((6.70, 4.00), (8.20, 4.70), "<<include>>", 0.05, -0.22),
        ((6.70, 3.00), (8.20, 3.00), "<<include>>", 0.0, 0.16),
        ((6.70, 2.00), (8.20, 2.75), "<<include>>", -0.10, 0.18),
        ((6.70, 2.00), (8.20, 1.55), "<<extend>>", 0.0, -0.22),
    ]
    for (x1, y1), (x2, y2), label, dx, dy in inclusiones:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", ls="--", color="#1565C0", lw=1.2))
        mx, my = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=7.5, color="#1565C0", style="italic")

    plt.tight_layout()
    fig.savefig(ruta_salida, bbox_inches="tight")
    plt.close(fig)


def generar_uml_secuencia(ruta_salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.2, 7.6), dpi=220)
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0, 8.4)
    ax.axis("off")

    ax.text(7.1, 8.1, "Diagrama de Secuencia UML - Calculo de Ruta Optima en los 3 Grafos y Renderizado", ha="center", va="center", fontsize=11.5, fontweight="bold", color="#1B5E20")

    participantes = [
        (1.2, "Usuario"),
        (3.8, "InterfazPERA\n(C++ / Tkinter)"),
        (6.8, "MotorGrafos\n(Dijkstra)"),
        (10.0, "PersistenciaPERA\n(datos_pera.txt)"),
        (12.9, "Visualizador\n(matplotlib / Folium)"),
    ]

    for x, nombre in participantes:
        caja = FancyBboxPatch((x - 1.1, 6.95), 2.2, 0.72, boxstyle="round,pad=0.06", fc="#E8F5E9", ec="#1B5E20", lw=1.6)
        ax.add_patch(caja)
        ax.text(x, 7.31, nombre, ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0F172A")
        ax.plot([x, x], [6.95, 0.45], ls="--", color="#64748B", lw=1.3)

    frag = FancyBboxPatch((5.6, 3.05), 5.0, 1.48, boxstyle="square,pad=0.05", fc="#FFF7ED", ec="#EA580C", lw=1.3, ls="--")
    ax.add_patch(frag)
    ax.text(5.75, 4.35, "loop [para cada grafo G en {Dist, Comb, Peajes}]", ha="left", va="center", fontsize=8, fontweight="bold", color="#C2410C")

    mensajes = [
        (1.2, 3.8, 6.4, "1: autenticar() y solicitarRuta(origen, destino)", False),
        (3.8, 6.8, 5.85, "2: calcularRutaOptima(G, origen, destino)", False),
        (6.8, 6.8, 5.25, "3: relajar aristas activas (Min-Heap)", False),
        (6.8, 6.8, 3.82, "4: reconstruir camino y 4 metricas", False),
        (6.8, 3.8, 2.6, "5: retornar ResultadoRuta (km, h, comb, peajes)", True),
        (3.8, 12.9, 1.98, "6: renderizarDashboard(estadisticas)", False),
        (3.8, 12.9, 1.40, "7: generarMapaFolium(redColombia, rutaOptima)", False),
        (3.8, 10.0, 0.88, "8: guardarPersistencia(datos_pera.txt)", False),
        (10.0, 3.8, 0.48, "9: confirmacionOK", True),
    ]

    for x1, x2, y, texto, retorno in mensajes:
        estilo = "--" if retorno else "-"
        color = "#1565C0" if retorno else "#0F172A"
        if x1 == x2:
            ax.plot([x1, x1 + 0.65, x1 + 0.65, x1], [y + 0.16, y + 0.16, y - 0.16, y - 0.16], color="#0F172A", lw=1.3)
            ax.annotate("", xy=(x1, y - 0.16), xytext=(x1 + 0.2, y - 0.16), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
            ax.text(x1 + 0.72, y, texto, ha="left", va="center", fontsize=8, color="#0F172A")
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", ls=estilo, color=color, lw=1.4))
            ax.text((x1 + x2) / 2, y + 0.11, texto, ha="center", va="bottom", fontsize=8, color=color)

    plt.tight_layout()
    fig.savefig(ruta_salida, bbox_inches="tight")
    plt.close(fig)


def generar_uml_estados(ruta_salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.8, 6.6), dpi=220)
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    ax.text(6.2, 6.85, "Diagrama de Estados UML - Ciclo de Vida de un Tramo Vial en PERA", ha="center", va="center", fontsize=11.5, fontweight="bold", color="#1B5E20")

    ax.add_patch(Circle((0.8, 4.0), 0.18, fc="#0F172A", ec="#0F172A"))
    ax.add_patch(Circle((11.7, 1.6), 0.22, fill=False, ec="#0F172A", lw=1.8))
    ax.add_patch(Circle((11.7, 1.6), 0.13, fc="#0F172A", ec="#0F172A"))

    estados = [
        (1.9, 3.4, 2.4, 1.0, "Activo\n(tramo habilitado)", "#E8F5E9", "#1B5E20"),
        (5.6, 4.9, 2.6, 1.0, "En Calculo\n(Dijkstra en ejecucion)", "#FFF7ED", "#EA580C"),
        (9.2, 3.4, 2.4, 1.0, "Validado\n(categoria y peaje OK)", "#E3F2FD", "#1565C0"),
        (1.9, 0.9, 2.4, 1.0, "Desactivado\n(cierre vial)", "#F1F5F9", "#475569"),
        (5.6, 0.9, 2.6, 1.0, "Eliminado\n(baja logica/fisica)", "#FEF2F2", "#B91C1C"),
    ]

    for x, y, w, h, txt, fc, ec in estados:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec=ec, lw=1.8)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0F172A")

    transiciones = [
        ((0.98, 4.0), (1.85, 4.0), "altaRuta()", 0.0, 0.20),
        ((4.35, 3.9), (5.55, 5.35), "calcularRuta()", -0.45, 0.28),
        ((8.25, 5.35), (9.15, 4.45), "validarCategoria()", 0.55, 0.24),
        ((9.15, 3.6), (4.35, 3.6), "grafos sincronizados\n(pesos actualizados)", 0.0, -0.28),
        ((2.65, 3.35), (2.65, 1.98), "desactivar()", -0.65, 0.0),
        ((3.55, 1.98), (3.55, 3.35), "reactivar()", 0.52, 0.12),
        ((4.35, 3.35), (5.55, 1.6), "eliminar()", 0.52, 0.18),
        ((4.35, 1.4), (5.55, 1.4), "eliminar()", 0.0, -0.22),
        ((8.25, 1.6), (11.45, 1.6), "fin ciclo", 0.0, 0.24),
    ]

    for (x1, y1), (x2, y2), lbl, dx, dy in transiciones:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5))
        ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, lbl, ha="center", va="center", fontsize=7.8, color="#1E293B")

    plt.tight_layout()
    fig.savefig(ruta_salida, bbox_inches="tight")
    plt.close(fig)


def _sombrear_celda(celda, color_hex: str) -> None:
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    celda._tc.get_or_add_tcPr().append(shading)


def _agregar_tabla_rf(doc: Document, num: str, nombre: str, fuente: str, prioridad: str, descripcion: str) -> None:
    tabla = doc.add_table(rows=5, cols=2)
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER

    prio_alta = "[X]" if prioridad == "Alta" else "[ ]"
    prio_med = "[X]" if prioridad == "Media" else "[ ]"
    filas = [
        ("Numero de requisito", num),
        ("Nombre de requisito", nombre),
        ("Tipo", "[X] Requisito    [ ] Restriccion"),
        ("Fuente del requisito", fuente),
        ("Prioridad del requisito", f"{prio_alta} Alta/Esencial   {prio_med} Media/Deseado   [ ] Baja/Opcional"),
    ]
    for i, (k, v) in enumerate(filas):
        c0, c1 = tabla.rows[i].cells[0], tabla.rows[i].cells[1]
        c0.width = Inches(2.1)
        c1.width = Inches(4.4)
        _sombrear_celda(c0, "E8F5E9")
        r0 = c0.paragraphs[0].add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        r1 = c1.paragraphs[0].add_run(v)
        r1.font.size = Pt(9.5)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    r_lbl = p.add_run("Descripcion: ")
    r_lbl.bold = True
    p.add_run(descripcion)


def generar_docx_ieee830(ruta_docx: Path, img_uc: Path, img_seq: Path, img_est: Path) -> None:
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    seccion = doc.sections[0]
    header_p = seccion.header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rh = header_p.add_run("Especificacion de Requisitos de Software (IEEE 830) | PERA - Rutas Colombia | Rev. 1.0")
    rh.font.size = Pt(8.5)
    rh.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    footer_p = seccion.footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf = footer_p.add_run("Universidad Popular del Cesar - Ingenieria de Sistemas - Estructura de Datos 2026-2")
    rf.font.size = Pt(8.5)
    rf.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # ================= PORTADA =================
    for _ in range(2):
        doc.add_paragraph()
    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_univ.add_run("UNIVERSIDAD POPULAR DEL CESAR\nFACULTAD DE INGENIERIA Y TECNOLOGICAS\nINGENIERIA DE SISTEMAS")
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x1B, 0x5E, 0x20)

    doc.add_paragraph()
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rt = p_tit.add_run("Especificacion de Requisitos de Software (SRS)\nConforme al Estandar IEEE Std 830-1998")
    rt.bold = True
    rt.font.size = Pt(18)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs = p_sub.add_run(
        "Proyecto: Programa Estadistico de Rutas de Automoviles (PERA) - Colombia\n"
        "Parcial 3 - Estructura de Datos\nRevision 1.0"
    )
    rs.font.size = Pt(12)
    rs.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_paragraph()
    p_aut = doc.add_paragraph()
    p_aut.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aut.add_run("Autores (KM-DV-ST):\n").bold = True
    p_aut.add_run(
        "Kovyn Been Mena Orcasita\n"
        "Damian Jose Velasquez Gonzalez\n"
        "Sofia Isabel Tovar Rodriguez\n\n"
        "Docente: Ing. Adith Perez\n"
        "Valledupar, Cesar - Noviembre de 2026"
    )
    doc.add_page_break()

    # ================= FICHA DEL DOCUMENTO =================
    doc.add_heading("Ficha del documento", level=1)
    t_ficha = doc.add_table(rows=2, cols=4)
    t_ficha.style = "Table Grid"
    headers_f = ["Fecha", "Revision", "Autor", "Verificado"]
    vals_f = ["25/11/2026", "1.0", "K. Mena, D. Velasquez, S. Tovar", "Equipo KM-DV-ST"]
    for i in range(4):
        _sombrear_celda(t_ficha.rows[0].cells[i], "1B5E20")
        rh_c = t_ficha.rows[0].cells[i].paragraphs[0].add_run(headers_f[i])
        rh_c.bold = True
        rh_c.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        t_ficha.rows[1].cells[i].paragraphs[0].add_run(vals_f[i])

    doc.add_paragraph()
    p_val = doc.add_paragraph("Documento validado por las partes en fecha: Noviembre de 2026.")
    p_val.runs[0].italic = True

    t_val = doc.add_table(rows=2, cols=2)
    t_val.style = "Table Grid"
    for i, txt in enumerate(["Por el cliente", "Por el equipo desarrollador"]):
        _sombrear_celda(t_val.rows[0].cells[i], "E8F5E9")
        t_val.rows[0].cells[i].paragraphs[0].add_run(txt).bold = True
    t_val.rows[1].cells[0].paragraphs[0].add_run("Ministerio de Transporte de Colombia (simulado UPC)\nDocente: Adith Perez")
    t_val.rows[1].cells[1].paragraphs[0].add_run("Kovyn Mena / Damian Velasquez / Sofia Tovar\nEquipo KM-DV-ST")

    doc.add_page_break()

    # ================= 1. INTRODUCCION =================
    doc.add_heading("1. Introduccion", level=1)
    doc.add_paragraph(
        "La presente Especificacion de Requisitos de Software (SRS) describe el diseno, la arquitectura, "
        "las variables del modelo, los requisitos funcionales y no funcionales, asi como el modelado UML "
        "del Programa Estadistico de Rutas de Automoviles (PERA), desarrollado para el calculo de rutas "
        "optimas entre las 32 capitales de Colombia sobre tres grafos ponderados sincronizados."
    )

    doc.add_heading("1.1 Proposito", level=2)
    doc.add_paragraph(
        "Establecer de manera precisa el comportamiento tecnico del software PERA, sirviendo como guia de "
        "evaluacion para el docente de Estructura de Datos y como referencia de mantenimiento para futuros "
        "estudiantes del programa de Ingenieria de Sistemas de la Universidad Popular del Cesar."
    )

    doc.add_heading("1.2 Alcance", level=2)
    doc.add_paragraph(
        "El sistema comprende dos aplicaciones independientes y equivalentes en funcionalidad: "
        "Parcial_3_KM-DV-ST.cpp (consola interactiva en C++17 con posicionamiento GotoXY) y "
        "Parcial_3_KM-DV-ST.py (interfaz grafica de escritorio en Python 3 con tkinter). Ambas "
        "aplicaciones comparten el mismo formato de persistencia en texto plano (datos_pera.txt), operan "
        "sobre tres grafos ponderados sincronizados (Distancia, Combustible, Peajes) con 32 capitales y "
        "48 corredores reales (CREG/INVIAS/ANI), calculan rutas optimas con Dijkstra en cuatro metricas "
        "y generan un Dashboard matplotlib y un mapa interactivo Folium (bono)."
    )

    doc.add_heading("1.3 Personal involucrado", level=2)
    t_per = doc.add_table(rows=5, cols=5)
    t_per.style = "Table Grid"
    per_h = ["Nombre", "Rol", "Categoria", "Responsabilidades", "Contacto"]
    per_rows = [
        ("Kovyn Been Mena Orcasita", "Arquitecto / Desarrollador", "Estudiante Ing. Sistemas", "Motor de grafos C++/Python, Dijkstra y persistencia", "kbmena@unicesar.edu.co"),
        ("Damian Jose Velasquez Gonzalez", "Desarrollador / QA", "Estudiante Ing. Sistemas", "Pruebas en Windows, dashboard matplotlib y mapa Folium", "Ingenieria de Sistemas UPC"),
        ("Sofia Isabel Tovar Rodriguez", "Analista / Documentacion", "Estudiante Ing. Sistemas", "Especificacion IEEE 830, UML y sustentacion", "Ingenieria de Sistemas UPC"),
        ("Ing. Adith Perez", "Cliente / Evaluador", "Docente Estructura de Datos", "Definicion de requisitos y evaluacion academica", "adithperez@unicesar.edu.co"),
    ]
    for i, h in enumerate(per_h):
        _sombrear_celda(t_per.rows[0].cells[i], "1B5E20")
        r = t_per.rows[0].cells[i].paragraphs[0].add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for r_idx, fila in enumerate(per_rows, start=1):
        for c_idx, val in enumerate(fila):
            t_per.rows[r_idx].cells[c_idx].paragraphs[0].add_run(val)

    doc.add_heading("1.4 Definiciones, acronimos y abreviaturas", level=2)
    defs = [
        ("PERA:", "Programa Estadistico de Rutas de Automoviles."),
        ("Grafo Ponderado:", "Estructura de datos formada por vertices (capitales) y aristas (corredores) con peso asociado (km, galones, COP)."),
        ("Lista de Adyacencia:", "Representacion del grafo mediante vector de listas de vecinos con peso."),
        ("Dijkstra:", "Algoritmo de camino minimo de fuente unica con cola de prioridad, complejidad O((V+E) log V)."),
        ("INVIAS:", "Instituto Nacional de Vias (referencia de distancias y peajes)."),
        ("ANI:", "Agencia Nacional de Infraestructura (referencia de concesiones y peajes)."),
        ("CREG:", "Comision de Regulacion de Energia y Gas (referencia de precio de combustible)."),
        ("CRUD:", "Operaciones de Creacion, Consulta, Modificacion y Eliminacion."),
        ("SRS:", "Especificacion de Requisitos de Software segun IEEE Std 830-1998."),
    ]
    for term, desc in defs:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(term + " ").bold = True
        p.add_run(desc)

    doc.add_heading("1.5 Referencias", level=2)
    t_ref = doc.add_table(rows=5, cols=4)
    t_ref.style = "Table Grid"
    for i, h in enumerate(["Referencia", "Titulo", "Fecha", "Autor / Entidad"]):
        _sombrear_celda(t_ref.rows[0].cells[i], "E8F5E9")
        t_ref.rows[0].cells[i].paragraphs[0].add_run(h).bold = True
    refs = [
        ("REF-01", "Enunciado Parcial 3 - Estructura de Datos (PERA)", "17/11/2026", "Ing. Adith Perez - UPC"),
        ("REF-02", "IEEE Std 830-1998 Software Requirements Specifications", "1998", "IEEE Computer Society"),
        ("REF-03", "Introduction to Algorithms (4th Edition)", "2022", "Cormen, Leiserson, Rivest, Stein"),
        ("REF-04", "Tarifas de peaje INVIAS/ANI Cat. I y precio combustible CREG", "2026", "Ministerio de Transporte de Colombia"),
    ]
    for r_i, fila in enumerate(refs, start=1):
        for c_i, val in enumerate(fila):
            t_ref.rows[r_i].cells[c_i].paragraphs[0].add_run(val)

    doc.add_heading("1.6 Resumen", level=2)
    doc.add_paragraph(
        "El resto del documento se organiza asi: la Seccion 2 describe la perspectiva general, usuarios y "
        "restricciones del producto; la Seccion 3 especifica las variables de entrada/salida, interfaces y "
        "requisitos funcionales y no funcionales; finalmente, la Seccion 4 presenta el diseno de los tres "
        "grafos ponderados, la estrategia Dijkstra y los diagramas UML."
    )

    # ================= 2. DESCRIPCION GENERAL =================
    doc.add_heading("2. Descripcion general", level=1)

    doc.add_heading("2.1 Perspectiva del producto", level=2)
    doc.add_paragraph(
        "PERA es un sistema autonomo de calculo de rutas diseñado bajo una arquitectura modular de cuatro "
        "capas dentro de un archivo fuente autocontenido por lenguaje: Capa 1 (Modelo de Datos: Vertice, "
        "Arista y RutaOptima), Capa 2 (Motor Algoritmico: tres Grafos sincronizados y Dijkstra), Capa 3 "
        "(Persistencia Compartida en datos_pera.txt) y Capa 4 (Interfaz de Usuario con GotoXY en C++17 y "
        "tkinter en Python 3, mas Dashboard matplotlib y mapa Folium como bono)."
    )

    doc.add_heading("2.2 Funcionalidad del producto", level=2)
    for item in [
        "Carga inicial de datos_pera.txt o inicio con grafos vacios.",
        "Operaciones completas de creacion, consulta, modificacion y eliminacion de ciudades, rutas y peajes.",
        "Desactivacion y reactivacion logica de tramos viales (cierres viales) sin alterar la topologia.",
        "Validacion de categoria y peaje por tramo, con agrupacion por regiones/productos.",
        "Calculo de ruta optima entre dos capitales en cuatro metricas: distancia, combustible, peajes y costo total.",
        "Comparativa lado a lado de las rutas optimas en los tres grafos sincronizados.",
        "Visualizacion del resumen estadistico descriptivo y del Dashboard matplotlib (4 graficos).",
        "Generacion del mapa interactivo Folium sobre tiles CartoDB (bono).",
        "Almacenamiento y recarga persistente compartida entre C++ y Python.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("2.3 Caracteristicas de los usuarios", level=2)
    t_usr = doc.add_table(rows=3, cols=4)
    t_usr.style = "Table Grid"
    for i, h in enumerate(["Tipo de usuario", "Formacion", "Habilidades", "Actividades"]):
        _sombrear_celda(t_usr.rows[0].cells[i], "E8F5E9")
        t_usr.rows[0].cells[i].paragraphs[0].add_run(h).bold = True
    usrs = [
        ("Analista de rutas", "Pregrado Ingenieria de Sistemas", "Manejo basico de consola y escritorio", "Calcular rutas optimas y comparar metricas entre capitales"),
        ("Docente Evaluador", "Ingeniero de Sistemas / Magister", "Dominio de estructuras de datos y grafos", "Validar Dijkstra, CRUD, persistencia y visualizaciones"),
    ]
    for r_i, fila in enumerate(usrs, start=1):
        for c_i, val in enumerate(fila):
            t_usr.rows[r_i].cells[c_i].paragraphs[0].add_run(val)

    doc.add_heading("2.4 Restricciones", level=2)
    doc.add_paragraph(
        "El software debe entregarse en dos archivos fuente nombrados con las iniciales del equipo "
        "(Parcial_3_KM-DV-ST.cpp y Parcial_3_KM-DV-ST.py), compilar con estandar C++17 sin librerias de "
        "terceros (compatible con MinGW/Dev-C++ en Windows y GCC en Linux), ejecutarse en Python 3 usando "
        "uniquement la biblioteca estandar mas matplotlib y folium para el bono, y operar sobre un archivo "
        "de persistencia local sin depender de motores de base de datos externos."
    )

    doc.add_heading("2.5 Suposiciones y dependencias", level=2)
    doc.add_paragraph(
        "Se asume la disponibilidad de un compilador C++17 (GCC o MinGW-w64) y del interprete Python 3.8+ "
        "con soporte Tcl/Tk. Para el bono de mapa interactivo se requiere conexion a Internet para cargar "
        "los tiles CartoDB/Esri, mientras que el Dashboard matplotlib opera completamente offline."
    )

    doc.add_heading("2.6 Evolucion previsible del sistema", level=2)
    doc.add_paragraph(
        "En futuras versiones el motor modular permite extenderse a grafos dirigidos con trafico en tiempo "
        "real, exportacion de rutas a GPX, incorporacion de algoritmos A* y Floyd-Warshall, y generacion de "
        "reportes PDF automaticos a partir del Dashboard."
    )

    # ================= 3. REQUISITOS ESPECIFICOS =================
    doc.add_heading("3. Requisitos especificos", level=1)

    doc.add_heading("3.1 Requisitos comunes de las interfaces (Variables de Entrada y Salida)", level=2)
    doc.add_paragraph(
        "A continuacion se identifican formalmente las variables de entrada y salida del modelo de grafos "
        "implementado en ambos lenguajes:"
    )

    t_vars = doc.add_table(rows=10, cols=4)
    t_vars.style = "Table Grid"
    for i, h in enumerate(["Variable", "Direccion", "Tipo de dato", "Descripcion funcional"]):
        _sombrear_celda(t_vars.rows[0].cells[i], "1B5E20")
        r = t_vars.rows[0].cells[i].paragraphs[0].add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    vars_rows = [
        ("opcionCargaInicial", "Entrada", "Booleano / Entero", "Define al inicio si se carga datos_pera.txt o se ejecuta sin datos."),
        ("origen, destino", "Entrada", "Cadena (string)", "Capitales de origen y destino del calculo de ruta."),
        ("distanciaKm", "Entrada / Salida", "Real (double)", "Peso de la arista en el grafo de Distancia (km)."),
        ("combustibleGal", "Entrada / Salida", "Real (double)", "Peso de la arista en el grafo de Combustible (galones)."),
        ("peajeCOP", "Entrada / Salida", "Entero (long)", "Peso de la arista en el grafo de Peajes (COP)."),
        ("activo", "Entrada / Estado", "Booleano (bool)", "Estado logico del tramo (1=Activo, 0=Desactivado/cierre vial)."),
        ("categoria, grupo", "Entrada", "Cadena (string)", "Categoria del tramo y agrupacion por regiones/productos."),
        ("costoTotal", "Salida", "Real (double)", "Metrica combinada distancia + combustible + peajes."),
        ("caminoOptimo", "Salida", "Lista de vertices", "Secuencia de capitales del camino minimo reconstruido."),
    ]
    for r_i, fila in enumerate(vars_rows, start=1):
        for c_i, val in enumerate(fila):
            t_vars.rows[r_i].cells[c_i].paragraphs[0].add_run(val)

    doc.add_heading("3.1.1 Interfaces de usuario", level=3)
    doc.add_paragraph(
        "En C++17 la interfaz utiliza posicionamiento directo de cursor mediante Consola::GotoXY(x, y) "
        "sobre una cuadricula de 120x34 caracteres con bordes ASCII de 7 bits para maxima portabilidad. "
        "En Python 3 se presenta una ventana tkinter con formularios CRUD, tabla de resultados, panel de "
        "comparativa de rutas y boton de generacion del Dashboard matplotlib y del mapa Folium."
    )

    doc.add_heading("3.1.2 Interfaces de hardware", level=3)
    doc.add_paragraph(
        "Requiere un computador estandar x86_64 con teclado, monitor de resolucion minima 1024x720 y al "
        "menos 256 MB de memoria RAM disponibles."
    )

    doc.add_heading("3.1.3 Interfaces de software", level=3)
    doc.add_paragraph(
        "Persistencia mediante archivo de texto plano UTF-8 denominado datos_pera.txt ubicado junto al "
        "ejecutable o script, con un registro por linea separado por punto y coma: "
        "origen;destino;distanciaKm;combustibleGal;peajeCOP;activo;categoria;grupo. Las lineas iniciadas "
        "con '#' son comentarios y los saltos de linea CRLF/LF se normalizan automaticamente."
    )

    doc.add_heading("3.1.4 Interfaces de comunicacion", level=3)
    doc.add_paragraph(
        "El nucleo opera de manera completamente local. El bono de mapa Folium requiere conexion a Internet "
        "para cargar los tiles CartoDB voyager / Esri, evitando el bloqueo 403 de OpenStreetMap en file://."
    )

    doc.add_heading("3.2 Requisitos funcionales", level=2)
    rfs = [
        ("RF-01", "Seleccion inicial de carga de persistencia", "Enunciado Parcial 3", "Alta",
         "Al iniciar, el programa solicita al usuario decidir si desea cargar los tramos almacenados en datos_pera.txt o iniciar con los grafos vacios."),
        ("RF-02", "Creacion y reinicio de los tres grafos", "Enunciado Parcial 3", "Alta",
         "Permite crear o vaciar los grafos de Distancia, Combustible y Peajes liberando correctamente toda la memoria dinamica y actualizando la vista."),
        ("RF-03", "CRUD de ciudades (capitales)", "Enunciado Parcial 3", "Alta",
         "Permite alta, baja, modificacion y consulta de capitales (vertices) con validacion de unicidad y existencia."),
        ("RF-04", "CRUD de rutas y peajes (corredores)", "Enunciado Parcial 3", "Alta",
         "Permite alta, baja, modificacion y consulta de corredores (aristas) actualizando simultaneamente los tres grafos sincronizados."),
        ("RF-05", "Desactivacion y reactivacion de tramos", "Enunciado Parcial 3", "Alta",
         "Cambia el atributo booleano activo del tramo sin alterar la topologia, simulando cierres viales y diferenciandolo visualmente."),
        ("RF-06", "Validacion de categoria y peaje", "Enunciado Parcial 3", "Alta",
         "Valida la categoria del tramo y el peaje asociado por corredor, con agrupacion por regiones y productos."),
        ("RF-07", "Calculo de ruta optima (Dijkstra 4 metricas)", "Enunciado Parcial 3", "Alta",
         "Calcula la ruta optima entre dos capitales en cuatro metricas: distancia, combustible, peajes y costo total, con complejidad O((V+E) log V)."),
        ("RF-08", "Comparativa lado a lado de rutas", "Enunciado Parcial 3", "Alta",
         "Muestra en paralelo las rutas optimas obtenidas en los tres grafos sincronizados para facilitar la comparacion."),
        ("RF-09", "Resumen estadistico y Dashboard", "Enunciado Parcial 3", "Media",
         "Genera un resumen estadistico descriptivo y un Dashboard matplotlib con cuatro graficos, mas el mapa Folium (bono)."),
    ]
    for num, nom, fnt, prio, desc in rfs:
        doc.add_heading(f"3.2.{rfs.index((num, nom, fnt, prio, desc)) + 1} {num} - {nom}", level=3)
        _agregar_tabla_rf(doc, num, nom, fnt, prio, desc)

    doc.add_heading("3.3 Requisitos no funcionales", level=2)
    rnfs = [
        ("3.3.1 Requisitos de rendimiento",
         "Todas las consultas de ruta operan en complejidad O((V+E) log V) en el peor caso, con tiempos de "
         "respuesta inferiores a 50 ms para grafos de hasta 1.000 vertices."),
        ("3.3.2 Seguridad",
         "Validacion estricta de todas las entradas numericas y textuales para impedir bloqueos por entradas "
         "no numericas o archivos de persistencia mal formados."),
        ("3.3.3 Fiabilidad",
         "La sincronizacion de los tres grafos se garantiza tras cada operacion CRUD; en C++ el destructor "
         "libera toda la memoria dinamica evitando fugas."),
        ("3.3.4 Disponibilidad",
         "Disponibilidad local del 100% para el nucleo sin dependencia de servicios externos ni conexion a Internet."),
        ("3.3.5 Mantenibilidad",
         "Codigo estructurado en cuatro capas independientes (Modelo, Motor de Grafos, Persistencia e "
         "Interfaz) con nombres descriptivos y separacion de la capa dependiente del sistema operativo."),
        ("3.3.6 Portabilidad",
         "El archivo C++17 compila sin modificaciones en Linux (GCC) y Windows 10/11 (MinGW-w64 / Dev-C++), "
         "y el archivo Python 3 se ejecuta sin instalar paquetes externos para el nucleo."),
    ]
    for tit, txt in rnfs:
        doc.add_heading(tit, level=3)
        doc.add_paragraph(txt)

    doc.add_heading("3.4 Otros requisitos", level=2)
    doc.add_paragraph(
        "El proyecto respeta la identidad institucional de la Universidad Popular del Cesar y se acompana "
        "de un video explicativo de aproximadamente 10 minutos cargado en YouTube."
    )

    # ================= 4. APENDICES Y DIAGRAMAS UML =================
    doc.add_page_break()
    doc.add_heading("4. Apendices: Diseno de la Estructura de Datos y Diagramas UML", level=1)

    doc.add_heading("4.1 Diseno de los 3 Grafos Ponderados y Estrategia Algoritmica (Dijkstra)", level=2)
    doc.add_paragraph(
        "La estructura central son tres grafos ponderados sincronizados representados mediante lista de "
        "adyacencia: GrafoDistancia (km), GrafoCombustible (galones) y GrafoPeajes (COP). Cada vertice "
        "representa una capital de Colombia y cada arista un corredor vial real (INVIAS/ANI) con sus tres "
        "pesos asociados. Tras cada operacion CRUD, los tres grafos se actualizan atomicamente."
    )
    for item in [
        "Dijkstra con cola de prioridad (min-heap) sobre cada grafo para obtener el camino minimo por metrica.",
        "Reconstruccion del camino optimo mediante el vector de predecesores.",
        "Calculo de la metrica combinada costoTotal = distancia + combustible + peajes normalizados.",
        "Complejidad temporal O((V+E) log V) y espacial O(V+E) por ejecucion.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("4.2 Diagrama de Casos de Uso (UML)", level=2)
    p_img1 = doc.add_paragraph()
    p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img1.add_run().add_picture(str(img_uc), width=Inches(6.3))

    doc.add_heading("4.3 Diagramas de Secuencia (UML)", level=2)
    p_img2 = doc.add_paragraph()
    p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img2.add_run().add_picture(str(img_seq), width=Inches(6.3))

    doc.add_page_break()
    doc.add_heading("4.4 Diagrama de Estado (UML)", level=2)
    p_img3 = doc.add_paragraph()
    p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img3.add_run().add_picture(str(img_est), width=Inches(6.3))

    doc.save(str(ruta_docx))


def main() -> None:
    img_uc = DOCS_DIR / "uml_casos_uso_parcial3.png"
    img_seq = DOCS_DIR / "uml_secuencia_parcial3.png"
    img_est = DOCS_DIR / "uml_estados_parcial3.png"
    ruta_docx = PERA_DIR / "Especificacion_Tecnica_Parcial_3.docx"

    generar_uml_casos_uso(img_uc)
    generar_uml_secuencia(img_seq)
    generar_uml_estados(img_est)
    generar_docx_ieee830(ruta_docx, img_uc, img_seq, img_est)

    print("Generados correctamente:")
    for p in (img_uc, img_seq, img_est, ruta_docx):
        print(f"  - {p.relative_to(ROOT)} ({p.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
