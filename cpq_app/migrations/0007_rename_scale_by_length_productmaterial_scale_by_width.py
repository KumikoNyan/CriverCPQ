# Generated by Django 5.1.7 on 2025-03-25 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cpq_app', '0006_product_product_labor_product_product_margin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productmaterial',
            old_name='scale_by_length',
            new_name='scale_by_width',
        ),
    ]
