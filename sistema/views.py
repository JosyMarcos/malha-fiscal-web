import json
import math

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Auditoria


def _trial_ctx(user, ctx):
    """Adiciona trial_segundos e is_trial ao contexto se aplicável."""
    ctx["is_trial"] = user.is_trial
    if user.is_trial:
        exp = user.trial_expira_em
        if exp:
            secs = max(0, math.floor((exp - timezone.now()).total_seconds()))
            ctx["trial_segundos"] = secs
    return ctx


@login_required
def dashboard(request):
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return render(request, "sistema/acesso_negado.html", {"usuario": user})
    try:
        user.ultimo_acesso_em = timezone.now()
        user.save(update_fields=["ultimo_acesso_em"])
    except Exception:
        pass
    auditorias = Auditoria.objects.filter(usuario=user).order_by("-criado_em")[:10]
    ctx = {"usuario": user, "auditorias": auditorias}
    _trial_ctx(user, ctx)
    return render(request, "sistema/dashboard.html", ctx)


@login_required
def auditoria(request):
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return render(request, "sistema/acesso_negado.html", {"usuario": user})
    ctx = {"usuario": user}
    _trial_ctx(user, ctx)
    return render(request, "sistema/auditoria.html", ctx)


@login_required
@require_POST
def salvar_auditoria(request):
    """Recebe o resumo JSON gerado pelo JS após o processamento client-side."""
    user = request.user
    if not user.acesso_valido:
        return JsonResponse({"ok": False, "erro": "Acesso inválido."}, status=403)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"ok": False, "erro": "JSON inválido."}, status=400)

    Auditoria.objects.create(
        usuario=user,
        empresa=payload.get("empresa", "")[:255],
        periodo=payload.get("periodo", "")[:20],
        total_notas=int(payload.get("total_notas", 0)),
        divergencias=int(payload.get("divergencias", 0)),
        score_risco=payload.get("score_risco", "")[:10],
        resumo=payload.get("resumo", {}),
    )
    return JsonResponse({"ok": True})
