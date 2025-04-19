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
    print(request.POST)
    if request.method == "POST":
        response = {}
        response['status'] = True
        customer = get_object_or_404(Customer, customer_id=request.POST.get("customer_id"))
        project = request.POST.get("project")
        quotation = Quotation.objects.create(
            customer=customer,
            project=project,
            quotation_status='new',
            version_number=1,
            is_active_version=True
        )
        print(request.POST)

        for item in json.loads(request.POST.get('item_data')):
            product = Product.objects.get(product_id=item['product_id'])

            QuotationItem.objects.create(
                quotation=quotation,
                product=product,
                item_quantity=int(item['item_quantity']),
                product_margin=int(item['submit_margin']),
                product_labor=int(item['submit_labor']),
                item_height=float(item['item_height']),
                item_width=float(item['item_width']),
                glass_finish=item['glass_finish'],
                aluminum_finish=['aluminum_finish'],
                excluded_materials=item.get('excluded_materials', ''),
                additional_materials=''  # Or adjust if this is collected from frontend later
            )
        response['url'] = reverse('quotation_list')
        return JsonResponse(response)
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
            supplier_id = request.POST.get("supplier")
            supplier = Supplier.objects.get(supplier_id=supplier_id)

            product = Product.objects.get(product_id = product_id)
            product.product_name = product_name
            product.product_category = product_category
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
                    new_pm = ProductMaterial.objects.create(product=product, material=material, material_quantity=material_quantity, scale_ratio=0)

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
            supplier_id = request.POST.get("supplier")
            supplier = Supplier.objects.get(supplier_id=supplier_id)

            new_product = Product.objects.create(product_name=product_name, 
            product_category=product_category, 
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
                        new_pm = ProductMaterial.objects.create(product=new_product, material=material, material_quantity=material_quantity, scale_ratio=0)

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


def get_bill_of_materials(request): 
    product_id = request.GET.get("product_id")
    height = float(request.GET.get("item_height"))
    width = float(request.GET.get("item_width"))
    item_quantity = float(request.GET.get("item_quantity"))
    excluded_materials = request.GET.getlist("excluded_materials[]")
    glass_finish = request.GET.get("glass_finish", "")
    aluminum_finish = request.GET.get("aluminum_finish", "")
    product_margin = float(request.GET.get("quotation_margin"))
    labor_margin = float(request.GET.get("quotation_labor"))

    product = get_object_or_404(Product, product_id=product_id)
    materials = ProductMaterial.objects.filter(product=product)
    
    bom = []

    for m in materials:
        mat_id = str(m.material.material_id)
        if mat_id in excluded_materials:
            continue

        mat = m.material
        finish = ""
        unit_cost = 0.0

        if mat.material_type == "accessory":
            single_unit = 1
            unit_cost = float(mat.material_cost)
        else:
            finish_name = glass_finish if mat.material_type == "glass" else aluminum_finish
            finish_obj = MaterialFinish.objects.get(finish_name=finish_name, material=mat)
            unit_cost = float(finish_obj.finish_cost)
            finish = finish_name
            dimension = height if m.scale_by_height else width
            single_unit = dimension * float(m.scale_ratio)

        single_item_qty = single_unit * float(m.material_quantity)
        single_unit_cost = single_unit * unit_cost
        single_item_cost = single_item_qty * unit_cost
        total_unit_qty = single_item_qty * item_quantity
        total_cost = total_unit_qty * unit_cost

        bom.append({
            "material_id": mat.material_id,
            "material_name": mat.material_name,
            "quantity": f"{m.material_quantity:.2f}",
            "material_unit": mat.material_unit.lower(),
            "material_single_unit": single_unit,
            "material_single_item_quantity": f"{single_item_qty:.2f}",
            "material_single_unit_cost": f"{single_unit_cost:.2f}",
            "material_single_item_quantity_cost": f"{single_item_cost:.2f}",
            "material_unit_total_quantity": f"{total_unit_qty:.2f}",
            "material_total_cost": f"{total_cost:.2f}",
            "material_finish": finish,
            "material_type": mat.material_type,
        })

    # Aggregate materials
    aggregated_bom = defaultdict(lambda: {
        "material_name": "",
        "quantity": 0.0,
        "material_unit": "",
        "material_single_unit": [],
        "material_single_item_quantity": 0.0,
        "material_single_unit_cost": [],
        "material_single_item_quantity_cost": 0.0,
        "material_unit_total_quantity": 0.0,
        "material_total_cost": 0.0,
        "material_finish": "",
        "material_type": "",
    })

    for item in bom:
        mat_id = item["material_id"]
        agg = aggregated_bom[mat_id]
        agg["material_name"] = item["material_name"]
        agg["quantity"] += float(item["quantity"])
        agg["material_unit"] = item["material_unit"]
        agg["material_single_unit"].append(item["material_single_unit"])
        agg["material_single_item_quantity"] += float(item["material_single_item_quantity"])
        agg["material_single_unit_cost"].append(float(item["material_single_unit_cost"]))
        agg["material_single_item_quantity_cost"] += float(item["material_single_item_quantity_cost"])
        agg["material_unit_total_quantity"] += float(item["material_unit_total_quantity"])
        agg["material_total_cost"] += float(item["material_total_cost"])
        agg["material_finish"] = item["material_finish"]
        agg["material_type"] = item["material_type"]

    # Prepare sorted result
    result_bom = sorted([
        {
            "material_id": mat_id,
            "material_name": data["material_name"],
            "quantity": f"{data['quantity']:.2f}",
            "material_unit": data["material_unit"],
            "material_single_unit": [f"{x:.2f}" for x in set(data["material_single_unit"])],
            "material_single_item_quantity": f"{data['material_single_item_quantity']:.2f}",
            "material_single_unit_cost": [f"{x:.2f}" for x in set(data["material_single_unit_cost"])],
            "material_single_item_quantity_cost": f"{data['material_single_item_quantity_cost']:.2f}",
            "material_unit_total_quantity": f"{data['material_unit_total_quantity']:.2f}",
            "material_total_cost": f"{data['material_total_cost']:.2f}",
            "material_finish": data["material_finish"],
            "material_type": data["material_type"],
        }
        for mat_id, data in aggregated_bom.items()
    ], key=lambda x: x["material_name"])

    # Compute totals
    total_cost = sum(float(item["material_total_cost"]) for item in result_bom)
    per_item_cost = sum(float(item["material_single_item_quantity_cost"]) for item in result_bom)
    price_per_item = per_item_cost * (1 + (labor_margin + product_margin) / 100)
    total_price = price_per_item * item_quantity

    return JsonResponse({
        "product": product.product_name,
        "product_id": product.product_id,
        "bom": result_bom,
        "total_cost_of_materials": f"{total_cost:.2f}",
        "cost_of_materials_per_item": f"{per_item_cost:.2f}",
        "product_margin": product_margin,
        "labor_margin": labor_margin,
        "price_per_item": f"{price_per_item:.2f}",
        "total_price": f"{total_price:.2f}",
        "item_quantity": item_quantity,
        "item_id": request.GET.get('item_id'),
    })



def get_total_bom(request):
    grand_bom = defaultdict(lambda: {
        "material_name": "",
        "quantity": 0.0,
        "material_unit": "",
        "material_single_unit": [],
        "material_single_item_quantity": 0.0,
        "material_single_unit_cost": [],
        "material_single_item_quantity_cost": 0.0,
        "material_unit_total_quantity": 0.0,
        "material_total_cost": 0.0,
        "material_finish": "",
        "material_type": "",
    })

    total_cost_of_materials = 0
    cost_of_materials_per_item = 0
    total_price = 0
    total_quantity = 0
    last_product_id = None
    last_margin = 0
    last_labor = 0
    data = json.loads(request.POST.get("submit_data", "[]"))
    total_item_quantity = 0
    for item in data:
        product_id = item["product_id"]
        height = float(item["item_height"])
        width = float(item["item_width"])
        item_quantity = float(item["item_quantity"])
        excluded_materials = item.get("excluded_materials", [])
        glass_finish = item.get("glass_finish", "")
        aluminum_finish = item.get("aluminum_finish", "")
        product_margin = float(item.get("submit_margin", 0))
        labor_margin = float(item.get("submit_labor", 0))

        product = get_object_or_404(Product, product_id=product_id)
        materials = ProductMaterial.objects.filter(product=product)

        for material in materials:
            if str(material.material.material_id) in excluded_materials:
                continue

            material_quantity = float(material.material_quantity)
            scale_by_height = material.scale_by_height
            scale_by_width = material.scale_by_width
            scale_ratio = float(material.scale_ratio)
            material_obj = material.material
            material_type = material_obj.material_type

            # Determine cost and quantity
            if material_type == "accessory":
                material_finish = ""
                cost = float(material_obj.material_cost)
                material_single_unit = 1
            else:
                material_finish = glass_finish if material_type == "glass" else aluminum_finish
                finish_object = MaterialFinish.objects.get(finish_name=material_finish, material=material_obj)
                cost = float(finish_object.finish_cost)
                material_single_unit = height * scale_ratio if scale_by_height else width * scale_ratio

            material_single_item_quantity = material_quantity * material_single_unit
            material_single_unit_cost = material_single_unit * cost
            material_single_item_quantity_cost = material_single_item_quantity * cost
            material_unit_total_quantity = material_single_item_quantity * item_quantity
            material_total_cost = material_unit_total_quantity * cost

            # Composite key: material_id + material_finish
            mat_key = (material_obj.material_id, material_finish)
            bom_entry = grand_bom[mat_key]
            bom_entry["material_name"] = material_obj.material_name
            bom_entry["material_unit"] = material_obj.material_unit.lower()
            bom_entry["material_finish"] = material_finish
            bom_entry["material_type"] = material_type
            bom_entry["quantity"] += material_quantity
            bom_entry["material_single_unit"].append(material_single_unit)
            bom_entry["material_single_item_quantity"] += material_single_item_quantity
            bom_entry["material_single_unit_cost"].append(material_single_unit_cost)
            bom_entry["material_single_item_quantity_cost"] += material_single_item_quantity_cost
            bom_entry["material_unit_total_quantity"] += material_unit_total_quantity
            bom_entry["material_total_cost"] += material_total_cost

        # Recalculate total costs only for non-excluded materials
        for material in materials:
            if str(material.material.material_id) in excluded_materials:
                continue
            material_quantity = float(material.material_quantity)
            scale_ratio = float(material.scale_ratio)
            scale_by_height = material.scale_by_height
            scale_by_width = material.scale_by_width
            material_obj = material.material
            material_type = material_obj.material_type

            if material_type == "accessory":
                cost = float(material_obj.material_cost)
                single_unit = 1
            else:
                finish_name = glass_finish if material_type == "glass" else aluminum_finish
                finish_object = MaterialFinish.objects.get(finish_name=finish_name, material=material_obj)
                cost = float(finish_object.finish_cost)
                single_unit = height * scale_ratio if scale_by_height else width * scale_ratio

            cost_of_materials_per_item += material_quantity * cost * single_unit
            total_cost_of_materials += material_quantity * single_unit * item_quantity * cost

        result_bom = sorted([
            {
                "material_id": mat_key[0],
                "material_finish": mat_key[1],
                "material_name": values["material_name"],
                "quantity": f"{values['quantity']:.2f}",
                "material_unit": values["material_unit"],
                "material_single_unit": [f"{x:.2f}" for x in set(values["material_single_unit"])],
                "material_single_item_quantity": f"{values['material_single_item_quantity']:.2f}",
                "material_single_unit_cost": [f"{x:.2f}" for x in set(values["material_single_unit_cost"])],
                "material_single_item_quantity_cost": f"{values['material_single_item_quantity_cost']:.2f}",
                "material_unit_total_quantity": f"{values['material_unit_total_quantity']:.2f}",
                "material_total_cost": f"{values['material_total_cost']:.2f}",
                "material_type": values["material_type"],
            }
            for mat_key, values in grand_bom.items()
        ], key=lambda x: x["material_name"])
        total_item_quantity+= item_quantity
    
    total_cost = sum(float(item["material_total_cost"]) for item in result_bom)
    total_price = total_cost * (1 + (labor_margin + product_margin) / 100)

    response_data = {
        "bom": result_bom,
        "total_cost_of_materials": f"{total_cost:.2f}",
        "product_margin": product_margin,
        "labor_margin": labor_margin,
        "total_price": f"{total_price:.2f}",
        "item_quantity": total_item_quantity,
    }

    return JsonResponse(response_data)

# misc for the faq and about
def faq(request):
    return render(request, 'cpq_app/faq.html')

def about(request):
    return render(request, 'cpq_app/about.html')
