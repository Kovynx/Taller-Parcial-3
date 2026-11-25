"""
Generador de diagramas UML (PNG 220 DPI) y especificacion tecnica IEEE 830 (.docx)
para el Taller 3 - Programa de Aprendizaje de Arboles (PAA - AVL).
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
TALLER_DIR = ROOT / "taller3_avl"
DOCS_DIR = TALLER_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def _dibujar_actor(ax, x: float, y: float, etiqueta: str) -> None:
    ax.add_patch(Circle((x, y + 0.45), 0.16, fill=False, ec="#1B5E20", lw=2))
    ax.plot([x, x], [y + 0.29, y - 0.18], color="#1B5E20", lw=2)
    ax.plot([x - 0.25, x + 0.25], [y + 0.12, y + 0.12], color="#1B5E20", lw=2)
    ax.plot([x, x - 0.22], [y - 0.18, y - 0.55], color="#1B5E20", lw=2)
    ax.plot([x, x + 0.22], [y - 0.18, y - 0.55], color="#1B5E20", lw=2)
    ax.text(x, y - 0.85, etiqueta, ha="center", va="top", fontsize=9, fontweight="bold", color="#0F172A")


def generar_uml_casos_uso(ruta_salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=220)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Limite del sistema
    sistema = FancyBboxPatch(
        (2.4, 0.4), 9.2, 7.2, boxstyle="round,pad=0.12", fc="#F8FAFC", ec="#1B5E20", lw=2
    )
    ax.add_patch(sistema)
    ax.text(
        7.0, 7.35, "Sistema PAA - Programa de Aprendizaje de Arboles AVL (C++17 y Python)",
        ha="center", va="center", fontsize=11, fontweight="bold", color="#1B5E20"
    )

    _dibujar_actor(ax, 1.0, 4.3, "Estudiante /\nDocente UPC")

    casos_izq = [
        (5.0, 6.5, "Seleccionar carga inicial\n(archivo o vacio)"),
        (5.0, 5.5, "Insertar nodo AVL"),
        (5.0, 4.5, "Eliminar nodo (fisico)"),
        (5.0, 3.5, "Desactivar / Reactivar nodo"),
        (5.0, 2.5, "Consultar y Modificar nodo"),
        (5.0, 1.5, "Ejecutar Demo Pedagogico\n(4 Rotaciones)"),
    ]

    casos_der = [
        (9.6, 6.5, "Guardar / Cargar\ndatos_avl.txt"),
        (9.6, 4.7, "Balancear arbol AVL\n(Rotaciones LL, RR, LR, RL)"),
        (9.6, 2.2, "Visualizar arbol y\nRecorridos fijos"),
    ]

    for cx, cy, txt in casos_izq:
        ax.add_patch(Ellipse((cx, cy), 3.2, 0.78, fc="#E8F5E9", ec="#2E7D32", lw=1.6))
        ax.text(cx, cy, txt, ha="center", va="center", fontsize=8.5, color="#0F172A", fontweight="bold")
        ax.plot([1.35, cx - 1.60], [4.35, cy], color="#334155", lw=1.3)

    for cx, cy, txt in casos_der:
        ax.add_patch(Ellipse((cx, cy), 3.3, 0.92, fc="#E3F2FD", ec="#1565C0", lw=1.6))
        ax.text(cx, cy, txt, ha="center", va="center", fontsize=8.5, color="#0F172A", fontweight="bold")

    inclusiones = [
        ((6.60, 6.50), (7.95, 6.50), "<<extend>>", 0.0, 0.14),
        ((6.60, 5.50), (7.95, 4.95), "<<include>>", 0.0, 0.16),
        ((6.60, 4.50), (7.95, 4.65), "<<include>>", 0.0, -0.22),
        ((6.60, 3.50), (7.95, 2.50), "<<include>>", 0.0, 0.16),
        ((6.60, 2.50), (7.95, 2.20), "<<include>>", 0.0, 0.14),
        ((6.60, 1.50), (7.95, 1.92), "<<include>>", 0.0, -0.22),
    ]
    for (x1, y1), (x2, y2), label, dx, dy in inclusiones:
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", ls="--", color="#1565C0", lw=1.2)
        )
        mx, my = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=7.5, color="#1565C0", style="italic")

    plt.tight_layout()
    fig.savefig(ruta_salida, bbox_inches="tight")
    plt.close(fig)


def generar_uml_secuencia(ruta_salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=220)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.2)
    ax.axis("off")

    ax.text(
        6.0, 7.9, "Diagrama de Secuencia UML - Insercion, Balanceo AVL y Persistencia",
        ha="center", va="center", fontsize=11.5, fontweight="bold", color="#1B5E20"
    )

    participantes = [
        (1.2, "Usuario"),
        (3.8, "InterfazPAA\n(GotoXY / Tkinter)"),
        (6.8, "ArbolAVL\n(Motor EdD)"),
        (10.8, "PersistenciaAVL\n(datos_avl.txt)"),
    ]

    for x, nombre in participantes:
        caja = FancyBboxPatch((x - 1.0, 6.85), 2.0, 0.72, boxstyle="round,pad=0.06", fc="#E8F5E9", ec="#1B5E20", lw=1.6)
        ax.add_patch(caja)
        ax.text(x, 7.21, nombre, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0F172A")
        ax.plot([x, x], [6.85, 0.5], ls="--", color="#64748B", lw=1.3)

    # Fragmento opt [|FE| > 1]
    frag = FancyBboxPatch((5.9, 3.35), 4.55, 1.35, boxstyle="square,pad=0.05", fc="#FFF7ED", ec="#EA580C", lw=1.3, ls="--")
    ax.add_patch(frag)
    ax.text(6.05, 4.52, "opt [|FE(nodo)| > 1]", ha="left", va="center", fontsize=8, fontweight="bold", color="#C2410C")

    mensajes = [
        (1.2, 3.8, 6.3, "1: ingresarDato(clave, etiqueta)", False),
        (3.8, 6.8, 5.75, "2: insertar(clave, etiqueta, activo=true)", False),
        (6.8, 6.8, 5.15, "3: insertarRec() + altura + FE", False),
        (6.8, 6.8, 3.92, "4: balancear() -> Rotacion LL/RR/LR/RL", False),
        (6.8, 3.8, 2.85, "5: retornar RegistroTraza (pasos, rotacion)", True),
        (3.8, 3.8, 2.25, "6: dibujarArbol() + actualizar recorridos", False),
        (1.2, 3.8, 1.55, "7: solicitarGuardar()", False),
        (3.8, 10.8, 1.15, "8: guardarArchivo(arbol.preOrden())", False),
        (10.8, 3.8, 0.72, "9: confirmacionOK (archivo actualizado)", True),
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
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=220)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.8)
    ax.axis("off")

    ax.text(
        6.0, 6.45, "Diagrama de Estados UML - Ciclo de Vida de un Nodo en el Arbol AVL",
        ha="center", va="center", fontsize=11.5, fontweight="bold", color="#1B5E20"
    )

    # Estado inicial y final
    ax.add_patch(Circle((0.8, 3.8), 0.18, fc="#0F172A", ec="#0F172A"))
    ax.add_patch(Circle((11.1, 1.3), 0.22, fill=False, ec="#0F172A", lw=1.8))
    ax.add_patch(Circle((11.1, 1.3), 0.13, fc="#0F172A", ec="#0F172A"))

    estados = [
        (2.0, 3.3, 2.3, 1.0, "Activo Balanceado\n(|FE| <= 1, activo=true)", "#E8F5E9", "#1B5E20"),
        (6.0, 4.7, 2.5, 1.0, "Desbalanceado\n(|FE| == 2)", "#FFF7ED", "#EA580C"),
        (9.3, 3.3, 2.3, 1.0, "En Rotacion AVL\n(LL / RR / LR / RL)", "#E3F2FD", "#1565C0"),
        (2.0, 0.8, 2.3, 1.0, "Desactivado\n(activo=false, clave*)", "#F1F5F9", "#475569"),
        (6.4, 0.8, 2.3, 1.0, "Eliminado Fisico\n(memoria liberada)", "#FEF2F2", "#B91C1C"),
    ]

    for x, y, w, h, txt, fc, ec in estados:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec=ec, lw=1.8)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0F172A")

    transiciones = [
        ((0.98, 3.8), (1.95, 3.8), "insertar()", 0.0, 0.18),
        ((4.35, 4.15), (5.95, 5.15), "insercion/borrado\nproduce |FE|=2", -0.35, 0.25),
        ((8.55, 5.15), (10.3, 4.38), "detectar caso\n(LL/RR/LR/RL)", 0.35, 0.22),
        ((9.25, 3.65), (4.35, 3.65), "rebalanceo completo\n(alturas actualizadas)", 0.0, -0.25),
        ((2.75, 3.25), (2.75, 1.88), "desactivar()", -0.62, 0.0),
        ((3.55, 1.88), (3.55, 3.25), "reactivar()", 0.62, 0.0),
        ((4.35, 3.32), (6.35, 1.5), "eliminar() fisico", 0.55, 0.15),
        ((4.35, 1.3), (6.35, 1.3), "eliminar() fisico", 0.0, -0.22),
        ((8.75, 1.3), (10.85, 1.3), "fin ciclo", 0.0, 0.22),
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

    # Configuracion tipografica base
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    # Encabezado y pie de pagina institucional
    seccion = doc.sections[0]
    header_p = seccion.header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rh = header_p.add_run("Especificacion de Requisitos de Software (IEEE 830) | PAA - Arboles AVL | Rev. 1.0")
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
        "Proyecto: Programa de Aprendizaje de Arboles (PAA) - Arboles Binarios AVL\n"
        "Taller 3 - Estructura de Datos\nRevision 1.0"
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
    t_val.rows[1].cells[0].paragraphs[0].add_run("Programa de Ingenieria de Sistemas - UPC\nDocente: Adith Perez")
    t_val.rows[1].cells[1].paragraphs[0].add_run("Kovyn Mena / Damian Velasquez / Sofia Tovar\nEquipo KM-DV-ST")

    doc.add_page_break()

    # ================= 1. INTRODUCCION =================
    doc.add_heading("1. Introduccion", level=1)
    doc.add_paragraph(
        "La presente Especificacion de Requisitos de Software (SRS) describe el diseno, "
        "la arquitectura, las variables del modelo, los requisitos funcionales y no funcionales, "
        "asi como el modelado UML del Programa de Aprendizaje de Arboles (PAA), desarrollado "
        "para la ensenanza visual de arboles binarios balanceados AVL en los lenguajes C++17 y Python 3."
    )

    doc.add_heading("1.1 Proposito", level=2)
    doc.add_paragraph(
        "Establecer de manera precisa el comportamiento tecnico y pedagogico del software PAA, "
        "sirviendo como guia de evaluacion para el docente de Estructura de Datos y como referencia "
        "de mantenimiento para futuros estudiantes del programa de Ingenieria de Sistemas de la "
        "Universidad Popular del Cesar."
    )

    doc.add_heading("1.2 Alcance", level=2)
    doc.add_paragraph(
        "El sistema comprende dos aplicaciones independientes y equivalentes en funcionalidad: "
        "Taller_3_KM-DV-ST.cpp (consola interactiva en C++17 con posicionamiento GotoXY) y "
        "Taller_3_KM-DV-ST.py (interfaz grafica de escritorio en Python 3 con tkinter). Ambas "
        "aplicaciones comparten el mismo formato de persistencia en texto plano (datos_avl.txt), "
        "permiten al usuario elegir al inicio entre cargar datos o ejecutar sin datos, y mantienen "
        "siempre visibles los recorridos pre-orden, in-orden y post-orden."
    )

    doc.add_heading("1.3 Personal involucrado", level=2)
    t_per = doc.add_table(rows=5, cols=5)
    t_per.style = "Table Grid"
    per_h = ["Nombre", "Rol", "Categoria", "Responsabilidades", "Contacto"]
    per_rows = [
        ("Kovyn Been Mena Orcasita", "Arquitecto / Desarrollador", "Estudiante Ing. Sistemas", "Motor AVL C++/Python, persistencia y validacion", "kbmena@unicesar.edu.co"),
        ("Damian Jose Velasquez Gonzalez", "Desarrollador / QA", "Estudiante Ing. Sistemas", "Pruebas en Windows, visualizacion y documentacion", "Ingenieria de Sistemas UPC"),
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
        ("PAA:", "Programa de Aprendizaje de Arboles."),
        ("AVL:", "Arbol binario de busqueda autobalanceado (Adelson-Velsky y Landis) donde |FE| <= 1."),
        ("FE:", "Factor de Equilibrio definido como altura(subarbol_izq) - altura(subarbol_der)."),
        ("LL / RR / LR / RL:", "Casos de rotacion simple (izquierda-izquierda, derecha-derecha) y doble (izquierda-derecha, derecha-izquierda)."),
        ("CRUD:", "Operaciones de Creacion, Consulta, Modificacion y Eliminacion."),
        ("SRS:", "Especificacion de Requisitos de Software segun IEEE Std 830-1998."),
    ]
    for term, desc in defs:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(term + " ").bold = True
        p.add_run(desc)

    doc.add_heading("1.5 Referencias", level=2)
    t_ref = doc.add_table(rows=4, cols=4)
    t_ref.style = "Table Grid"
    for i, h in enumerate(["Referencia", "Titulo", "Fecha", "Autor / Entidad"]):
        _sombrear_celda(t_ref.rows[0].cells[i], "E8F5E9")
        t_ref.rows[0].cells[i].paragraphs[0].add_run(h).bold = True
    refs = [
        ("REF-01", "Enunciado Taller 3 - Estructura de Datos (PAA)", "17/11/2026", "Ing. Adith Perez - UPC"),
        ("REF-02", "IEEE Std 830-1998 Software Requirements Specifications", "1998", "IEEE Computer Society"),
        ("REF-03", "Introduction to Algorithms (4th Edition)", "2022", "Cormen, Leiserson, Rivest, Stein"),
    ]
    for r_i, fila in enumerate(refs, start=1):
        for c_i, val in enumerate(fila):
            t_ref.rows[r_i].cells[c_i].paragraphs[0].add_run(val)

    doc.add_heading("1.6 Resumen", level=2)
    doc.add_paragraph(
        "El resto del documento se organiza asi: la Seccion 2 describe la perspectiva general, "
        "usuarios y restricciones del producto; la Seccion 3 especifica las variables de entrada/salida, "
        "interfaces y requisitos funcionales y no funcionales; finalmente, la Seccion 4 presenta el diseno "
        "de la estructura de datos AVL, la estrategia de balanceo y los diagramas UML."
    )

    # ================= 2. DESCRIPCION GENERAL =================
    doc.add_heading("2. Descripcion general", level=1)

    doc.add_heading("2.1 Perspectiva del producto", level=2)
    doc.add_paragraph(
        "PAA es un sistema educativo autonomo disenado bajo una arquitectura modular de cuatro capas "
        "dentro de un archivo fuente autocontenido por lenguaje: Capa 1 (Modelo de Datos NodoAVL y Trazas), "
        "Capa 2 (Motor Algoritmico ArbolAVL), Capa 3 (Persistencia Compartida en datos_avl.txt) y "
        "Capa 4 (Interfaz de Usuario con GotoXY en C++17 y Canvas vectorial tkinter en Python 3)."
    )

    doc.add_heading("2.2 Funcionalidad del producto", level=2)
    for item in [
        "Decision inicial de cargar datos persistidos o iniciar con un arbol AVL vacio.",
        "Operaciones completas de creacion, insercion, eliminacion fisica, desactivacion/reactivacion logica, consulta y modificacion.",
        "Visualizacion grafica/2D del arbol AVL mostrando altura y factor de equilibrio por nodo.",
        "Visualizacion permanente de los recorridos Pre-orden, In-orden y Post-orden.",
        "Traza pedagogica de comparaciones y rotaciones aplicadas (LL, RR, LR, RL) mas Modo Demo guiado de 7 pasos.",
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
        ("Estudiante UPC", "Pregrado Ingenieria de Sistemas", "Manejo basico de consola y escritorio", "Experimentar inserciones, borrados y observar rotaciones AVL"),
        ("Docente Evaluador", "Ingeniero de Sistemas / Magister", "Dominio de estructuras de datos", "Validar rotaciones LL/RR/LR/RL, recorridos y persistencia"),
    ]
    for r_i, fila in enumerate(usrs, start=1):
        for c_i, val in enumerate(fila):
            t_usr.rows[r_i].cells[c_i].paragraphs[0].add_run(val)

    doc.add_heading("2.4 Restricciones", level=2)
    doc.add_paragraph(
        "El software debe entregarse en dos archivos fuente nombrados con las iniciales del equipo "
        "(Taller_3_KM-DV-ST.cpp y Taller_3_KM-DV-ST.py), compilar con estandar C++17 sin librerias de "
        "terceros (compatible con MinGW/Dev-C++ en Windows y GCC en Linux), ejecutarse en Python 3 "
        "usando unicamente la biblioteca estandar (tkinter), y operar sobre un archivo de persistencia "
        "local sin depender de motores de base de datos externos."
    )

    doc.add_heading("2.5 Suposiciones y dependencias", level=2)
    doc.add_paragraph(
        "Se asume la disponibilidad de un compilador C++17 (GCC o MinGW-w64) y del interprete Python 3.8+ "
        "con soporte Tcl/Tk (incluido por defecto en el instalador oficial de Python para Windows). "
        "En consola Windows se configura un ancho minimo de 120 columnas para el lienzo GotoXY."
    )

    doc.add_heading("2.6 Evolucion previsible del sistema", level=2)
    doc.add_paragraph(
        "En futuras versiones el motor modular permite extenderse facilmente a arboles Rojo-Negro, "
        "arboles B/B+, exportacion directa de estados a imagenes PNG y generacion de cuestionarios "
        "interactivos de autoevaluacion sobre factores de equilibrio."
    )

    # ================= 3. REQUISITOS ESPECIFICOS =================
    doc.add_heading("3. Requisitos especificos", level=1)

    doc.add_heading("3.1 Requisitos comunes de las interfaces (Variables de Entrada y Salida)", level=2)
    doc.add_paragraph(
        "A continuacion se identifican formalmente las variables de entrada y salida del modelo AVL "
        "implementado en ambos lenguajes:"
    )

    t_vars = doc.add_table(rows=9, cols=4)
    t_vars.style = "Table Grid"
    for i, h in enumerate(["Variable", "Direccion", "Tipo de dato", "Descripcion funcional"]):
        _sombrear_celda(t_vars.rows[0].cells[i], "1B5E20")
        r = t_vars.rows[0].cells[i].paragraphs[0].add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    vars_rows = [
        ("opcionCargaInicial", "Entrada", "Booleano / Entero", "Define al inicio si se carga datos_avl.txt o se ejecuta sin datos."),
        ("clave", "Entrada", "Entero (int)", "Clave numerica unica que determina la posicion en el arbol AVL."),
        ("etiqueta", "Entrada", "Cadena (string)", "Nombre o descripcion asociada al nodo."),
        ("activo", "Entrada / Estado", "Booleano (bool)", "Estado logico del nodo (1=Activo, 0=Desactivado)."),
        ("altura", "Salida", "Entero (int)", "Altura calculada del subarbol en cada nodo (hoja = 1)."),
        ("factorEquilibrio (FE)", "Salida", "Entero {-1, 0, +1}", "Diferencia h(izq) - h(der) usada para verificar balanceo."),
        ("tipoRotacion y traza", "Salida", "Cadena / Lista", "Secuencia de comparaciones y rotacion aplicada (LL, RR, LR, RL)."),
        ("preOrden, inOrden, postOrden", "Salida", "Listas / Cadenas", "Recorridos del arbol mostrados permanentemente en pantalla."),
    ]
    for r_i, fila in enumerate(vars_rows, start=1):
        for c_i, val in enumerate(fila):
            t_vars.rows[r_i].cells[c_i].paragraphs[0].add_run(val)

    doc.add_heading("3.1.1 Interfaces de usuario", level=3)
    doc.add_paragraph(
        "En C++17 la interfaz utiliza posicionamiento directo de cursor mediante Consola::GotoXY(x, y) "
        "sobre una cuadricula de 120x34 caracteres con bordes ASCII de 7 bits para maxima portabilidad "
        "en cmd.exe de Windows y terminales Linux. En Python 3 se presenta una ventana tkinter con "
        "lienzo vectorial coloreado por factor de equilibrio (verde FE=0, azul FE=+-1, naranja rotacion "
        "activa, gris punteado desactivado) y franja inferior fija para los tres recorridos."
    )

    doc.add_heading("3.1.2 Interfaces de hardware", level=3)
    doc.add_paragraph(
        "Requiere un computador estandar x86_64 con teclado, monitor de resolucion minima 1024x720 "
        "y al menos 128 MB de memoria RAM disponibles."
    )

    doc.add_heading("3.1.3 Interfaces de software", level=3)
    doc.add_paragraph(
        "Persistencia mediante archivo de texto plano UTF-8 denominado datos_avl.txt ubicado junto al "
        "ejecutable o script, con un registro por linea separado por punto y coma: clave;etiqueta;activo. "
        "Las lineas iniciadas con '#' son comentarios y los saltos de linea CRLF/LF se normalizan automaticamente."
    )

    doc.add_heading("3.1.4 Interfaces de comunicacion", level=3)
    doc.add_paragraph(
        "No aplicable (NA). El sistema opera de manera completamente local sin requerir conectividad de red."
    )

    doc.add_heading("3.2 Requisitos funcionales", level=2)
    rfs = [
        ("RF-01", "Seleccion inicial de carga de persistencia", "Enunciado Taller 3 (#10)", "Alta",
         "Al iniciar, el programa solicita al usuario decidir si desea cargar los nodos almacenados en datos_avl.txt o iniciar con el arbol vacio."),
        ("RF-02", "Creacion y reinicio del arbol AVL", "Enunciado Taller 3", "Alta",
         "Permite crear o vaciar el arbol liberando correctamente todos los nodos en memoria dinamica y actualizando inmediatamente la vista."),
        ("RF-03", "Insercion con balanceo visual automatico", "Enunciado Taller 3 (#1)", "Alta",
         "Inserta un nuevo nodo por clave unica, registra las comparaciones desde la raiz, recalcula alturas y FE, y aplica rotaciones LL, RR, LR o RL informando el giro ejecutado."),
        ("RF-04", "Eliminacion fisica con rebalanceo", "Enunciado Taller 3 (#1)", "Alta",
         "Elimina fisicamente un nodo (casos de 0, 1 o 2 hijos mediante sucesor in-orden) y rebalancea el camino de retorno hasta la raiz."),
        ("RF-05", "Desactivacion y reactivacion logica", "Enunciado Taller 3", "Alta",
         "Cambia el atributo booleano activo del nodo sin alterar la topologia ni las alturas del arbol AVL, diferenciandolo visualmente con asterisco (*) y estilo atenuado."),
        ("RF-06", "Consulta (busqueda) con traza de recorrido", "Enunciado Taller 3 (#1)", "Alta",
         "Localiza una clave en tiempo O(log n) mostrando la ruta de comparaciones seguida, la etiqueta, altura, factor de equilibrio y estado del nodo."),
        ("RF-07", "Modificacion de etiqueta o clave", "Enunciado Taller 3", "Alta",
         "Permite actualizar la etiqueta en el sitio O(log n) o reubicar la clave ejecutando eliminacion y reinsercion balanceada preservando el estado activo."),
        ("RF-08", "Visualizacion permanente de recorridos", "Enunciado Taller 3", "Alta",
         "Muestra en todo momento y en un panel fijo los recorridos Pre-orden, In-orden y Post-orden actualizados tras cada operacion."),
        ("RF-09", "Modo Demo Pedagogico de las 4 rotaciones", "Diseno pedagogico PAA", "Media",
         "Ejecuta de forma guiada la secuencia 10, 20, 30, 5, 3, 8, 25 demostrando en vivo las rotaciones RR, LL, LR y RL hasta obtener un arbol simetrico perfecto."),
    ]
    for num, nom, fnt, prio, desc in rfs:
        doc.add_heading(f"3.2.{rfs.index((num, nom, fnt, prio, desc)) + 1} {num} - {nom}", level=3)
        _agregar_tabla_rf(doc, num, nom, fnt, prio, desc)

    doc.add_heading("3.3 Requisitos no funcionales", level=2)
    rnfs = [
        ("3.3.1 Requisitos de rendimiento",
         "Todas las operaciones de insercion, eliminacion, consulta y desactivacion operan en complejidad "
         "O(log n) en el peor caso, con tiempos de respuesta inferiores a 5 ms para arboles de hasta 10.000 nodos."),
        ("3.3.2 Seguridad",
         "Validacion estricta de todas las entradas numericas y textuales para impedir bloqueos por entradas "
         "no numericas o archivos de persistencia mal formados."),
        ("3.3.3 Fiabilidad",
         "El invariante AVL (|FE| <= 1) se garantiza despues de cada insercion y eliminacion; en C++ el "
         "destructor de ArbolAVL libera toda la memoria dinamica evitando fugas."),
        ("3.3.4 Disponibilidad",
         "Disponibilidad local del 100% sin dependencia de servicios externos ni conexion a Internet."),
        ("3.3.5 Mantenibilidad",
         "Codigo estructurado en cuatro capas independientes (Modelo, Motor AVL, Persistencia e Interfaz) "
         "con nombres descriptivos y separacion de la capa dependiente del sistema operativo."),
        ("3.3.6 Portabilidad",
         "El archivo C++17 compila sin modificaciones en Linux (GCC) y Windows 10/11 (MinGW-w64 / Dev-C++), "
         "y el archivo Python 3 se ejecuta sin instalar paquetes externos."),
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

    doc.add_heading("4.1 Diseno de la Estructura de Datos AVL y Estrategia de Solucion", level=2)
    doc.add_paragraph(
        "La estructura central es un arbol binario de busqueda enlazado dinamicamente mediante nodos "
        "NodoAVL(clave, etiqueta, altura, activo, izq, der). Tras cada insercion o eliminacion recursiva, "
        "el retorno actualiza la altura del nodo en O(1) y calcula FE = h(izq) - h(der). Si |FE| == 2, "
        "se selecciona automaticamente la rotacion correspondiente:"
    )
    for rot in [
        "Caso LL (FE = +2 y FE_izq >= 0): Rotacion Simple a la Derecha.",
        "Caso RR (FE = -2 y FE_der <= 0): Rotacion Simple a la Izquierda.",
        "Caso LR (FE = +2 y FE_izq < 0): Rotacion Izquierda en hijo izquierdo + Rotacion Derecha en pivote.",
        "Caso RL (FE = -2 y FE_der > 0): Rotacion Derecha en hijo derecho + Rotacion Izquierda en pivote.",
    ]:
        doc.add_paragraph(rot, style="List Bullet")

    doc.add_paragraph(
        "Para fines demostrativos, el Modo Demo inserta secuencialmente las claves 10, 20, 30, 5, 3, 8 y 25, "
        "disparando exactamente RR (al insertar 30), LL (al insertar 3), LR (al insertar 8) y RL (al insertar 25), "
        "concluyendo en el arbol perfectamente balanceado de raiz 10 con subarboles 5(3, 8) y 25(20, 30)."
    )

    doc.add_heading("4.2 Diagrama de Casos de Uso (UML)", level=2)
    p_img1 = doc.add_paragraph()
    p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img1.add_run().add_picture(str(img_uc), width=Inches(6.3))

    doc.add_heading("4.3 Diagrama de Secuencia (UML)", level=2)
    p_img2 = doc.add_paragraph()
    p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img2.add_run().add_picture(str(img_seq), width=Inches(6.3))

    doc.add_page_break()
    doc.add_heading("4.4 Diagrama de Estados (UML)", level=2)
    p_img3 = doc.add_paragraph()
    p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img3.add_run().add_picture(str(img_est), width=Inches(6.3))

    doc.save(str(ruta_docx))


def main() -> None:
    img_uc = DOCS_DIR / "uml_casos_uso_taller3.png"
    img_seq = DOCS_DIR / "uml_secuencia_taller3.png"
    img_est = DOCS_DIR / "uml_estados_taller3.png"
    ruta_docx = TALLER_DIR / "Especificacion_Tecnica_Taller_3.docx"

    generar_uml_casos_uso(img_uc)
    generar_uml_secuencia(img_seq)
    generar_uml_estados(img_est)
    generar_docx_ieee830(ruta_docx, img_uc, img_seq, img_est)

    print("Generados correctamente:")
    for p in (img_uc, img_seq, img_est, ruta_docx):
        print(f"  - {p.relative_to(ROOT)} ({p.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
