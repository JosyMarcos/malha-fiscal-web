from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Usuario
from .forms import LoginForm, CriarUsuarioForm, EditarUsuarioForm

is_admin = lambda u: u.is_staff or u.is_superuser


# ── AUTENTICAÇÃO ─────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('sistema:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not user.acesso_valido and not user.is_staff:
            messages.error(request, 'Sua conta está inativa. Entre em contato com o administrador.')
            return render(request, 'registration/login.html', {'form': form})
        login(request, user)
        user.ultimo_acesso_em = timezone.now()
        user.save(update_fields=['ultimo_acesso_em'])
        return redirect(request.GET.get('next', 'sistema:dashboard'))
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ── PAINEL ADMIN ─────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', 'todos')
    usuarios = Usuario.objects.filter(is_superuser=False)

    if q:
        usuarios = usuarios.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(email__icontains=q) | Q(empresa__icontains=q) | Q(username__icontains=q)
        )
    if filtro == 'ativos':
        usuarios = usuarios.filter(ativo=True)
    elif filtro == 'inativos':
        usuarios = usuarios.filter(ativo=False)
    elif filtro == 'expirados':
        usuarios = usuarios.filter(data_expiracao__lt=timezone.now().date())

    total   = Usuario.objects.filter(is_superuser=False).count()
    ativos  = Usuario.objects.filter(is_superuser=False, ativo=True).count()
    hoje    = timezone.now().date()
    exp7    = Usuario.objects.filter(is_superuser=False, ativo=True,
                                     data_expiracao__gte=hoje,
                                     data_expiracao__lte=hoje + timezone.timedelta(days=7)).count()

    return render(request, 'admin_panel/dashboard.html', {
        'usuarios': usuarios, 'q': q, 'filtro': filtro,
        'total': total, 'ativos': ativos, 'exp7': exp7,
    })


@login_required
@user_passes_test(is_admin)
def criar_usuario(request):
    form = CriarUsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Usuário {user.username} criado com sucesso.')
        return redirect('accounts:admin_dashboard')
    return render(request, 'admin_panel/form_usuario.html', {'form': form, 'titulo': 'Novo usuário'})


@login_required
@user_passes_test(is_admin)
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = EditarUsuarioForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Usuário {usuario.username} atualizado.')
        return redirect('accounts:admin_dashboard')
    return render(request, 'admin_panel/form_usuario.html', {
        'form': form, 'titulo': f'Editar — {usuario}', 'usuario': usuario
    })


@login_required
@user_passes_test(is_admin)
def toggle_ativo(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.ativo = not usuario.ativo
    usuario.save(update_fields=['ativo'])
    status = 'ativado' if usuario.ativo else 'desativado'
    messages.success(request, f'{usuario.username} foi {status}.')
    return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def deletar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        nome = usuario.username
        usuario.delete()
        messages.success(request, f'Usuário {nome} removido.')
        return redirect('accounts:admin_dashboard')
    return render(request, 'admin_panel/confirmar_delete.html', {'usuario': usuario})
