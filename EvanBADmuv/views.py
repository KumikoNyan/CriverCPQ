from django.shortcuts import render, redirect, get_object_or_404
from .models import User, SARF, Scholar, EnlistedSHO
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.models import Group, Permission
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.http import HttpResponse
from django.http import Http404
from .resources import *
from tablib import Dataset
import csv,io


# Debug account creation (was used before oaa_manage_users and oaa_manage_users2 existed)
def sign_up(request):
    if request.method == "POST":
        NAME = request.POST.get('name')
        PASSWORD = request.POST.get('password')
        USER_TYPE = request.POST.get('user_type')

        user = User.objects.create_user(username=NAME, password=PASSWORD)
        user.user_type = USER_TYPE
        user.save()

        print("Username: ", user.username)
        print("Password: ", user.password)
        print("User Type: ", user.user_type)

        # If the user type is "Scholar", create a Scholar instance
        if user.user_type == 'Scholar':
            scholar = Scholar.objects.create(
                id_number=user,
                
                first_name='',  # Add required scholar details here
                last_name='',
                email='',
                phone_number='',
                year=0,
                required_service_hours=0,
                total_required_service_hours=0,
                service_hours_status='Incomplete'
            )
            scholar.save()

        return redirect('login')
    
    else:  
        return render(request, 'SHIMS_System/sign_up.html')

# Login and Authentication of users
def login(request):
    if request.method == "POST":
        username = request.POST.get('name')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        print("Username: ", username)
        print("Password: ", password)
        print("User Type: ", user_type)
        # Authenticate user
        user = authenticate(request, username=username, password=password, user_type=user_type)
        print("Authenticated User: ", user)
        if user is not None:
            # Log the user in
            auth_login(request, user)
            # Redirect to the appropriate page based on user_type
            if user.user_type == 'Offices/Departments':
                # Get the group 'Offices/Departments'
                officeDepartmentsGroup = Group.objects.get(name='Offices/Departments')

                # Get the 'add_sarf' permission
                create_sarf_permission = Permission.objects.get(codename='add_sarf')
                # Get the 'view_sarf' permission
                view_sarf_permission = Permission.objects.get(codename='view_sarf')
                # Add 'view_sarf' permission to the group
                officeDepartmentsGroup.permissions.add(view_sarf_permission)
                # Add 'add_sarf' permission to the group
                officeDepartmentsGroup.permissions.add(create_sarf_permission)
                # Add the user to the group
                user.groups.add(officeDepartmentsGroup)

                return redirect('rform', pk=user.pk)
            
            elif user.user_type == 'OAA':
                OAAGroup = Group.objects.get(name='OAA')
                change_sarf_permission = Permission.objects.get(codename='change_sarf')
                view_sarf_permission = Permission.objects.get(codename='view_sarf')
                OAAGroup.permissions.add(view_sarf_permission)
                OAAGroup.permissions.add(change_sarf_permission)
                user.groups.add(OAAGroup)
                return redirect('oaa_rformtable', pk=user.pk)
            
            elif user.user_type == 'Scholar':
                scholarGroup = Group.objects.get(name='Scholar')
                view_sarf_permission = Permission.objects.get(codename='view_sarf')
                scholarGroup.permissions.add(view_sarf_permission)
                user.groups.add(scholarGroup)
                return redirect('scholar', pk=user.pk)
            
        else:
            # Invalid login credentials
            error_message = "Invalid username or password."
            return render(request, 'SHIMS_System/login.html', {'error_message': error_message})
    else:
        # GET request, render login form
        return render(request, 'SHIMS_System/login.html')

# Scholar Assistance Request Form (SARF) submission page
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.add_sarf')
def rform(request, pk):
    e = get_object_or_404(User, pk=pk)
    sarf = SARF.objects.all()
    return render(request, 'SHIMS_System/rform.html', {'sarf': sarf, 'e': e})

# Shows the Offices/Departments all Scholar Assistance Requests that they have submitted.
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.add_sarf')
def rformtable(request, pk):
    e = get_object_or_404(User, pk=pk)
    sarf = SARF.objects.filter(owner=e)
    return render(request, 'SHIMS_System/rformtable.html', {'sarf': sarf, 'e': e})

# The function that creates the SARF.
@login_required
@permission_required('SHIMS_System.add_sarf')
def create_Request(request, pk):
    e = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        NAME = request.POST.get('name')
        EMAIL = request.POST.get('email')
        TN = request.POST.get('tn')
        TD = request.POST.get('td')
        TM = request.POST.get('tm')
        ST = request.POST.get('st')
        DATE = request.POST.get('date')
        LOC = request.POST.get('loc')
        START_TIME = request.POST.get('start_time')
        END_TIME = request.POST.get('end_time')
        DURATION = request.POST.get('duration')
        SKILL = request.POST.get('skill')
        SL = request.POST.get('sl')
        SCHOLARS = request.POST.get('scholars')


        # Parse start_time and end_time strings to datetime.time objects
        start_time_obj = datetime.strptime(START_TIME, '%H:%M').time()
        end_time_obj = datetime.strptime(END_TIME, '%H:%M').time()

        # Calculate required_hours
        start_datetime = datetime.combine(datetime.now().date(), start_time_obj)
        end_datetime = datetime.combine(datetime.now().date(), end_time_obj)

        # Make sure end_time is greater than start_time
        if end_datetime < start_datetime:
            # If end_time is before start_time, assume it's on the next day
            end_datetime += timedelta(days=1)

        required_hours = (end_datetime - start_datetime).total_seconds() / 3600  # Convert to hours

        # Create SARF object with calculated required_hours
        SARF.objects.create(owner=e, name=NAME, email=EMAIL, task_name=TN, task_description=TD,
                            task_mode=TM, service_type=ST, date=DATE, location=LOC, start_time=start_time_obj,
                            end_time=end_time_obj, required_hours=required_hours,
                            duration=DURATION, skills=SKILL, signup_link=SL, scholars_needed=SCHOLARS)
        return redirect('create_Request', pk=pk)
    else:  
        sarf = SARF.objects.all()
        return render(request, 'SHIMS_System/rform.html', {'sarf': sarf, 'e': e})

# Overview for scholar user to view their relevant statistics and enlisted opportunities.
@login_required
@permission_required('SHIMS_System.view_sarf')
def scholar_breakdown(request, pk):
    e = get_object_or_404(User, pk=pk)
    # Fetch the related Scholar instance
    scholar_instance = get_object_or_404(Scholar, id_number=e)
    # Filter EnlistedSHO objects based on the related Scholar instance
    f = EnlistedSHO.objects.filter(scholar=scholar_instance)
    return render(request, 'SHIMS_System/scholar_breakdown.html', {'scholar': scholar_instance, 'e': e, 'f':f})

# The scholar's home page. Shows all of the posted approved Service Hour Opportunities (SHOs).
@login_required
@permission_required('SHIMS_System.view_sarf')
def scholar(request, pk):
    e = get_object_or_404(User, pk=pk)
    sarf = SARF.objects.filter(status="Approved")
    return render(request, 'SHIMS_System/scholar_opportunities.html', {'sarf': sarf, 'e': e})


# Scholar user can update their own information.
@login_required
@permission_required('SHIMS_System.view_sarf')
def scholar_update_details(request, pk):
    e = get_object_or_404(User, pk=pk)
    scholar_instance = Scholar.objects.get(id_number=e)

    return render(request, 'SHIMS_System/scholar_update_details.html', {'e': e})

# Scholar user can update their own information (2).
@login_required
def update_contact_details(request, pk):
    e = get_object_or_404(User, pk=pk)
    scholar_instance = Scholar.objects.get(id_number=e)
    
    if request.method == 'POST':
        # Retrieve updated contact details from the form
        email = request.POST.get('email')
        phone_number = request.POST.get('phone-number')

        # Update the scholar's contact details
        scholar_instance.email = email
        scholar_instance.phone_number = phone_number
        scholar_instance.save()

        # Redirect to a success page or render a confirmation message
        # For example, you could redirect to the profile page
        return redirect('scholar_update_details', pk=e.pk)

    return render(request, 'SHIMS_System/scholar_update_details.html', {'e': e})

# Scholar user can update their own information (3).
@login_required
def change_password(request, pk):
    e = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        # Retrieve new password from the form
        new_password = request.POST.get('new-password')

        # Change the user's password
        e.set_password(new_password)
        e.save()

        # Redirect to a success page or render a confirmation message
        # For example, you could redirect to the login page
        logout(request)
        return redirect('login')

    return render(request, 'SHIMS_System/scholar_update_details.html', {'e': e})


# Scholar can view more details about specific opportunities here.
@login_required
@permission_required('SHIMS_System.view_sarf')
def scholar_opp_details(request, pk, pk2):
    e = get_object_or_404(User, pk=pk)
    d = get_object_or_404(SARF, pk=pk2)
    scholar_instance = Scholar.objects.get(id_number=e)
    already_enlisted = EnlistedSHO.objects.filter(sarf=d, scholar__id_number=e).exists()
    
    if request.method == 'POST':
        status = request.POST.get('status')
        action = request.POST.get('action')
        if status == 'enlisted':
            if not already_enlisted and d.scholars_needed > 0:
                d.scholars_needed -= 1
                EnlistedSHO.objects.create(
                    scholar=scholar_instance,
                    sarf=d,
                )

        elif status == 'delisted':
            if already_enlisted:
                d.scholars_needed += 1
                EnlistedSHO.objects.filter(sarf=d, scholar=e.scholar).delete()

        # Save the SARF instance after all modifications
        d.save()
        
        return redirect('scholar', pk=e.pk)
    
    return render(request, 'SHIMS_System/scholar_opp_details.html', {'d': d, 'e': e})

# OAA can see all posted SARFs here.
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_rformtable(request, pk):
    e = get_object_or_404(User, pk=pk)
    sarf = SARF.objects.all()
    return render(request, 'SHIMS_System/oaa_rformtable.html', {'sarf': sarf, 'e': e})

# OAA can see all posted SARFs here.
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_opp_details(request, pk, pk2):
    sarf = get_object_or_404(SARF, pk=pk2)
    e = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status == 'approved':
            sarf.status = 'Approved'
        elif status == 'rejected':
            sarf.status = 'Rejected'
        sarf.save()
        return redirect('oaa_rformtable', pk=e.pk)
    
    return render(request, 'SHIMS_System/oaa_opp_details.html', {'sarf': sarf, 'e': e, 'd': sarf, 'user_pk': pk})

# OAA accounts creation page.
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_manage_users(request, pk):
    e = get_object_or_404(User, pk=pk)
    return render(request, 'SHIMS_System/oaa_manage_users.html', {'e': e})

@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_office_user(request, pk):
    e = get_object_or_404(User, pk=pk)
    # Filter users based on user_type 'Offices/Departments'
    users = User.objects.filter(user_type='Offices/Departments')
    return render(request, 'SHIMS_System/oaa_office_user.html', {'e': e, 'users': users})

#OAA CREATION OF OFFICE ACCOUNTS
# OAA can create Scholar accounts.
def oaa_create_office(request, pk):
    e = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        USERNAME = request.POST.get('username')
        PASSWORD = request.POST.get('password')

        user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        user.user_type = 'Offices/Departments'
        user.save()

        # Redirect to the same page after form submission
        return redirect('oaa_office_user', pk=pk)

    return render(request, 'SHIMS_System/oaa_office_user.html', {'e': e})

# OAA DELETION OF OFFICE ACCOUNTS
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_delete_office(request, pk):
    e = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        DELUSERNAME = request.POST.get('username-delete')  # Retrieving DELUSERNAME from the form
        try:
            user = User.objects.get(username=DELUSERNAME)  # Trying to retrieve the user with this username
            user.delete()  # Deleting the user
        except User.DoesNotExist:
            raise Http404("User does not exist")

        # Redirect to the same page after form submission
        return redirect('oaa_office_user', pk=pk)

    return render(request, 'SHIMS_System/oaa_office_user.html', {'e': e})

# OAA can create Scholar accounts.
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_create_scholar(request, pk):
    e = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        ID_NUM = request.POST.get('id-number')
        FIRST_NAME = request.POST.get('first_name')
        LAST_NAME = request.POST.get('last_name')
        EMAIL = request.POST.get('email')
        PHONE_NUMBER = request.POST.get('phone_number')
        YEAR = int(request.POST.get('year'))  # Convert year to int
        TERM = request.POST.get('term', 'Intersession')  # Default term to 'Intersession'

        if TERM == 'Intersession':
            if YEAR in [1, 2, 3]:
                required_service_hours = 3
            else:
                required_service_hours = 3  # Set to default value if year is not in [1, 2, 3]
        elif TERM == 'Semester':
            if YEAR in [1, 2, 3]:
                required_service_hours = 10
            else:
                required_service_hours = 5

        user = User.objects.create_user(username=ID_NUM, password=ID_NUM)
        user.user_type = 'Scholar'
        user.save()

        scholar = Scholar.objects.create(
                id_number=user,
                first_name=FIRST_NAME,  # Add required scholar details here
                last_name=LAST_NAME,
                email=EMAIL,
                phone_number=PHONE_NUMBER,
                year=YEAR,
                required_service_hours=required_service_hours,
                service_hours_status='Incomplete',
                term=TERM,  # Set the term
                total_required_service_hours = required_service_hours

            )
        scholar.save()
    return render(request, 'SHIMS_System/oaa_manage_users.html', {'e': e})


@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_delete_scholar(request, pk):
    e = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        DELUSERNAME = request.POST.get('username-delete')  # Retrieving DELUSERNAME from the form
        try:
            user = User.objects.get(username=DELUSERNAME)  # Trying to retrieve the user with this username
            user.delete()  # Deleting the user
        except User.DoesNotExist:
            raise Http404("User does not exist")

        # Redirect to the same page after form submission
        return redirect('oaa_manage_users', pk=pk)

    return render(request, 'SHIMS_System/oaa_manage_users.html', {'e': e})

# OAA can create Offices/Departments accounts.
@login_required
@permission_required('SHIMS_System.view_sarf')
@permission_required('SHIMS_System.change_sarf')
def oaa_manage_users2(request, pk):
    e = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        NAME = request.POST.get('name')
        PASSWORD = request.POST.get('password')

        user = User.objects.create_user(username=NAME, password=PASSWORD)
        user.user_type = 'Offices/Departments'
        user.save()

    return render(request, 'SHIMS_System/oaa_manage_users2.html', {'e': e})

# OAA can view more details about a specific Service Hour Opportunity.
@login_required
@permission_required('SHIMS_System.view_sarf')
def opp_details(request, pk, pk2):
    sarf = get_object_or_404(SARF, pk=pk2)
    e = get_object_or_404(User, pk=pk)
    d = get_object_or_404(SARF, pk=pk2)
    return render(request, 'SHIMS_System/opp_details.html', {'sarf': sarf, 'e': e, 'd': d})

# Offices/Departments users can view which scholars enlisted for their approved SHOs.
@login_required
@permission_required('SHIMS_System.view_sarf')
def enlisted_scholars_table(request, pk, pk2, pk3):
    e = get_object_or_404(User, pk=pk)
    d = get_object_or_404(SARF, pk=pk2)
    sarf = get_object_or_404(SARF, pk=pk3)
    enlisted_scholars = EnlistedSHO.objects.filter(sarf=sarf)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_service_hours = int(request.POST.get('service_hours'))

        # Retrieve the EnlistedSHO instance using the user PK
        enlisted_sho_instance = EnlistedSHO.objects.get(scholar__id_number=user_id, sarf=sarf)
        scholar_instance = Scholar.objects.get(id_number_id=user_id)

        # Update the hours_completed and the enlisted_status
        enlisted_sho_instance.hours_completed = new_service_hours
        enlisted_sho_instance.enlisted_status = "Encoded"
        enlisted_sho_instance.save()

        # Recalculate total_rendered_service_hours of the scholar_instance
        total_rendered_service_hours = EnlistedSHO.objects.filter(scholar=scholar_instance).aggregate(
            total_hours_completed=Sum('hours_completed')
        )['total_hours_completed'] or 0

        scholar_instance.total_rendered_service_hours = total_rendered_service_hours
        scholar_instance.total_required_service_hours-= scholar_instance.total_rendered_service_hours
        scholar_instance.save()

        return JsonResponse({'message': 'Data saved successfully.'})

    return render(request, 'SHIMS_System/enlisted_scholars_table.html', {'sarf': sarf, 'enlisted_scholars': enlisted_scholars, 'e': e, 'd': d})


# Offices/Departments user can manually add a scholar to the SHO.
@login_required
@permission_required('SHIMS_System.view_sarf')
def add_scholar(request, pk, pk2, pk3):
    e = get_object_or_404(User, pk=pk)
    d = get_object_or_404(SARF, pk=pk2)
    sarf = get_object_or_404(SARF, pk=pk3)
    enlisted_scholars = EnlistedSHO.objects.filter(sarf=sarf)

    if request.method == 'POST':
        scholar_id = request.POST.get('scholarId')
        service_hours = request.POST.get('serviceHours')

        # Retrieve user and scholar instances
        user_instance = get_object_or_404(User, username=scholar_id)
        scholar = get_object_or_404(Scholar, id_number=user_instance)

        # Create EnlistedSHO instance
        EnlistedSHO.objects.create(
            sarf=sarf,
            scholar=scholar,
            hours_completed=service_hours
        )

    return render(request, 'SHIMS_System/enlisted_scholars_table.html', {'sarf': sarf, 'enlisted_scholars': enlisted_scholars, 'e': e, 'd': d})

# OAA can view all scholars and details, including service hours status.
@login_required
@permission_required('SHIMS_System.view_sarf')
def oaa_scholar_status(request, pk):
    e = get_object_or_404(User, pk=pk)
    scholars = Scholar.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        penalty_service_hours = int(request.POST.get('penalty_service_hours'))
        rendered_service_hours = int(request.POST.get('rendered_service_hours'))

        # Retrieve the Scholar instance using the user PK
      
        scholar_instance = Scholar.objects.get(id_number_id=user_id)


        #Update the penalty service hours and rendered service hours of the scholar instance
        scholar_instance.total_rendered_service_hours= rendered_service_hours
        scholar_instance.penalty_service_hours= penalty_service_hours
        scholar_instance.total_required_service_hours= scholar_instance.penalty_service_hours + scholar_instance.required_service_hours-scholar_instance.total_rendered_service_hours
        scholar_instance.save()
        

        return JsonResponse({'message': 'Data saved successfully.'})
    
    for scholar_instance in scholars:
            if scholar_instance.total_required_service_hours <= 0:
                scholar_instance.service_hours_status = "Complete"
            else:
                scholar_instance.service_hours_status = "Incomplete"
            scholar_instance.save()

    return render(request, 'SHIMS_System/oaa_scholar_status.html', {'e': e, 'scholars': scholars})

@login_required
@permission_required('SHIMS_System.view_sarf')
def oaa_upkeep(request, pk):
    e = get_object_or_404(User, pk=pk)
    scholars = Scholar.objects.all()

    for scholar in scholars:
        # Perform the upkeep operations based on the term
        term = scholar.term.lower()
        print(f"Performing upkeep for scholar {scholar.id_number.username} ({scholar.term}):")
        if term == '1st semester':
            perform_2ndsemester_upkeep(scholar)
        elif term == '2nd semester':
            perform_intersession_upkeep(scholar)
        elif term == 'intersession':
            perform_1stsemester_upkeep(scholar)
        

    # Redirect to the scholar status page
    return redirect('oaa_scholar_status', pk=e.pk)

def perform_1stsemester_upkeep(scholar):
    print("Performing 1st semester upkeep...")
    pastTotal=scholar.total_required_service_hours

    scholar.total_rendered_service_hours=0

    if scholar.year in [1, 2, 3]:
        required_service_hours = 10
    else:
        required_service_hours = 5

    scholar.required_service_hours = required_service_hours
    
    # Check if total required hours are met
    if scholar.year > 0:
        if scholar.total_required_service_hours > 0 :
            scholar.penalty_service_hours = 10
            scholar.total_required_service_hours = scholar.penalty_service_hours + scholar.required_service_hours


        # Check if there are excess rendered service hours
        if pastTotal <= 0 :
            print(pastTotal)
            scholar.penalty_service_hours = 0
            scholar.total_required_service_hours = scholar.required_service_hours + pastTotal
            print(scholar.total_required_service_hours)

    # Determine required service hours based on year level
    
    scholar.term = "1st semester"
    
    # Save the changes

    scholar.save()


def perform_intersession_upkeep(scholar):
    print("Performing Intersession upkeep...")
    pastTotal=scholar.total_required_service_hours

    scholar.total_rendered_service_hours=0

    if scholar.year in [1, 2, 3]:
        required_service_hours = 3
    else:
        required_service_hours = 3

    scholar.required_service_hours = required_service_hours
    
    # Check if total required hours are met
    if scholar.year > 0:
        if scholar.total_required_service_hours > 0 :
            scholar.penalty_service_hours = 50
            scholar.total_required_service_hours = scholar.penalty_service_hours + scholar.required_service_hours


        # Check if there are excess rendered service hours
        if pastTotal <= 0 :
            scholar.penalty_service_hours = 0
            print(pastTotal)
            scholar.total_required_service_hours = scholar.required_service_hours + pastTotal
            print(scholar.total_required_service_hours)

    # Determine required service hours based on year level
    
    scholar.term = "intersession"
    scholar.year += 1
    
    # Save the changes
    scholar.save()


def perform_2ndsemester_upkeep(scholar):
    print("Performing 2nd semester upkeep...")
    pastTotal=scholar.total_required_service_hours

    scholar.total_rendered_service_hours=0

    if scholar.year in [1, 2, 3]:
        required_service_hours = 10
    else:
        required_service_hours = 5

    scholar.required_service_hours = required_service_hours
    
    # Check if total required hours are met
    if scholar.year > 0:
        if scholar.total_required_service_hours > 0 :
            scholar.penalty_service_hours = 50
            scholar.total_required_service_hours = scholar.penalty_service_hours + scholar.required_service_hours


        # Check if there are excess rendered service hours
        if pastTotal <= 0 :
            print(pastTotal)
            scholar.penalty_service_hours = 0
            scholar.total_required_service_hours = scholar.required_service_hours + pastTotal
            print(scholar.total_required_service_hours)

    # Determine required service hours based on year level
    
    scholar.term = "2nd semester"
    
    # Save the changes

    scholar.save()

def check_credentials(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Credentials are correct
            return JsonResponse({'valid': True})
        else:
            # Credentials are incorrect
            return JsonResponse({'valid': False})

def upload_scholar(request):
    scholar_database = Scholar.objects.all()
    if request.method == 'POST':
        TERM = 'Semester'  # Assuming you have TERM defined somewhere

        dataset = Dataset()
        scholar_datum = request.FILES['myfile']
        data_set = scholar_datum.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            id_number, created = User.objects.get_or_create(username=column[0])

            # Extract and convert the year from CSV data to integer
            YEAR = int(column[5])

            # Set required_service_hours based on TERM and YEAR
            if TERM == 'Intersession':
                if YEAR in [1, 2, 3]:
                    required_service_hours = 3
                else:
                    required_service_hours = 3  # Set to default value if year is not in [1, 2, 3]
            elif TERM == 'Semester':
                if YEAR in [1, 2, 3]:
                    required_service_hours = 10
                else:
                    required_service_hours = 5

            scholar_instance, created = Scholar.objects.update_or_create(
                id_number=id_number,
                defaults={
                    'first_name': column[1],
                    'last_name': column[2],
                    'email': column[3],
                    'phone_number': column[4],
                    'year': YEAR,  # Use the extracted year from CSV
                    'required_service_hours': required_service_hours,  # Set required_service_hours
                    'total_rendered_service_hours': 0,
                    'penalty_service_hours': 0,
                    'total_required_service_hours': required_service_hours,
                    'service_hours_status': 'Pending',  # Assuming you have a default status
                    'term': TERM,  # Set the term value
                }
            )
    return redirect('oaa_scholar_status', pk=request.user.pk)

def bulkdelete(request):
    return render(request, "SHIMS_System/bulkdelete.html")

# Logout Function
def logout_view(request):
    logout(request)
    return redirect('login')