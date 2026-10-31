from django.db import models
from django.conf import settings


class Auditoria(models.Model):
    usuario      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    criado_em    = models.DateTimeField(auto_now_add=True)
    empresa      = models.CharField(max_length=255, blank=True)
    periodo      = models.CharField(max_length=20, blank=True,
                                    help_text='Ex.: 01/2025 ou Jan-Mar 2025')
    total_notas  = models.PositiveIntegerField(default=0)
    divergencias = models.PositiveIntegerField(default=0)
    score_risco  = models.CharField(max_length=10, blank=True,
                                    help_text='BAIXO / MÉDIO / ALTO')
    resumo       = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'

    def __str__(self):
        return f"{self.empresa} — {self.periodo} ({self.criado_em:%d/%m/%Y})"


class RegimeTributario(models.TextChoices):
    SIMPLES    = 'simples',    'Simples Nacional'
    PRESUMIDO  = 'presumido',  'Lucro Presumido'
    REAL       = 'real',       'Lucro Real'
    MEI        = 'mei',        'MEI'


UF_CHOICES = [
    ('AC','AC'),('AL','AL'),('AM','AM'),('AP','AP'),('BA','BA'),
    ('CE','CE'),('DF','DF'),('ES','ES'),('GO','GO'),('MA','MA'),
    ('MG','MG'),('MS','MS'),('MT','MT'),('PA','PA'),('PB','PB'),
    ('PE','PE'),('PI','PI'),('PR','PR'),('RJ','RJ'),('RN','RN'),
    ('RO','RO'),('RR','RR'),('RS','RS'),('SC','SC'),('SE','SE'),
    ('SP','SP'),('TO','TO'),
]


class Empresa(models.Model):
    usuario             = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='empresas'
    )
    razao_social        = models.CharField(max_length=255, verbose_name='Razão Social')
    cnpj                = models.CharField(max_length=18, verbose_name='CNPJ')
    nome_fantasia       = models.CharField(max_length=255, blank=True, verbose_name='Nome Fantasia')
    inscricao_estadual  = models.CharField(max_length=30, blank=True, verbose_name='Inscrição Estadual')
    uf                  = models.CharField(max_length=2, choices=UF_CHOICES, default='PB', verbose_name='UF')
    regime_tributario   = models.CharField(
        max_length=20,
        choices=RegimeTributario.choices,
        default=RegimeTributario.SIMPLES,
        verbose_name='Regime Tributário'
    )
    email               = models.EmailField(blank=True, verbose_name='E-mail')
    telefone            = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    responsavel         = models.CharField(max_length=150, blank=True, verbose_name='Responsável')
    ativo               = models.BooleanField(default=True, verbose_name='Ativa')
    criado_em           = models.DateTimeField(auto_now_add=True)
    atualizado_em       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['razao_social']
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        unique_together = [('usuario', 'cnpj')]

    def __str__(self):
        return f"{self.razao_social} ({self.cnpj})"

    def cnpj_formatado(self):
        c = ''.join(filter(str.isdigit, self.cnpj))
        if len(c) == 14:
            return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
        return self.cnpj
