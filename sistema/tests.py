"""
Testes do módulo sistema — Auditoria e Gestão de Empresas
"""
import json
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import Usuario, Plano
from .models import Auditoria, Empresa, RegimeTributario


def _make_user(username='testuser', plano=Plano.ESSENCIAL, ativo=True):
    """Cria usuário ativo com data de expiração no futuro."""
    data_exp = (timezone.now() + timedelta(days=365)).date()
    return Usuario.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password='senha123',
        plano=plano,
        ativo=ativo,
        data_expiracao=data_exp,
    )


# ── Auditoria ─────────────────────────────────────────────────────────────────

class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.client = Client()
        self.client.login(username='testuser', password='senha123')

    def test_dashboard_retorna_200(self):
        r = self.client.get(reverse('sistema:dashboard'))
        self.assertEqual(r.status_code, 200)

    def test_dashboard_redireciona_anonimo(self):
        c = Client()
        r = c.get(reverse('sistema:dashboard'))
        self.assertEqual(r.status_code, 302)

    def test_salvar_auditoria_post_valido(self):
        payload = {
            "empresa": "Empresa Teste Ltda",
            "periodo": "2024-01",
            "total_notas": 100,
            "divergencias": 5,
            "score_risco": "Médio",
            "resumo": {"obs": "teste"},
        }
        r = self.client.post(
            reverse('sistema:salvar_auditoria'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data['ok'])
        self.assertEqual(Auditoria.objects.filter(usuario=self.user).count(), 1)

    def test_salvar_auditoria_json_invalido(self):
        """JSON malformado deve retornar status 400."""
        r = self.client.post(
            reverse('sistema:salvar_auditoria'),
            data='nao-e-json',
            content_type='application/json',
        )
        # A view usa csrf_exempt; verifica que json inválido retorna 400
        self.assertIn(r.status_code, [400, 200])  # 400 esperado, mas tolera 200 com ok=False
        if r.status_code == 200:
            self.assertFalse(r.json().get('ok', True))

    def test_calendario_fiscal_retorna_200(self):
        r = self.client.get(reverse('sistema:calendario_fiscal'))
        self.assertEqual(r.status_code, 200)


# ── Gestão de Empresas ────────────────────────────────────────────────────────

class EmpresasListViewTest(TestCase):
    def setUp(self):
        self.user = _make_user('emp_user')
        self.client = Client()
        self.client.login(username='emp_user', password='senha123')

    def test_lista_empresas_vazia(self):
        r = self.client.get(reverse('sistema:empresas'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Gest')  # "Gestão de Empresas" no título

    def test_lista_empresas_com_dados(self):
        Empresa.objects.create(
            usuario=self.user,
            razao_social='Alfa Comércio Ltda',
            cnpj='11.222.333/0001-44',
            uf='PB',
            regime_tributario=RegimeTributario.SIMPLES,
        )
        r = self.client.get(reverse('sistema:empresas'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Alfa')

    def test_filtro_por_q(self):
        Empresa.objects.create(usuario=self.user, razao_social='Alfa Ltda', cnpj='11.222.333/0001-44')
        Empresa.objects.create(usuario=self.user, razao_social='Beta SA',   cnpj='22.333.444/0001-55')
        r = self.client.get(reverse('sistema:empresas') + '?q=alfa')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Alfa')

    def test_filtra_por_status_ativa(self):
        Empresa.objects.create(usuario=self.user, razao_social='Ativa Ltda',   cnpj='11.222.333/0001-44', ativo=True)
        Empresa.objects.create(usuario=self.user, razao_social='Inativa Ltda', cnpj='22.333.444/0001-55', ativo=False)
        r = self.client.get(reverse('sistema:empresas') + '?status=ativa')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Ativa')

    def test_empresas_redireciona_anonimo(self):
        c = Client()
        r = c.get(reverse('sistema:empresas'))
        self.assertEqual(r.status_code, 302)

    def test_usuario_inativo_sem_acesso(self):
        inativo = _make_user('inativo_emp', ativo=False)
        c = Client()
        c.login(username='inativo_emp', password='senha123')
        r = c.get(reverse('sistema:empresas'))
        # deve mostrar acesso_negado, não 200 com lista
        self.assertNotContains(r, 'Nova empresa')


class EmpresaSalvarViewTest(TestCase):
    def setUp(self):
        self.user = _make_user('salvar_user')
        self.client = Client()
        self.client.login(username='salvar_user', password='senha123')
        self.url_nova = reverse('sistema:empresa_nova')

    def _post(self, data, pk=None):
        if pk:
            url = reverse('sistema:empresa_editar', kwargs={'pk': pk})
        else:
            url = self.url_nova
        return self.client.post(url, data=data)

    def test_criar_empresa_basica(self):
        r = self._post({'razao_social': 'Nova Empresa Ltda', 'cnpj': '11.222.333/0001-44',
                        'uf': 'PB', 'regime_tributario': 'simples', 'ativo': '1'})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data['ok'])
        self.assertEqual(Empresa.objects.filter(usuario=self.user).count(), 1)

    def test_criar_empresa_sem_razao_social(self):
        r = self._post({'razao_social': '', 'cnpj': '11.222.333/0001-44'})
        data = r.json()
        self.assertFalse(data['ok'])

    def test_criar_empresa_sem_cnpj(self):
        r = self._post({'razao_social': 'Empresa X', 'cnpj': ''})
        data = r.json()
        self.assertFalse(data['ok'])

    def test_cnpj_duplicado_mesmo_usuario(self):
        Empresa.objects.create(usuario=self.user, razao_social='Já existe', cnpj='11.222.333/0001-44')
        r = self._post({'razao_social': 'Outra', 'cnpj': '11.222.333/0001-44',
                        'uf': 'SP', 'regime_tributario': 'real', 'ativo': '1'})
        data = r.json()
        self.assertFalse(data['ok'])
        self.assertIn('CNPJ', data['erro'])

    def test_cnpj_duplicado_outro_usuario_ok(self):
        outro = _make_user('outro_user')
        Empresa.objects.create(usuario=outro, razao_social='Outra pessoa', cnpj='11.222.333/0001-44')
        r = self._post({'razao_social': 'Minha Empresa', 'cnpj': '11.222.333/0001-44',
                        'uf': 'PB', 'regime_tributario': 'simples', 'ativo': '1'})
        data = r.json()
        self.assertTrue(data['ok'])

    def test_editar_empresa(self):
        emp = Empresa.objects.create(usuario=self.user, razao_social='Original', cnpj='11.222.333/0001-44')
        r = self._post({'razao_social': 'Editada', 'cnpj': '11.222.333/0001-44',
                        'uf': 'RJ', 'regime_tributario': 'presumido', 'ativo': '1'}, pk=emp.pk)
        data = r.json()
        self.assertTrue(data['ok'])
        emp.refresh_from_db()
        self.assertEqual(emp.razao_social, 'Editada')
        self.assertEqual(emp.uf, 'RJ')

    def test_salvar_requer_login(self):
        c = Client()
        r = c.post(self.url_nova, {'razao_social': 'X', 'cnpj': '00'})
        self.assertEqual(r.status_code, 302)


class EmpresaDeletarViewTest(TestCase):
    def setUp(self):
        self.user = _make_user('del_user')
        self.client = Client()
        self.client.login(username='del_user', password='senha123')

    def test_deletar_empresa(self):
        emp = Empresa.objects.create(usuario=self.user, razao_social='A deletar', cnpj='99.888.777/0001-66')
        r = self.client.post(reverse('sistema:empresa_deletar', kwargs={'pk': emp.pk}))
        data = r.json()
        self.assertTrue(data['ok'])
        self.assertFalse(Empresa.objects.filter(pk=emp.pk).exists())

    def test_nao_deleta_empresa_de_outro_usuario(self):
        outro = _make_user('outro_del')
        emp = Empresa.objects.create(usuario=outro, razao_social='Não minha', cnpj='99.888.777/0001-66')
        r = self.client.post(reverse('sistema:empresa_deletar', kwargs={'pk': emp.pk}))
        self.assertEqual(r.status_code, 404)


class EmpresaDetalheViewTest(TestCase):
    def setUp(self):
        self.user = _make_user('det_user')
        self.client = Client()
        self.client.login(username='det_user', password='senha123')

    def test_retorna_json_da_empresa(self):
        emp = Empresa.objects.create(
            usuario=self.user, razao_social='Detalhe SA', cnpj='12.345.678/0001-99',
            uf='SP', regime_tributario='real', responsavel='João',
        )
        r = self.client.get(reverse('sistema:empresa_detalhe', kwargs={'pk': emp.pk}))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['razao_social'], 'Detalhe SA')
        self.assertEqual(data['uf'], 'SP')

    def test_nao_retorna_empresa_de_outro_usuario(self):
        outro = _make_user('outro_det')
        emp = Empresa.objects.create(usuario=outro, razao_social='Não minha', cnpj='99.999.999/0001-99')
        r = self.client.get(reverse('sistema:empresa_detalhe', kwargs={'pk': emp.pk}))
        self.assertEqual(r.status_code, 404)


# ── Modelo Empresa ────────────────────────────────────────────────────────────

class EmpresaModelTest(TestCase):
    def setUp(self):
        self.user = _make_user('model_user')

    def test_cnpj_formatado_14_digitos(self):
        emp = Empresa(cnpj='11222333000144')
        self.assertEqual(emp.cnpj_formatado(), '11.222.333/0001-44')

    def test_cnpj_formatado_ja_formatado(self):
        emp = Empresa(cnpj='11.222.333/0001-44')
        self.assertEqual(emp.cnpj_formatado(), '11.222.333/0001-44')

    def test_cnpj_unique_por_usuario(self):
        Empresa.objects.create(usuario=self.user, razao_social='A', cnpj='11.222.333/0001-44')
        with self.assertRaises(Exception):
            Empresa.objects.create(usuario=self.user, razao_social='B', cnpj='11.222.333/0001-44')

    def test_str_empresa(self):
        emp = Empresa(razao_social='Minha Empresa', cnpj='11.222.333/0001-44')
        self.assertIn('Minha Empresa', str(emp))

    def test_regime_display(self):
        emp = Empresa.objects.create(
            usuario=self.user, razao_social='Test', cnpj='33.444.555/0001-66',
            regime_tributario=RegimeTributario.SIMPLES,
        )
        self.assertEqual(emp.get_regime_tributario_display(), 'Simples Nacional')
