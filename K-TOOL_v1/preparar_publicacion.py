"""Prepara una carpeta nueva por lista permitida. No publica ni obtiene sellos."""
import argparse
import hashlib
import re
import shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", required=True, help="Carpeta kits nueva, preferentemente fuera de git")
    ap.add_argument("--maestro", required=True, help="Solo se incorpora su hash, nunca su contenido")
    a = ap.parse_args()
    origen = Path(__file__).resolve().parent
    reglas = (origen / "REGLAS_B01.md").read_text(encoding="utf-8")
    if not re.search(r"k\s*≥\s*\*\*(?:[0-9]|1[0-9]|20)\*\*/20", reglas):
        ap.error("R1 sigue pendiente o no tiene el formato k ≥ **N**/20; debe decidirlo Omar")
    maestro = Path(a.maestro).read_bytes()
    destino = Path(a.destino).resolve()
    if destino.exists():
        ap.error("El destino ya existe; no se sobrescribe una preparación anterior")
    comunes = ["KIT.md", "REGLAS_B01.md", ".gitignore", "control_ejecucion.py"]
    archivos = {
        "K-TOOL_v1": comunes + ["comandos_publicos.json", "prueba_needle.py", "verificar_reserva.py", "medir_tamanos.py", "preparar_publicacion.py"],
        "K-STT_v1": comunes + ["prueba_whistle.py", "frases_whistle.txt", "referencias_whistle.json"],
    }
    for nombre in [n for nombres in archivos.values() for n in nombres] + ["verificar_huellas.py"]:
        if not (origen / nombre).is_file():
            ap.error("Falta archivo permitido: " + nombre)
    lineas = []
    for kit, nombres in archivos.items():
        carpeta = destino / kit
        carpeta.mkdir(parents=True)
        for nombre in nombres:
            copia = carpeta / nombre
            shutil.copyfile(origen / nombre, copia)
            lineas.append(f"{hashlib.sha256(copia.read_bytes()).hexdigest()}  {kit}/{nombre}")
    # Git para Windows convierte CRLF→LF al hacer commit si no se le dice lo contrario: el repositorio publicaría
    # bytes distintos de los hasheados. «* -text» guarda los bytes tal cual. verificar_huellas.py lo comprueba.
    (destino / ".gitattributes").write_bytes(b"* -text\n")
    shutil.copyfile(origen / "verificar_huellas.py", destino / "verificar_huellas.py")
    for nombre in (".gitattributes", "verificar_huellas.py"):
        lineas.append(f"{hashlib.sha256((destino / nombre).read_bytes()).hexdigest()}  {nombre}")
    lineas.append(f"{hashlib.sha256(maestro).hexdigest()}  PRIVADO/comandos.json")
    (destino / "SHA256.txt").write_text("\n".join(sorted(lineas)) + "\n", encoding="utf-8")
    print("PREPARADO SIN SELLO: revisar, publicar y obtener/verificar el sello antes de ejecutar. No acredita E3.")


if __name__ == "__main__":
    main()
