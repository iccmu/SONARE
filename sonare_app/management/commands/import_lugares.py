"""
Parsea el campo `lugar` de cada Documento (string Excel tipo "Sitio > Dependencia"),
crea los objetos Lugar y enlaza Documento.lugar_ref.
"""
import re
from django.core.management.base import BaseCommand
from sonare_app.models import Documento, Lugar


def limpiar(s):
    """Elimina brackets, interrogaciones sueltas y espacios extra."""
    s = re.sub(r'\]+$', '', s or '')   # brackets al final
    s = re.sub(r'\?+$', '', s)          # interrogaciones al final
    s = s.strip(' ,;')
    return s.strip()


def get_o_crear(nombre, padre=None):
    nombre = limpiar(nombre)
    if not nombre or nombre in ('?', ''):
        return None
    obj, _ = Lugar.objects.get_or_create(nombre=nombre, padre=padre)
    return obj


class Command(BaseCommand):
    help = "Importa lugares jerárquicos desde el campo lugar de Documento"

    def handle(self, *args, **options):
        sin_lugar = 0
        asignados = 0
        no_resueltos = 0

        for doc in Documento.objects.all():
            raw = (doc.lugar or '').strip()
            if not raw:
                sin_lugar += 1
                continue

            # Separar por " > "
            partes = [limpiar(p) for p in raw.split('>')]
            partes = [p for p in partes if p and p != '?']

            if not partes:
                no_resueltos += 1
                continue

            # Algunos documentos tienen múltiples dependencias separadas por coma
            # dentro del último nivel: "Cuarto del Rey, Cuarto de la Reina"
            # → usamos el primer valor como lugar principal
            nivel1_raw = partes[0].split(',')[0].strip()
            nivel1 = get_o_crear(nivel1_raw)

            if len(partes) >= 2:
                nivel2_raw = partes[1].split(',')[0].strip()
                lugar_final = get_o_crear(nivel2_raw, padre=nivel1)
            else:
                lugar_final = nivel1

            if lugar_final:
                doc.lugar_ref = lugar_final
                doc.save(update_fields=['lugar_ref'])
                asignados += 1
            else:
                no_resueltos += 1

        total_lugares = Lugar.objects.count()
        nivel1_count = Lugar.objects.filter(padre__isnull=True).count()
        nivel2_count = Lugar.objects.filter(padre__isnull=False).count()

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Lugares creados: {total_lugares} "
            f"({nivel1_count} sitios reales, {nivel2_count} dependencias)"
        ))
        self.stdout.write(self.style.SUCCESS(f"✓ Documentos enlazados: {asignados}"))
        if sin_lugar:
            self.stdout.write(f"  · Sin lugar: {sin_lugar}")
        if no_resueltos:
            self.stdout.write(f"  · No resueltos: {no_resueltos}")
