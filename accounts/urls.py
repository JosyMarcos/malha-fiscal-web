from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/',  views.login_view,      name='login'),
    path('logout/', views.logout_view,     name='logout'),

    # ── Recuperação de senha ─────────────────────────────────────────
    path('senha/recuperar/',
         views.recuperar_senha,
         name='password_reset'),
    path('senha/recuperar/enviado/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('senha/recuperar/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             success_url='/senha/recuperar/concluido/',
         ),
         name='password_reset_confirm'),
    path('senha/recuperar/concluido/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    # ── Painel Admin ─────────────────────────────────────────────────
    path('admin-painel/',             views.admin_dashboard,  name='admin_dashboard'),
    path('admin-painel/<int:pk>/',    views.editar_usuario,   name='editar_usuario'),
    path('admin-painel/<int:pk>/toggle/', views.toggle_ativo, name='toggle_ativo'),
    path('admin-painel/<int:pk>/deletar/', views.deletar_usuario, name='deletar_usuario'),
    path('admin-painel/minha-senha/', views.minha_senha, name='minha_senha'),
]
