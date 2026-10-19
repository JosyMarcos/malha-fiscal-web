from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .auditoria import parse_sped, parse_xmls, cruzar_dados


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
    ctx = {'usuario': user}
    if request.method == 'POST':
        erros = []
        sped_notas = {}
        for f in request.FILES.getlist('sped_files'):
            try:
                sped_notas.update(parse_sped(f.read().decode('latin-1')))
            except Exception as e:
                erros.append(f'SPED {f.name}: {e}')
        xml_data = []
        for f in request.FILES.getlist('xml_files'):
            try:
                xml_data.append((f.name, f.read()))
            except Exception as e:
                erros.append(f'XML {f.name}: {e}')
        xml_notas, xml_erros = parse_xmls(xml_data)
        erros.extend(xml_erros)
        resultados = cruzar_dados(sped_notas, xml_notas)
        ctx.update({
            'resultados':  resultados,
            'total':       len(resultados),
            'divergentes': sum(1 for r in resultados if r['status'] == 'divergente'),
            'sem_xml':     sum(1 for r in resultados if r['status'] == 'sem_xml'),
            'sem_sped':    sum(1 for r in resultados if r['status'] == 'sem_sped'),
            'ok':          sum(1 for r in resultados if r['status'] == 'ok'),
            'erros':       erros,
            'processado':  True,
        })
    return render(request, 'sistema/auditoria.html', ctx)
