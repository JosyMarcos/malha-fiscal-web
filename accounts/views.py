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

    trials = Usuario.objects.filter(plano='trial', ativo=True).order_by('criado_em')
    return render(request, 'admin_panel/dashboard.html', {
        'usuarios': usuarios, 'q': q, 'filtro': filtro,
        'total': total, 'ativos': ativos, 'exp7': exp7,
        'trials': trials,
    })


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


# ── MINHA SENHA ──────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def minha_senha(request):
    if request.method == 'POST':
        nova = request.POST.get('nova_senha', '').strip()
        confirma = request.POST.get('confirma_senha', '').strip()
        if not nova or len(nova) < 6:
            messages.error(request, 'A senha precisa ter pelo menos 6 caracteres.')
        elif nova != confirma:
            messages.error(request, 'As senhas não coincidem.')
        else:
            request.user.set_password(nova)
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
    return render(request, 'admin_panel/minha_senha.html')


# ── REGISTRO PÚBLICO (Trial 48h) ─────────────────────────────────

def registro(request):
    """Cadastro público — cria conta com plano Trial (48h, ativo=True)."""
    if request.user.is_authenticated:
        return redirect('sistema:dashboard')

    error = None
    if request.method == 'POST':
        nome     = request.POST.get('nome', '').strip()
        empresa  = request.POST.get('empresa', '').strip()
        email    = request.POST.get('email', '').strip()
        senha    = request.POST.get('senha', '').strip()
        confirma = request.POST.get('confirma', '').strip()

        if not all([nome, empresa, email, senha]):
            error = 'Preencha todos os campos obrigatórios.'
        elif senha != confirma:
            error = 'As senhas não coincidem.'
        elif len(senha) < 6:
            error = 'A senha precisa ter pelo menos 6 caracteres.'
        elif Usuario.objects.filter(email=email).exists():
            error = 'Já existe uma conta com este e-mail.'
        else:
            from datetime import timedelta
            # username = parte antes do @ do e-mail (garante unicidade)
            base_username = email.split('@')[0][:30]
            username = base_username
            counter = 1
            while Usuario.objects.filter(username=username).exists():
                username = f'{base_username}{counter}'
                counter += 1

            parts = nome.split(' ', 1)
            first = parts[0]; last = parts[1] if len(parts) > 1 else ''

            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=first,
                last_name=last,
                empresa=empresa,
                plano='trial',
                ativo=True,
                data_expiracao=(timezone.now() + timedelta(hours=48)).date(),
            )
            from django.contrib.auth import authenticate, login as auth_login
            # Notificação ao admin
            try:
                from django.core.mail import send_mail
                from django.conf import settings as djsettings
                admin_email = getattr(djsettings, 'ADMIN_EMAIL', 'marcosnobrega2299@gmail.com')
                send_mail(
                    subject=f'🆕 Novo Trial — {first} {last} ({empresa})',
                    message=(
                        f'Novo cadastro no Trial da Malha Fiscal:\n\n'
                        f'Nome: {first} {last}\n'
                        f'Empresa: {empresa}\n'
                        f'E-mail: {email}\n\n'
                        f'Acesse o painel para converter em cliente:\n'
                        f'https://malha-fiscal-web-liart.vercel.app/admin-painel/'
                    ),
                    from_email=None,
                    recipient_list=[admin_email],
                    fail_silently=True,
                )
            except Exception:
                pass

            user = authenticate(request, username=username, password=senha)
            if user:
                auth_login(request, user)
            return redirect('sistema:dashboard')

    return render(request, 'registration/registro.html', {'error': error})
