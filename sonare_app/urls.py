from django.urls import path

from . import views

app_name = "sonare"

urlpatterns = [
    path("", views.home, name="home"),
    path("documentos/", views.documento_list, name="documento_list"),
    path("documentos/<str:pk>/", views.documento_detail, name="documento_detail"),
    path("documentos/<str:pk>/editar/", views.documento_edit, name="documento_edit"),
    path("personas/", views.persona_list, name="persona_list"),
    path("personas/<str:pk>/", views.persona_detail, name="persona_detail"),
    path("personas/<str:pk>/editar/", views.persona_edit, name="persona_edit"),
]
