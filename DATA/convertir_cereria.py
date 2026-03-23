#!/usr/bin/env python3
"""
Convierte el Excel de Cerería a JSON compatibles con la web SONARE.
Genera:
  - documentos_cereria.json  (179 registros nuevos)
  - personas_cereria.json    (personas nuevas extraídas del Excel)
  - personas_merged.json     (personas.json + nuevas, para revisión)
  - documentos_merged.json   (documentos.json + nuevos, para revisión)
"""

import json
import re
import openpyxl
from pathlib import Path

BASE = Path(__file__).parent.parent
EXCEL = Path(__file__).parent / "260301 Cerería EXCEL para filtrar.xlsx"

# ── Cargar datos existentes ─────────────────────────────────────────────────
with open(BASE / "personas.json", encoding="utf-8") as f:
    personas_existentes = json.load(f)

with open(BASE / "documentos.json", encoding="utf-8") as f:
    documentos_existentes = json.load(f)


# ── Índice de personas existentes por nombre normalizado ────────────────────
def normalizar_nombre(s):
    """Quita acentos, pasa a minúsculas y colapsa espacios."""
    import unicodedata

    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


indice_personas = {}
for p in personas_existentes:
    n = normalizar_nombre(f"{p['nombre_uniforme']} {p['apellidos_uniforme']}")
    indice_personas[n] = p["id"]
    # También indexar formas alternativas
    for forma in (p.get("otras_formas_nombre") or "").split(","):
        forma = normalizar_nombre(forma.strip())
        if forma:
            indice_personas[forma] = p["id"]

# Alias manuales conocidos del Excel → IDs existentes
ALIAS_MANUALES = {
    "carlos iv":          None,   # se creará como CER_PER
    "principe de parma":  None,
    "infante don antonio": None,
}


# ── Parsear nombre en formato "Apellidos, Nombre" ───────────────────────────
def parsear_nombre(raw):
    """Devuelve (nombre, apellidos, nombre_completo_normalizado)."""
    raw = (raw or "").strip()
    if not raw:
        return None, None, None
    if "," in raw:
        partes = raw.split(",", 1)
        apellidos = partes[0].strip()
        nombre = partes[1].strip()
    else:
        # Sin coma: tomar última palabra como apellido si hay varias
        partes = raw.rsplit(" ", 1)
        if len(partes) == 2:
            nombre, apellidos = partes[0], partes[1]
        else:
            nombre, apellidos = raw, ""
    return nombre, apellidos, normalizar_nombre(raw)


# ── Registro de personas nuevas ─────────────────────────────────────────────
personas_nuevas = {}  # raw_name → dict


def get_o_crear_persona_id(raw_name):
    """Devuelve el ID de una persona, buscando primero en existentes."""
    if not raw_name or not raw_name.strip():
        return None
    raw = raw_name.strip()
    key = normalizar_nombre(raw)

    # 1. Alias manual
    if key in ALIAS_MANUALES:
        pid = ALIAS_MANUALES[key]
        if pid:
            return pid
        # Si alias apunta a None, cae a creación

    # 2. Índice existentes
    if key in indice_personas:
        return indice_personas[key]

    # 3. Ya creado antes
    if key in personas_nuevas:
        return personas_nuevas[key]["id"]

    # 4. Crear nueva
    idx = len(personas_nuevas) + 1
    nuevo_id = f"CER_PER{idx:03d}"
    nombre, apellidos, _ = parsear_nombre(raw)
    personas_nuevas[key] = {
        "id": nuevo_id,
        "nombre_uniforme": nombre or raw,
        "apellidos_uniforme": apellidos or "",
        "otras_formas_nombre": raw if raw != f"{nombre} {apellidos}".strip() else "",
        "titulo_nobiliario": None,
        "id_viaff": None,
        "genero": None,
        "fecha_nacimiento": None,
        "fecha_muerte": None,
        "funcion": "no músico",
        "cargo_profesional": None,
        "documentos_ids": [],
        "eventos_ids": [],
        "obras_ids": [],
    }
    indice_personas[key] = nuevo_id
    return nuevo_id


# ── Leer Excel ───────────────────────────────────────────────────────────────
wb = openpyxl.load_workbook(EXCEL, read_only=True, data_only=True)
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
headers = [str(h).strip() if h is not None else "" for h in rows[0]]


def col(row, nombre_col):
    """Obtiene el valor de una columna por nombre."""
    try:
        idx = headers.index(nombre_col)
        val = row[idx] if idx < len(row) else None
    except ValueError:
        return None
    if val is None:
        return None
    return str(val).strip() if str(val).strip() else None


# ── Construir lugar jerárquico ───────────────────────────────────────────────
def construir_lugar(lugar_raw, detalle_raw):
    """Intenta construir 'Ciudad > Lugar > Detalle' para el campo lugar."""
    parts = []
    if lugar_raw:
        parts.append(lugar_raw.strip())
    if detalle_raw:
        detalle = detalle_raw.strip()
        # Evitar duplicar si el detalle ya está incluido en lugar
        if detalle and detalle not in (lugar_raw or ""):
            parts.append(detalle)
    return " > ".join(parts) if parts else None


# ── Convertir filas ──────────────────────────────────────────────────────────
documentos_nuevos = []
skipped = []

for i, row in enumerate(rows[1:], start=1):
    # Ignorar filas marcadas como FALTA PASAR o sin Doc ID
    tipo = col(row, "Tipo de documento") or ""
    if "FALTA PASAR" in tipo.upper():
        skipped.append(i)
        continue
    doc_id_raw = col(row, "Doc ID")
    if not doc_id_raw:
        skipped.append(i)
        continue

    doc_id = f"CER{int(float(doc_id_raw)):03d}"

    # Personas (columnas actualizadas en el Excel)
    emisor_raw = col(row, "Emisor") or col(row, "Emisor 1")
    visto_raw = col(row, "Supervisor") or col(row, "Visto")
    destinatario_raw = col(row, "Destinatario")
    personas_raw = col(row, "Personas")
    otras_raw = col(row, "Otras personas")

    emisor_id = get_o_crear_persona_id(emisor_raw)
    destinatario_id = get_o_crear_persona_id(destinatario_raw)
    visto_id = get_o_crear_persona_id(visto_raw)

    # Personas citadas (campo "Personas" puede contener varias separadas por coma o ;)
    otras_ids = []
    if personas_raw:
        for p in re.split(r"[;,]", personas_raw):
            pid = get_o_crear_persona_id(p.strip())
            if pid and pid not in otras_ids:
                otras_ids.append(pid)

    lugar_evento = construir_lugar(col(row, "Lugar"), col(row, "Detalle lugar"))

    mencion_raw = (col(row, "Mención música") or "").strip().upper()
    mencion_bool = mencion_raw in ("SÍ", "SI", "S", "YES", "Y", "1", "TRUE")

    doc = {
        "id": doc_id,
        "tipo_documento": tipo or "Cuenta simple de gasto extraordinario",
        "fecha_documento": col(row, "Fecha documento"),
        "lugar_documento": col(row, "Lugar documento"),
        "fecha_inicio": col(row, "Fecha inicio"),
        "fecha_fin": col(row, "Fecha fin"),
        "lugar": lugar_evento,
        "observaciones_lugar": col(row, "Detalle lugar"),
        "texto": col(row, "Texto"),
        "emisor_id": emisor_id,
        "visto_id": visto_id,
        "destinatario_id": destinatario_id,
        "seccion_administrativa_emision": col(row, "Sección administrativa"),
        "seccion_administrativa_recepcion": None,
        "hora": col(row, "Hora"),
        "luces": col(row, "Luces"),
        "otras_personas_ids": otras_ids,
        "evento_id": None,
        "obra_musical_id": None,
        "objeto_musical_id": None,
        "evento_descripcion": col(row, "Evento"),
        "signatura": col(row, "Signatura"),
        "practica_musical": col(row, "Práctica musical"),
        "objeto_musical_desc": col(row, "Objeto musical"),
        "autor": col(row, "Autor"),
        "mencion_musica": mencion_bool,
        "observaciones": col(row, "Observaciones"),
        "metadata": {
            "ref_orden_entrada": col(row, "Ref orden entrada"),
            "dias": col(row, "Días"),
            "numero_eventos": col(row, "Número eventos"),
            "numero_total": col(row, "Número total"),
            "numero_musica": col(row, "Número música"),
            "carpeta_fotos": col(row, "Carpeta fotos"),
            "otras_personas_ref": otras_raw,
        },
    }

    # Registrar doc_id en las personas involucradas
    for pid in [emisor_id, visto_id, destinatario_id] + otras_ids:
        if not pid:
            continue
        for pn in personas_nuevas.values():
            if pn["id"] == pid and doc_id not in pn["documentos_ids"]:
                pn["documentos_ids"].append(doc_id)

    documentos_nuevos.append(doc)

wb.close()

# ── Escribir archivos intermedios ────────────────────────────────────────────
personas_nuevas_list = list(personas_nuevas.values())

with open(BASE / "DATA/documentos_cereria.json", "w", encoding="utf-8") as f:
    json.dump(documentos_nuevos, f, ensure_ascii=False, indent=2)

with open(BASE / "DATA/personas_cereria.json", "w", encoding="utf-8") as f:
    json.dump(personas_nuevas_list, f, ensure_ascii=False, indent=2)

# ── Escribir archivos merged (para uso directo en la web) ────────────────────
documentos_merged = documentos_existentes + documentos_nuevos
personas_merged = personas_existentes + personas_nuevas_list

with open(BASE / "DATA/documentos_merged.json", "w", encoding="utf-8") as f:
    json.dump(documentos_merged, f, ensure_ascii=False, indent=2)

with open(BASE / "DATA/personas_merged.json", "w", encoding="utf-8") as f:
    json.dump(personas_merged, f, ensure_ascii=False, indent=2)

print(f"✓ Documentos convertidos:  {len(documentos_nuevos)}")
print(f"✓ Documentos omitidos:     {len(skipped)} (FALTA PASAR / sin ID)")
print(f"✓ Personas nuevas creadas: {len(personas_nuevas_list)}")
print(f"✓ Total documentos merged: {len(documentos_merged)}")
print(f"✓ Total personas merged:   {len(personas_merged)}")
print()
print("Archivos generados:")
print("  DATA/documentos_cereria.json")
print("  DATA/personas_cereria.json")
print("  DATA/documentos_merged.json  ← copia esto a documentos.json")
print("  DATA/personas_merged.json    ← copia esto a personas.json")
