# Generated for existing restaurant data

import django.db.models.deletion
from django.db import migrations, models


def atribuir_organizacao_padrao(apps, schema_editor):
    Organizacao = apps.get_model('core', 'Organizacao')
    organizacao, _ = Organizacao.objects.get_or_create(nome='Organizacao Principal')

    for model_name in ('Prato', 'Combo', 'Mesa', 'Comanda'):
        model = apps.get_model('pedidos', model_name)
        model.objects.filter(organizacao__isnull=True).update(organizacao=organizacao)


def remover_organizacao_padrao(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('pedidos', '0002_prato_categoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='prato',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AddField(
            model_name='combo',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AddField(
            model_name='mesa',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AddField(
            model_name='comanda',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.RunPython(atribuir_organizacao_padrao, remover_organizacao_padrao),
        migrations.AlterField(
            model_name='prato',
            name='organizacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AlterField(
            model_name='combo',
            name='organizacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AlterField(
            model_name='mesa',
            name='organizacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AlterField(
            model_name='comanda',
            name='organizacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AddConstraint(
            model_name='mesa',
            constraint=models.UniqueConstraint(fields=('organizacao', 'numero'), name='mesa_unica_por_org'),
        ),
    ]
