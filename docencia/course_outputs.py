"""Resolver el destino de una operación situada dentro de un curso configurado."""
from pathlib import Path
import os

from .project import CONFIG_NAME, MANAGEMENT_NAMES, DEFAULT_SPACES, find_project, load_project
from .spaces import resolve_space


def output_project(path):
    """Los formatos independientes y anteriores conservan sus validadores originales."""
    path = Path(path).expanduser().resolve()
    for parent in (path, *path.parents):
        if any((parent / name / CONFIG_NAME).is_file() for name in MANAGEMENT_NAMES) or all((parent / dirs[0]).is_dir() for dirs in DEFAULT_SPACES.values()):
            return find_project(path)
    return None


def course_output(path, role, *, inputs=()):
    """En un curso v4 vincular los productos al espacio correspondiente antes de escribir."""
    target = Path(os.path.abspath(Path(path).expanduser()))
    project = output_project(target)
    for item in inputs:
        if item is None:
            continue
        anchor = output_project(item)
        if anchor and load_project(anchor)["structure"] == "curso-v4" and anchor != project:
            raise ValueError("La salida debe estar en el mismo proyecto que sus entradas.")
    if project and load_project(project)["structure"] == "curso-v4":
        # Usar la ruta léxica para que resolve_space compruebe también los enlaces.
        if not target.is_relative_to(project):
            for parent in target.parents:
                if parent.resolve() == project:
                    target = project / target.relative_to(parent)
                    break
        target = resolve_space(project, role, target.relative_to(project).as_posix())
    return target.resolve()
