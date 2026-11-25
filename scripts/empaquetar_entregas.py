"""
Validacion industrial y empaquetado de entregas (Taller 3 y Parcial 3).

Uso:
    .venv/bin/python scripts/empaquetar_entregas.py --grupo 1
"""

import argparse
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALLER_DIR = ROOT / "taller3_avl"
PERA_DIR = ROOT / "parcial3_pera"

FORBIDDEN_PATHS = ["vault/", ".agents/", "AGENTS.md", "tests_compatibilidad/", "scripts/"]
FORBIDDEN_NAMES = [".exe", "_linux", ".o", ".obj"]

AI_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bMACROBUTTON\b",
    r"\bClaude\b",
    r"\bKiro\b",
    r"\bCarbon\b",
    r"\bHydrogen\b",
    r"\bNeon\b",
    r"\bChatGPT\b",
    r"\bOpenCode\b",
    r"\bAntigravity\b",
    r"\bCopilot\b",
    r"\bGemini\b",
    r"Inserte aqu[ií]",
    r"pon esto",
    r"ac[aá] haremos",
    r"\bSugerencia\b",
    r"<[^>]*>",
]

TALLER_REQUIRED = [
    "Taller_3_KM-DV-ST.cpp",
    "Taller_3_KM-DV-ST.py",
    "datos_avl.txt",
    "Especificacion_Tecnica_Taller_3.docx",
    "Identificacion_Estudiantes.txt",
    "README.txt",
    "docs/uml_casos_uso_taller3.png",
    "docs/uml_secuencia_taller3.png",
    "docs/uml_estados_taller3.png",
]

PERA_REQUIRED = [
    "Parcial_3_KM-DV-ST.cpp",
    "Parcial_3_KM-DV-ST.py",
    "datos_pera.txt",
    "requirements.txt",
    "Especificacion_Tecnica_Parcial_3.docx",
    "Identificacion_Estudiantes.txt",
    "README.txt",
    "docs/uml_casos_uso_parcial3.png",
    "docs/uml_secuencia_parcial3.png",
    "docs/uml_estados_parcial3.png",
]


def compile_cpp(path: Path, std: str, compiler: str, static: bool) -> None:
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
        out = tmp.name
    try:
        cmd = [compiler, f"-std={std}", "-Wall", "-Wextra", "-Werror", str(path), "-o", out]
        if static:
            cmd = [compiler, f"-std={std}", "-Wall", "-Wextra", "-Werror", "-static", "-static-libgcc", "-static-libstdc++", str(path), "-o", out]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  FALLO compilacion {compiler} {std} static={static}:\n{res.stderr}")
            sys.exit(1)
    finally:
        try:
            os.remove(out)
        except OSError:
            pass


def audit_text(content: str, label: str, is_code: bool = False, allow_placeholders: bool = True) -> None:
    text = content
    if is_code:
        lines = [ln for ln in text.splitlines() if not re.match(r"^\s*#\s*include", ln)]
        text = "\n".join(lines)
    patterns = AI_PATTERNS if allow_placeholders else [p for p in AI_PATTERNS if p != r"<[^>]*>"]
    for pat in patterns:
        if re.search(pat, text):
            print(f"  FALLO auditoria anti-IA en {label}: patron {pat!r} detectado")
            sys.exit(1)


def audit_docx(path: Path, label: str) -> None:
    with zipfile.ZipFile(path) as z:
        if "word/document.xml" not in z.namelist():
            print(f"  FALLO: {path} no contiene word/document.xml")
            sys.exit(1)
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        # Auditoria de tokens prohibidos sobre el XML crudo (sin placeholders genericos)
        audit_text(xml, f"{label}/word/document.xml", allow_placeholders=False)
        # Auditoria de placeholders sobre el texto visible (sin etiquetas XML)
        texto_visible = re.sub(r"<[^>]+>", " ", xml)
        audit_text(texto_visible, f"{label}/word/document.xml (texto)", allow_placeholders=True)


def audit_file(path: Path, label: str) -> None:
    if not path.exists():
        print(f"  FALLO: falta entregable {path}")
        sys.exit(1)
    suffix = path.suffix.lower()
    if suffix in {".cpp", ".py", ".txt"}:
        content = path.read_text(encoding="utf-8", errors="replace")
        is_code = suffix in {".cpp", ".py"}
        placeholders = suffix == ".txt"
        audit_text(content, str(path.relative_to(ROOT)), is_code=is_code, allow_placeholders=placeholders)
    elif suffix == ".docx":
        audit_docx(path, str(path.relative_to(ROOT)))
    elif suffix == ".png":
        pass
    else:
        pass


def check_python(path: Path) -> None:
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as e:
        print(f"  FALLO sintaxis Python en {path}: {e}")
        sys.exit(1)


def build_zip(base_dir: Path, required: list, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in required:
            full = base_dir / rel if not (base_dir / rel).exists() else base_dir / rel
            # base_dir is the project subdir; rel relative to it
            full = base_dir / rel
            if not full.exists():
                print(f"  FALLO: falta {full}")
                sys.exit(1)
            z.write(full, arcname=rel)
    # verify
    with zipfile.ZipFile(zip_path) as z:
        bad = z.testzip()
        if bad is not None:
            print(f"  FALLO: zip corrupto ({bad})")
            sys.exit(1)
        names = z.namelist()
        for forbidden in FORBIDDEN_PATHS:
            for n in names:
                if n.startswith(forbidden) or forbidden.strip("/") in n.split("/"):
                    pass
        for n in names:
            for fp in FORBIDDEN_PATHS:
                if n.startswith(fp.rstrip("/")) or fp.rstrip("/") + "/" in n:
                    print(f"  FALLO: ruta prohibida en zip: {n}")
                    sys.exit(1)
            if any(n.endswith(ext) for ext in (".exe", "_linux", ".o", ".obj")):
                print(f"  FALLO: binario en zip: {n}")
                sys.exit(1)


def process_group(grupo: str) -> None:
    print(f"=== Empaquetado Grupo {grupo} ===")

    # Taller 3
    print("-- Taller 3 --")
    cpp_t = TALLER_DIR / "Taller_3_KM-DV-ST.cpp"
    py_t = TALLER_DIR / "Taller_3_KM-DV-ST.py"
    print("Compilando C++ (Taller)...")
    for std in ("c++11", "c++17"):
        compile_cpp(cpp_t, std, "g++", False)
    for std in ("c++11", "c++17"):
        compile_cpp(cpp_t, std, "x86_64-w64-mingw32-g++", True)
    print("Verificando sintaxis Python (Taller)...")
    check_python(py_t)
    print("Auditando entregables (Taller)...")
    for rel in TALLER_REQUIRED:
        audit_file(TALLER_DIR / rel, "taller3")
    zip_t = ROOT / f"Taller_3_Grupo_{grupo}.zip"
    print(f"Creando {zip_t.name}...")
    build_zip(TALLER_DIR, TALLER_REQUIRED, zip_t)

    # Parcial 3
    print("-- Parcial 3 --")
    cpp_p = PERA_DIR / "Parcial_3_KM-DV-ST.cpp"
    py_p = PERA_DIR / "Parcial_3_KM-DV-ST.py"
    print("Compilando C++ (Parcial)...")
    for std in ("c++11", "c++17"):
        compile_cpp(cpp_p, std, "g++", False)
    for std in ("c++11", "c++17"):
        compile_cpp(cpp_p, std, "x86_64-w64-mingw32-g++", True)
    print("Verificando sintaxis Python (Parcial)...")
    check_python(py_p)
    print("Auditando entregables (Parcial)...")
    for rel in PERA_REQUIRED:
        audit_file(PERA_DIR / rel, "parcial3")
    zip_p = ROOT / f"Parcial_3_Grupo_{grupo}.zip"
    print(f"Creando {zip_p.name}...")
    build_zip(PERA_DIR, PERA_REQUIRED, zip_p)

    print("OK: ambos zips validos.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grupo", default="05")
    args = parser.parse_args()
    process_group(args.grupo)


if __name__ == "__main__":
    main()
