from django.db import models


class Lugar(models.Model):
    nombre = models.CharField(max_length=400)
    padre = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='hijos',
    )

    def __str__(self):
        if self.padre:
            return f"{self.padre.nombre} › {self.nombre}"
        return self.nombre

    @property
    def ruta(self):
        return str(self)

    class Meta:
        verbose_name = "Lugar"
        verbose_name_plural = "Lugares"
        ordering = ["padre__nombre", "nombre"]


class Persona(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    nombre_uniforme = models.CharField(max_length=200)
    apellidos_uniforme = models.CharField(max_length=200, blank=True, default="")
    otras_formas_nombre = models.TextField(blank=True, default="")
    titulo_nobiliario = models.CharField(max_length=200, blank=True, null=True)
    id_viaff = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.CharField(max_length=50, blank=True, null=True)
    fecha_muerte = models.CharField(max_length=50, blank=True, null=True)
    funcion = models.CharField(max_length=100, default="no músico")
    cargo_profesional = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_uniforme} {self.apellidos_uniforme}".strip()

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ["apellidos_uniforme", "nombre_uniforme"]


class Documento(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    tipo_documento = models.CharField(max_length=200)
    fecha_documento = models.CharField(max_length=50, blank=True, null=True)
    lugar_documento = models.CharField(max_length=300, blank=True, null=True)
    fecha_inicio = models.CharField(max_length=50, blank=True, null=True)
    fecha_fin = models.CharField(max_length=50, blank=True, null=True)
    lugar = models.CharField(max_length=500, blank=True, null=True)  # string original del Excel
    lugar_ref = models.ForeignKey(
        Lugar, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='documentos',
        verbose_name="Lugar (jerárquico)",
    )
    observaciones_lugar = models.TextField(blank=True, null=True)
    texto = models.TextField(blank=True, null=True)
    emisor = models.ForeignKey(
        Persona, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="documentos_emitidos",
    )
    visto = models.ForeignKey(
        Persona, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="documentos_vistos",
    )
    destinatario = models.ForeignKey(
        Persona, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="documentos_recibidos",
    )
    seccion_administrativa_emision = models.CharField(max_length=200, blank=True, null=True)
    seccion_administrativa_recepcion = models.CharField(max_length=200, blank=True, null=True)
    hora = models.CharField(max_length=50, blank=True, null=True)
    luces = models.TextField(blank=True, null=True)
    otras_personas = models.ManyToManyField(Persona, blank=True, related_name="documentos_citado")
    signatura = models.CharField(max_length=200, blank=True, null=True)
    practica_musical = models.TextField(blank=True, null=True)
    objeto_musical_desc = models.TextField(blank=True, null=True)
    autor = models.CharField(max_length=200, blank=True, null=True)
    mencion_musica = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    evento_descripcion = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.id} – {self.tipo_documento} ({self.fecha_documento or '?'})"

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["fecha_documento"]
