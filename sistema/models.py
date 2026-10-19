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
