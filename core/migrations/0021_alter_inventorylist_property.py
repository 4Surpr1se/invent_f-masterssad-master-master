# Generated by Django 4.1.7 on 2023-05-26 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_remove_operation_waybill_alter_operation_pdf_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorylist',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prop', to='core.property', verbose_name='Имущество'),
        ),
    ]
