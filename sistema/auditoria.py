from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET


def parse_decimal(value):
    try:
        v = str(value).strip().replace(',', '.')
        return Decimal(v) if v else Decimal('0')
    except (InvalidOperation, AttributeError):
        return Decimal('0')


def parse_sped(content):
    notas = {}
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith('|C100|'):
            continue
        parts = line.split('|')
        if len(parts) < 13:
            continue
        try:
            ind_oper  = parts[2].strip()
            cod_mod   = parts[5].strip()
            cod_sit   = parts[6].strip()
            serie     = parts[7].strip()
            num_doc   = parts[8].strip()
            chave     = parts[9].strip()
            dt_doc    = parts[10].strip()
            vl_doc    = parse_decimal(parts[12]) if len(parts) > 12 else Decimal('0')
            vl_icms   = parse_decimal(parts[19]) if len(parts) > 19 else Decimal('0')
            vl_pis    = parse_decimal(parts[23]) if len(parts) > 23 else Decimal('0')
            vl_cofins = parse_decimal(parts[24]) if len(parts) > 24 else Decimal('0')
            nota = {
                'chave': chave, 'num_doc': num_doc, 'serie': serie,
                'dt_doc': dt_doc, 'valor_sped': vl_doc, 'icms_sped': vl_icms,
                'pis_sped': vl_pis, 'cofins_sped': vl_cofins,
                'tipo': 'Entrada' if ind_oper == '0' else 'Saída',
                'modelo': {'55': 'NF-e', '65': 'NFC-e', '57': 'CT-e'}.get(cod_mod, cod_mod),
                'cancelada': cod_sit == '02',
            }
            key = chave if (chave and len(chave) == 44) else f'SEM_CHAVE_{num_doc}_{serie}'
            notas[key] = nota
        except Exception:
            continue
    return notas


def parse_xmls(xml_files):
    notas, erros = {}, []
    for filename, content in xml_files:
        try:
            root = ET.fromstring(content)
            data = {'arquivo': filename}
            for elem in root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                txt = elem.text.strip() if elem.text and elem.text.strip() else None
                if not txt:
                    continue
                if tag in ('chNFe', 'chCTe') and 'chave' not in data:
                    data['chave'] = txt
                elif tag == 'nNF' and 'num_doc' not in data:
                    data['num_doc'] = txt
                elif tag == 'serie' and 'serie' not in data:
                    data['serie'] = txt
                elif tag in ('dhEmi', 'dEmi') and 'dt_doc' not in data:
                    data['dt_doc'] = txt[:10]
                elif tag == 'xNome' and 'emitente' not in data:
                    data['emitente'] = txt
                elif tag == 'tpNF' and 'tipo' not in data:
                    data['tipo'] = 'Entrada' if txt == '0' else 'Saída'
                elif tag == 'vNF' and 'valor_xml' not in data:
                    data['valor_xml'] = parse_decimal(txt)
                elif tag == 'vICMS' and 'icms_xml' not in data:
                    data['icms_xml'] = parse_decimal(txt)
                elif tag == 'vPIS' and 'pis_xml' not in data:
                    data['pis_xml'] = parse_decimal(txt)
                elif tag == 'vCOFINS' and 'cofins_xml' not in data:
                    data['cofins_xml'] = parse_decimal(txt)
            chave = data.get('chave')
            if not chave:
                erros.append(f'{filename}: chave não encontrada')
                continue
            data.setdefault('valor_xml', Decimal('0'))
            data.setdefault('icms_xml',  Decimal('0'))
            data.setdefault('pis_xml',   Decimal('0'))
            data.setdefault('cofins_xml',Decimal('0'))
            data.setdefault('emitente',  'N/D')
            data.setdefault('tipo',      'N/D')
            notas[chave] = data
        except ET.ParseError as e:
            erros.append(f'{filename}: XML inválido ({e})')
        except Exception as e:
            erros.append(f'{filename}: erro ({e})')
    return notas, erros


def cruzar_dados(sped_notas, xml_notas, tol=Decimal('0.01')):
    resultados = []
    for chave in set(sped_notas) | set(xml_notas):
        s = sped_notas.get(chave)
        x = xml_notas.get(chave)
        if s and x:
            divs = []
            dv = abs(s['valor_sped']  - x.get('valor_xml',  Decimal('0')))
            di = abs(s['icms_sped']   - x.get('icms_xml',   Decimal('0')))
            dp = abs(s['pis_sped']    - x.get('pis_xml',    Decimal('0')))
            dc = abs(s['cofins_sped'] - x.get('cofins_xml', Decimal('0')))
            if dv > tol: divs.append(f'Valor: SPED R${s["valor_sped"]:.2f} x XML R${x["valor_xml"]:.2f} (dif R${dv:.2f})')
            if di > tol: divs.append(f'ICMS: R${s["icms_sped"]:.2f} x R${x["icms_xml"]:.2f} (dif R${di:.2f})')
            if dp > tol: divs.append(f'PIS: R${s["pis_sped"]:.2f} x R${x["pis_xml"]:.2f} (dif R${dp:.2f})')
            if dc > tol: divs.append(f'COFINS: R${s["cofins_sped"]:.2f} x R${x["cofins_xml"]:.2f} (dif R${dc:.2f})')
            resultados.append({
                'chave': chave,
                'num_doc': s.get('num_doc', x.get('num_doc', '')),
                'serie':   s.get('serie',   x.get('serie', '')),
                'dt_doc':  s.get('dt_doc',  x.get('dt_doc', '')),
                'tipo':    s.get('tipo',    x.get('tipo', '')),
                'modelo':  s.get('modelo', 'NF-e'),
                'emitente': x.get('emitente', 'N/D'),
                'valor_sped': f'{s["valor_sped"]:.2f}',
                'valor_xml':  f'{x["valor_xml"]:.2f}',
                'status': 'divergente' if divs else 'ok',
                'divergencias': divs, 'fonte': 'ambos',
            })
        elif s:
            resultados.append({
                'chave': chave, 'num_doc': s.get('num_doc',''), 'serie': s.get('serie',''),
                'dt_doc': s.get('dt_doc',''), 'tipo': s.get('tipo',''), 'modelo': s.get('modelo','NF-e'),
                'emitente': 'N/D', 'valor_sped': f'{s["valor_sped"]:.2f}', 'valor_xml': '-',
                'status': 'sem_xml', 'divergencias': ['NF no SPED sem XML correspondente'], 'fonte': 'sped',
            })
        else:
            resultados.append({
                'chave': chave, 'num_doc': x.get('num_doc',''), 'serie': x.get('serie',''),
                'dt_doc': x.get('dt_doc',''), 'tipo': x.get('tipo',''), 'modelo': 'NF-e',
                'emitente': x.get('emitente','N/D'), 'valor_sped': '-',
                'valor_xml': f'{x["valor_xml"]:.2f}',
                'status': 'sem_sped', 'divergencias': ['XML sem registro no SPED'], 'fonte': 'xml',
            })
    order = {'divergente': 0, 'sem_xml': 1, 'sem_sped': 2, 'ok': 3}
    resultados.sort(key=lambda r: (order.get(r['status'], 9), r.get('num_doc', '')))
    return resultados
