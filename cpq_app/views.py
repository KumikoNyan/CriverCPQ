from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse

# Change welcome message later or remove if not needed
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

# quotation versioning
@csrf_exempt
def create_quotation_version(request, quotation_id):
    if request.method == "POST":
        old_quotation = get_object_or_404(Quotation, pk=quotation_id)
        new_version_number = old_quotation.version_number + 1
        
        new_quotation = Quotation.objects.create(
            date_created=old_quotation.date_created,
            quotation_status=old_quotation.quotation_status,
            version_number=new_version_number,
            is_active_version=True # sets the new quotation as active
        )
        old_quotation.is_active_version = False
        old_quotation.save() # saves the old version/s and sets it to not active
        
        return JsonResponse({"message": "Quotation version created", "new_version_id": new_quotation.id})

# func to get quotation versions
def get_quotation_versions(request, quotation_id):
    versions = list(Quotation.objects.filter(id=quotation_id).values())
    return JsonResponse({"quotation_versions": versions})

# BoM breakdown
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


def supplier_operations(supplier):
    supplier_id = supplier["supplier_id"]
    supplier_name = supplier["supplier_name"]
    if supplier_name == "delete":
        print('delete!')
        if supplier_id:
            Supplier.objects.filter(supplier_id=supplier_id).delete()
    elif supplier_id:
        print('edit!')
        supplier_object = Supplier.objects.get(supplier_id=supplier_id)
        supplier_object.supplier_name = supplier_name
        supplier_object.save()
    else:
        new_supplier = Supplier.objects.create(supplier_name = supplier_name)
    return True

def delete_material(material_id):
    material_object = Material.objects.get(material_id=material_id)
    material_object.delete()

# product views
def delete_product(product_id):
    product_object = Product.objects.get(product_id=product_id)
    product_object.delete()

def product_list(request):
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    supplier_count = len(suppliers) or 0

    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("action") == "delete":
            product_id = request.POST.get("product_id")
            delete_product(product_id)
            response['url'] = reverse('product_list')
            print(response)
            return JsonResponse(response)

        elif request.POST.get("supplier_data"):
            for supplier in json.loads(request.POST.get("supplier_data")):
                print(supplier)
                supplier_operations(supplier)
            response['url'] = reverse('product_list')
            print(response)
            return JsonResponse(response)

    return render(request, 'cpq_app/product_list.html', {"products": products, 'suppliers': suppliers, 'supplier_count': supplier_count})

def product_detail(request, product_id):
    product_object = Product.objects.get(product_id=product_id)
    product_material_object = ProductMaterial.objects.filter(product=product, material=material)
    suppliers = Supplier.objects.all()
    supplier_count = len(suppliers) or 0

    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("action") == "delete":
            product_id = request.POST.get("product_id")
            delete_product(product_id)
            response['url'] = reverse('product_list')
            print(response)
            return JsonResponse(response)

        else:
            if request.POST.get("supplier_data"):
                for supplier in json.loads(request.POST.get("supplier_data")):
                    print(supplier)
                    supplier_operations(supplier)
                response['url'] = reverse('create_product')
                print(response)
                return JsonResponse(response)

            else:
                product_id = request.POST.get("product_id")
                product_name = request.POST.get("product_name")
                product_category = request.POST.get("product_category")
                product_margin = request.POST.get("product_margin")
                product_labor = request.POST.get("product_labor")
                supplier_id = request.POST.get("supplier")
                pm_data = json.loads(request.POST.get("pm_data", "[]"))

                product = get_object_or_404(Product, product_id=product_id)
                product.product_name = product_name
                product.product_category = product_category
                product.product_margin = product_margin
                product.product_labor = product_labor
                product.supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
                product.save()

                ProductMaterial.objects.filter(product=product, material=material).delete()

                pm_data = json.loads(request.POST.get("pm_data"))
                if pm_data:
                    for pm in pm_data:
                        material_id = pm["material_id"]
                        material = get_object_or_404(Material, material_id=material_id)
                        material_name = material.material_name
                        material_quantity = pm["material_quantity"]
                        scale_by_height = pm["scale_by_height"]
                        scale_by_length = pm["scale_by_length"]
                        scale_ratio = pm["scale_ratio"]

                    # was thinking a dropdown would be here for the materials
                    # access the ID of the material
                    # since this wont be an input field for products

                response['url'] = reverse('product_list')
                return JsonResponse(response)
    return render(request, 'cpq_app/product_detail.html', {'product_object': product_object, 'product_material_object': product_material_object, 'suppliers': suppliers, 'supplier_count': supplier_count})

def create_product(request):
    materials = Material.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("supplier_data"):
            for supplier in json.loads(request.POST.get("supplier_data")):
                print(supplier)
                supplier_operations(supplier)
            response['url'] = reverse('create_product')
            print(response)
            return JsonResponse(response)

        else:
            product_id = request.POST.get("product_id")
            product_name = request.POST.get("product_name")
            product_category = request.POST.get("product_category")
            product_margin = request.POST.get("product_margin")
            product_labor = request.POST.get("product_labor")
            supplier_id = request.POST.get("supplier")
            supplier = Supplier.objects.get(supplier_id=supplier_id)

            new_product = Product.objects.create(product_name=product_name, 
            product_category=product_category, 
            product_margin=product_margin, 
            product_labor=product_labor, 
            supplier=supplier)

            pm_data = json.loads(request.POST.get("pm_data"))
            if pm_data:
                for pm in pm_data:
                    material_id = pm["material_id"]
                    material = get_object_or_404(Material, material_id=material_id)
                    material_name = material.material_name
                    material_quantity = pm["material_quantity"]
                    scale_by_height = pm["scale_by_height"]
                    scale_by_length = pm["scale_by_length"]
                    scale_ratio = pm["scale_ratio"]

                    # was thinking a dropdown would be here for the materials
                    # access the ID of the material
                    # since this wont be an input field for products

            response['url'] = reverse('product_list')
            print(response)
            return JsonResponse(response)
    return render(request, 'cpq_app/create_product.html', {"materials": materials, "suppliers": suppliers})

# material views
def material_list(request):
    materials = Material.objects.all()
    suppliers = Supplier.objects.all()
    supplier_count = len(suppliers) or 0

    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("action") == "delete":
            material_id = request.POST.get("material_id")
            delete_material(material_id)
            response['url'] = reverse('material_list')  # URL to direct is str
            print(response)
            return JsonResponse(response)
        elif request.POST.get("supplier_data"):
            for supplier in json.loads(request.POST.get("supplier_data")):
                print(supplier)
                supplier_operations(supplier)
            response['url'] = reverse('material_list')  # URL to direct is str
            print(response)
            return JsonResponse(response)
    return render(request, 'cpq_app/material_list.html', {"materials": materials, 'suppliers': suppliers, 'supplier_count': supplier_count})

def material_detail(request, material_id):
    material_object = Material.objects.get(material_id=material_id)
    finishes = MaterialFinish.objects.filter(material=material_object)
    suppliers = Supplier.objects.all()
    supplier_count = len(suppliers) or 0
    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("action") == "delete":
            material_id = request.POST.get("material_id")
            delete_material(material_id)
            response['url'] = reverse('material_list')  # URL to direct is str
            print(response)
            return JsonResponse(response)
        else:
            if request.POST.get("supplier_data"):
                for supplier in json.loads(request.POST.get("supplier_data")):
                    print(supplier)
                    supplier_operations(supplier)
                response['url'] = reverse('create_material')  # URL to direct is str
                print(response)
                return JsonResponse(response)
            else:
                material_id = request.POST.get("material_id")
                material_name = request.POST.get("material_name")
                material_cost = request.POST.get("material_cost")
                material_type = request.POST.get("material_type")
                material_unit = request.POST.get("material_unit")
                supplier_id = request.POST.get("supplier")
                finish_data = json.loads(request.POST.get("finish_data", "[]"))  # Load finishes

                material = get_object_or_404(Material, material_id=material_id)
                material.material_name = material_name
                material.material_cost = material_cost
                material.material_type = material_type
                material.material_unit = material_unit
                material.supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
                material.save()

                MaterialFinish.objects.filter(material=material).delete()

                finish_data = json.loads(request.POST.get("finish_data"))
                if finish_data:
                    for finish in finish_data:
                        finish_name = finish["finish_name"]
                        finish_cost = finish["finish_cost"]
                        if finish_name != 'delete':
                            new_finish = MaterialFinish.objects.create(finish_name=finish_name, finish_cost=finish_cost, material=material)

                response['url'] = reverse('material_list')  # URL to direct is str
                return JsonResponse(response)
    return render(request, 'cpq_app/material_detail.html', {'material_object': material_object, 'finishes': finishes, 'suppliers': suppliers, 'supplier_count': supplier_count})

def create_material(request):
    suppliers = Supplier.objects.all()
    supplier_count = len(suppliers) or 0
    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("supplier_data"):
            for supplier in json.loads(request.POST.get("supplier_data")):
                print(supplier)
                supplier_operations(supplier)
            response['url'] = reverse('create_material')  # URL to direct is str
            print(response)
            return JsonResponse(response)
        else:
            material_name = request.POST.get("material_name")
            material_cost = request.POST.get("material_cost")
            material_type = request.POST.get("material_type")
            material_unit = request.POST.get("material_unit")
            supplier_id = request.POST.get("supplier")
            supplier = Supplier.objects.get(supplier_id=supplier_id)

            new_material = Material.objects.create(material_name=material_name, 
            material_cost=material_cost, 
            material_type=material_type, 
            material_unit=material_unit, 
            supplier=supplier)

            finish_data = json.loads(request.POST.get("finish_data"))
            if finish_data:
                for finish in finish_data:
                    finish_name = finish["finish_name"]
                    finish_cost = finish["finish_cost"]
                    if finish_name != 'delete':
                        new_finish = MaterialFinish.objects.create(finish_name=finish_name, finish_cost=finish_cost, material=new_material)

            response['url'] = reverse('material_list')  # URL to direct is str
            print(response)
            return JsonResponse(response)
    return render(request, 'cpq_app/create_material.html', {'suppliers': suppliers, 'supplier_count': supplier_count})

# quotation status tracking
def update_quotation_status(request, quotation_id, status):
    quotation = get_object_or_404(Quotation, pk=quotation_id)
    quotation.quotation_status = status
    quotation.save()
    return JsonResponse({"message": "Quotation status updated", "quotation_id": quotation_id, "status": status})

# misc for the faq and about
def faq(request):
    return render(request, 'cpq_app/faq.html')

def about(request):
    return render(request, 'cpq_app/about.html')