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
    ctx = {'usuario': user}
    if user.is_trial:
        exp = user.trial_expira_em
        if exp:
            import math
            from django.utils import timezone as tz
            secs = max(0, math.floor((exp - tz.now()).total_seconds()))
            ctx['trial_segundos'] = secs
    return render(request, 'sistema/dashboard.html', ctx)


@login_required
def auditoria(request):
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return render(request, 'sistema/acesso_negado.html', {'usuario': user})
    ctx = {'usuario': user, 'is_trial': user.is_trial}
    if user.is_trial:
        exp = user.trial_expira_em
        if exp:
            import math
            from django.utils import timezone as tz
            secs = max(0, math.floor((exp - tz.now()).total_seconds()))
            ctx['trial_segundos'] = secs
    return render(request, 'sistema/auditoria.html', ctx)
