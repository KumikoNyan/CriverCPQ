# Generated by Django 5.1.7 on 2025-03-11 18:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_address', models.TextField()),
                ('customer_mobile', models.CharField(max_length=20)),
                ('customer_email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('material_id', models.AutoField(primary_key=True, serialize=False)),
                ('material_name', models.CharField(max_length=255)),
                ('material_type', models.CharField(max_length=255)),
                ('material_unit', models.CharField(max_length=50)),
                ('material_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialFinish',
            fields=[
                ('finish_id', models.AutoField(primary_key=True, serialize=False)),
                ('finish_name', models.CharField(max_length=255)),
                ('finish_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=255)),
                ('product_category', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('supplier_id', models.AutoField(primary_key=True, serialize=False)),
                ('supplier_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='cpq_app.customer')),
                ('account_name', models.CharField(max_length=255)),
                ('account_password', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('access_level', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ProductMaterial',
            fields=[
                ('product_material_id', models.AutoField(primary_key=True, serialize=False)),
                ('material_quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('scale_by_height', models.DecimalField(decimal_places=2, max_digits=5)),
                ('scale_by_length', models.DecimalField(decimal_places=2, max_digits=5)),
                ('scale_ratio', models.DecimalField(decimal_places=2, max_digits=5)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cpq_app.material')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cpq_app.product')),
            ],
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('quotation_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('quotation_status', models.CharField(max_length=50)),
                ('version_number', models.IntegerField()),
                ('is_active_version', models.BooleanField(default=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cpq_app.customer')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationItem',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cpq_app.product')),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cpq_app.quotation')),
            ],
        ),
        migrations.AddField(
            model_name='material',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cpq_app.supplier'),
        ),
    ]
