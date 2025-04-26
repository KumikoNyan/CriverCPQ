from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='index'),

    # login URLs
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('create_account/', views.create_account, name='create_account'),
    path('change_password/', views.change_password, name='change_password'),
    path('error/', views.access_error, name='access_error'),
    
    # temp remove after init superuser account - DO NOT ENABLE only use ONCE
    # path('init_create_superuser/', views.init_create_superuser, name='init_create_superuser'),
    
    # quotation URLs
    path('quotations/', views.quotation_list, name='quotation_list'),
    path('quotations/<int:quotation_id>/', views.quotation_detail, name='quotation_detail'),
    path('quotations/create/', views.create_quotation, name='create_quotation'),
    path('quotations/view_version/<int:quotation_id>', views.view_version, name='view_version'),
    path('get_bill_of_materials/', views.get_bill_of_materials, name='get_bill_of_materials'),
    path('get_total_bom/', views.get_total_bom, name='get_total_bom'),
    path('download-quotation-excel/<int:quotation_id>/', views.download_quotation_excel, name='download_quotation_excel'),
    
    # bill of materials (BOM) URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create_product/', views.create_product, name='create_product'),
    path('products/<int:product_id>/bom/', views.get_bill_of_materials, name='get_bill_of_materials'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('get_products/', views.get_products, name='get_products'),
    
    # quotation item URLs
    path('quotations/<int:quotation_id>/items/add/', views.add_quotation_item, name='add_quotation_item'),
    path('quotations/<int:quotation_id>/items/', views.get_quotation_items, name='get_quotation_items'),
    
    # customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/add_customer/', views.add_customer, name='add_customer'),
    path('get_customer/', views.get_customer, name='get_customer'),
    
    # material URLs
    path('materials/', views.material_list, name='material_list'),
    path('materials/<int:material_id>/', views.material_detail, name='material_detail'),
    path('materials/create_material/', views.create_material, name='create_material'),

    # misc URLs
    path('faq/', views.faq, name='faq'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback, name='feedback')

]