from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'empresa', 'plano', 'ativo', 'data_expiracao', 'criado_em']
    list_filter  = ['ativo', 'plano', 'is_staff']
    search_fields = ['username', 'email', 'empresa', 'first_name', 'last_name']
    list_editable = ['ativo', 'plano']
    fieldsets = UserAdmin.fieldsets + (
        ('Malha Fiscal', {'fields': ('empresa', 'telefone', 'plano', 'ativo', 'data_expiracao', 'observacoes')}),
    )
