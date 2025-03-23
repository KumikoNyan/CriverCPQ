from django.db import models

# Models
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField()
    customer_mobile = models.CharField(max_length=20)
    customer_email = models.EmailField()

    def __str__(self):
        return self.customer_name

# ideally, the Account models should have a: superuser and users
# only the superuser is allowed to create accounts
class Account(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    account_name = models.CharField(max_length=255)
    account_password = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    access_level = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')], default='user') # should contain the access level for the current logged in user

    def __str__(self):
        return self.account_name

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)

    def __str__(self):
        return self.supplier_name
    
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_category = models.CharField(max_length=255)
    product_margin = models.IntegerField()
    product_labor = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.product_name

class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    material_name = models.CharField(max_length=255)
    material_type = models.CharField(max_length=255)
    material_unit = models.CharField(max_length=50)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2)
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
    scale_by_length = models.BooleanField(default=False)
    scale_ratio = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.material.material_name} for {self.product.product_name}"
    
class Quotation(models.Model):
    quotation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    quotation_status = models.CharField(max_length=50)
    version_number = models.IntegerField()
    is_active_version = models.BooleanField(default=True)

    def __str__(self):
        return f"Quotation {self.quotation_id} - Version {self.version_number}"


class QuotationItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    item_quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.item_quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.item_id} in Quotation {self.quotation.quotation_id}"
