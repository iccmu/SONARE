from django import forms
from .models import Documento, Persona


class PersonaRadioSelect(forms.RadioSelect):
    """RadioSelect con opción vacía más legible."""
    def optgroups(self, name, value, attrs=None):
        groups = super().optgroups(name, value, attrs)
        # Renombrar la primera opción vacía
        for group_name, subgroup, index in groups:
            for option in subgroup:
                if option["value"] in ("", None):
                    option["label"] = "— Ninguno —"
        return groups


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            "tipo_documento", "signatura",
            "fecha_documento", "lugar_documento", "fecha_inicio", "fecha_fin",
            "lugar_ref", "observaciones_lugar",
            "emisor", "visto", "destinatario", "otras_personas",
            "seccion_administrativa_emision", "seccion_administrativa_recepcion",
            "texto", "practica_musical", "objeto_musical_desc",
            "luces", "hora", "autor", "evento_descripcion",
            "mencion_musica", "observaciones",
        ]
        widgets = {
            "tipo_documento": forms.TextInput(attrs={"class": "form-control"}),
            "signatura":      forms.TextInput(attrs={"class": "form-control"}),
            "fecha_documento": forms.TextInput(attrs={"class": "form-control", "placeholder": "YYYY-MM-DD"}),
            "lugar_documento": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_inicio":   forms.TextInput(attrs={"class": "form-control", "placeholder": "YYYY-MM-DD"}),
            "fecha_fin":      forms.TextInput(attrs={"class": "form-control", "placeholder": "YYYY-MM-DD"}),
            "lugar_ref":      forms.Select(attrs={"class": "form-control"}),
            "observaciones_lugar": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "emisor":         PersonaRadioSelect(),
            "visto":          PersonaRadioSelect(),
            "destinatario":   PersonaRadioSelect(),
            "otras_personas": forms.CheckboxSelectMultiple(),
            "seccion_administrativa_emision":   forms.TextInput(attrs={"class": "form-control"}),
            "seccion_administrativa_recepcion": forms.TextInput(attrs={"class": "form-control"}),
            "texto":              forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "practica_musical":   forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "objeto_musical_desc": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "luces":          forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "hora":           forms.TextInput(attrs={"class": "form-control"}),
            "autor":          forms.TextInput(attrs={"class": "form-control"}),
            "evento_descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "mencion_musica": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observaciones":  forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "tipo_documento": "Tipo de documento",
            "signatura": "Signatura",
            "fecha_documento": "Fecha documento",
            "lugar_documento": "Lugar documento",
            "fecha_inicio": "Fecha inicio",
            "fecha_fin": "Fecha fin",
            "lugar_ref": "Lugar (jerárquico)",
            "observaciones_lugar": "Detalle de lugar",
            "emisor": "Emisor",
            "visto": "Visto / Supervisor",
            "destinatario": "Destinatario",
            "otras_personas": "Otras personas citadas",
            "seccion_administrativa_emision": "Sección administrativa (emisión)",
            "seccion_administrativa_recepcion": "Sección administrativa (recepción)",
            "texto": "Texto del documento",
            "practica_musical": "Práctica musical",
            "objeto_musical_desc": "Objeto musical",
            "luces": "Luces",
            "hora": "Hora",
            "autor": "Autor",
            "evento_descripcion": "Descripción del evento",
            "mencion_musica": "Mención musical",
            "observaciones": "Observaciones",
        }


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            "nombre_uniforme", "apellidos_uniforme", "otras_formas_nombre",
            "titulo_nobiliario", "id_viaff",
            "genero", "fecha_nacimiento", "fecha_muerte",
            "funcion", "cargo_profesional",
        ]
        widgets = {
            "nombre_uniforme":    forms.TextInput(attrs={"class": "form-control"}),
            "apellidos_uniforme": forms.TextInput(attrs={"class": "form-control"}),
            "otras_formas_nombre": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "titulo_nobiliario":  forms.TextInput(attrs={"class": "form-control"}),
            "id_viaff":           forms.TextInput(attrs={"class": "form-control"}),
            "genero":             forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento":   forms.TextInput(attrs={"class": "form-control", "placeholder": "YYYY"}),
            "fecha_muerte":       forms.TextInput(attrs={"class": "form-control", "placeholder": "YYYY"}),
            "funcion":            forms.TextInput(attrs={"class": "form-control"}),
            "cargo_profesional":  forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "nombre_uniforme": "Nombre",
            "apellidos_uniforme": "Apellidos",
            "otras_formas_nombre": "Otras formas del nombre",
            "titulo_nobiliario": "Título nobiliario",
            "id_viaff": "ID VIAFF",
            "genero": "Género",
            "fecha_nacimiento": "Fecha de nacimiento",
            "fecha_muerte": "Fecha de muerte",
            "funcion": "Función",
            "cargo_profesional": "Cargo profesional",
        }
