from django.urls import path
from . import views

app_name = "sistema"

urlpatterns = [
    path("",                                      views.dashboard,          name="dashboard"),
    path("auditoria/",                            views.auditoria,          name="auditoria"),
    path("salvar-auditoria/",                     views.salvar_auditoria,   name="salvar_auditoria"),
    path("agenda-fiscal/",                        views.calendario_fiscal,  name="calendario_fiscal"),
    # Gestão de Empresas
    path("empresas/",                             views.empresas,           name="empresas"),
    path("empresas/salvar/",                      views.empresa_salvar,     name="empresa_nova"),
    path("empresas/<int:pk>/salvar/",             views.empresa_salvar,     name="empresa_editar"),
    path("empresas/<int:pk>/deletar/",            views.empresa_deletar,    name="empresa_deletar"),
    path("empresas/<int:pk>/detalhe/",            views.empresa_detalhe,    name="empresa_detalhe"),
]
