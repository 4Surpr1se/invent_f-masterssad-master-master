# Generated by Django 4.1.7 on 2023-05-31 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_alter_inventorylist_property'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='data_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='аккаунт_дата'),
        ),
    ]