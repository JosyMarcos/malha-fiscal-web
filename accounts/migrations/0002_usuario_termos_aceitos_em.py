from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='termos_aceitos_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Termos aceitos em'),
        ),
    ]
