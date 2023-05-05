# Generated by Django 4.1.7 on 2023-05-02 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_type_operation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Закупка'), (2, 'Перемещение'), (3, 'Списание')], default=2, verbose_name='Тип операции'),
        ),
        migrations.DeleteModel(
            name='Type',
        ),
    ]
