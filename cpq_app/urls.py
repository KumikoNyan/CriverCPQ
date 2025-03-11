from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    
    # just basic return stuff here, WOULD need to edit once Boostrap Templates and Django Tags are used
    # quotation stuff urls
    path('quotations/', quotation_list, name='quotation_list'),
    path('quotations/<int:quotation_id>/', quotation_detail, name='quotation_detail'),
    path('quotations/create/', create_quotation, name='create_quotation'),
    path('quotations/<int:quotation_id>/version/', create_quotation_version, name='create_quotation_version'),
    path('quotations/<int:quotation_id>/versions/', get_quotation_versions, name='get_quotation_versions'),
    path('quotations/<int:quotation_id>/status/<str:status>/', update_quotation_status, name='update_quotation_status'),
    
    # bom
    path('products/<int:product_id>/bom/', get_bill_of_materials, name='get_bill_of_materials'),
    
    # quotation item
    path('quotations/<int:quotation_id>/items/add/', add_quotation_item, name='add_quotation_item'),
    path('quotations/<int:quotation_id>/items/', get_quotation_items, name='get_quotation_items'),
    
    # customer
    path('customers/', customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', customer_detail, name='customer_detail'),
    
    # supplier
    path('suppliers/', supplier_list, name='supplier_list'),
    path('suppliers/<int:supplier_id>/', supplier_detail, name='supplier_detail'),
    
    # material
    path('materials/', material_list, name='material_list'),
    path('materials/<int:material_id>/', material_detail, name='material_detail'),
    
    # material finish
    path('materials/finishes/', material_finish_list, name='material_finish_list'),
    path('materials/finishes/<int:finish_id>/', material_finish_detail, name='material_finish_detail'),
]
