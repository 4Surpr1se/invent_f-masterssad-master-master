# Generated by Django 4.1.7 on 2023-05-02 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_operation_type_delete_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Удален'),
        ),
    ]
