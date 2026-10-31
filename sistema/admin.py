from django.contrib import admin
from .models import Auditoria, Empresa


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display  = ['empresa', 'periodo', 'total_notas', 'divergencias', 'score_risco', 'usuario', 'criado_em']
    list_filter   = ['score_risco']
    search_fields = ['empresa', 'usuario__email']
    raw_id_fields = ['usuario']


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display  = ['razao_social', 'cnpj', 'uf', 'regime_tributario', 'ativo', 'usuario', 'criado_em']
    list_filter   = ['uf', 'regime_tributario', 'ativo']
    search_fields = ['razao_social', 'cnpj', 'email']
    raw_id_fields = ['usuario']
