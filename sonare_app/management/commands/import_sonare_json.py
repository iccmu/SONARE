import json
from pathlib import Path

from django.core.management.base import BaseCommand

from sonare_app.models import Documento, Persona


class Command(BaseCommand):
    help = "Importa personas y documentos desde los JSON de SONARE"

    def add_arguments(self, parser):
        parser.add_argument("--personas", type=Path, required=True, help="Ruta a personas.json")
        parser.add_argument("--docs", type=Path, required=True, help="Ruta a documentos.json")

    def handle(self, *args, **options):
        # ── 1. Personas ──────────────────────────────────────────────────────
        self.stdout.write("Importando personas...")
        with open(options["personas"], encoding="utf-8") as f:
            personas_data = json.load(f)

        personas_creadas = 0
        for p in personas_data:
            _, created = Persona.objects.update_or_create(
                id=p["id"],
                defaults={
                    "nombre_uniforme": p.get("nombre_uniforme") or "",
                    "apellidos_uniforme": p.get("apellidos_uniforme") or "",
                    "otras_formas_nombre": p.get("otras_formas_nombre") or "",
                    "titulo_nobiliario": p.get("titulo_nobiliario"),
                    "id_viaff": p.get("id_viaff"),
                    "genero": p.get("genero"),
                    "fecha_nacimiento": p.get("fecha_nacimiento"),
                    "fecha_muerte": p.get("fecha_muerte"),
                    "funcion": p.get("funcion") or "no músico",
                    "cargo_profesional": p.get("cargo_profesional"),
                },
            )
            if created:
                personas_creadas += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ {personas_creadas} personas creadas / {len(personas_data) - personas_creadas} actualizadas"))

        # ── 2. Documentos (sin M2M) ───────────────────────────────────────────
        self.stdout.write("Importando documentos...")
        with open(options["docs"], encoding="utf-8") as f:
            docs_data = json.load(f)

        docs_creados = 0
        otras_personas_pendiente = []  # [(doc_id, [persona_ids])]

        for d in docs_data:
            def fk(field):
                pid = d.get(field)
                if not pid:
                    return None
                try:
                    return Persona.objects.get(id=pid)
                except Persona.DoesNotExist:
                    self.stderr.write(f"  ! Persona {pid} no encontrada (doc {d['id']}, campo {field})")
                    return None

            _, created = Documento.objects.update_or_create(
                id=d["id"],
                defaults={
                    "tipo_documento": d.get("tipo_documento") or "",
                    "fecha_documento": d.get("fecha_documento"),
                    "lugar_documento": d.get("lugar_documento"),
                    "fecha_inicio": d.get("fecha_inicio"),
                    "fecha_fin": d.get("fecha_fin"),
                    "lugar": d.get("lugar"),
                    "observaciones_lugar": d.get("observaciones_lugar"),
                    "texto": d.get("texto"),
                    "emisor": fk("emisor_id"),
                    "visto": fk("visto_id"),
                    "destinatario": fk("destinatario_id"),
                    "seccion_administrativa_emision": d.get("seccion_administrativa_emision"),
                    "seccion_administrativa_recepcion": d.get("seccion_administrativa_recepcion"),
                    "hora": d.get("hora"),
                    "luces": d.get("luces"),
                    "signatura": d.get("signatura"),
                    "practica_musical": d.get("practica_musical"),
                    "objeto_musical_desc": d.get("objeto_musical_desc"),
                    "autor": d.get("autor"),
                    "mencion_musica": bool(d.get("mencion_musica", False)),
                    "observaciones": d.get("observaciones"),
                    "evento_descripcion": d.get("evento_descripcion"),
                    "metadata": d.get("metadata") or {},
                },
            )
            if created:
                docs_creados += 1

            otras_ids = d.get("otras_personas_ids") or []
            if otras_ids:
                otras_personas_pendiente.append((d["id"], otras_ids))

        self.stdout.write(self.style.SUCCESS(f"  ✓ {docs_creados} documentos creados / {len(docs_data) - docs_creados} actualizados"))

        # ── 3. M2M otras_personas ─────────────────────────────────────────────
        self.stdout.write("Enlazando otras_personas (M2M)...")
        m2m_total = 0
        for doc_id, persona_ids in otras_personas_pendiente:
            try:
                doc = Documento.objects.get(id=doc_id)
            except Documento.DoesNotExist:
                continue
            for pid in persona_ids:
                try:
                    p = Persona.objects.get(id=pid)
                    doc.otras_personas.add(p)
                    m2m_total += 1
                except Persona.DoesNotExist:
                    self.stderr.write(f"  ! Persona M2M {pid} no encontrada (doc {doc_id})")

        self.stdout.write(self.style.SUCCESS(f"  ✓ {m2m_total} relaciones M2M creadas"))
        self.stdout.write(self.style.SUCCESS("\nImportación completada."))
