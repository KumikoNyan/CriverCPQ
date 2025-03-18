from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse

# this shld be changed later
def index(request):
    return JsonResponse({"message": "Welcome Bitch!"})

# quotation views
def quotation_list(request):
    quotations = list(Quotation.objects.values())
    return render(request, 'cpq_app/quotations_list.html', {"quotations": quotations})

def quotation_detail(request, quotation_id):
    quotation = get_object_or_404(Quotation, pk=quotation_id)
    return JsonResponse({"quotation": {
        "id": quotation.id,
        "date_created": quotation.date_created,
        "status": quotation.quotation_status,
        "version": quotation.version_number,
        "is_active": quotation.is_active_version
    }})

# ideally, this should create a quotation
@csrf_exempt # not sure if this was the right way, i just skimmed on the tapas project back in msys22
def create_quotation(request):
    if request.method == "POST":
        data = json.loads(request.body)
        customer = get_object_or_404(Customer, pk=data['customer_id'])
        quotation = Quotation.objects.create(
            date_created=data['date_created'],
            quotation_status='Draft',
            version_number=1,
            is_active_version=True
        )
        return JsonResponse({"message": "Quotation created successfully", "quotation_id": quotation.id})

# quotation versioning i have no clue if this will work, but generally it should save the previous versions
@csrf_exempt
def create_quotation_version(request, quotation_id):
    if request.method == "POST":
        old_quotation = get_object_or_404(Quotation, pk=quotation_id)
        new_version_number = old_quotation.version_number + 1
        
        new_quotation = Quotation.objects.create(
            date_created=old_quotation.date_created,
            quotation_status=old_quotation.quotation_status,
            version_number=new_version_number,
            is_active_version=True
        )
        old_quotation.is_active_version = False
        old_quotation.save()
        
        return JsonResponse({"message": "Quotation version created", "new_version_id": new_quotation.id})

# func to get quotation versions
def get_quotation_versions(request, quotation_id):
    versions = list(Quotation.objects.filter(id=quotation_id).values())
    return JsonResponse({"quotation_versions": versions})

# bom breakdown (is this really it lang? can someone confirm)
def get_bill_of_materials(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    materials = ProductMaterial.objects.filter(product_id=product.id)
    bom = [{
        "material": material.material_id,
        "quantity": material.material_quantity,
        "scale_by_height": material.scale_by_height,
        "scale_by_length": material.scale_by_length,
        "scale_ratio": material.scale_ratio
    } for material in materials]
    return JsonResponse({"product": product.product_name, "bill_of_materials": bom})

# quotation item views
@csrf_exempt
def add_quotation_item(request, quotation_id):
    if request.method == "POST":
        data = json.loads(request.body)
        quotation = get_object_or_404(Quotation, pk=quotation_id)
        product = get_object_or_404(Product, pk=data['product_id'])
        
        item = QuotationItem.objects.create(
            quotation=quotation,
            product=product,
            item_quantity=data['item_quantity'],
            unit_price=data['unit_price'],
            total_price=data['item_quantity'] * data['unit_price']
        )
        
        return JsonResponse({"message": "Item added to quotation", "item_id": item.id})

def get_quotation_items(request, quotation_id):
    items = QuotationItem.objects.filter(quotation_id=quotation_id)
    items_list = [{
        "id": item.id,
        "product": item.product.product_name,
        "quantity": item.item_quantity,
        "unit_price": item.unit_price,
        "total_price": item.total_price
    } for item in items]
    return JsonResponse({"quotation_items": items_list})

# customer views
def customer_list(request):
    customers = list(Customer.objects.values())
    return JsonResponse({"customers": customers})

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    return JsonResponse({"customer": {
        "id": customer.id,
        "name": customer.customer_name,
        "address": customer.customer_address,
        "mobile": customer.customer_mobile,
        "email": customer.customer_email
    }})

# supplier views
def supplier_list(request):
    suppliers = list(Supplier.objects.values())
    return JsonResponse({"suppliers": suppliers})

def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    return JsonResponse({"supplier": {
        "id": supplier.id,
        "name": supplier.supplier_name
    }})

# material views
def material_list(request):
    materials = list(Material.objects.values())
    return render(request, 'cpq_app/material_list.html', {"materials": materials})

def material_detail(request, material_id):
    material = get_object_or_404(Material, pk=material_id)
    return JsonResponse({"material": {
        "id": material.id,
        "name": material.material_name,
        "type": material.material_type,
        "unit": material.material_unit,
        "price": material.material_price
    }})

def create_material(request):
    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        
        response['url'] = reverse('material_list')  # URL to direct is str
        print(response)
        return JsonResponse(response)
    return render(request, 'cpq_app/create_material.html')

# material finish views
def material_finish_list(request):
    finishes = list(MaterialFinish.objects.values())
    return JsonResponse({"finishes": finishes})

def material_finish_detail(request, finish_id):
    finish = get_object_or_404(MaterialFinish, pk=finish_id)
    return JsonResponse({"finish": {
        "id": finish.id,
        "name": finish.finish_name,
        "price": finish.finish_price
    }})

# quotation status tracking
def update_quotation_status(request, quotation_id, status):
    quotation = get_object_or_404(Quotation, pk=quotation_id)
    quotation.quotation_status = status
    quotation.save()
    return JsonResponse({"message": "Quotation status updated", "quotation_id": quotation_id, "status": status})
