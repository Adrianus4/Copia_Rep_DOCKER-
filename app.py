"""
EduManager Pro — Gestor Académico de Cursos, Aulas y Proyectos
Solo Python estándar + rich (para la UI de terminal)
"""

import json
import os
import sys
from datetime import datetime, date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.layout import Layout
from rich.live import Live

console = Console()
DATA_FILE = "edumanager_data.json"

# ─── Datos por defecto ────────────────────────────────────────────────────────
DEFAULT_DATA = {
    "cursos": [
        {"id": "C001", "nombre": "Matemáticas Avanzadas", "docente": "Dr. Ramírez",    "aula": "A-201", "creditos": 4, "estudiantes": 32, "progreso": 68, "estado": "Activo",     "inicio": "2025-03-01"},
        {"id": "C002", "nombre": "Física Cuántica",        "docente": "Dra. Torres",    "aula": "B-105", "creditos": 5, "estudiantes": 24, "progreso": 45, "estado": "Activo",     "inicio": "2025-03-01"},
        {"id": "C003", "nombre": "Python Avanzado",        "docente": "Ing. Vargas",    "aula": "Lab-3", "creditos": 3, "estudiantes": 40, "progreso": 82, "estado": "Activo",     "inicio": "2025-03-01"},
        {"id": "C004", "nombre": "Estadística Aplicada",   "docente": "Mg. Flores",     "aula": "A-110", "creditos": 3, "estudiantes": 28, "progreso": 91, "estado": "Finalizado", "inicio": "2024-09-01"},
        {"id": "C005", "nombre": "Cálculo Diferencial",    "docente": "Dr. Mendoza",    "aula": "C-302", "creditos": 4, "estudiantes": 36, "progreso": 30, "estado": "Activo",     "inicio": "2025-03-01"},
        {"id": "C006", "nombre": "Base de Datos",          "docente": "Ing. Castillo",  "aula": "Lab-1", "creditos": 4, "estudiantes": 30, "progreso": 55, "estado": "Activo",     "inicio": "2025-03-01"},
    ],
    "aulas": [
        {"id": "A-201", "edificio": "Bloque A", "tipo": "Teoría",      "capacidad": 40, "equipos": "Proyector, AC, WiFi"},
        {"id": "A-110", "edificio": "Bloque A", "tipo": "Teoría",      "capacidad": 35, "equipos": "Proyector, AC"},
        {"id": "B-105", "edificio": "Bloque B", "tipo": "Laboratorio", "capacidad": 30, "equipos": "PCs x30, Proyector, AC"},
        {"id": "Lab-1", "edificio": "Bloque C", "tipo": "Laboratorio", "capacidad": 30, "equipos": "PCs x30, Servidores"},
        {"id": "Lab-3", "edificio": "Bloque C", "tipo": "Laboratorio", "capacidad": 45, "equipos": "PCs x45, Proyector"},
        {"id": "C-302", "edificio": "Bloque C", "tipo": "Auditorio",   "capacidad": 50, "equipos": "Proyector HD, Sonido"},
    ],
    "proyectos": [
        {"id": "P001", "nombre": "Sistema de Gestión Académica", "curso": "C003", "equipo": 4, "progreso": 75, "entrega": "2025-07-15", "estado": "En progreso"},
        {"id": "P002", "nombre": "Modelo Predictivo de Notas",   "curso": "C004", "equipo": 3, "progreso":100, "entrega": "2025-05-30", "estado": "Completado"},
        {"id": "P003", "nombre": "Simulador de Partículas",      "curso": "C002", "equipo": 5, "progreso": 40, "entrega": "2025-08-01", "estado": "En progreso"},
        {"id": "P004", "nombre": "API REST Campus",              "curso": "C006", "equipo": 4, "progreso": 60, "entrega": "2025-06-20", "estado": "En progreso"},
        {"id": "P005", "nombre": "Dashboard BI Educativo",       "curso": "C004", "equipo": 3, "progreso": 90, "entrega": "2025-06-01", "estado": "Revisión"},
        {"id": "P006", "nombre": "App Móvil de Matemáticas",     "curso": "C001", "equipo": 6, "progreso": 20, "entrega": "2025-09-10", "estado": "Inicio"},
    ],
}

# ─── Persistencia ─────────────────────────────────────────────────────────────
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_DATA

def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── Helpers visuales ─────────────────────────────────────────────────────────
def barra_progreso(pct, width=20):
    lleno = int(pct / 100 * width)
    vacio = width - lleno
    if pct >= 80:   color = "bright_green"
    elif pct >= 50: color = "yellow"
    else:           color = "red"
    barra = f"[{color}]{'█' * lleno}[/{color}][dim]{'░' * vacio}[/dim]"
    return barra + f" [bold]{pct}%[/bold]"

def estado_badge(estado):
    colores = {
        "Activo":      "bold bright_green",
        "Finalizado":  "bold dim",
        "En progreso": "bold cyan",
        "Completado":  "bold green",
        "Revisión":    "bold yellow",
        "Inicio":      "bold magenta",
    }
    color = colores.get(estado, "white")
    return f"[{color}]{estado}[/{color}]"

def dias_restantes_str(fecha_str):
    try:
        entrega = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        dias = (entrega - date.today()).days
        if dias < 0:    return f"[red]Vencido ({abs(dias)}d)[/red]"
        if dias < 7:    return f"[bold red]🔴 {dias}d[/bold red]"
        if dias < 30:   return f"[yellow]🟡 {dias}d[/yellow]"
        return f"[green]🟢 {dias}d[/green]"
    except:
        return fecha_str

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def encabezado():
    console.print()
    console.print(Align.center(
        Panel(
            Align.center(
                "[bold bright_magenta]🎓  EduManager Pro[/bold bright_magenta]\n"
                "[dim]Plataforma Académica · Ciclo 2025-I[/dim]"
            ),
            border_style="bright_magenta",
            padding=(0, 4),
        ),
        vertical="middle"
    ))
    console.print()

def nuevo_id(lista, prefijo):
    nums = [int(x["id"][len(prefijo):]) for x in lista if x["id"].startswith(prefijo)]
    siguiente = max(nums, default=0) + 1
    return f"{prefijo}{siguiente:03d}"

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
def ver_dashboard(data):
    limpiar(); encabezado()
    cursos    = data["cursos"]
    aulas     = data["aulas"]
    proyectos = data["proyectos"]

    # KPIs
    total_est    = sum(c["estudiantes"] for c in cursos)
    act          = sum(1 for c in cursos if c["estado"] == "Activo")
    proy_activos = sum(1 for p in proyectos if p["estado"] == "En progreso")
    avg_prog     = round(sum(c["progreso"] for c in cursos) / len(cursos)) if cursos else 0

    kpi_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    kpi_table.add_column(justify="center"); kpi_table.add_column(justify="center")
    kpi_table.add_column(justify="center"); kpi_table.add_column(justify="center")
    kpi_table.add_row(
        Panel(f"[bold bright_magenta]{total_est}[/bold bright_magenta]\n[dim]Estudiantes[/dim]", border_style="bright_magenta", padding=(0,2)),
        Panel(f"[bold cyan]{act}[/bold cyan]\n[dim]Cursos Activos[/dim]", border_style="cyan", padding=(0,2)),
        Panel(f"[bold yellow]{proy_activos}[/bold yellow]\n[dim]Proyectos en Curso[/dim]", border_style="yellow", padding=(0,2)),
        Panel(f"[bold green]{avg_prog}%[/bold green]\n[dim]Avance Promedio[/dim]", border_style="green", padding=(0,2)),
    )
    console.print(kpi_table)

    # Progreso cursos
    console.print(Rule("[bold]Progreso de Cursos[/bold]", style="bright_magenta"))
    t = Table(box=box.ROUNDED, border_style="bright_magenta", header_style="bold bright_magenta", show_lines=False)
    t.add_column("Curso",    style="bold white",  min_width=24)
    t.add_column("Docente",  style="dim",          min_width=16)
    t.add_column("Progreso", min_width=28)
    t.add_column("Estado",   justify="center")
    for c in cursos:
        t.add_row(c["nombre"], c["docente"], barra_progreso(c["progreso"]), estado_badge(c["estado"]))
    console.print(t)

    # Proyectos próximos a vencer
    console.print(Rule("[bold]Proyectos por Vencer[/bold]", style="yellow"))
    urgentes = sorted(proyectos, key=lambda p: p["entrega"])[:4]
    cols_data = []
    for p in urgentes:
        curso_nombre = next((c["nombre"] for c in cursos if c["id"] == p["curso"]), p["curso"])
        cols_data.append(Panel(
            f"[bold]{p['nombre']}[/bold]\n"
            f"[dim]{curso_nombre}[/dim]\n"
            f"Entrega: {dias_restantes_str(p['entrega'])}\n"
            f"{barra_progreso(p['progreso'], 12)}",
            border_style="yellow", padding=(0,1)
        ))
    console.print(Columns(cols_data, equal=True))
    console.print()

# ─── CURSOS ───────────────────────────────────────────────────────────────────
def ver_cursos(data):
    limpiar(); encabezado()
    console.print(Rule("[bold cyan]📚 Gestión de Cursos[/bold cyan]", style="cyan"))
    t = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", show_lines=True)
    t.add_column("ID",          style="dim",          width=6)
    t.add_column("Nombre",      style="bold white",   min_width=22)
    t.add_column("Docente",     style="white",        min_width=16)
    t.add_column("Aula",        justify="center",     width=8)
    t.add_column("Créditos",    justify="center",     width=8)
    t.add_column("Estudiantes", justify="center",     width=11)
    t.add_column("Progreso",    min_width=26)
    t.add_column("Estado",      justify="center")
    for c in data["cursos"]:
        t.add_row(
            c["id"], c["nombre"], c["docente"], c["aula"],
            str(c["creditos"]), str(c["estudiantes"]),
            barra_progreso(c["progreso"]), estado_badge(c["estado"])
        )
    console.print(t)
    console.print()

def agregar_curso(data):
    console.print(Rule("[bold cyan]➕ Nuevo Curso[/bold cyan]", style="cyan"))
    nombre     = Prompt.ask("  Nombre del curso")
    docente    = Prompt.ask("  Docente")
    aulas_ids  = [a["id"] for a in data["aulas"]]
    console.print(f"  Aulas disponibles: {', '.join(aulas_ids)}")
    aula       = Prompt.ask("  Aula", choices=aulas_ids)
    creditos   = IntPrompt.ask("  Créditos", default=3)
    estudiantes= IntPrompt.ask("  Estudiantes", default=20)
    estado     = Prompt.ask("  Estado", choices=["Activo", "Finalizado"], default="Activo")
    nuevo = {
        "id": nuevo_id(data["cursos"], "C"),
        "nombre": nombre, "docente": docente, "aula": aula,
        "creditos": creditos, "estudiantes": estudiantes,
        "progreso": 0, "estado": estado,
        "inicio": date.today().isoformat()
    }
    data["cursos"].append(nuevo)
    guardar_datos(data)
    console.print(f"\n  [bold green]✅ Curso '{nombre}' registrado con ID {nuevo['id']}[/bold green]\n")

def editar_progreso_curso(data):
    console.print(Rule("[bold cyan]✏️  Actualizar Progreso[/bold cyan]", style="cyan"))
    ids = [c["id"] for c in data["cursos"]]
    console.print("  IDs disponibles: " + ", ".join(ids))
    cid  = Prompt.ask("  ID del curso", choices=ids)
    curso = next(c for c in data["cursos"] if c["id"] == cid)
    prog  = IntPrompt.ask(f"  Nuevo progreso para '{curso['nombre']}' (0-100)", default=curso["progreso"])
    curso["progreso"] = max(0, min(100, prog))
    if prog >= 100:
        curso["estado"] = "Finalizado"
    guardar_datos(data)
    console.print(f"\n  [bold green]✅ Progreso actualizado a {prog}%[/bold green]\n")

def eliminar_curso(data):
    console.print(Rule("[bold red]🗑️  Eliminar Curso[/bold red]", style="red"))
    ids = [c["id"] for c in data["cursos"]]
    console.print("  IDs disponibles: " + ", ".join(ids))
    cid = Prompt.ask("  ID a eliminar", choices=ids)
    curso = next(c for c in data["cursos"] if c["id"] == cid)
    if Confirm.ask(f"  ¿Eliminar '{curso['nombre']}'?", default=False):
        data["cursos"] = [c for c in data["cursos"] if c["id"] != cid]
        guardar_datos(data)
        console.print(f"\n  [bold green]✅ Curso eliminado[/bold green]\n")
    else:
        console.print("  [yellow]Operación cancelada[/yellow]\n")

# ─── AULAS ────────────────────────────────────────────────────────────────────
def ver_aulas(data):
    limpiar(); encabezado()
    console.print(Rule("[bold bright_magenta]🏫 Gestión de Aulas[/bold bright_magenta]", style="bright_magenta"))
    t = Table(box=box.ROUNDED, border_style="bright_magenta", header_style="bold bright_magenta", show_lines=True)
    t.add_column("ID",        style="bold white",  width=8)
    t.add_column("Edificio",  style="dim",          width=12)
    t.add_column("Tipo",      justify="center",     width=12)
    t.add_column("Capacidad", justify="center",     width=10)
    t.add_column("Curso Asignado",    min_width=22)
    t.add_column("Equipos",  style="dim",           min_width=22)
    for a in data["aulas"]:
        curso_asignado = next((c["nombre"] for c in data["cursos"] if c["aula"] == a["id"] and c["estado"] == "Activo"), "[dim]—[/dim]")
        tipo_color = {"Teoría": "cyan", "Laboratorio": "magenta", "Auditorio": "yellow"}.get(a["tipo"], "white")
        t.add_row(
            a["id"], a["edificio"],
            f"[{tipo_color}]{a['tipo']}[/{tipo_color}]",
            str(a["capacidad"]), curso_asignado, a["equipos"]
        )
    console.print(t)
    console.print()

def agregar_aula(data):
    console.print(Rule("[bold bright_magenta]➕ Nueva Aula[/bold bright_magenta]", style="bright_magenta"))
    aid       = Prompt.ask("  ID del aula (ej: D-101)")
    edificio  = Prompt.ask("  Edificio")
    tipo      = Prompt.ask("  Tipo", choices=["Teoría", "Laboratorio", "Auditorio"])
    capacidad = IntPrompt.ask("  Capacidad", default=30)
    equipos   = Prompt.ask("  Equipos disponibles", default="Proyector, AC")
    nuevo = {"id": aid, "edificio": edificio, "tipo": tipo, "capacidad": capacidad, "equipos": equipos}
    data["aulas"].append(nuevo)
    guardar_datos(data)
    console.print(f"\n  [bold green]✅ Aula '{aid}' registrada[/bold green]\n")

# ─── PROYECTOS ────────────────────────────────────────────────────────────────
def ver_proyectos(data):
    limpiar(); encabezado()
    console.print(Rule("[bold yellow]🚀 Gestión de Proyectos[/bold yellow]", style="yellow"))
    t = Table(box=box.ROUNDED, border_style="yellow", header_style="bold yellow", show_lines=True)
    t.add_column("ID",      style="dim",         width=6)
    t.add_column("Proyecto",style="bold white",  min_width=26)
    t.add_column("Curso",   style="dim",         min_width=18)
    t.add_column("Equipo",  justify="center",    width=7)
    t.add_column("Progreso",min_width=24)
    t.add_column("Entrega", justify="center",    width=12)
    t.add_column("Vence en",justify="center",    width=12)
    t.add_column("Estado",  justify="center")
    for p in data["proyectos"]:
        curso_nombre = next((c["nombre"] for c in data["cursos"] if c["id"] == p["curso"]), p["curso"])
        t.add_row(
            p["id"], p["nombre"], curso_nombre,
            f"👥 {p['equipo']}", barra_progreso(p["progreso"]),
            p["entrega"], dias_restantes_str(p["entrega"]),
            estado_badge(p["estado"])
        )
    console.print(t)
    console.print()

def agregar_proyecto(data):
    console.print(Rule("[bold yellow]➕ Nuevo Proyecto[/bold yellow]", style="yellow"))
    nombre  = Prompt.ask("  Nombre del proyecto")
    cursos_ids = [c["id"] for c in data["cursos"]]
    console.print("  Cursos: " + ", ".join(f"{c['id']}={c['nombre']}" for c in data["cursos"]))
    curso   = Prompt.ask("  ID del curso", choices=cursos_ids)
    equipo  = IntPrompt.ask("  Miembros del equipo", default=3)
    entrega = Prompt.ask("  Fecha de entrega (YYYY-MM-DD)")
    estado  = Prompt.ask("  Estado", choices=["Inicio", "En progreso", "Revisión", "Completado"], default="Inicio")
    nuevo = {
        "id": nuevo_id(data["proyectos"], "P"),
        "nombre": nombre, "curso": curso, "equipo": equipo,
        "progreso": 0, "entrega": entrega, "estado": estado
    }
    data["proyectos"].append(nuevo)
    guardar_datos(data)
    console.print(f"\n  [bold green]✅ Proyecto '{nombre}' registrado con ID {nuevo['id']}[/bold green]\n")

def actualizar_proyecto(data):
    console.print(Rule("[bold yellow]✏️  Actualizar Proyecto[/bold yellow]", style="yellow"))
    ids = [p["id"] for p in data["proyectos"]]
    console.print("  IDs: " + ", ".join(ids))
    pid  = Prompt.ask("  ID del proyecto", choices=ids)
    proy = next(p for p in data["proyectos"] if p["id"] == pid)
    prog = IntPrompt.ask(f"  Progreso para '{proy['nombre']}' (0-100)", default=proy["progreso"])
    est  = Prompt.ask("  Estado", choices=["Inicio", "En progreso", "Revisión", "Completado"], default=proy["estado"])
    proy["progreso"] = max(0, min(100, prog))
    proy["estado"]   = est
    guardar_datos(data)
    console.print(f"\n  [bold green]✅ Proyecto actualizado[/bold green]\n")

# ─── MENÚS ────────────────────────────────────────────────────────────────────
def menu_cursos(data):
    while True:
        limpiar(); encabezado()
        ver_cursos(data)
        console.print("[1] Agregar curso  [2] Actualizar progreso  [3] Eliminar  [0] Volver\n")
        op = Prompt.ask("  Opción", choices=["0","1","2","3"], default="0")
        if op == "1": agregar_curso(data);        input("  Presiona Enter para continuar...")
        elif op == "2": editar_progreso_curso(data); input("  Presiona Enter para continuar...")
        elif op == "3": eliminar_curso(data);     input("  Presiona Enter para continuar...")
        elif op == "0": break

def menu_aulas(data):
    while True:
        limpiar(); encabezado()
        ver_aulas(data)
        console.print("[1] Agregar aula  [0] Volver\n")
        op = Prompt.ask("  Opción", choices=["0","1"], default="0")
        if op == "1": agregar_aula(data); input("  Presiona Enter para continuar...")
        elif op == "0": break

def menu_proyectos(data):
    while True:
        limpiar(); encabezado()
        ver_proyectos(data)
        console.print("[1] Agregar proyecto  [2] Actualizar estado  [0] Volver\n")
        op = Prompt.ask("  Opción", choices=["0","1","2"], default="0")
        if op == "1": agregar_proyecto(data);    input("  Presiona Enter para continuar...")
        elif op == "2": actualizar_proyecto(data); input("  Presiona Enter para continuar...")
        elif op == "0": break

def menu_principal():
    data = cargar_datos()
    while True:
        limpiar(); encabezado()
        console.print(Align.center(
            "[bold bright_magenta][1][/bold bright_magenta] 📊 Dashboard    "
            "[bold cyan][2][/bold cyan] 📚 Cursos    "
            "[bold bright_magenta][3][/bold bright_magenta] 🏫 Aulas    "
            "[bold yellow][4][/bold yellow] 🚀 Proyectos    "
            "[bold red][0][/bold red] Salir"
        ))
        console.print()
        op = Prompt.ask("  Selecciona", choices=["0","1","2","3","4"], default="1")
        if op == "1":
            ver_dashboard(data)
            input("  Presiona Enter para continuar...")
        elif op == "2": menu_cursos(data)
        elif op == "3": menu_aulas(data)
        elif op == "4": menu_proyectos(data)
        elif op == "0":
            console.print("\n  [bold bright_magenta]¡Hasta pronto! 🎓[/bold bright_magenta]\n")
            sys.exit(0)

if __name__ == "__main__":
    menu_principal()
