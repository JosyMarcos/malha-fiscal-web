from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razao_social', models.CharField(max_length=255, verbose_name='Razão Social')),
                ('cnpj', models.CharField(max_length=18, verbose_name='CNPJ')),
                ('nome_fantasia', models.CharField(blank=True, max_length=255, verbose_name='Nome Fantasia')),
                ('inscricao_estadual', models.CharField(blank=True, max_length=30, verbose_name='Inscrição Estadual')),
                ('uf', models.CharField(choices=[('AC', 'AC'), ('AL', 'AL'), ('AM', 'AM'), ('AP', 'AP'), ('BA', 'BA'), ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'), ('MG', 'MG'), ('MS', 'MS'), ('MT', 'MT'), ('PA', 'PA'), ('PB', 'PB'), ('PE', 'PE'), ('PI', 'PI'), ('PR', 'PR'), ('RJ', 'RJ'), ('RN', 'RN'), ('RO', 'RO'), ('RR', 'RR'), ('RS', 'RS'), ('SC', 'SC'), ('SE', 'SE'), ('SP', 'SP'), ('TO', 'TO')], default='PB', max_length=2, verbose_name='UF')),
                ('regime_tributario', models.CharField(choices=[('simples', 'Simples Nacional'), ('presumido', 'Lucro Presumido'), ('real', 'Lucro Real'), ('mei', 'MEI')], default='simples', max_length=20, verbose_name='Regime Tributário')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='E-mail')),
                ('telefone', models.CharField(blank=True, max_length=20, verbose_name='Telefone')),
                ('responsavel', models.CharField(blank=True, max_length=150, verbose_name='Responsável')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativa')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='empresas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Empresa',
                'verbose_name_plural': 'Empresas',
                'ordering': ['razao_social'],
                'unique_together': {('usuario', 'cnpj')},
            },
        ),
    ]
