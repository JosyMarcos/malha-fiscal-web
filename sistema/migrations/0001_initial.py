from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auditoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('empresa', models.CharField(blank=True, max_length=255)),
                ('periodo', models.CharField(blank=True, help_text='Ex.: 01/2025 ou Jan-Mar 2025', max_length=20)),
                ('total_notas', models.PositiveIntegerField(default=0)),
                ('divergencias', models.PositiveIntegerField(default=0)),
                ('score_risco', models.CharField(blank=True, help_text='BAIXO / MÉDIO / ALTO', max_length=10)),
                ('resumo', models.JSONField(blank=True, default=dict)),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='auditorias',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Auditoria',
                'verbose_name_plural': 'Auditorias',
                'ordering': ['-criado_em'],
            },
        ),
    ]
