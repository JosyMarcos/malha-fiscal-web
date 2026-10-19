from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/',  views.login_view,      name='login'),
    path('logout/', views.logout_view,     name='logout'),
    # Painel Admin
    path('admin-painel/',             views.admin_dashboard,  name='admin_dashboard'),
    path('admin-painel/criar/',       views.criar_usuario,    name='criar_usuario'),
    path('admin-painel/<int:pk>/',    views.editar_usuario,   name='editar_usuario'),
    path('admin-painel/<int:pk>/toggle/', views.toggle_ativo, name='toggle_ativo'),
    path('admin-painel/<int:pk>/deletar/', views.deletar_usuario, name='deletar_usuario'),
    path('admin-painel/minha-senha/', views.minha_senha, name='minha_senha'),
]
