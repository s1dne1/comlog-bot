# Generated by Django 5.1.7 on 2025-04-07 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_chegadamotorista_periodo_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chegadamotorista',
            old_name='trasnportadora',
            new_name='transportadora',
        ),
    ]
