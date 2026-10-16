from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def dashboard(request):
    user = request.user
    # Staff/admin sempre tem acesso
    if not user.is_staff and not user.acesso_valido:
        return render(request, 'sistema/acesso_negado.html', {'usuario': user})
    # Atualizar último acesso
    try:
        user.ultimo_acesso_em = timezone.now()
        user.save(update_fields=['ultimo_acesso_em'])
    except Exception:
        pass
    return render(request, 'sistema/dashboard.html', {'usuario': user})
