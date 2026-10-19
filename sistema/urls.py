from django.urls import path
from . import views

app_name = "sistema"

urlpatterns = [
    path("",             views.dashboard,       name="dashboard"),
    path("auditoria/",   views.auditoria,       name="auditoria"),
    path("salvar-auditoria/", views.salvar_auditoria, name="salvar_auditoria"),
]
