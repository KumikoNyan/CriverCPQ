from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Quotation)
admin.site.register(QuotationItem)
admin.site.register(Product)
admin.site.register(ProductMaterial)
admin.site.register(Supplier)
admin.site.register(Material)
admin.site.register(MaterialFinish)