# Generated by Django 4.1.7 on 2023-04-28 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_holding_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventorylist',
            old_name='MOL',
            new_name='mol',
        ),
    ]