"""Interfaz común para el catálogo semántico y las decisiones del docente."""
import json
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def add_commands(commands):
    help_texts = {
        "catalog-sync": "Reconciliar identidades, versiones y referencias",
        "catalog-show": "Consultar el catálogo",
        "catalog-classify": "Registrar clasificación, evidencia y confirmación",
        "catalog-group": "Crear una agrupación lógica",
        "catalog-regroup": "Cambiar la agrupación lógica de un material",
        "catalog-resolve": "Resolver una identidad ambigua con la decisión del docente",
        "organize-plan": "Guardar una propuesta, sin mover originales",
        "organize-apply": "Ejecutar únicamente las operaciones aceptadas",
    }
    for name, label in help_texts.items():
        parser = commands.add_parser(name, help=label)
        parser.add_argument("root", type=Path)
        if name == "catalog-sync":
            parser.add_argument("--scope", help="Ruta relativa para reconciliar una unidad")
        elif name == "catalog-classify":
            parser.add_argument("material_id")
            parser.add_argument("primary")
            parser.add_argument("--secondary", action="append")
            parser.add_argument("--access", choices=("estudiante", "docente"))
            parser.add_argument("--inferred", action="store_true", help="Clasificación propuesta por el agente")
            parser.add_argument("--evidence", required=True)
            parser.add_argument("--confidence", type=float, help="Confianza entre 0 y 1")
        elif name == "catalog-group":
            parser.add_argument("title")
            parser.add_argument("--parent")
        elif name == "catalog-regroup":
            parser.add_argument("material_id")
            parser.add_argument("--parent")
        elif name == "catalog-resolve":
            parser.add_argument("path")
            choice = parser.add_mutually_exclusive_group(required=True)
            choice.add_argument("--material-id")
            choice.add_argument("--new", action="store_true")
        elif name == "organize-plan":
            parser.add_argument("--mode", choices=("moves", "categories", "keep", "promote"), default="moves")
            parser.add_argument("--moves", type=Path, help="Lista JSON con material_id y destination")
            parser.add_argument("--directory")
        elif name == "organize-apply":
            parser.add_argument("plan_id")
            choice = parser.add_mutually_exclusive_group(required=True)
            choice.add_argument("--all", action="store_true")
            choice.add_argument("--operation", action="append")
            parser.add_argument("--changes", type=Path, help="Objeto JSON con destinos corregidos por operación")


def dispatch(args):
    from . import catalog
    from .knowledge import refresh_knowledge
    from .organization import apply_organization, plan_organization
    from .dependencies import recover_dependencies, refresh_dependencies
    root = args.root
    if args.command == "catalog-show":
        return catalog.read_catalog(root)
    if args.command == "catalog-sync":
        recover_dependencies(root)
        result = catalog.reconcile(root, scope=args.scope)
        result["dependencies"] = refresh_dependencies(root, result["moves"])
        result["knowledge"] = refresh_knowledge(root)
        return result
    if args.command == "catalog-classify":
        result = catalog.classify(root, args.material_id, primary=args.primary, secondary=args.secondary,
                                  confirmed=not args.inferred, evidence=args.evidence,
                                  confidence=args.confidence, access=args.access)
        if args.access:
            return {"material": result, "knowledge": refresh_knowledge(root)}
        return result
    if args.command == "catalog-group":
        return catalog.create_group(root, args.title, parent_id=args.parent)
    if args.command == "catalog-regroup":
        return catalog.regroup(root, args.material_id, args.parent)
    if args.command == "catalog-resolve":
        result = catalog.resolve_identity(root, args.path, material_id=args.material_id)
        return {"material": result, "dependencies": refresh_dependencies(root), "knowledge": refresh_knowledge(root)}
    if args.command == "organize-plan":
        if args.mode != "keep":
            refresh_dependencies(root)
        return plan_organization(root, read_json(args.moves) if args.moves else [], mode=args.mode,
                                 directory=args.directory)
    result = apply_organization(root, args.plan_id, accepted="all" if args.all else args.operation,
                                changes=read_json(args.changes) if args.changes else None)
    result["dependencies"] = refresh_dependencies(root, result["changes"])
    result["knowledge"] = refresh_knowledge(root)
    return result
