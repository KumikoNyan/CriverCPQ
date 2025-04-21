from django.db import models
from collections import defaultdict

# Models
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField()
    customer_mobile = models.CharField(max_length=20)
    customer_email = models.EmailField()

    def __str__(self):
        return self.customer_name

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    account_name = models.CharField(max_length=255)
    account_password = models.CharField(max_length=255)
    account_created = models.DateTimeField(auto_now_add=True)
    account_level = models.CharField(max_length=50, choices=[('regular', 'Regular'), ('superuser', 'Superuser')], default='regular')
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account_name} ({'Superuser' if self.is_superuser else 'Regular'})"

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)

    def __str__(self):
        return self.supplier_name
    
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_category = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.product_name

class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    material_name = models.CharField(max_length=255)
    material_type = models.CharField(max_length=255)
    material_unit = models.CharField(max_length=50)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.material_name

class MaterialFinish(models.Model):
    finish_id = models.AutoField(primary_key=True)
    finish_name = models.CharField(max_length=255)
    finish_cost = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.finish_name

class ProductMaterial(models.Model):
    product_material_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    material_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    scale_by_height = models.BooleanField(default=False)
    scale_by_width = models.BooleanField(default=False)
    scale_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    scale_ratio_second = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.material.material_name} for {self.product.product_name}"
    
class Quotation(models.Model):
    quotation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    project = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    quotation_status = models.CharField(max_length=50)
    version_number = models.IntegerField()
    is_active_version = models.BooleanField(default=True)

    def __str__(self):
        return f"Quotation {self.quotation_id} - Version {self.version_number}"


class QuotationItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_label = models.CharField(max_length=50)
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    item_quantity = models.IntegerField()
    product_margin = models.IntegerField()
    product_labor = models.IntegerField()
    item_height = models.FloatField()
    item_width = models.FloatField()
    glass_finish = models.CharField(max_length=50, null=True)
    aluminum_finish = models.CharField(max_length=50, null=True)
    excluded_materials = models.CharField(max_length=50, null=True)
    additional_materials = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"Item {self.item_id} in Quotation {self.quotation.quotation_id}"
    
    def get_unit_price(self):
        height = self.item_height
        width = self.item_width
        quantity = self.item_quantity
        product_margin = self.product_margin
        labor_margin = self.product_labor
        glass_finish = self.glass_finish or ""
        aluminum_finish = self.aluminum_finish or ""

        # Parse excluded materials list from string if it's stored as CSV
        excluded_materials = self.excluded_materials.split(',') if self.excluded_materials else []

        materials = ProductMaterial.objects.filter(product=self.product)
        per_item_cost = 0.0

        for m in materials:
            mat_id = str(m.material.material_id)
            if mat_id in excluded_materials:
                continue

            mat = m.material
            unit_cost = 0.0

            if mat.material_type == "accessory":
                single_unit = 1
                unit_cost = float(mat.material_cost)

            elif mat.material_type == "glass":
                finish_obj = MaterialFinish.objects.get(finish_name=glass_finish, material=mat)
                unit_cost = float(finish_obj.finish_cost)
                single_unit = (height * float(m.scale_ratio_second or 0)) * (width * float(m.scale_ratio or 0))

            else:  # aluminum
                finish_obj = MaterialFinish.objects.get(finish_name=aluminum_finish, material=mat)
                unit_cost = float(finish_obj.finish_cost)
                dimension = height if m.scale_by_height else width
                single_unit = dimension * float(m.scale_ratio or 0)

            single_item_qty = single_unit * float(m.material_quantity)
            single_item_cost = single_item_qty * unit_cost

            per_item_cost += single_item_cost

        unit_price = per_item_cost * (1 + (labor_margin + product_margin) / 100)
        return round(unit_price, 2)
