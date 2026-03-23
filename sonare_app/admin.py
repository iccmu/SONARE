from django.contrib import admin
from .models import Documento, Lugar, Persona


class HijosInline(admin.TabularInline):
    model = Lugar
    fk_name = "padre"
    extra = 1
    fields = ["nombre"]
    verbose_name = "Dependencia"
    verbose_name_plural = "Dependencias"


@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display = ["nombre", "padre", "num_documentos"]
    list_filter = ["padre"]
    search_fields = ["nombre"]
    inlines = [HijosInline]
    # Solo mostrar los nodos raíz en la lista principal
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("padre")

    def num_documentos(self, obj):
        return obj.documentos.count()
    num_documentos.short_description = "Docs"


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre_uniforme", "apellidos_uniforme", "funcion", "cargo_profesional", "genero"]
    search_fields = ["id", "nombre_uniforme", "apellidos_uniforme", "otras_formas_nombre"]
    list_filter = ["funcion", "genero"]
    fieldsets = (
        ("Identificación", {"fields": ("id", "id_viaff")}),
        ("Nombre", {"fields": ("nombre_uniforme", "apellidos_uniforme", "otras_formas_nombre", "titulo_nobiliario")}),
        ("Datos personales", {"fields": ("genero", "fecha_nacimiento", "fecha_muerte")}),
        ("Función", {"fields": ("funcion", "cargo_profesional")}),
    )


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ["id", "tipo_documento", "fecha_documento", "get_lugar", "emisor", "mencion_musica"]
    search_fields = ["id", "tipo_documento", "signatura", "texto", "practica_musical", "lugar"]
    list_filter = ["tipo_documento", "mencion_musica", "hora", "lugar_ref__padre", "lugar_ref"]
    raw_id_fields = ["emisor", "visto", "destinatario"]
    filter_horizontal = ["otras_personas"]
    fieldsets = (
        ("Identificación", {"fields": ("id", "tipo_documento", "signatura")}),
        ("Fechas y Lugar", {"fields": (
            "fecha_documento", "lugar_documento",
            "fecha_inicio", "fecha_fin",
            "lugar_ref", "observaciones_lugar", "hora",
        )}),
        ("Personas", {"fields": ("emisor", "visto", "destinatario", "otras_personas")}),
        ("Administración", {"fields": ("seccion_administrativa_emision", "seccion_administrativa_recepcion")}),
        ("Contenido", {"fields": ("texto", "practica_musical", "objeto_musical_desc", "luces", "autor", "evento_descripcion")}),
        ("Flags", {"fields": ("mencion_musica",)}),
        ("Notas", {"fields": ("observaciones",)}),
        ("Texto original Excel", {"fields": ("lugar",), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
    )

    def get_lugar(self, obj):
        return str(obj.lugar_ref) if obj.lugar_ref else obj.lugar_documento or "—"
    get_lugar.short_description = "Lugar"
