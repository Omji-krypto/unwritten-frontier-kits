"""Controles locales compartidos; no carga modelos ni transmite datos."""
import json
import os
import time
from pathlib import Path


def preparar(a):
    if a.procesos not in (1, 3) or getattr(a, "repeticiones", 1) != 1:
        raise ValueError("B01 exige tres procesos con una pasada; 1 se reserva al proceso individual.")
    if os.environ.get("NEEDLE_TELEMETRY") != "0":
        raise ValueError("Establece NEEDLE_TELEMETRY=0 antes de ejecutar.")
    base = Path(a.salida)
    rutas = [base, base.with_name(base.stem + "_publico.json")]
    rutas += list(base.parent.glob(base.stem + "_proceso*.json"))
    if any(p.exists() for p in rutas):
        raise ValueError("Ya existen resultados con ese nombre: usa otro --salida; no se sobrescriben.")
    if not base.parent.is_dir():
        raise ValueError("La carpeta de salida debe existir.")


def abortar(a, motivo):
    base = Path(a.salida)
    recibo = base.with_name(f"{base.stem}_ABORTADA_{time.time_ns()}.json")
    with recibo.open("x", encoding="utf-8") as f:
        json.dump({"estado": "ABORTADA", "motivo": motivo,
                   "fecha_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "sin_veredicto": True}, f, ensure_ascii=False, indent=2)


def ejecutar(a, accion):
    preparar(a)
    try:
        return accion(a)
    except (Exception, SystemExit, KeyboardInterrupt) as exc:
        # No publicar mensajes de SDK: pueden contener órdenes o rutas privadas.
        abortar(a, type(exc).__name__ + ": ejecución interrumpida; revisar registro privado")
        raise
