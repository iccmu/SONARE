import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Q, When
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DocumentoForm, PersonaForm
from .models import Documento, Lugar, Persona


@login_required
def home(request):
    rel = ("emisor", "visto", "destinatario", "lugar_ref", "lugar_ref__padre")
    base_qs = Documento.objects.select_related(*rel)

    # Score de completitud: suma de campos clave presentes (0–6)
    def _anotar_score(qs):
        return qs.annotate(
            completitud=
                Case(When(emisor__isnull=False, then=1), default=0, output_field=IntegerField()) +
                Case(When(visto__isnull=False, then=1), default=0, output_field=IntegerField()) +
                Case(When(destinatario__isnull=False, then=1), default=0, output_field=IntegerField()) +
                Case(When(practica_musical__isnull=False, then=1), default=0, output_field=IntegerField()) +
                Case(When(objeto_musical_desc__isnull=False, then=1), default=0, output_field=IntegerField()) +
                Case(When(observaciones__isnull=False, then=1), default=0, output_field=IntegerField())
        )

    scored = _anotar_score(base_qs)

    # Completos: score >= 4, muestra aleatoria
    docs_completos = list(scored.filter(completitud__gte=4).order_by("?")[:5])

    # Incompletos: score <= 3, muestra aleatoria
    docs_incompletos = list(scored.filter(completitud__lte=3).order_by("?")[:5])

    context = {
        "total_documentos": Documento.objects.count(),
        "total_personas": Persona.objects.count(),
        "docs_con_musica": Documento.objects.filter(mencion_musica=True).count(),
        "docs_completos": docs_completos,
        "docs_incompletos": docs_incompletos,
    }
    return render(request, "sonare_app/home.html", context)


def _lugares_json():
    """Devuelve todos los lugares como JSON para los selects en cascada."""
    lugares = Lugar.objects.select_related("padre").order_by("padre__nombre", "nombre")
    return json.dumps([
        {"id": l.id, "nombre": l.nombre, "padre_id": l.padre_id}
        for l in lugares
    ])


@login_required
def documento_list(request):
    qs = Documento.objects.select_related("emisor", "destinatario", "lugar_ref", "lugar_ref__padre")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(id__icontains=q)
            | Q(signatura__icontains=q)
            | Q(texto__icontains=q)
            | Q(lugar__icontains=q)
            | Q(lugar_documento__icontains=q)
            | Q(practica_musical__icontains=q)
            | Q(tipo_documento__icontains=q)
            | Q(autor__icontains=q)
            | Q(hora__icontains=q)
            | Q(luces__icontains=q)
            | Q(observaciones__icontains=q)
            | Q(evento_descripcion__icontains=q)
            | Q(objeto_musical_desc__icontains=q)
            | Q(emisor__nombre_uniforme__icontains=q)
            | Q(emisor__apellidos_uniforme__icontains=q)
            | Q(destinatario__nombre_uniforme__icontains=q)
            | Q(destinatario__apellidos_uniforme__icontains=q)
            | Q(visto__nombre_uniforme__icontains=q)
            | Q(visto__apellidos_uniforme__icontains=q)
        )

    tipo = request.GET.get("tipo", "")
    if tipo:
        qs = qs.filter(tipo_documento=tipo)

    musica = request.GET.get("musica", "")
    if musica == "1":
        qs = qs.filter(mencion_musica=True)
    elif musica == "0":
        qs = qs.filter(mencion_musica=False)

    emisor = request.GET.get("emisor", "")
    if emisor:
        qs = qs.filter(emisor_id=emisor)

    sitio = request.GET.get("sitio", "")
    dependencia = request.GET.get("dependencia", "")
    if dependencia:
        qs = qs.filter(lugar_ref_id=dependencia)
    elif sitio:
        qs = qs.filter(
            Q(lugar_ref__padre_id=sitio) | Q(lugar_ref_id=sitio)
        )

    desde = request.GET.get("desde", "")
    if desde:
        qs = qs.filter(fecha_documento__gte=desde)

    hasta = request.GET.get("hasta", "")
    if hasta:
        qs = qs.filter(fecha_documento__lte=hasta)

    # Ordenación
    SORT_FIELDS_DOC = {
        "id":       "id",
        "tipo":     "tipo_documento",
        "fecha":    "fecha_documento",
        "lugar":    "lugar_ref__nombre",
        "emisor":   "emisor__apellidos_uniforme",
        "practica": "practica_musical",
        "musica":   "mencion_musica",
    }
    sort = request.GET.get("sort", "fecha")
    direction = request.GET.get("dir", "asc")
    sort_field = SORT_FIELDS_DOC.get(sort, "fecha_documento")
    qs = qs.order_by(f"-{sort_field}" if direction == "desc" else sort_field)

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    tipos = (
        Documento.objects.exclude(tipo_documento="")
        .values_list("tipo_documento", flat=True)
        .distinct()
        .order_by("tipo_documento")
    )
    personas_con_docs = (
        Persona.objects.filter(documentos_emitidos__isnull=False)
        .distinct()
        .order_by("apellidos_uniforme", "nombre_uniforme")
    )

    sitios = Lugar.objects.filter(padre__isnull=True).order_by("nombre")

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "tipos": tipos,
        "personas_con_docs": personas_con_docs,
        "sitios": sitios,
        "lugares_json": _lugares_json(),
        "q": q,
        "sort": sort,
        "dir": direction,
    }
    return render(request, "sonare_app/documentos/list.html", context)


@login_required
def documento_detail(request, pk):
    doc = get_object_or_404(
        Documento.objects.select_related("emisor", "visto", "destinatario"),
        id=pk,
    )
    otras_personas = doc.otras_personas.all()
    return render(request, "sonare_app/documentos/detail.html", {
        "doc": doc,
        "otras_personas": otras_personas,
    })


@login_required
def persona_list(request):
    qs = Persona.objects.annotate(
        num_docs=Count("documentos_emitidos", distinct=True)
        + Count("documentos_recibidos", distinct=True)
        + Count("documentos_citado", distinct=True)
    )

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(nombre_uniforme__icontains=q)
            | Q(apellidos_uniforme__icontains=q)
            | Q(otras_formas_nombre__icontains=q)
        )

    funcion = request.GET.get("funcion", "")
    if funcion:
        qs = qs.filter(funcion=funcion)

    genero = request.GET.get("genero", "")
    if genero:
        qs = qs.filter(genero=genero)

    # Ordenación
    SORT_FIELDS_PER = {
        "id":       "id",
        "nombre":   "apellidos_uniforme",
        "funcion":  "funcion",
        "cargo":    "cargo_profesional",
        "nacimiento": "fecha_nacimiento",
        "docs":     "num_docs",
    }
    sort = request.GET.get("sort", "nombre")
    direction = request.GET.get("dir", "asc")
    sort_field = SORT_FIELDS_PER.get(sort, "apellidos_uniforme")
    qs = qs.order_by(f"-{sort_field}" if direction == "desc" else sort_field)

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    funciones = (
        Persona.objects.exclude(funcion="")
        .values_list("funcion", flat=True)
        .distinct()
        .order_by("funcion")
    )
    generos = (
        Persona.objects.exclude(genero__isnull=True).exclude(genero="")
        .values_list("genero", flat=True)
        .distinct()
        .order_by("genero")
    )

    return render(request, "sonare_app/personas/list.html", {
        "page_obj": page_obj,
        "paginator": paginator,
        "funciones": funciones,
        "generos": generos,
        "sort": sort,
        "dir": direction,
    })


@login_required
def persona_detail(request, pk):
    persona = get_object_or_404(Persona, id=pk)
    rel = "emisor", "visto", "destinatario", "lugar_ref", "lugar_ref__padre"
    return render(request, "sonare_app/personas/detail.html", {
        "persona": persona,
        "docs_emitidos":  persona.documentos_emitidos.select_related(*rel).order_by("fecha_documento"),
        "docs_visados":   persona.documentos_vistos.select_related(*rel).order_by("fecha_documento"),
        "docs_recibidos": persona.documentos_recibidos.select_related(*rel).order_by("fecha_documento"),
        "docs_citado":    persona.documentos_citado.select_related(*rel).order_by("fecha_documento"),
    })


@login_required
def documento_edit(request, pk):
    doc = get_object_or_404(Documento, id=pk)
    if request.method == "POST":
        form = DocumentoForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            return redirect("sonare:documento_detail", pk=pk)
    else:
        form = DocumentoForm(instance=doc)
    field_personas = [
        ("emisor", "Emisor"),
        ("visto", "Supervisor / Visto"),
        ("destinatario", "Destinatario"),
        ("otras_personas", "Otras personas citadas"),
    ]
    return render(request, "sonare_app/documentos/edit.html", {"form": form, "doc": doc, "field_personas": field_personas})


@login_required
def persona_edit(request, pk):
    persona = get_object_or_404(Persona, id=pk)
    if request.method == "POST":
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            return redirect("sonare:persona_detail", pk=pk)
    else:
        form = PersonaForm(instance=persona)
    return render(request, "sonare_app/personas/edit.html", {"form": form, "persona": persona})
