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


@login_required
def calendario_fiscal(request):
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return render(request, "sistema/acesso_negado.html", {"usuario": user})
    ctx = {"usuario": user}
    _trial_ctx(user, ctx)
    return render(request, "sistema/calendario_fiscal.html", ctx)


# ── Gestão de Empresas ──────────────────────────────────────────────────────
from .models import Empresa, RegimeTributario, UF_CHOICES
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
def empresas(request):
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return render(request, "sistema/acesso_negado.html", {"usuario": user})

    qs = Empresa.objects.filter(usuario=user)

    # filtros simples via GET
    q = request.GET.get('q', '').strip()
    regime = request.GET.get('regime', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(razao_social__icontains=q) | qs.filter(cnpj__icontains=q)
        qs = Empresa.objects.filter(usuario=user).filter(
            razao_social__icontains=q
        ) | Empresa.objects.filter(usuario=user).filter(cnpj__icontains=q)
    if regime:
        qs = qs.filter(regime_tributario=regime)
    if status == 'ativa':
        qs = qs.filter(ativo=True)
    elif status == 'inativa':
        qs = qs.filter(ativo=False)

    ctx = {
        "usuario": user,
        "empresas": qs,
        "regimes": RegimeTributario.choices,
        "ufs": UF_CHOICES,
        "q": q,
        "regime_sel": regime,
        "status_sel": status,
        "total": Empresa.objects.filter(usuario=user).count(),
        "ativas": Empresa.objects.filter(usuario=user, ativo=True).count(),
    }
    _trial_ctx(user, ctx)
    return render(request, "sistema/empresas.html", ctx)


@login_required
def empresa_salvar(request, pk=None):
    """Cria (pk=None) ou edita (pk=int) uma empresa via POST."""
    user = request.user
    if not user.is_staff and not user.acesso_valido:
        return JsonResponse({"ok": False, "erro": "Acesso inválido."}, status=403)

    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if pk:
        empresa = get_object_or_404(Empresa, pk=pk, usuario=user)
    else:
        empresa = Empresa(usuario=user)

    razao = request.POST.get("razao_social", "").strip()
    cnpj  = request.POST.get("cnpj", "").strip()

    if not razao or not cnpj:
        return JsonResponse({"ok": False, "erro": "Razão Social e CNPJ são obrigatórios."})

    # checa CNPJ duplicado
    existe = Empresa.objects.filter(usuario=user, cnpj=cnpj).exclude(pk=empresa.pk).exists()
    if existe:
        return JsonResponse({"ok": False, "erro": "Já existe uma empresa cadastrada com esse CNPJ."})

    empresa.razao_social       = razao[:255]
    empresa.cnpj               = cnpj[:18]
    empresa.nome_fantasia      = request.POST.get("nome_fantasia", "")[:255]
    empresa.inscricao_estadual = request.POST.get("inscricao_estadual", "")[:30]
    empresa.uf                 = request.POST.get("uf", "PB")[:2]
    empresa.regime_tributario  = request.POST.get("regime_tributario", "simples")[:20]
    empresa.email              = request.POST.get("email", "")[:254]
    empresa.telefone           = request.POST.get("telefone", "")[:20]
    empresa.responsavel        = request.POST.get("responsavel", "")[:150]
    empresa.ativo              = request.POST.get("ativo", "1") == "1"
    empresa.save()

    return JsonResponse({
        "ok": True,
        "pk": empresa.pk,
        "razao_social": empresa.razao_social,
        "cnpj": empresa.cnpj_formatado(),
        "uf": empresa.uf,
        "regime": empresa.get_regime_tributario_display(),
        "ativo": empresa.ativo,
    })


@login_required
@require_POST
def empresa_deletar(request, pk):
    user = request.user
    empresa = get_object_or_404(Empresa, pk=pk, usuario=user)
    empresa.delete()
    return JsonResponse({"ok": True})


@login_required
def empresa_detalhe(request, pk):
    """Retorna dados JSON de uma empresa para preencher o modal de edição."""
    user = request.user
    empresa = get_object_or_404(Empresa, pk=pk, usuario=user)
    return JsonResponse({
        "ok": True,
        "pk": empresa.pk,
        "razao_social": empresa.razao_social,
        "cnpj": empresa.cnpj,
        "nome_fantasia": empresa.nome_fantasia,
        "inscricao_estadual": empresa.inscricao_estadual,
        "uf": empresa.uf,
        "regime_tributario": empresa.regime_tributario,
        "email": empresa.email,
        "telefone": empresa.telefone,
        "responsavel": empresa.responsavel,
        "ativo": "1" if empresa.ativo else "0",
    })
