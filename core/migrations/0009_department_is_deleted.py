# Generated by Django 4.1.7 on 2023-04-24 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_inventorylist_invent_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Удален'),
        ),
    ]