from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='index'),
    
    # quotation URLs
    path('quotations/<str:account_name>/', views.quotation_list, name='quotation_list'),
    path('quotations/<int:quotation_id>/', views.quotation_detail, name='quotation_detail'),
    path('quotations/create/', views.create_quotation, name='create_quotation'),
    path('quotations/<int:quotation_id>/version/', views.create_quotation_version, name='create_quotation_version'),
    path('quotations/<int:quotation_id>/versions/', views.get_quotation_versions, name='get_quotation_versions'),
    path('quotations/<int:quotation_id>/status/<str:status>/', views.update_quotation_status, name='update_quotation_status'),
    
    # bill of materials (BOM)
    path('products/', views.product_list, name='product_list'),
    path('products/create_product/', views.create_product, name='create_product'),
    path('products/<int:product_id>/bom/', views.get_bill_of_materials, name='get_bill_of_materials'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # quotation item
    path('quotations/<int:quotation_id>/items/add/', views.add_quotation_item, name='add_quotation_item'),
    path('quotations/<int:quotation_id>/items/', views.get_quotation_items, name='get_quotation_items'),
    
    # customer
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/add_customer/', views.add_customer, name='add_customer'),
    
    # material
    path('materials/', views.material_list, name='material_list'),
    path('materials/<int:material_id>/', views.material_detail, name='material_detail'),
    path('materials/create_material/', views.create_material, name='create_material'),

    # misc
    path('faq/', views.faq, name='faq'),
    path('about/', views.about, name='about')

]

#READ ME
# we will be changing the default to start at the login screen when we get to it
# All users will be visible in the url through an additional format /u/<str:account_name>
# For all the obfuscated data, we do the following format
#                        {% if Account.access_level == "Admin" %}
#                        {{data.unobfuscated_data}}
#                        <!---{% else %}---->
#                        <!--- XXXXX.XX ------>
#                        <!---{% endif %} ---->