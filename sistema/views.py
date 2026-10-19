from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def dashboard(request):
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return render(request, 'sistema/acesso_negado.html', {'usuario': user})
    try:
        user.ultimo_acesso_em = timezone.now()
        user.save(update_fields=['ultimo_acesso_em'])
    except Exception:
        pass
    return render(request, 'sistema/dashboard.html', {'usuario': user})


@login_required
def auditoria(request):
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return render(request, 'sistema/acesso_negado.html', {'usuario': user})
    return render(request, 'sistema/auditoria.html', {'usuario': user})
