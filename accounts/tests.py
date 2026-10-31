"""
Testes do módulo accounts — registro, login, logout, modelos e admin
"""
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Usuario, Plano


def _make_user(username='user1', plano=Plano.ESSENCIAL, is_staff=False, ativo=True):
    """Cria um usuário de teste com acesso ativo por padrão."""
    data_exp = (timezone.now() + timedelta(days=365)).date()
    u = Usuario.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password='senha123',
        plano=plano,
        ativo=ativo,
        data_expiracao=data_exp,
    )
    if is_staff:
        u.is_staff = True
        u.save()
    return u


# ── Registro ──────────────────────────────────────────────────────────────────

class RegistroViewTest(TestCase):
    def test_get_registro(self):
        r = self.client.get(reverse('accounts:registro'))
        self.assertEqual(r.status_code, 200)

    def test_registro_cria_usuario(self):
        """Registro usa campos custom: nome, empresa, email, senha, confirma, aceita_termos."""
        r = self.client.post(reverse('accounts:registro'), {
            'nome':        'Maria Contadora',
            'empresa':     'Escritório Contábil',
            'email':       'maria@contadora.com',
            'senha':       'Senha@Forte123',
            'confirma':    'Senha@Forte123',
            'aceita_termos': 'on',
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Usuario.objects.filter(email='maria@contadora.com').exists())

    def test_registro_sem_aceite_termos_falha(self):
        r = self.client.post(reverse('accounts:registro'), {
            'nome':     'Sem Aceite',
            'empresa':  'Empresa X',
            'email':    'semaceite@test.com',
            'senha':    'Senha@123',
            'confirma': 'Senha@123',
            # sem aceita_termos
        })
        self.assertFalse(Usuario.objects.filter(email='semaceite@test.com').exists())

    def test_registro_senhas_diferentes_falha(self):
        r = self.client.post(reverse('accounts:registro'), {
            'nome':     'Teste',
            'empresa':  'Empresa X',
            'email':    'dif@test.com',
            'senha':    'Senha@123',
            'confirma': 'SenhaDiferente@456',
            'aceita_termos': 'on',
        })
        self.assertFalse(Usuario.objects.filter(email='dif@test.com').exists())


# ── Login / Logout ────────────────────────────────────────────────────────────

class LoginViewTest(TestCase):
    def setUp(self):
        self.user = _make_user()

    def test_login_valido_redireciona(self):
        """LoginForm usa campos 'username' e 'password' (AuthenticationForm)."""
        r = self.client.post(reverse('accounts:login'), {
            'username': 'user1',
            'password': 'senha123',
        })
        self.assertEqual(r.status_code, 302)

    def test_login_invalido_permanece(self):
        r = self.client.post(reverse('accounts:login'), {
            'username': 'user1',
            'password': 'errada',
        })
        self.assertEqual(r.status_code, 200)

    def test_login_usuario_inativo_bloqueia(self):
        inativo = _make_user('inativo_u', ativo=False)
        r = self.client.post(reverse('accounts:login'), {
            'username': 'inativo_u',
            'password': 'senha123',
        })
        # não redireciona — fica na página de login com mensagem
        self.assertEqual(r.status_code, 200)

    def test_logout(self):
        self.client.login(username='user1', password='senha123')
        r = self.client.post(reverse('accounts:logout'))
        self.assertEqual(r.status_code, 302)


# ── Modelo Usuario ────────────────────────────────────────────────────────────

class AcessoValidoTest(TestCase):
    def test_plano_essencial_acesso_valido(self):
        u = _make_user(plano=Plano.ESSENCIAL, ativo=True)
        self.assertTrue(u.acesso_valido)

    def test_plano_profissional_acesso_valido(self):
        u = _make_user('prof_u', plano=Plano.PROFISSIONAL, ativo=True)
        self.assertTrue(u.acesso_valido)

    def test_usuario_inativo_sem_acesso(self):
        u = _make_user('inat_u', ativo=False)
        self.assertFalse(u.acesso_valido)

    def test_data_expirada_sem_acesso(self):
        u = _make_user('exp_u', ativo=True)
        u.data_expiracao = (timezone.now() - timedelta(days=1)).date()
        u.save()
        self.assertFalse(u.acesso_valido)

    def test_trial_recem_criado_acesso_valido(self):
        """Trial criado agora deve ter acesso (expira em 48h)."""
        u = _make_user('trial_u', plano=Plano.TRIAL, ativo=True)
        self.assertTrue(u.acesso_valido)

    def test_is_trial_true_para_plano_trial(self):
        u = _make_user('trial2', plano=Plano.TRIAL)
        self.assertTrue(u.is_trial)

    def test_is_trial_false_para_plano_pago(self):
        u = _make_user('pago_u', plano=Plano.ESSENCIAL)
        self.assertFalse(u.is_trial)


# ── Admin Dashboard ───────────────────────────────────────────────────────────

class AdminDashboardTest(TestCase):
    def test_admin_pode_acessar(self):
        admin = _make_user('admin_u', is_staff=True)
        self.client.login(username='admin_u', password='senha123')
        r = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(r.status_code, 200)

    def test_usuario_comum_nao_acessa_admin(self):
        _make_user('comum_u')
        self.client.login(username='comum_u', password='senha123')
        r = self.client.get(reverse('accounts:admin_dashboard'))
        # deve redirecionar (302) ou retornar 403, nunca 200
        self.assertNotEqual(r.status_code, 200)
