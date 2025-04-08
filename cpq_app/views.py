from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from collections import defaultdict

# Change welcome message later or remove if not needed
def index(request):
    return JsonResponse({"message": "Welcome Bitch!"})

# quotation views
def quotation_list(request):
    quotations = list(Quotation.objects.values())
    return render(request, 'cpq_app/quotation_list.html', {"quotations": quotations})

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
    customers = Customer.objects.all()
    suppliers = Supplier.objects.all()

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
    return render(request, 'cpq_app/create_quotation.html', {'customers': customers, 'suppliers': suppliers})

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
    customers = Customer.objects.all()

    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("action") == "delete":
            customer_id = request.POST.get("customer_id")
            delete_customer(request)
            response['url'] = reverse('customer_list') 
            print(response)
            return JsonResponse(response)
    return render(request, 'cpq_app/customer_list.html', {"customers": customers})

def customer_detail(request, customer_id):
    customer_object = get_object_or_404(Customer, customer_id=customer_id)

    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        if request.POST.get("action") == "delete":
            customer_id = request.POST.get("customer_id")
            delete_customer(customer_id) # customer_id works here for some reason instead of request
            response['url'] = reverse('customer_list') 
            print(response)
            return JsonResponse(response)
        
        else:
            customer_id = request.POST.get("customer_id")
            customer_name = request.POST.get("customer_name")
            customer_address = request.POST.get("customer_address")
            customer_mobile = request.POST.get("customer_mobile")
            customer_email = request.POST.get("customer_email")

            customer = get_object_or_404(Customer, customer_id=customer_id)
            customer.customer_name = customer_name
            customer.customer_address = customer_address
            customer.customer_mobile = customer_mobile
            customer.customer_email = customer_email
            customer.save()

            response['url'] = reverse('customer_list')
            return JsonResponse(response)
    return render(request, 'cpq_app/customer_detail.html', {'customer_object': customer_object})

def add_customer(request):
    customers = Customer.objects.all()

    if request.method == "POST":
        response = {}
        response['status'] = True
        print(request.POST)

        customer_name = request.POST.get("customer_name")
        customer_address = request.POST.get("customer_address")
        customer_mobile = request.POST.get("customer_mobile")
        customer_email = request.POST.get("customer_email")

        if Customer.objects.filter(customer_email=customer_email).exists():
            return JsonResponse({"status": False, "error": "Customer with this email already exists."}, status=400)
            
        new_customer = Customer.objects.create(customer_name=customer_name,
        customer_address=customer_address,
        customer_mobile=customer_mobile,
        customer_email=customer_email)

        response['url'] = reverse('customer_list')
        print(response)
        return JsonResponse(response)
    return render(request, 'cpq_app/add_customer.html', {'customers': customers})

def delete_customer(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        customer_object = get_object_or_404(Customer, customer_id=customer_id)
        customer_object.delete()
        return JsonResponse({"status": True, "message": "Customer deleted successfully."})
    return JsonResponse({"status": False, "message": "Invalid Request"}, status=400)

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
    product_material_object = ProductMaterial.objects.filter(product=product_object)
    suppliers = Supplier.objects.all()
    supplier_count = len(suppliers) or 0
    material_data_by_suppliers = get_material_data_by_suppliers(suppliers)
    selected_supplier_data = get_material_data_by_suppliers(suppliers, supplier_id=product_object.supplier.supplier_id)
    
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

            product = Product.objects.get(product_id = product_id)
            product.product_name = product_name
            product.product_category = product_category
            product.product_margin = product_margin
            product.product_labor = product_labor
            product.supplier = supplier
            
            product.save()

            pm_data = json.loads(request.POST.get("pm_data"))
            
            ProductMaterial.objects.filter(product=product).delete()
            for pm in pm_data:
                material_id = pm["material_id"]
                material_quantity = pm["material_quantity"]
                material_scale = pm["material_scale"]
                scale_ratio = pm["scale_ratio"]

                print(scale_ratio)

                material = get_object_or_404(Material, material_id=material_id)

                if material_scale == 'by_height':
                    new_pm = ProductMaterial.objects.create(product=product, material=material, material_quantity=material_quantity, scale_by_height=True, scale_ratio=scale_ratio)
                elif material_scale == "by_width":
                    new_pm = ProductMaterial.objects.create(product=product, material=material, material_quantity=material_quantity, scale_by_width=True, scale_ratio=scale_ratio)
                else:
                    new_pm = ProductMaterial.objects.create(product=product, material=material, material_quantity=material_quantity)

                print(new_pm)

            response['url'] = reverse('product_list')
            print(response)
            return JsonResponse(response)
    return render(request, 'cpq_app/product_detail.html', {'product': product_object, 'product_materials': product_material_object, 'material_data': material_data_by_suppliers, 'suppliers': suppliers, 'supplier_count': supplier_count, 'selected_supplier_pm_data': selected_supplier_data})

def create_product(request):
    materials = Material.objects.all()
    suppliers = Supplier.objects.all()

    material_data_by_suppliers = get_material_data_by_suppliers(suppliers)

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
                    material_quantity = pm["material_quantity"]
                    material_scale = pm["material_scale"]
                    scale_ratio = pm["scale_ratio"]

                    material = get_object_or_404(Material, material_id=material_id)

                    if material_scale == 'by_height':
                        new_pm = ProductMaterial.objects.create(product=new_product, material=material, material_quantity=material_quantity, scale_by_height=True, scale_ratio=scale_ratio)
                    elif material_scale == "by_width":
                        new_pm = ProductMaterial.objects.create(product=new_product, material=material, material_quantity=material_quantity, scale_by_width=True, scale_ratio=scale_ratio)
                    else:
                        new_pm = ProductMaterial.objects.create(product=new_product, material=material, material_quantity=material_quantity)

                    print(new_pm)

            response['url'] = reverse('product_list')
            print(response)
            return JsonResponse(response)
    return render(request, 'cpq_app/create_product.html', {"materials": materials, "suppliers": suppliers, "material_data": material_data_by_suppliers})

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
                material_cost = request.POST.get("material_cost") or 0
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
            material_cost = request.POST.get("material_cost") or 0
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

def get_material_data_by_suppliers(suppliers, supplier_id = None):
    if supplier_id:
        supplier = Supplier.objects.get(supplier_id=supplier_id)
        material_data_by_suppliers = {
            "supplier_id": supplier.supplier_id,
            "supplier_name": supplier.supplier_name,
            "materials": []
        }
        supplier_materials = supplier.material_set.all()
        for material in supplier_materials:
            temp_material = {
                "material_id": material.material_id,
                "material_name": material.material_name,
                "material_type": material.material_type,
                "material_unit": material.material_unit,
                "material_cost": material.material_cost,
                "material_finishes": [],
            }
            finishes = material.materialfinish_set.all()
            for finish in finishes:
                temp_material["material_finishes"].append({
                    "finish_id": finish.finish_id,
                    "finish_name": finish.finish_name,
                    "finish_cost": finish.finish_cost,
                })
            material_data_by_suppliers["materials"].append(temp_material)
    else:
        material_data_by_suppliers = []
        for supplier in suppliers:
            temp_supplier = {
                "supplier_id": supplier.supplier_id,
                "supplier_name": supplier.supplier_name,
                "accessories": [],
                "glass": [],
                "aluminum": [],
            }

            supplier_materials = supplier.material_set.all()
            for material in supplier_materials:
                temp_material = {
                    "material_id": material.material_id,
                    "material_name": material.material_name,
                    "material_type": material.material_type,
                    "material_unit": material.material_unit,
                    "material_cost": material.material_cost,
                    "material_finishes": [],
                }

                finishes = material.materialfinish_set.all()
                for finish in finishes:
                    temp_material["material_finishes"].append({
                        "finish_id": finish.finish_id,
                        "finish_name": finish.finish_name,
                        "finish_cost": finish.finish_cost,
                    })

                # Categorize based on material_type
                if material.material_type == "accessory":
                    temp_supplier["accessories"].append(temp_material)
                elif material.material_type == "glass":
                    temp_supplier["glass"].append(temp_material)
                elif material.material_type == "aluminum":
                    temp_supplier["aluminum"].append(temp_material)
            material_data_by_suppliers.append(temp_supplier)

    print(material_data_by_suppliers)
    return material_data_by_suppliers

def get_products(request):
    supplier_id = request.GET.get("supplier_id")  # Get supplier ID from AJAX request
    if supplier_id:
        supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
        products = supplier.product_set.values("product_id", "product_name")  # Get product IDs and names
        print(list(products))
        return JsonResponse({"products": list(products)})  # Return JSON response
    return JsonResponse({"error": "Invalid request"}, status=400)

def delete_material(material_id):
    material_object = Material.objects.get(material_id=material_id)
    material_object.delete()

# quotation status tracking
def update_quotation_status(request, quotation_id, status):
    quotation = get_object_or_404(Quotation, pk=quotation_id)
    quotation.quotation_status = status
    quotation.save()
    return JsonResponse({"message": "Quotation status updated", "quotation_id": quotation_id, "status": status})

def get_customer(request):
    customer_id = request.GET.get('customer_id') 
    if customer_id:
        customer = get_object_or_404(Customer, customer_id=customer_id)  
        data = {
            "address": customer.customer_address,
            "mobile": customer.customer_mobile,
            "email": customer.customer_email
        }
        return JsonResponse(data) 
    return JsonResponse({"error": "Invalid request"}, status=400) 

def calculate_product_cost(request, product_id, width, height, quantity):
    pass

# BoM breakdown
def get_bill_of_materials(request): # need to add finishes here
    product_id = request.GET.get("product_id")
    height = float(request.GET.get("item_height"))
    width = float(request.GET.get("item_width"))
    item_quantity = float(request.GET.get("item_quantity"))

    print(request.GET)

    product = get_object_or_404(Product, product_id=product_id)
    materials = ProductMaterial.objects.filter(product = product)
    print(ProductMaterial.objects.all())
    bom = []
    for material in materials:
        material_quantity = float(material.material_quantity)
        scale_by_height = material.scale_by_height
        scale_by_width = material.scale_by_width
        scale_ratio = float(material.scale_ratio)
        material_type = material.material.material_type


        if material_type == "Accessory":
            material_single_unit = 1
            material_single_item_quantity = material_single_unit*material_quantity
            material_single_unit_cost = material.material.material_cost
            material_single_item_quantity_cost = material_single_item_quantity*material_single_unit_cost
            material_unit_total_quantity = material_single_item_quantity*item_quantity
            material_total_cost = material_unit_total_quantity*cost
            
        else:
            material_finish = request.GET.get("material_finish")
            material_obj = material.material
            
            finish = MaterialFinish.objects.get(finish_name="Mill-Finish", material=material_obj)
            if not material_finish:
                cost = float(finish.finish_cost)
                if scale_by_height:
                    material_single_unit = height*scale_ratio
                else:
                    material_single_unit = width*scale_ratio
                material_single_item_quantity = material_quantity*material_single_unit

                material_single_unit_cost = material_single_unit*cost
                material_single_item_quantity_cost = material_single_item_quantity*cost

                material_unit_total_quantity = material_single_item_quantity*item_quantity
                material_total_cost = material_unit_total_quantity*cost
            else:
                pass


        bom.append({
        "material_id": material.material.material_id,
        "material_name": material.material.material_name,
        "quantity": material.material_quantity,
        "material_single_unit": material_single_unit,
        "material_single_item_quantity": material_single_item_quantity,
        "material_single_unit_cost": material_single_unit_cost,
        "material_single_item_quantity_cost": material_single_item_quantity_cost,
        "material_unit_total_quantity": material_unit_total_quantity,
        "material_total_cost": material_total_cost,
        })
        
    return JsonResponse({"product": product.product_name, "bom": bom})
# misc for the faq and about
def faq(request):
    return render(request, 'cpq_app/faq.html')

def about(request):
    return render(request, 'cpq_app/about.html')
