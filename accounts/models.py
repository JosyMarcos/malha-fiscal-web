from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Plano(models.TextChoices):
    TRIAL         = 'trial',         'Trial — 48h gratuito'
    ESSENCIAL     = 'essencial',     'Essencial — R$157/mês'
    PROFISSIONAL  = 'profissional',  'Profissional — R$397/mês'
    ENTERPRISE    = 'enterprise',    'Enterprise — R$697/mês'


class Usuario(AbstractUser):
    # Campos de negócio
    plano            = models.CharField(max_length=20, choices=Plano.choices, default=Plano.ESSENCIAL, verbose_name='Plano')
    ativo            = models.BooleanField(default=False, verbose_name='Acesso ativo')
    data_expiracao   = models.DateField(null=True, blank=True, verbose_name='Expira em')
    empresa          = models.CharField(max_length=200, blank=True, verbose_name='Empresa / Escritório')
    telefone         = models.CharField(max_length=20, blank=True, verbose_name='Telefone/WhatsApp')
    observacoes      = models.TextField(blank=True, verbose_name='Observações')
    criado_em        = models.DateTimeField(auto_now_add=True)
    ultimo_acesso_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.email})'

    @property
    def acesso_valido(self):
        """Retorna True se o usuário está ativo E dentro da validade."""
        if not self.ativo:
            return False
        if self.data_expiracao and self.data_expiracao < timezone.now().date():
            return False
        return True

    @property
    def is_trial(self):
        return self.plano == Plano.TRIAL

    @property
    def trial_expira_em(self):
        """Datetime exato de expiração do trial (criado_em + 48h)."""
        if self.is_trial and self.criado_em:
            from datetime import timedelta
            return self.criado_em + timedelta(hours=48)
        return None

    @property
    def status_display(self):
        if not self.ativo:
            return 'Inativo'
        if self.data_expiracao and self.data_expiracao < timezone.now().date():
            return 'Expirado'
        return 'Ativo'

    @property
    def dias_restantes(self):
        if not self.data_expiracao:
            return None
        delta = (self.data_expiracao - timezone.now().date()).days
        return delta
