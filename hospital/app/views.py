from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
import json
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import re
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
import json
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
import re
from django.views.decorators.http import require_POST
from django.urls import reverse
from datetime import date, datetime
import secrets
from django.db import IntegrityError
import string
from django.http import HttpResponse
from django.db import transaction
from django.core.exceptions import ValidationError
import openpyxl
from .models import Registration, FrontOffice, OperationCategory, Operation, ICDGroup, ICDCode
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Case, When, Value, IntegerField
from django.core.paginator import Paginator  
from .models import Registration, FrontOffice, OperationCategory, Operation, ICDGroup, ICDCode
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
import json
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
import re
from django.views.decorators.http import require_POST
from django.urls import reverse
from datetime import date, datetime
import secrets
from django.db import IntegrityError
import string
from django.http import HttpResponse
from django.db import transaction
from django.core.exceptions import ValidationError
import openpyxl
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import HumanResource
from .models import IncomeHead, ExpenseHead
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from .models import SymptomType, SymptomHead
from openpyxl import Workbook
from django.http import HttpResponse
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER
from django.db.models import Q
from .models import Vital
from decimal import Decimal, InvalidOperation


# Create your views here.
def home_page(request):
    doctors = Registration.objects.filter(
        role="doctor",
        status="approved"
    ).order_by("first_name")

    return render(request, "home_page.html", {
        "doctors": doctors
    })

def login_page(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = Registration.objects.get(username=username)

        except Registration.DoesNotExist:
            messages.error(
                request,
                "Invalid username or password."
            )
            return redirect("login_page")

        if user.status == "disabled":

            messages.error(
                request,
                "Your account has been disabled. Please contact the administrator."
            )

            return redirect("login_page")

        # Check password
        if not check_password(password, user.password):

            messages.error(
                request,
                "Invalid username or password."
            )
            return redirect("login_page")

        if user.role == "manager":

            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["role"] = user.role

            return redirect("manager_home")

        if user.role == "super_admin":

            if user.status != "approved":

                messages.error(
                    request,
                    "Your Super Admin account is waiting for Manager approval."
                )

                return redirect("login_page")


            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["role"] = user.role

            return redirect("super_admin_home")

        if user.role == "admin":

            if user.status != "approved":

                messages.error(
                    request,
                    "Your Admin account is waiting for approval."
                )

                return redirect("login_page")


            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["role"] = user.role

            return redirect("admin_home")

        if user.status != "approved":

            messages.error(
                request,
                "Your account is waiting for approval."
            )

            return redirect("login_page")

        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["role"] = user.role

        return redirect("dashboard")


    return render(request, "login_page.html")

def signup_page(request):

    if request.method == "POST":

        role = request.POST.get("role")

        status = "approved" if role == "manager" else "pending"

        registration = Registration.objects.create(

            role=role,

            profile_image=request.FILES.get("profile_image"),

            aadhar_number=request.POST.get("aadhar_number"),

            first_name=request.POST.get("first_name"),

            last_name=request.POST.get("last_name"),

            email=request.POST.get("email"),

            username=request.POST.get("username"),

            phone=request.POST.get("phone"),

            date_of_birth=request.POST.get("date_of_birth"),

            password=make_password(request.POST.get("password")),

            status=status
        )

        role_name = registration.get_role_display()

        if role == "manager":

            subject = "Registration Completed - LHospital"

            message = f"""
Dear {registration.first_name},

Your registration as {role_name} has been completed successfully.

Your account is now active and you can log in to LHospital.

Thank you,
LHospital Management
"""

        else:

            subject = "Registration Request Received - LHospital"

            message = f"""
Dear {registration.first_name},

Your registration request as {role_name} has been submitted successfully.

Your account is currently pending approval from the hospital administration.

You will receive a notification once your account has been approved.

Thank you,
LHospital Management
"""

        try:

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [registration.email],
                fail_silently=False
            )

        except Exception as e:

            print("Email error:", e)


        if role == "manager":

            messages.success(
                request,
                "Registration completed successfully. You can now log in."
            )

        else:

            messages.success(
                request,
                f"Registration completed successfully as {role_name}. "
                "Your account is waiting for approval."
            )


        return redirect("login_page")


    return render(
        request,
        "signup_page.html"
    )


def manager_home(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    return render(
        request,
        "manager_home.html",
        {
            "manager": manager
        }
    )


def super_admin_approval(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
            return redirect("login_page")
    
    try:
            manager = Registration.objects.get(
                id=user_id,
                role="manager"
            )
    
    except Registration.DoesNotExist:
            request.session.flush()
            return redirect("login_page")

    selected_status = request.GET.get("status", "")

    super_admins = Registration.objects.filter(
        role="super_admin"
    )

    if selected_status in ["pending", "approved", "rejected"]:

        super_admins = super_admins.filter(
            status=selected_status
        )

    return render(
        request,
        "super_admin_approval.html",
        {
            "super_admins": super_admins,
            "selected_status": selected_status,
             "manager":manager
        }
    )


@require_POST
def approve_super_admin(request, user_id):

    user = get_object_or_404(
        Registration,
        id=user_id
    )

    # Approve user
    user.status = "approved"
    user.save()

    # Send verification success email
    subject = "Account Verification Successful"

    message = f"""
Dear {user.first_name} {user.last_name},

Congratulations!

Your Super Admin account verification has been successful.

Your account has been approved and you can now log in to the system.

Thank you.
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender email
            [user.email],             # Receiver email
            fail_silently=False,
        )

        messages.success(
            request,
            f"{user.first_name} {user.last_name} has been approved successfully and a verification email has been sent."
        )

    except Exception as e:

        messages.warning(
            request,
            f"{user.first_name} {user.last_name} was approved, but the email could not be sent."
        )

        print("Email error:", e)

    return redirect("super_admin_approval")


@require_POST
def reject_super_admin(request, user_id):

    user = get_object_or_404(
        Registration,
        id=user_id
    )

    user.delete()

    messages.success(
            request,
            f"{user.first_name} {user.last_name} has been rejected."
        )

    return redirect("super_admin_approval")


def logout_view(request):
    request.session.flush()

    messages.success(request, "You have been logged out successfully.")

    return redirect('login_page')



def super_admin_home(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        manager = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    return render(
        request,
        "super_admin_home.html",
        {
            "manager": manager
        }
    )

def admin_approval(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
            return redirect("login_page")
    
    try:
            manager = Registration.objects.get(
                id=user_id,
                role="super_admin"
            )
    
    except Registration.DoesNotExist:
            request.session.flush()
            return redirect("login_page")

    selected_status = request.GET.get("status", "")

    super_admins = Registration.objects.filter(
        role="admin"
    )

    if selected_status in ["pending", "approved", "rejected"]:

        super_admins = super_admins.filter(
            status=selected_status
        )

    return render(
        request,
        "admin_approval.html",
        {
            "super_admins": super_admins,
            "selected_status": selected_status,
             "manager":manager
        }
    )

@require_POST
def approve_admin(request, user_id):

    user = get_object_or_404(
        Registration,
        id=user_id
    )

    # Approve user
    user.status = "approved"
    user.save()

    # Send verification success email
    subject = "Account Verification Successful"

    message = f"""
Dear {user.first_name} {user.last_name},

Congratulations!

Your Admin account verification has been successful.

Your account has been approved and you can now log in to the system.

Thank you.
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender email
            [user.email],             # Receiver email
            fail_silently=False,
        )

        messages.success(
            request,
            f"{user.first_name} {user.last_name} has been approved successfully and a verification email has been sent."
        )

    except Exception as e:

        messages.warning(
            request,
            f"{user.first_name} {user.last_name} was approved, but the email could not be sent."
        )

        print("Email error:", e)

    return redirect("admin_approval")


@require_POST
def reject_admin(request, user_id):

    user = get_object_or_404(
        Registration,
        id=user_id
    )

    user.delete()

    messages.success(
            request,
            f"{user.first_name} {user.last_name} has been rejected."
        )

    return redirect("admin_approval")


def admin_home(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        manager = Registration.objects.get(
            id=user_id,
            role="admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    return render(
        request,
        "admin_home.html",
        {
            "manager": manager
        }
    )

def user_approval(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
            return redirect("login_page")
    
    try:
            manager = Registration.objects.get(
                id=user_id,
                role="admin"
            )
    
    except Registration.DoesNotExist:
            request.session.flush()
            return redirect("login_page")

    selected_status = request.GET.get("status", "")

    super_admins = Registration.objects.exclude(
        role__in=[
            "manager",
            "super_admin",
            "admin"
        ]
    )

    if selected_status in ["pending", "approved", "rejected"]:

        super_admins = super_admins.filter(
            status=selected_status
        )

    return render(
        request,
        "user_approval.html",
        {
            "super_admins": super_admins,
            "selected_status": selected_status,
             "manager":manager
        }
    )

@require_POST
def approve_user(request, user_id):

    user = get_object_or_404(
        Registration,
        id=user_id
    )

    # Approve user
    user.status = "approved"
    user.save()

    # Send verification success email
    subject = "Account Verification Successful"

    message = f"""
Dear {user.first_name} {user.last_name},

Congratulations!

Your account verification has been successful.

Your account has been approved and you can now log in to the system.

Thank you.
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender email
            [user.email],             # Receiver email
            fail_silently=False,
        )

        messages.success(
            request,
            f"{user.first_name} {user.last_name} has been approved successfully and a verification email has been sent."
        )

    except Exception as e:

        messages.warning(
            request,
            f"{user.first_name} {user.last_name} was approved, but the email could not be sent."
        )

        print("Email error:", e)

    return redirect("user_approval")


@require_POST
def reject_user(request, user_id):

    user = get_object_or_404(
        Registration,
        id=user_id
    )

    user.delete()

    messages.success(
            request,
            f"{user.first_name} {user.last_name} has been rejected."
        )

    return redirect("user_approval")


def dashboard(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        user = Registration.objects.get(
            id=user_id,
            role__in=[
                "doctor",
                "accountant",
                "receptionist",
                "pharmacist",
                "pathologist",
                "radiologist",
                "head_nurse",
                "nurse",
                "billing_executive",
                "patient",
            ],
            status="approved"
        )

    except Registration.DoesNotExist:

        request.session.flush()
        return redirect("login_page")

    return render(
        request,
        "dashboard.html",
        {
            "user": user
        }
    )


def check_registration_field(request):

    field = request.GET.get("field")
    value = request.GET.get("value", "").strip()

    exists = False

    if field == "email":
        exists = Registration.objects.filter(
            email__iexact=value
        ).exists()

    elif field == "phone":
        exists = Registration.objects.filter(
            phone=value
        ).exists()

    elif field == "aadhar":
        exists = Registration.objects.filter(
            aadhar_number=value
        ).exists()

    return JsonResponse({
        "exists": exists
    })
    
# front office 

from django.db.models import Q, Case, When, Value, IntegerField

def front_office_view(request):
    # 1. Session Authentication
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    # 2. Fetch User allowing Super Admin, Admin, and Manager
    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    # 3. Dynamic Base Template Selection based on Role
    user_role = str(getattr(current_user, 'role', '')).lower()
    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    # 4. Search & Category Filter Logic
    active_category = request.GET.get("category", "purpose")
    search_query = request.GET.get("q", "")

    items = FrontOffice.objects.filter(category=active_category)
    if search_query:
        items = items.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    items = items.annotate(
        role_priority=Case(
            When(created_by__role='manager', then=Value(1)),
            When(created_by__role='super_admin', then=Value(2)),
            When(created_by__role='admin', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('role_priority', '-created_at')

    # 5. Context Payload
    context = {
        "base_template": base_template, # Evaluated in line 1 of front_office.html
        "manager": current_user,        # Populates navbar name & role in base layout
        "active_category": active_category,
        "items": items,
        "search_query": search_query,
    }

    return render(request, "front_office.html", context)

# 2. Add / Edit View (Processes raw POST inputs manually)
def save_front_office(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        category = request.POST.get('category')
        title = request.POST.get('title')
        description = request.POST.get('description', '')

        if not title or not category:
            return JsonResponse({'status': 'error', 'message': 'Title and Category are required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        if item_id:
            # Update existing record
            item = get_object_or_404(FrontOffice, id=item_id)

            # Check permissions for editing
            can_edit = False
            if current_user.role == "manager":
                can_edit = True
            elif current_user.role == "super_admin":
                if not item.created_by or item.created_by.role != "manager":
                    can_edit = True
            elif current_user.role == "admin":
                if item.created_by == current_user:
                    can_edit = True

            if not can_edit:
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)

            item.category = category
            item.title = title
            item.description = description
            item.save()
        else:
            # Create new record
            FrontOffice.objects.create(
                category=category,
                title=title,
                description=description,
                created_by=current_user
            )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

# 3. Delete View
def delete_front_office(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

        current_user = get_object_or_404(Registration, id=user_id)
        item = get_object_or_404(FrontOffice, pk=pk)

        # Check permissions
        can_delete = False
        if current_user.role == "manager":
            can_delete = True
        elif current_user.role == "super_admin":
            if not item.created_by or item.created_by.role != "manager":
                can_delete = True
        elif current_user.role == "admin":
            if item.created_by == current_user:
                can_delete = True

        if not can_delete:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        item.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)
#End

def list_patients(request):

    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id or not role:
        return redirect("login_page")

    # Select the correct home template
    if role == "manager":
        home_template = "manager_home.html"

    elif role == "super_admin":
        home_template = "super_admin_home.html"

    elif role == "admin":
        home_template = "admin_home.html"

    else:
        return redirect("login_page")

    # Get the logged-in user
    try:
        user = Registration.objects.get(
            id=user_id,
            role=role
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    patients = Registration.objects.filter(
        role="patient",
        status="approved"
    ).order_by("-created_at")

    return render(
        request,
        "list_patients.html",
        {
            "home_template": home_template,
            "user": user,
            "manager": user,
             "patients": patients,
        }
    )

def add_patient(request):

    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id or not role:
        return redirect("login_page")

    # Select home template
    if role == "manager":
        home_template = "manager_home.html"

    elif role == "super_admin":
        home_template = "super_admin_home.html"

    elif role == "admin":
        home_template = "admin_home.html"

    else:
        return redirect("login_page")

    # Logged-in user
    try:

        user = Registration.objects.get(
            id=user_id,
            role=role
        )

    except Registration.DoesNotExist:

        request.session.flush()

        return redirect("login_page")

    if request.method == "POST":


        patient_name = request.POST.get(
            "patient_name", ""
        ).strip()

        guardian_name = request.POST.get(
            "guardian_name", ""
        ).strip()

        phone = request.POST.get(
            "phone", ""
        ).strip()

        alternative_number = request.POST.get(
            "alternative_number", ""
        ).strip()

        gender = request.POST.get(
            "gender", ""
        ).strip()

        date_of_birth = request.POST.get(
            "date_of_birth", ""
        ).strip()

        blood_group = request.POST.get(
            "blood_group", ""
        ).strip()

        email = request.POST.get(
            "email", ""
        ).strip().lower()

        marital_status = request.POST.get(
            "marital_status", ""
        ).strip()

        address = request.POST.get(
            "address", ""
        ).strip()

        aadhar_number = request.POST.get(
            "aadhar_number", ""
        ).strip()

        remarks = request.POST.get(
            "remarks", ""
        ).strip()

        allergies = request.POST.get(
            "allergies", ""
        ).strip()

        tpa = request.POST.get(
            "tpa", ""
        ).strip()

        tpa_id = request.POST.get(
            "tpa_id", ""
        ).strip()

        tpa_validity = request.POST.get(
            "tpa_validity", ""
        ).strip()

        profile_image = request.FILES.get(
            "profile_image"
        )


        dob = None

        if date_of_birth:

            try:

                dob = datetime.strptime(
                    date_of_birth,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                dob = None

        age = None

        if dob:

            today = date.today()

            age = (
                today.year
                - dob.year
                - (
                    (today.month, today.day)
                    < (dob.month, dob.day)
                )
            )

        name_parts = patient_name.split(
            maxsplit=1
        )

        first_name = (
            name_parts[0]
            if name_parts
            else ""
        )

        last_name = (
            name_parts[1]
            if len(name_parts) > 1
            else ""
        )

        username_base = (
            first_name.lower()
            + phone[-4:]
        )

        username = username_base

        counter = 1

        while Registration.objects.filter(
            username=username
        ).exists():

            username = (
                username_base
                + str(counter)
            )

            counter += 1

        characters = (
            string.ascii_letters
            + string.digits
        )

        plain_password = "".join(
            secrets.choice(characters)
            for _ in range(8)
        )

        patient = Registration(

            role="patient",

            profile_image=profile_image,

            aadhar_number=aadhar_number,

            first_name=first_name,

            last_name=last_name,

            email=email,

            username=username,

            phone=phone,

            date_of_birth=dob,

            gender=gender,

            guardian_name=guardian_name,

            address=address,

            age=age,

            blood_group=blood_group,

            marital_status=marital_status,

            alternative_number=(
                alternative_number
                if alternative_number
                else None
            ),

            remarks=remarks,

            allergies=allergies,

            tpa=tpa,

            tpa_id=tpa_id,

            tpa_validity=(
                tpa_validity
                if tpa_validity
                else None
            ),

            status="approved",

            # Store hashed password
            password=make_password(
                plain_password
            )
        )

        patient.save()


        if email:

            send_mail(

                subject="Your Patient Login Credentials",

                message=(
                    f"Dear {patient.first_name},\n\n"

                    f"Your patient account has been created "
                    f"successfully.\n\n"

                    f"Login Credentials:\n"
                    f"Username: {username}\n"
                    f"Password: {plain_password}\n\n"

                    f"Please keep your login credentials "
                    f"secure.\n\n"

                    f"Regards,\n"
                    f"LHospital"
                ),

                from_email=None,

                recipient_list=[
                    email
                ],

                fail_silently=False
            )

        messages.success(
            request,
            "Patient added successfully. Login credentials have been sent to the patient."
        )

        return JsonResponse({

            "success": True,

            "message":
                "Patient added successfully. "
                "Login credentials have been sent to the patient.",

            "redirect_url":
                reverse(
                    "list_patients"
                )
        })


    return render(
        request,
        "add_patient.html",
        {
            "home_template": home_template,
            "user": user,
            "manager": user,
        }
    )

def check_patient_phone(request):

    phone = request.GET.get(
        "phone",
        ""
    ).strip()

    patient_id = request.GET.get(
        "patient_id"
    )

    exists = Registration.objects.filter(
        phone=phone
    ).exclude(
        id=patient_id
    ).exists()

    return JsonResponse({
        "exists": exists
    })

def check_patient_alternative(request):

    number = request.GET.get(
        "alternative_number",
        ""
    ).strip()

    patient_id = request.GET.get(
        "patient_id"
    )

    exists = Registration.objects.filter(
        alternative_number=number
    ).exclude(
        id=patient_id
    ).exists()

    return JsonResponse({
        "exists": exists
    })

def check_patient_email(request):

    email = request.GET.get(
        "email",
        ""
    ).strip().lower()

    patient_id = request.GET.get(
        "patient_id"
    )

    exists = Registration.objects.filter(
        email__iexact=email
    ).exclude(
        id=patient_id
    ).exists()

    return JsonResponse({
        "exists": exists
    })

def check_patient_aadhar(request):

    aadhar = request.GET.get(
        "aadhar_number",
        ""
    ).strip()

    patient_id = request.GET.get(
        "patient_id"
    )

    exists = Registration.objects.filter(
        aadhar_number=aadhar
    ).exclude(
        id=patient_id
    ).exists()

    return JsonResponse({
        "exists": exists
    })

@require_POST
def delete_patients(request):

    patient_ids = request.POST.getlist("patient_ids[]")

    # Also support a single patient_id
    if not patient_ids:
        single_id = request.POST.get("patient_id")

        if single_id:
            patient_ids = [single_id]

    if not patient_ids:
        return JsonResponse({
            "success": False,
            "message": "No patients selected."
        }, status=400)

    try:

        patients = Registration.objects.filter(
            id__in=patient_ids
        )

        deleted_count = patients.count()

        if deleted_count == 0:
            return JsonResponse({
                "success": False,
                "message": "Patient not found."
            }, status=404)

        # PERMANENT DELETE
        patients.delete()

        return JsonResponse({
            "success": True,
            "message": (
                f"{deleted_count} patient(s) deleted successfully."
            ),
            "deleted_count": deleted_count
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": "Unable to delete patient."
        }, status=500)


@require_POST
def disable_patient(request):

    patient_id = request.POST.get("patient_id")

    if not patient_id:
        return JsonResponse({
            "success": False,
            "message": "Patient ID is required."
        }, status=400)

    try:

        patient = Registration.objects.get(
            id=patient_id,
            role="patient"
        )

        patient.status = "disabled"

        patient.save(update_fields=["status"])

        messages.success(
                          request,
                        "Patient account has been disabled successfully."
                        )
        return JsonResponse({
            "success": True,
             "redirect_url": reverse("list_patients")
        })

    except Registration.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "Patient not found."
        }, status=404)



def edit_patient(request, user_id):

    # -----------------------------------------
    # LOGGED-IN USER
    # -----------------------------------------
    logged_user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not logged_user_id or not role:
        return redirect("login_page")

    # -----------------------------------------
    # HOME TEMPLATE
    # -----------------------------------------
    if role == "manager":
        home_template = "manager_home.html"

    elif role == "super_admin":
        home_template = "super_admin_home.html"

    elif role == "admin":
        home_template = "admin_home.html"

    else:
        return redirect("login_page")

    # -----------------------------------------
    # LOGGED-IN USER DETAILS
    # -----------------------------------------
    try:
        user = Registration.objects.get(
            id=logged_user_id,
            role=role
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    # -----------------------------------------
    # IMPORTANT:
    # GET THE PATIENT USING THE URL ID
    # NOT THE LOGGED-IN USER ID
    # -----------------------------------------
    patient = get_object_or_404(
        Registration,
        id=user_id,
        role="patient"
    )

    # -----------------------------------------
    # POST
    # -----------------------------------------
    if request.method == "POST":

        patient.first_name = request.POST.get(
            "patient_name", ""
        ).strip()

        patient.guardian_name = request.POST.get(
            "guardian_name", ""
        ).strip()

        patient.phone = request.POST.get(
            "phone", ""
        ).strip()

        patient.alternative_number = request.POST.get(
            "alternative_number", ""
        ).strip()

        patient.gender = request.POST.get(
            "gender", ""
        ).strip()

        # -----------------------------------------
        # DATE OF BIRTH
        # -----------------------------------------
        dob = request.POST.get("date_of_birth", "").strip()

        if dob:
            patient.date_of_birth = parse_date(dob)
        else:
            patient.date_of_birth = None

        # -----------------------------------------
        # AGE
        # IMPORTANT: CONVERT "26 years" -> 26
        # -----------------------------------------
        age_value = request.POST.get(
            "age", ""
        ).strip()

        if age_value:

            try:
                # Handles:
                # 26
                # 26 years
                # 26 Years
                patient.age = int(
                    age_value.split()[0]
                )

            except (ValueError, IndexError):
                return JsonResponse({
                    "success": False,
                    "message": "Invalid age value."
                }, status=400)

        else:
            patient.age = None

        patient.blood_group = request.POST.get(
            "blood_group", ""
        ).strip()

        patient.email = request.POST.get(
            "email", ""
        ).strip()

        patient.marital_status = request.POST.get(
            "marital_status", ""
        ).strip()

        patient.aadhar_number = request.POST.get(
            "aadhar_number", ""
        ).strip()

        patient.tpa = request.POST.get(
            "tpa", ""
        ).strip()

        patient.tpa_id = request.POST.get(
            "tpa_id", ""
        ).strip()

        tpa_validity = request.POST.get(
            "tpa_validity", ""
        ).strip()

        if tpa_validity:
            patient.tpa_validity = parse_date(
                tpa_validity
            )
        else:
            patient.tpa_validity = None

        patient.address = request.POST.get(
            "address", ""
        ).strip()

        patient.allergies = request.POST.get(
            "allergies", ""
        ).strip()

        patient.remarks = request.POST.get(
            "remarks", ""
        ).strip()

        # -----------------------------------------
        # PROFILE IMAGE
        # -----------------------------------------
        if request.FILES.get("profile_image"):
            patient.profile_image = request.FILES[
                "profile_image"
            ]

        # -----------------------------------------
        # SAVE
        # -----------------------------------------
        try:

            patient.save()

        except Exception as e:

            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=400)

        messages.success(
          request,
        "Patient updated successfully."
        )
        
        return JsonResponse({
            "success": True,
            "message": "Patient updated successfully.",
            "redirect_url": reverse("list_patients")
        })

    # -----------------------------------------
    # GET
    # -----------------------------------------
    return render(
        request,
        "edit_patient.html",
        {
            "patient": patient,
            "home_template": home_template,
            "user": user,
            "manager": user,
        }
    )


def disable_patients(request):

    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id or not role:
        return redirect("login_page")

    # Select the correct home template
    if role == "manager":
        home_template = "manager_home.html"

    elif role == "super_admin":
        home_template = "super_admin_home.html"

    elif role == "admin":
        home_template = "admin_home.html"

    else:
        return redirect("login_page")

    # Get the logged-in user
    try:
        user = Registration.objects.get(
            id=user_id,
            role=role
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    patients = Registration.objects.filter(
        role="patient",
        status="disabled"
    ).order_by("-created_at")

    return render(
        request,
        "disable_patients.html",
        {
            "home_template": home_template,
            "user": user,
            "manager": user,
             "patients": patients,
        }
    )


@require_POST
def enable_patient(request):

    patient_id = request.POST.get("patient_id")

    if not patient_id:
        return JsonResponse({
            "success": False,
            "message": "Patient ID is required."
        })

    try:
        patient = Registration.objects.get(id=patient_id)

        # Change disabled → approved
        patient.status = "approved"
        patient.save(update_fields=["status"])

        messages.success(
                  request,
                "Patient has been enabled successfully."
                )

        return JsonResponse({
            "success": True,
            "message": "Patient has been enabled successfully.",
             "redirect_url": reverse("list_patients")
        })

    except Registration.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "Patient not found."
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": "Unable to enable patient."
        })


def import_patients(request):

    user_id = request.session.get("user_id")
    role = request.session.get("role")

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not user_id or not role:
        return redirect("login_page")

    # =====================================================
    # SELECT HOME TEMPLATE
    # =====================================================

    if role == "manager":
        home_template = "manager_home.html"

    elif role == "super_admin":
        home_template = "super_admin_home.html"

    elif role == "admin":
        home_template = "admin_home.html"

    else:
        return redirect("login_page")

    # =====================================================
    # GET LOGGED-IN USER
    # =====================================================

    try:

        user = Registration.objects.get(
            id=user_id,
            role=role
        )

    except Registration.DoesNotExist:

        request.session.flush()

        return redirect("login_page")

    # =====================================================
    # BASE CONTEXT
    # =====================================================

    base_context = {
        "home_template": home_template,
        "user": user,
        "manager": user,
    }

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        excel_file = request.FILES.get("patient_excel")

        # =================================================
        # FILE REQUIRED
        # =================================================

        if not excel_file:

            messages.error(
                request,
                "Please choose an Excel file."
            )

            return render(
                request,
                "import_patients.html",
                base_context
            )

        # =================================================
        # FILE EXTENSION
        # =================================================

        file_name = excel_file.name.lower()

        if not file_name.endswith(
            (".xlsx", ".xlsm")
        ):

            messages.error(
                request,
                "Please upload a valid Excel file (.xlsx or .xlsm)."
            )

            return render(
                request,
                "import_patients.html",
                base_context
            )

        # =================================================
        # OPEN EXCEL
        # =================================================

        try:

            workbook = openpyxl.load_workbook(
                excel_file,
                data_only=True
            )

            sheet = workbook.active

        except Exception:

            messages.error(
                request,
                "Unable to read the Excel file. Please use the sample format."
            )

            return render(
                request,
                "import_patients.html",
                base_context
            )

        # =================================================
        # EXPECTED HEADERS
        # =================================================

        expected_headers = [

            "Patient Name",
            "Guardian Name",
            "Phone",
            "Alternative Number",
            "Gender",
            "Date of Birth",
            "Age",
            "Blood Group",
            "Email",
            "Marital Status",
            "Aadhar Number",
            "TPA",
            "TPA ID",
            "TPA Validity",
            "Address",
            "Allergies",
            "Remarks",

        ]

        # =================================================
        # READ HEADERS
        # =================================================

        actual_headers = []

        for cell in sheet[1]:

            value = cell.value

            if value is None:

                actual_headers.append("")

            else:

                actual_headers.append(
                    str(value).strip()
                )

        # Remove extra empty columns
        while (
            actual_headers
            and actual_headers[-1] == ""
        ):

            actual_headers.pop()

        # =================================================
        # HEADER VALIDATION
        # =================================================

        if actual_headers != expected_headers:

            messages.error(
                request,
                "Invalid Excel format. Please download and use the sample Excel file."
            )

            return render(
                request,
                "import_patients.html",
                base_context
            )

        # =================================================
        # COUNTERS
        # =================================================

        total_rows = 0
        success_count = 0
        failed_count = 0

        errors = []

        # =================================================
        # PROCESS EACH ROW
        # =================================================

        for row_number, row in enumerate(
            sheet.iter_rows(
                min_row=2,
                values_only=True
            ),
            start=2
        ):

            # =================================================
            # SKIP EMPTY ROW
            # =================================================

            if not any(
                value is not None
                and str(value).strip() != ""
                for value in row
            ):
                continue

            total_rows += 1

            row_errors = []

            # =================================================
            # GET VALUES
            # =================================================

            patient_name = clean_value(row[0])

            guardian_name = clean_value(row[1])

            phone = clean_value(row[2])

            alternative_number = clean_value(row[3])

            gender = clean_value(row[4])

            date_of_birth = parse_excel_date(row[5])

            age = clean_value(row[6])

            blood_group = clean_value(row[7])

            email = clean_value(row[8])

            marital_status = clean_value(row[9])

            aadhar_number = clean_value(row[10])

            tpa = clean_value(row[11])

            tpa_id = clean_value(row[12])

            tpa_validity = parse_excel_date(row[13])

            address = clean_value(row[14])

            allergies = clean_value(row[15])

            remarks = clean_value(row[16])

            # =================================================
            # REQUIRED FIELDS
            # =================================================

            if not patient_name:

                row_errors.append(
                    "Patient name is required."
                )

            if not phone:

                row_errors.append(
                    "Phone number is required."
                )

            if not email:

                row_errors.append(
                    "Email is required."
                )

            # =================================================
            # PHONE VALIDATION
            # =================================================

            if phone:

                phone = str(phone).strip()

                if not re.fullmatch(
                    r"[6-9]\d{9}",
                    phone
                ):

                    row_errors.append(
                        "Phone number must contain 10 valid digits."
                    )

            # =================================================
            # ALTERNATIVE PHONE
            # =================================================

            if alternative_number:

                alternative_number = str(
                    alternative_number
                ).strip()

                if not re.fullmatch(
                    r"[6-9]\d{9}",
                    alternative_number
                ):

                    row_errors.append(
                        "Alternative number must contain 10 valid digits."
                    )

            # =================================================
            # AADHAR
            # =================================================

            if aadhar_number:

                aadhar_number = str(
                    aadhar_number
                ).strip()

                if not re.fullmatch(
                    r"\d{12}",
                    aadhar_number
                ):

                    row_errors.append(
                        "Aadhar number must contain exactly 12 digits."
                    )

            # =================================================
            # EMAIL
            # =================================================

            if email:

                email = email.lower().strip()

                if not re.fullmatch(
                    r"^[A-Za-z0-9._%+-]+@gmail\.com$",
                    email
                ):

                    row_errors.append(
                        "Email must be a valid Gmail address."
                    )

            # =================================================
            # USERNAME
            # =================================================

            username = ""

            if phone:

                username = "PAT" + phone

            # =================================================
            # DATE OF BIRTH
            # =================================================

            if row[5] and not date_of_birth:

                row_errors.append(
                    "Invalid date of birth."
                )

            # =================================================
            # AGE
            # =================================================

            if age:

                try:

                    age = int(float(age))

                    if age < 0 or age > 150:

                        row_errors.append(
                            "Age must be between 0 and 150."
                        )

                except (
                    ValueError,
                    TypeError
                ):

                    row_errors.append(
                        "Age must be a valid number."
                    )

            else:

                age = None

            # =================================================
            # TPA VALIDITY
            # =================================================

            if row[13] and not tpa_validity:

                row_errors.append(
                    "Invalid TPA validity date."
                )

            # =================================================
            # DATABASE DUPLICATE CHECK
            # =================================================

            if aadhar_number:

                if Registration.objects.filter(
                    aadhar_number=aadhar_number
                ).exists():

                    row_errors.append(
                        "Aadhar number already exists."
                    )

            if email:

                if Registration.objects.filter(
                    email=email
                ).exists():

                    row_errors.append(
                        "Email already exists."
                    )

            if phone:

                if Registration.objects.filter(
                    phone=phone
                ).exists():

                    row_errors.append(
                        "Phone number already exists."
                    )

            if username:

                if Registration.objects.filter(
                    username=username
                ).exists():

                    row_errors.append(
                        "Username already exists."
                    )

            # =================================================
            # DUPLICATE CHECK INSIDE EXCEL
            # =================================================

            previous_rows = sheet.iter_rows(
                min_row=2,
                max_row=row_number - 1,
                values_only=True
            )

            for previous_row in previous_rows:

                previous_phone = clean_value(
                    previous_row[2]
                )

                previous_email = clean_value(
                    previous_row[8]
                )

                previous_aadhar = clean_value(
                    previous_row[10]
                )

                # PHONE
                if (
                    phone
                    and previous_phone
                    and previous_phone == phone
                ):

                    row_errors.append(
                        "Duplicate phone number in Excel."
                    )

                    break

                # EMAIL
                if (
                    email
                    and previous_email
                    and previous_email.lower() == email.lower()
                ):

                    row_errors.append(
                        "Duplicate email in Excel."
                    )

                    break

                # AADHAR
                if (
                    aadhar_number
                    and previous_aadhar
                    and previous_aadhar == aadhar_number
                ):

                    row_errors.append(
                        "Duplicate Aadhar number in Excel."
                    )

                    break

            # =================================================
            # IF ROW HAS ERRORS
            # =================================================

            if row_errors:

                failed_count += 1

                errors.append({

                    "row": row_number,

                    "errors": row_errors

                })

                continue

            # =================================================
            # GENERATE RANDOM PASSWORD
            # =================================================

            plain_password = secrets.token_urlsafe(8)

            # =================================================
            # CREATE PATIENT
            # =================================================

            try:

                with transaction.atomic():

                    patient = Registration(

                        first_name=patient_name,

                        last_name="",

                        phone=phone,

                        alternative_number=(
                            alternative_number
                            or None
                        ),

                        username=username,

                        email=email or None,

                        date_of_birth=date_of_birth,

                        age=age,

                        gender=gender or None,

                        guardian_name=(
                            guardian_name
                            or None
                        ),

                        address=address or None,

                        blood_group=(
                            blood_group
                            or None
                        ),

                        marital_status=(
                            marital_status
                            or None
                        ),

                        aadhar_number=(
                            aadhar_number
                            or None
                        ),

                        allergies=(
                            allergies
                            or None
                        ),

                        remarks=(
                            remarks
                            or None
                        ),

                        tpa=tpa or None,

                        tpa_id=tpa_id or None,

                        tpa_validity=tpa_validity,

                        role="patient",

                        # IMPORTANT
                        status="approved",

                    )

                    # =================================================
                    # SET RANDOM PASSWORD
                    # =================================================
                    plain_password = secrets.token_urlsafe(8)

                    patient.password = make_password(plain_password)

                    # =================================================
                    # MODEL VALIDATION
                    # =================================================

                    patient.full_clean(
                        exclude=["password"]
                    )

                    # =================================================
                    # SAVE
                    # =================================================

                    patient.save()

                # =================================================
                # SEND EMAIL
                # =================================================

                send_mail(

                    subject="Your Patient Login Credentials",

                    message=(
                        f"Dear {patient.first_name},\n\n"

                        f"Your patient account has been created "
                        f"successfully.\n\n"

                        f"Login Credentials:\n"
                        f"Username: {username}\n"
                        f"Password: {plain_password}\n\n"

                        f"Please keep your login credentials "
                        f"secure.\n\n"

                        f"Regards,\n"
                        f"LHospital"
                    ),

                    from_email=settings.DEFAULT_FROM_EMAIL,

                    recipient_list=[
                        email
                    ],

                    fail_silently=False,

                )

                success_count += 1

            # =================================================
            # ERROR
            # =================================================

            except Exception as e:

               import traceback

               print("\n==============================")
               print("IMPORT ERROR - ROW:", row_number)
               print("ERROR TYPE:", type(e).__name__)
               print("ERROR:", e)
               print("PATIENT:", patient_name)
               print("PHONE:", phone)
               print("EMAIL:", email)
               print("AADHAR:", aadhar_number)
               print("==============================")

               traceback.print_exc()

               failed_count += 1

               errors.append({
                    "row": row_number,
                    "errors": [
                    str(e)
                    ]
               })

        # =====================================================
        # REDIRECT TO PATIENT LIST
        # =====================================================

        messages.success(
            request,
            f"{success_count} patient(s) added successfully "
            f"and {failed_count} patient(s) skipped."
        )

        return redirect("list_patients")

    # =========================================================
    # GET REQUEST
    # =========================================================

    return render(
        request,
        "import_patients.html",
        base_context
    )

def clean_value(value):

    if value is None:
        return ""

    return str(value).strip()

def parse_excel_date(value):

    if not value:
        return None

    # Excel already returned a datetime/date
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    value = str(value).strip()

    date_formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%m/%d/%Y",
    ]

    for fmt in date_formats:

        try:
            return datetime.strptime(
                value,
                fmt
            ).date()

        except ValueError:
            continue

    return None


def parse_boolean(value):

    if value is None:
        return False

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    return value in [
        "yes",
        "true",
        "1",
        "y",
    ]

def download_patient_sample(request):

    workbook = openpyxl.Workbook()

    sheet = workbook.active
    sheet.title = "Patients"

    # =====================================================
    # TABLE HEADERS
    # =====================================================

    headers = [
        "Patient Name",
        "Guardian Name",
        "Phone",
        "Alternative Number",
        "Gender",
        "Date of Birth",
        "Age",
        "Blood Group",
        "Email",
        "Marital Status",
        "Aadhar Number",
        "TPA",
        "TPA ID",
        "TPA Validity",
        "Address",
        "Allergies",
        "Remarks",
    ]

    sheet.append(headers)

    # =====================================================
    # COLUMN WIDTHS
    # Same order as headers above
    # =====================================================

    widths = [
        25,  # Patient Name
        25,  # Guardian Name
        16,  # Phone
        20,  # Alternative Number
        15,  # Gender
        18,  # Date of Birth
        10,  # Age
        15,  # Blood Group
        30,  # Email
        18,  # Marital Status
        20,  # Aadhar Number
        22,  # TPA
        20,  # TPA ID
        20,  # TPA Validity
        40,  # Address
        30,  # Allergies
        35,  # Remarks
    ]

    for index, width in enumerate(widths, start=1):

        sheet.column_dimensions[
            openpyxl.utils.get_column_letter(index)
        ].width = width

    # =====================================================
    # HEADER STYLE
    # =====================================================

    from openpyxl.styles import Font, PatternFill, Alignment

    for cell in sheet[1]:

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            start_color="FF6B00",
            end_color="FF6B00",
            fill_type="solid"
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # =====================================================
    # HEADER ROW HEIGHT
    # =====================================================

    sheet.row_dimensions[1].height = 25

    # =====================================================
    # FREEZE HEADER
    # =====================================================

    sheet.freeze_panes = "A2"

    # =====================================================
    # AUTO FILTER
    # =====================================================

    sheet.auto_filter.ref = sheet.dimensions

    # =====================================================
    # RESPONSE
    # =====================================================

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="patient_import_sample.xlsx"'
    )

    workbook.save(response)

    return response
    
def check_setup_permission(user, item):
    if not user or not getattr(user, 'role', None):
        return False
    user_role = str(user.role).lower().strip()
    if user_role in ['manager', 'super_admin', 'superadmin', 'super admin']:
        return True
    if user_role == 'admin':
        if not getattr(item, 'created_by', None):
            return True
        creator_role = str(getattr(item.created_by, 'role', '')).lower().strip()
        if creator_role in ['manager', 'super_admin', 'superadmin', 'super admin']:
            return False
        return True
    return False




# ==========================================
# SETUP: OPERATIONS & ICD MODULES
# ==========================================

# ------------------------------------------
# OPERATIONS MODULE VIEWS
# ------------------------------------------
from django.db.models import Q, Case, When, Value, IntegerField
from django.core.paginator import Paginator
from .models import Registration, OperationCategory, Operation, ICDGroup, ICDCode

# MY SECTION: OPERATIONS & ICD MODULE VIEWS

def operations_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    user_role = str(getattr(current_user, 'role', '')).lower()
    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    active_tab = request.GET.get("tab", "operation")
    search_query = request.GET.get("q", "").strip()
    per_page_param = request.GET.get("per_page", "10")
    page_number = request.GET.get("page", 1)

    categories = OperationCategory.objects.all().order_by('name')

    if active_tab == "category":
        qs = OperationCategory.objects.all()
        if search_query:
            qs = qs.filter(name__icontains=search_query)
    else:
        qs = Operation.objects.select_related('category', 'created_by').all()
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) | Q(category__name__icontains=search_query)
            )

    qs = qs.annotate(
        role_priority=Case(
            When(created_by__role='manager', then=Value(1)),
            When(created_by__role='super_admin', then=Value(2)),
            When(created_by__role='admin', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('role_priority', '-created_at')

    total_records = qs.count()

    if per_page_param.lower() == 'all':
        items_list = list(qs)
        page_obj = None
    else:
        try:
            per_page = int(per_page_param)
        except ValueError:
            per_page = 10
        paginator = Paginator(qs, per_page)
        try:
            page_obj = paginator.page(page_number)
        except Exception:
            page_obj = paginator.page(1)
        items_list = page_obj.object_list

    for item in items_list:
        item.can_edit = check_setup_permission(current_user, item)
        item.can_delete = check_setup_permission(current_user, item)

    context = {
        "base_template": base_template,
        "manager": current_user,
        "active_tab": active_tab,
        "search_query": search_query,
        "per_page": per_page_param,
        "categories": categories,
        "items": items_list,
        "page_obj": page_obj,
        "total_records": total_records,
    }
    return render(request, "operations.html", context)


def check_setup_field(request):
    model_type = request.GET.get("model_type")
    field = request.GET.get("field")
    value = request.GET.get("value", "").strip()
    item_id = request.GET.get("item_id", "").strip()
    extra_id = request.GET.get("extra_id", "").strip()

    if not value or not model_type:
        return JsonResponse({"exists": False})

    exists = False

    if model_type == "op_category":
        qs = OperationCategory.objects.filter(name__iexact=value)
        if item_id:
            qs = qs.exclude(id=item_id)
        exists = qs.exists()

    elif model_type == "operation":
        qs = Operation.objects.filter(name__iexact=value)
        if extra_id:
            qs = qs.filter(category_id=extra_id)
        if item_id:
            qs = qs.exclude(id=item_id)
        exists = qs.exists()

    elif model_type == "icd_group":
        qs = ICDGroup.objects.filter(name__iexact=value)
        if item_id:
            qs = qs.exclude(id=item_id)
        exists = qs.exists()

    elif model_type == "icd_code":
        qs = ICDCode.objects.filter(code__iexact=value)
        if item_id:
            qs = qs.exclude(id=item_id)
        exists = qs.exists()

    return JsonResponse({"exists": exists})


def save_operation_category(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        name = request.POST.get('name', '').strip()

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Category Name is required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        # Duplicate Validation
        dup_qs = OperationCategory.objects.filter(name__iexact=name)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'Operation Category "{name}" already exists.'}, status=400)

        if item_id:
            category = get_object_or_404(OperationCategory, id=item_id)
            if not check_setup_permission(current_user, category):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            category.name = name
            category.save()
        else:
            OperationCategory.objects.create(name=name, created_by=current_user)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_operation_category(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

        current_user = get_object_or_404(Registration, id=user_id)
        category = get_object_or_404(OperationCategory, pk=pk)

        if not check_setup_permission(current_user, category):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        # Check if Category is in use by operations
        in_use_count = Operation.objects.filter(category=category).count()
        if in_use_count > 0:
            return JsonResponse({'status': 'error', 'message': f'Cannot delete category "{category.name}" because it is currently used by {in_use_count} operation(s).'}, status=400)

        category.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


def save_operation(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category_id')

        if not name or not category_id:
            return JsonResponse({'status': 'error', 'message': 'Operation Name and Category are required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        category = get_object_or_404(OperationCategory, id=category_id)

        # Duplicate Validation
        dup_qs = Operation.objects.filter(name__iexact=name, category=category)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'Operation "{name}" already exists in this category.'}, status=400)

        if item_id:
            operation = get_object_or_404(Operation, id=item_id)
            if not check_setup_permission(current_user, operation):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            operation.name = name
            operation.category = category
            operation.save()
        else:
            Operation.objects.create(name=name, category=category, created_by=current_user)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_operation(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

        current_user = get_object_or_404(Registration, id=user_id)
        operation = get_object_or_404(Operation, pk=pk)

        if not check_setup_permission(current_user, operation):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        operation.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


# ------------------------------------------
# ICD MODULE VIEWS
# ------------------------------------------

def icd_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    user_role = str(getattr(current_user, 'role', '')).lower()
    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    active_tab = request.GET.get("tab", "group")
    search_query = request.GET.get("q", "").strip()
    per_page_param = request.GET.get("per_page", "10")
    page_number = request.GET.get("page", 1)

    icd_groups = ICDGroup.objects.all().order_by('name')

    if active_tab == "icd":
        qs = ICDCode.objects.select_related('group', 'created_by').all()
        if search_query:
            qs = qs.filter(
                Q(code__icontains=search_query) | Q(description__icontains=search_query) | Q(group__name__icontains=search_query)
            )
    else:
        qs = ICDGroup.objects.all()
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

    qs = qs.annotate(
        role_priority=Case(
            When(created_by__role='manager', then=Value(1)),
            When(created_by__role='super_admin', then=Value(2)),
            When(created_by__role='admin', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('role_priority', '-created_at')

    total_records = qs.count()

    if per_page_param.lower() == 'all':
        items_list = list(qs)
        page_obj = None
    else:
        try:
            per_page = int(per_page_param)
        except ValueError:
            per_page = 10
        paginator = Paginator(qs, per_page)
        try:
            page_obj = paginator.page(page_number)
        except Exception:
            page_obj = paginator.page(1)
        items_list = page_obj.object_list

    for item in items_list:
        item.can_edit = check_setup_permission(current_user, item)
        item.can_delete = check_setup_permission(current_user, item)

    context = {
        "base_template": base_template,
        "manager": current_user,
        "active_tab": active_tab,
        "search_query": search_query,
        "per_page": per_page_param,
        "icd_groups": icd_groups,
        "items": items_list,
        "page_obj": page_obj,
        "total_records": total_records,
    }
    return render(request, "icd.html", context)


def save_icd_group(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Group Name is required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        # Duplicate Validation
        dup_qs = ICDGroup.objects.filter(name__iexact=name)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'ICD Group "{name}" already exists.'}, status=400)

        if item_id:
            group = get_object_or_404(ICDGroup, id=item_id)
            if not check_setup_permission(current_user, group):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            group.name = name
            group.description = description
            group.save()
        else:
            ICDGroup.objects.create(name=name, description=description, created_by=current_user)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_icd_group(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

        current_user = get_object_or_404(Registration, id=user_id)
        group = get_object_or_404(ICDGroup, pk=pk)

        if not check_setup_permission(current_user, group):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        # Check if Group is in use by ICD codes
        in_use_count = ICDCode.objects.filter(group=group).count()
        if in_use_count > 0:
            return JsonResponse({'status': 'error', 'message': f'Cannot delete ICD Group "{group.name}" because it is currently used by {in_use_count} ICD code(s).'}, status=400)

        group.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


def save_icd_code(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()
        group_id = request.POST.get('group_id')

        if not code or not group_id:
            return JsonResponse({'status': 'error', 'message': 'ICD Code and Group are required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        group = get_object_or_404(ICDGroup, id=group_id)

        # Duplicate Validation
        dup_qs = ICDCode.objects.filter(code__iexact=code)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'ICD Code "{code}" already exists.'}, status=400)

        if item_id:
            icd_item = get_object_or_404(ICDCode, id=item_id)
            if not check_setup_permission(current_user, icd_item):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            icd_item.code = code
            icd_item.description = description
            icd_item.group = group
            icd_item.save()
        else:
            ICDCode.objects.create(code=code, description=description, group=group, created_by=current_user)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_icd_code(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

        current_user = get_object_or_404(Registration, id=user_id)
        icd_item = get_object_or_404(ICDCode, pk=pk)

        if not check_setup_permission(current_user, icd_item):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        icd_item.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

def bed_manager(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    active_section = request.GET.get("section", "status")
    allowed_roles = ["manager", "admin", "super_admin"]
    
    bed_search = request.GET.get("bed_search", "").strip()

    beds = Bed.objects.filter(
            role__role__in=allowed_roles
        ).select_related(
            "floor",
            "bedtype",
            "bedgroup",
            "role"
        )

    if bed_search:
        beds = beds.filter(
            Q(bed_name__icontains=bed_search) |
            Q(bedtype__type_name__icontains=bed_search) |
            Q(bedgroup__group_name__icontains=bed_search)
        )
    status_search = request.GET.get("status_search", "").strip()

    bed_status = Bed.objects.filter(
        role__role__in=allowed_roles
    ).select_related(
        "floor",
        "bedtype",
        "bedgroup"
    )

    if status_search:
        bed_status = bed_status.filter(
            Q(bed_name__icontains=status_search) |
            Q(bedtype__type_name__icontains=status_search) |
            Q(bedgroup__group_name__icontains=status_search)
        )
    floor_search = request.GET.get("floor_search", "").strip()

    floors = Floor.objects.filter(
        role__role__in=allowed_roles
    )

    if floor_search:
        floors = floors.filter(
            Q(floor_name__icontains=floor_search) |
            Q(description__icontains=floor_search)
        )
    group_search = request.GET.get("group_search", "").strip()

    bedgroups = Bedgroup.objects.filter(
        role__role__in=allowed_roles
    )

    if group_search:
        bedgroups = bedgroups.filter(
            Q(group_name__icontains=group_search) |
            Q(colour__icontains=group_search) |
            Q(description__icontains=group_search)
        )

    type_search = request.GET.get("type_search", "").strip()

    bedtypes = Bedtype.objects.filter(
        role__role__in=allowed_roles
    )

    if type_search:
        bedtypes = bedtypes.filter(
            Q(type_name__icontains=type_search)
        )


    return render(
        request,
        "bed_manager.html",
        {
            "manager": manager,
            "beds": beds,
            "bed_status": bed_status,
            "floors": floors,
            "bedgroup": bedgroups,
            "bedtype": bedtypes,
            "bed_search": bed_search,
            "status_search": status_search,
            "floor_search": floor_search,
            "group_search": group_search,
            "type_search": type_search,
            "active_section": active_section,
        }
    )

from django.urls import reverse
def add_floor(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    if request.method == "POST":
        floor_name = request.POST.get("floor_name", "").strip()
        description = request.POST.get("description", "").strip()
        floor_id = request.POST.get(
            "floor_id"
        )

        if floor_id:

            floor = get_object_or_404(
                Floor,
                id=floor_id,
                role__role__in=allowed_roles
            )

            floor.floor_name = floor_name
            floor.description = description

            floor.save()

            messages.success(
                request,
                "Floor updated successfully."
            )

        else:
            Floor.objects.create(
            role=manager,
            floor_name=floor_name,
            description=description,
        )

        messages.success(
            request,
            "Floor added successfully."
        )
        

    return redirect(reverse("bed_manager") + "?section=floor")

def add_bedgroup(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    
    allowed_roles = ["manager", "admin", "super_admin"]
    if request.method == "POST":
        group_name = request.POST.get("group_name", "").strip()
        colour = request.POST.get("colour", "").strip()
        floor_id = request.POST.get("floor")
        
        bedgroup_id = request.POST.get(
            "bedgroup_id"
        )
        floor = Floor.objects.get(id=floor_id)
        description = request.POST.get("description", "").strip()
        if bedgroup_id:

            bedgroup = get_object_or_404(
                Bedgroup,
                id=bedgroup_id,
                role__role__in=allowed_roles
            )

            bedgroup.group_name = group_name
            bedgroup.colour = colour
            bedgroup.floor = floor
            bedgroup.description = description
            bedgroup.save()
            messages.success(request,"Bed Group updated successfully.")
        else:
            Bedgroup.objects.create(
            role=manager,
            group_name=group_name,
            colour=colour,
            floor=floor,
            description=description,
        )
            messages.success(
            request,
            "Bed Group added successfully."
        )

    return redirect(reverse("bed_manager") + "?section=group")
def add_bedtype(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    if request.method == "POST":
        type_name = request.POST.get("type_name", "").strip()
        bedtype_id = request.POST.get("bedtype_id")
        if bedtype_id:
            bedtype = get_object_or_404(
                Bedtype,
                id=bedtype_id,
                role__role__in=allowed_roles
            )
            bedtype.type_name = type_name
            bedtype.save()

            messages.success(
                request,
                "Bed Type updated successfully."
            )
        else:
            Bedtype.objects.create(
            role=manager,
            type_name=type_name
        )
            messages.success(
            request,
            "Bed type added successfully."
        )

    return redirect(reverse("bed_manager") + "?section=type")

from django.shortcuts import redirect, get_object_or_404
def add_bed(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    if request.method == "POST":
        bed_id = request.POST.get("bed_id")
        bed_name = request.POST.get("bed_name", "").strip()
        bedtype_id = request.POST.get("type")
        bedgroup_id = request.POST.get("group")
        not_available = request.POST.get("not_available") == "on"
        bedtype = get_object_or_404(
            Bedtype,
            id=bedtype_id,
            role__role__in=allowed_roles
        )
        bedgroup = get_object_or_404(
            Bedgroup,
            id=bedgroup_id,
            role__role__in=allowed_roles
        )
        if bed_id:

            bed = get_object_or_404(
                Bed,
                id=bed_id,
                role__role__in=allowed_roles
            )

            bed.bed_name = bed_name
            bed.bedtype = bedtype
            bed.bedgroup = bedgroup
            bed.not_available = not_available
            bed.save()
            messages.success(
                request,
                "Bed updated successfully."
            )
        else:
            Bed.objects.create(
            role=manager,
            bed_name=bed_name,
            bedtype=bedtype,
            bedgroup=bedgroup,
            
            not_available=not_available
        )
            messages.success(
            request,
            "Bed added successfully."
        )
    return redirect(reverse("bed_manager") + "?section=bed")
def delete_bed(request, bed_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(id=user_id,role="manager")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    bed = get_object_or_404(Bed,id=bed_id,role__role__in=allowed_roles)
    bed.delete()
    messages.success(request,"Bed deleted successfully.")
    return redirect(reverse("bed_manager") + "?section=bed")
def delete_bed_type(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(id=user_id,role="manager")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    bedtype = get_object_or_404(Bedtype,id=id,role__role__in=allowed_roles)
    bedtype.delete()
    messages.success(request,"Bed type deleted successfully.")
    return redirect(reverse("bed_manager") + "?section=type")
def delete_bed_group(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(id=user_id,role="manager")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    bedgroup = get_object_or_404(Bedgroup,id=id,role__role__in=allowed_roles)
    bedgroup.delete()
    messages.success(request,"Bed group deleted successfully.")
    return redirect(reverse("bed_manager") + "?section=group")
def delete_floor(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        manager = Registration.objects.get(id=user_id,role="manager")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    floors = get_object_or_404(Floor,id=id,role__role__in=allowed_roles)
    floors.delete()
    messages.success(request,"Floor deleted successfully.")
    return redirect(reverse("bed_manager") + "?section=floor")




def bed_superadmin(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    

    active_section = request.GET.get("section", "status")
    bed_search = request.GET.get("bed_search", "").strip()

    beds = Bed.objects.filter(
        role__role__in=allowed_roles
    ).select_related(
        "floor",
        "bedtype",
        "bedgroup"
    )

    if bed_search:
        beds = beds.filter(
            Q(bed_name__icontains=bed_search) |
            Q(bedtype__type_name__icontains=bed_search) |
            Q(bedgroup__group_name__icontains=bed_search)
        )
    status_search = request.GET.get("status_search", "").strip()

    bed_status = Bed.objects.filter(
        role__role__in=allowed_roles
    ).select_related(
        "floor",
        "bedtype",
        "bedgroup"
    )

    if status_search:
        bed_status = bed_status.filter(
            Q(bed_name__icontains=status_search) |
            Q(bedtype__type_name__icontains=status_search) |
            Q(bedgroup__group_name__icontains=status_search)
        )
    floor_search = request.GET.get("floor_search", "").strip()

    floors = Floor.objects.filter(
        role__role__in=allowed_roles
    )

    if floor_search:
        floors = floors.filter(
            Q(floor_name__icontains=floor_search) |
            Q(description__icontains=floor_search)
        )
    group_search = request.GET.get("group_search", "").strip()

    bedgroups = Bedgroup.objects.filter(
       role__role__in=allowed_roles
    )

    if group_search:
        bedgroups = bedgroups.filter(
            Q(group_name__icontains=group_search) |
            Q(colour__icontains=group_search) |
            Q(description__icontains=group_search)
        )

    type_search = request.GET.get("type_search", "").strip()

    bedtypes = Bedtype.objects.filter(
        role__role__in=allowed_roles
    )

    if type_search:
        bedtypes = bedtypes.filter(
            Q(type_name__icontains=type_search)
        )


    return render(
        request,
        "bed_superadmin.html",
        {
           
            "manager": super_admin,
            "beds": beds,
            "bed_status": bed_status,
            "floors": floors,
            "bedgroup": bedgroups,
            "bedtype": bedtypes,
            "bed_search": bed_search,
            "status_search": status_search,
            "floor_search": floor_search,
            "group_search": group_search,
            "type_search": type_search,
            "active_section": active_section,
        }
    )

def add_floor1(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    
    if request.method == "POST":
        floor_name = request.POST.get("floor_name", "").strip()
        description = request.POST.get("description", "").strip()
        floor_id = request.POST.get(
            "floor_id"
        )

        if floor_id:

            floor = get_object_or_404(
                Floor,
                id=floor_id,
                role__role__in=allowed_roles
            )

            floor.floor_name = floor_name
            floor.description = description

            floor.save()

            messages.success(
                request,
                "Floor updated successfully."
            )

        else:
            Floor.objects.create(
            role=super_admin,
            floor_name=floor_name,
            description=description,
        )
            messages.success(
            request,
            "Floor added successfully."
        )
    return redirect(reverse("bed_superadmin") + "?section=floor")

def add_bedgroup1(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    
    if request.method == "POST":
        group_name = request.POST.get("group_name", "").strip()
        colour = request.POST.get("colour", "").strip()
        floor_id = request.POST.get("floor")
        
        bedgroup_id = request.POST.get(
            "bedgroup_id"
        )
        floor = Floor.objects.get(id=floor_id)
        description = request.POST.get("description", "").strip()
        if bedgroup_id:

            bedgroup = get_object_or_404(
                Bedgroup,
                id=bedgroup_id,
                role__role__in=allowed_roles
            )

            bedgroup.group_name = group_name
            bedgroup.colour = colour
            bedgroup.floor = floor
            bedgroup.description = description
            bedgroup.save()
            messages.success(request,"Bed Group updated successfully.")
        else:
            Bedgroup.objects.create(
            role=super_admin,
            group_name=group_name,
            colour=colour,
            floor=floor,
            description=description,
        )
            messages.success(
            request,
            "Bed Group added successfully."
        )

    return redirect(reverse("bed_superadmin") + "?section=group")
def add_bedtype1(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    
    if request.method == "POST":
        type_name = request.POST.get("type_name", "").strip()
        bedtype_id = request.POST.get("bedtype_id")
        if bedtype_id:
            bedtype = get_object_or_404(
                Bedtype,
                id=bedtype_id,
                role__role__in=allowed_roles
            )
            bedtype.type_name = type_name
            bedtype.save()

            messages.success(
                request,
                "Bed Type updated successfully."
            )
        else:
            Bedtype.objects.create(
            role=super_admin,
            type_name=type_name
        )
            messages.success(
            request,
            "Bed type added successfully."
        )

    return redirect(reverse("bed_superadmin") + "?section=type")

from django.shortcuts import redirect, get_object_or_404
def add_bed1(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["manager", "admin", "super_admin"]
    
    if request.method == "POST":
        bed_id = request.POST.get("bed_id")
        bed_name = request.POST.get("bed_name", "").strip()
        bedtype_id = request.POST.get("type")
        bedgroup_id = request.POST.get("group")
        not_available = request.POST.get("not_available") == "on"
        bedtype = get_object_or_404(
            Bedtype,
            id=bedtype_id,
            role__role__in=allowed_roles
        )
        bedgroup = get_object_or_404(
            Bedgroup,
            id=bedgroup_id,
            role__role__in=allowed_roles
        )
        if bed_id:

            bed = get_object_or_404(
                Bed,
                id=bed_id,
                role__role__in=allowed_roles
            )

            bed.bed_name = bed_name
            bed.bedtype = bedtype
            bed.bedgroup = bedgroup
            bed.not_available = not_available
            bed.save()
            messages.success(
                request,
                "Bed updated successfully."
            )
        else:
            Bed.objects.create(
            role=super_admin,
            bed_name=bed_name,
            bedtype=bedtype,
            bedgroup=bedgroup,
            
            not_available=not_available
        )
            messages.success(
            request,
            "Bed added successfully."
        )
    return redirect(reverse("bed_superadmin") + "?section=bed")
def delete_bed1(request, bed_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(id=user_id,role="super_admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    bed = get_object_or_404(Bed,id=bed_id,role__role__in=allowed_roles)
    bed.delete()
    messages.success(request,"Bed deleted successfully.")
    return redirect(reverse("bed_superadmin") + "?section=bed")
def delete_bed_type1(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(id=user_id,role="super_admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    bedtype = get_object_or_404(Bedtype,id=id,role__role__in=allowed_roles)
    bedtype.delete()
    messages.success(request,"Bed type deleted successfully.")
    return redirect(reverse("bed_superadmin") + "?section=type")
def delete_bed_group1(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(id=user_id,role="super_admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    bedgroup = get_object_or_404(Bedgroup,id=id,role__role__in=allowed_roles)
    bedgroup.delete()
    messages.success(request,"Bed group deleted successfully.")
    return redirect(reverse("bed_superadmin") + "?section=group")
def delete_floor1(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        super_admin = Registration.objects.get(id=user_id,role="super_admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    floors = get_object_or_404(Floor,id=id,role__role__in=allowed_roles)
    floors.delete()
    messages.success(request,"Floor deleted successfully.")
    return redirect(reverse("bed_superadmin") + "?section=floor")


def bed_admin(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    active_section = request.GET.get("section", "bed")
    bed_search = request.GET.get("bed_search", "").strip()

    beds = Bed.objects.filter(
        role__role__in=allowed_roles
    ).select_related(
        "floor",
        "bedtype",
        "bedgroup"
    )

    if bed_search:
        beds = beds.filter(
            Q(bed_name__icontains=bed_search) |
            Q(bedtype__type_name__icontains=bed_search) |
            Q(bedgroup__group_name__icontains=bed_search)
        )
    status_search = request.GET.get("status_search", "").strip()

    bed_status = Bed.objects.filter(
        role__role__in=allowed_roles
    ).select_related(
        "floor",
        "bedtype",
        "bedgroup"
    )

    if status_search:
        bed_status = bed_status.filter(
            Q(bed_name__icontains=status_search) |
            Q(bedtype__type_name__icontains=status_search) |
            Q(bedgroup__group_name__icontains=status_search)
        )
    floor_search = request.GET.get("floor_search", "").strip()

    floors = Floor.objects.filter(
        role__role__in=allowed_roles
    )

    if floor_search:
        floors = floors.filter(
            Q(floor_name__icontains=floor_search) |
            Q(description__icontains=floor_search)
        )
    group_search = request.GET.get("group_search", "").strip()

    bedgroups = Bedgroup.objects.filter(
        role__role__in=allowed_roles
    )

    if group_search:
        bedgroups = bedgroups.filter(
            Q(group_name__icontains=group_search) |
            Q(colour__icontains=group_search) |
            Q(description__icontains=group_search)
        )

    type_search = request.GET.get("type_search", "").strip()

    bedtypes = Bedtype.objects.filter(
        role__role__in=allowed_roles
    )

    if type_search:
        bedtypes = bedtypes.filter(
            Q(type_name__icontains=type_search)
        )


    return render(
        request,
        "bed_admin.html",
        {
            "manager": admin,
            "beds": beds,
            "bed_status": bed_status,
            "floors": floors,
            "bedgroup": bedgroups,
            "bedtype": bedtypes,
            "bed_search": bed_search,
            "status_search": status_search,
            "floor_search": floor_search,
            "group_search": group_search,
            "type_search": type_search,
            "active_section": active_section,
        }
    )

def add_floor2(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    if request.method == "POST":
        floor_name = request.POST.get("floor_name", "").strip()
        description = request.POST.get("description", "").strip()
        floor_id = request.POST.get(
            "floor_id"
        )

        if floor_id:

            floor = get_object_or_404(
                Floor,
                id=floor_id,
                role__role__in=allowed_roles
            )

            floor.floor_name = floor_name
            floor.description = description

            floor.save()

            messages.success(
                request,
                "Floor updated successfully."
            )

        else:
            Floor.objects.create(
            role=admin,
            floor_name=floor_name,
            description=description,
        )
            messages.success(
            request,
            "Floor added successfully."
        )
        

    return redirect(reverse("bed_admin") + "?section=floor")

def add_bedgroup2(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    if request.method == "POST":
        group_name = request.POST.get("group_name", "").strip()
        colour = request.POST.get("colour", "").strip()
        floor_id = request.POST.get("floor")
        
        bedgroup_id = request.POST.get(
            "bedgroup_id"
        )
        floor = Floor.objects.get(id=floor_id)
        description = request.POST.get("description", "").strip()
        if bedgroup_id:

            bedgroup = get_object_or_404(
                Bedgroup,
                id=bedgroup_id,
                role__role__in=allowed_roles
            )

            bedgroup.group_name = group_name
            bedgroup.colour = colour
            bedgroup.floor = floor
            bedgroup.description = description
            bedgroup.save()
            messages.success(request,"Bed Group updated successfully.")
        else:
            Bedgroup.objects.create(
            role=admin,
            group_name=group_name,
            colour=colour,
            floor=floor,
            description=description,
        )
            messages.success(
            request,
            "Bed Group added successfully."
        )

    return redirect(reverse("bed_admin") + "?section=group")
def add_bedtype2(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    if request.method == "POST":
        type_name = request.POST.get("type_name", "").strip()
        bedtype_id = request.POST.get("bedtype_id")
        if bedtype_id:
            bedtype = get_object_or_404(
                Bedtype,
                id=bedtype_id,
                role__role__in=allowed_roles
            )
            bedtype.type_name = type_name
            bedtype.save()

            messages.success(
                request,
                "Bed Type updated successfully."
            )
        else:
            Bedtype.objects.create(
            role=admin,
            type_name=type_name
        )
            messages.success(
            request,
            "Bed type added successfully."
        )

    return redirect(reverse("bed_admin") + "?section=type")

from django.shortcuts import redirect, get_object_or_404
def add_bed2(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    if request.method == "POST":
        bed_id = request.POST.get("bed_id")
        bed_name = request.POST.get("bed_name", "").strip()
        bedtype_id = request.POST.get("type")
        bedgroup_id = request.POST.get("group")
        not_available = request.POST.get("not_available") == "on"
        bedtype = get_object_or_404(
            Bedtype,
            id=bedtype_id,
            role__role__in=allowed_roles
        )
        bedgroup = get_object_or_404(
            Bedgroup,
            id=bedgroup_id,
            role__role__in=allowed_roles
        )
        if bed_id:

            bed = get_object_or_404(
                Bed,
                id=bed_id,
                role__role__in=allowed_roles
            )

            bed.bed_name = bed_name
            bed.bedtype = bedtype
            bed.bedgroup = bedgroup
            bed.not_available = not_available
            bed.save()
            messages.success(
                request,
                "Bed updated successfully."
            )
        else:
            Bed.objects.create(
            role=admin,
            bed_name=bed_name,
            bedtype=bedtype,
            bedgroup=bedgroup,
            
            not_available=not_available
        )
            messages.success(
            request,
            "Bed added successfully."
        )
    return redirect(reverse("bed_admin") + "?section=bed")
def delete_bed2(request, bed_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(id=user_id,role="admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    bed = get_object_or_404(Bed,id=bed_id,role__role__in=allowed_roles)
    bed.delete()
    messages.success(request,"Bed deleted successfully.")
    return redirect(reverse("bed_admin") + "?section=bed")
def delete_bed_type2(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(id=user_id,role="admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    bedtype = get_object_or_404(Bedtype,id=id,role__role__in=allowed_roles)
    bedtype.delete()
    messages.success(request,"Bed type deleted successfully.")
    return redirect(reverse("bed_admin") + "?section=type")
def delete_bed_group2(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(id=user_id,role="admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    bedgroup = get_object_or_404(Bedgroup,id=id,role__role__in=allowed_roles)
    bedgroup.delete()
    messages.success(request,"Bed group deleted successfully.")
    return redirect(reverse("bed_admin") + "?section=group")
def delete_floor2(request,id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")
    try:
        admin = Registration.objects.get(id=user_id,role="admin")
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")
    allowed_roles = ["super_admin", "admin", "manager"]
    floors = get_object_or_404(Floor,id=id,role__role__in=allowed_roles)
    floors.delete()
    messages.success(request,"Floor deleted successfully.")
    return redirect(reverse("bed_admin") + "?section=floor")


def tpa_management(request):
     user_id = request.session.get("user_id")
     role = request.session.get("role")
    
     if not user_id or not role:
            return redirect("login_page")
    
        # Select the correct home template
     if role == "manager":
            home_template = "manager_home.html"
    
     elif role == "super_admin":
            home_template = "super_admin_home.html"
    
     elif role == "admin":
            home_template = "admin_home.html"
    
     else:
            return redirect("login_page")
    
        # Get the logged-in user
     try:
            user = Registration.objects.get(
                id=user_id,
                role=role
            )
    
     except Registration.DoesNotExist:
            request.session.flush()
            return redirect("login_page")
     
     tpas = TPA.objects.all()
     
     return render(request, "tpa_management.html",
        {
            "home_template": home_template,
            "user": user,
            "tpas": tpas,
            "manager": user
        })


@require_http_methods(["POST"])
def save_tpa(request):

    tpa_id = request.POST.get("tpa_id")

    tpa_name = request.POST.get("tpa_name", "").strip()
    code = request.POST.get("code", "").strip()
    contact_number = request.POST.get("contact_number", "").strip()
    address = request.POST.get("address", "").strip()
    contact_person = request.POST.get("contact_person", "").strip()
    contact_person_mobile = request.POST.get(
        "contact_person_mobile", ""
    ).strip()

    # ==============================
    # VALIDATION
    # ==============================

    if not tpa_name:
        return JsonResponse({
            "success": False,
            "message": "TPA name is required."
        })

    if not code:
        return JsonResponse({
            "success": False,
            "message": "TPA code is required."
        })

    if not contact_number:
        return JsonResponse({
            "success": False,
            "message": "Contact number is required."
        })

    if not address:
        return JsonResponse({
            "success": False,
            "message": "Address is required."
        })

    if not contact_person:
        return JsonResponse({
            "success": False,
            "message": "Contact person is required."
        })

    if not contact_person_mobile:
        return JsonResponse({
            "success": False,
            "message": "Contact person mobile number is required."
        })

    # ==============================
    # EDIT
    # ==============================

    if tpa_id:

        tpa = get_object_or_404(
            TPA,
            id=tpa_id
        )

        tpa.tpa_name = tpa_name
        tpa.code = code
        tpa.contact_number = contact_number
        tpa.address = address
        tpa.contact_person = contact_person
        tpa.contact_person_mobile = contact_person_mobile

        tpa.save()

        messages.success(request,"TPA updated successfully.")
        
        return JsonResponse({
            "success": True,
            "message": "TPA updated successfully."
        })

    # ==============================
    # ADD
    # ==============================

    TPA.objects.create(
        tpa_name=tpa_name,
        code=code,
        contact_number=contact_number,
        address=address,
        contact_person=contact_person,
        contact_person_mobile=contact_person_mobile
    )

    messages.success(request,"TPA added successfully.")
    
    return JsonResponse({
        "success": True,
        "message": "TPA added successfully."
    })


def get_tpa(request, tpa_id):

    tpa = get_object_or_404(
        TPA,
        id=tpa_id
    )

    return JsonResponse({
        "success": True,

        "tpa": {
            "id": tpa.id,
            "tpa_name": tpa.tpa_name,
            "code": tpa.code,
            "contact_number": tpa.contact_number,
            "address": tpa.address,
            "contact_person": tpa.contact_person,
            "contact_person_mobile": tpa.contact_person_mobile,
        }
    })


@require_http_methods(["POST"])
def delete_tpa(request, tpa_id):

    tpa = get_object_or_404(
        TPA,
        id=tpa_id
    )

    tpa_name = tpa.tpa_name

    tpa.delete()

    return JsonResponse({
        "success": True,
        "message": f"{tpa_name} deleted successfully."
    })


def hospital_charges(request):
         user_id = request.session.get("user_id")
         role = request.session.get("role")
        
         if not user_id or not role:
                return redirect("login_page")
        
            # Select the correct home template
         if role == "manager":
                home_template = "manager_home.html"
        
         elif role == "super_admin":
                home_template = "super_admin_home.html"
        
         elif role == "admin":
                home_template = "admin_home.html"
        
         else:
                return redirect("login_page")
        
            # Get the logged-in user
         try:
                user = Registration.objects.get(
                    id=user_id,
                    role=role
                )
        
         except Registration.DoesNotExist:
                request.session.flush()
                return redirect("login_page")

         units = HospitalChargeUnit.objects.all().order_by("name")

         taxes = HospitalTax.objects.all().order_by("name")

         charge_types = HospitalChargeType.objects.all().order_by("name")

         categories = HospitalChargeCategory.objects.select_related(
           "charge_type"
         ).all().order_by("name")

         charges = HospitalCharge.objects.select_related(
           "charge_type",
           "category",
           "unit",
           "tax"
         ).prefetch_related(
          "tpa_charges__tpa"
         ).all().order_by("name")

         tpas = TPA.objects.all().order_by("tpa_name")
         
         return render(request, "hospital_charges.html",{
         
                "home_template": home_template,
                "user": user,
                "manager": user,
                "units": units,
                "taxes": taxes,
                "charge_types": charge_types,
                "charge_categories": categories,
                "hospital_charges": charges,
                "tpas": tpas,
         })


def hospital_charges_data(request, charge_type):

    # =====================================================
    # UNIT
    # =====================================================

    if charge_type == "unit":

        units = (
            HospitalChargeUnit.objects
            .all()
            .order_by("name")
        )

        rows = []

        for unit in units:

            rows.append({
                "id": unit.id,
                "name": unit.name,
            })

        return JsonResponse({
            "success": True,
            "rows": rows
        })


    # =====================================================
    # TAX
    # =====================================================

    elif charge_type == "tax":

        taxes = (
            HospitalTax.objects
            .all()
            .order_by("name")
        )

        rows = []

        for tax in taxes:

            rows.append({
                "id": tax.id,
                "name": tax.name,
                "percentage": str(tax.percentage),
            })

        return JsonResponse({
            "success": True,
            "rows": rows
        })


    # =====================================================
    # CHARGE TYPE
    # =====================================================

    elif charge_type == "charge_type":

        charge_types = (
            HospitalChargeType.objects
            .all()
            .order_by("name")
        )

        rows = []

        for obj in charge_types:

            modules = []

            if obj.appointment:
                modules.append("Appointment")

            if obj.opd:
                modules.append("OPD")

            if obj.ipd:
                modules.append("IPD")

            if obj.pathology:
                modules.append("Pathology")

            if obj.radiology:
                modules.append("Radiology")

            if obj.blood_bank:
                modules.append("Blood Bank")

            if obj.ambulance:
                modules.append("Ambulance")

            rows.append({
                "id": obj.id,
                "name": obj.name,

                "charge_type": obj.name,

                "appointment": obj.appointment,
                "opd": obj.opd,
                "ipd": obj.ipd,
                "pathology": obj.pathology,
                "radiology": obj.radiology,
                "blood_bank": obj.blood_bank,
                "ambulance": obj.ambulance,

                "modules": modules,
            })

        return JsonResponse({
            "success": True,
            "rows": rows
        })


    # =====================================================
    # CHARGE CATEGORY
    # =====================================================

    elif charge_type == "charge_category":

        categories = (
            HospitalChargeCategory.objects
            .select_related("charge_type")
            .all()
            .order_by("name")
        )

        rows = []

        for category in categories:

            rows.append({
                "id": category.id,

                "name": category.name,
                "category_name": category.name,

                "charge_type_id":
                    category.charge_type_id,

                "charge_type":
                    category.charge_type.name,

                "description":
                    category.description or "",
            })

        return JsonResponse({
            "success": True,
            "rows": rows
        })


    # =====================================================
    # CHARGE
    # =====================================================

    elif charge_type == "charge":

        charges = (
            HospitalCharge.objects
            .select_related(
                "charge_type",
                "category",
                "unit",
                "tax"
            )
            .prefetch_related(
                "tpa_charges__tpa"
            )
            .all()
            .order_by("name")
        )

        rows = []

        for charge in charges:

            tpa_charges = {}

            tpa_list = []

            for tpa_charge in charge.tpa_charges.all():

                tpa_charges[
                    str(tpa_charge.tpa_id)
                ] = str(
                    tpa_charge.amount
                )

                tpa_list.append({
                    "id": tpa_charge.tpa_id,
                    "name": tpa_charge.tpa.tpa_name,
                    "amount": str(tpa_charge.amount),
                })

            rows.append({

                "id": charge.id,

                "name": charge.name,
                "charge_name": charge.name,

                "charge_type_id":
                    charge.charge_type_id,

                "charge_type":
                    charge.charge_type.name,

                "category_id":
                    charge.category_id,

                "category":
                    charge.category.name,

                "category_name":
                    charge.category.name,

                "unit_id":
                    charge.unit_id,

                "unit":
                    charge.unit.name,

                "unit_name":
                    charge.unit.name,

                "tax_id":
                    charge.tax_id,

                "tax":
                    charge.tax.name
                    if charge.tax
                    else "",

                "tax_name":
                    charge.tax.name
                    if charge.tax
                    else "",

                "standard_charge":
                    str(charge.standard_charge),

                "description":
                    charge.description or "",

                "tpas":
                    tpa_list,

                "tpa_charges":
                    tpa_charges,
            })

        return JsonResponse({
            "success": True,
            "rows": rows
        })


    # =====================================================
    # INVALID
    # =====================================================

    return JsonResponse(
        {
            "success": False,
            "message": "Invalid charge section."
        },
        status=400
    )

@require_http_methods(["POST"])
def save_hospital_charge(request, charge_type):

    try:

        item_id = request.POST.get("id")

        # =================================================
        # UNIT
        # =================================================

        if charge_type == "unit":

            name = request.POST.get(
                "unit_name"
            ) or request.POST.get(
                "name"
            )

            if not name:
                return JsonResponse({
                    "success": False,
                    "message": "Unit name is required."
                })

            if item_id:

                obj = get_object_or_404(
                    HospitalChargeUnit,
                    id=item_id
                )

                obj.name = name
                obj.save()

            else:

                obj = HospitalChargeUnit.objects.create(
                    name=name
                )

            return JsonResponse({
                "success": True,
                "message": "Unit saved successfully.",
                "id": obj.id
            })


        # =================================================
        # TAX
        # =================================================

        elif charge_type == "tax":

            name = request.POST.get(
                "tax_name"
            )

            percentage = request.POST.get(
                "percentage"
            )

            if not name:
                return JsonResponse({
                    "success": False,
                    "message": "Tax name is required."
                })

            if percentage == "":
                return JsonResponse({
                    "success": False,
                    "message": "Percentage is required."
                })

            if item_id:

                obj = get_object_or_404(
                    HospitalTax,
                    id=item_id
                )

                obj.name = name
                obj.percentage = percentage

                obj.save()

            else:

                obj = HospitalTax.objects.create(
                    name=name,
                    percentage=percentage
                )

            return JsonResponse({
                "success": True,
                "message": "Tax saved successfully.",
                "id": obj.id
            })


        # =================================================
        # CHARGE TYPE
        # =================================================

        elif charge_type == "charge_type":

            name = request.POST.get(
                "charge_type"
            )

            modules_raw = request.POST.get(
                "modules",
                "[]"
            )

            try:
                modules = json.loads(
                    modules_raw
                )
            except (json.JSONDecodeError, TypeError):
                modules = []

            if not name:
                return JsonResponse({
                    "success": False,
                    "message": "Charge type is required."
                })

            if item_id:

                obj = get_object_or_404(
                    HospitalChargeType,
                    id=item_id
                )

            else:

                obj = HospitalChargeType()

            obj.name = name

            obj.appointment = (
                "Appointment" in modules
            )

            obj.opd = (
                "OPD" in modules
            )

            obj.ipd = (
                "IPD" in modules
            )

            obj.pathology = (
                "Pathology" in modules
            )

            obj.radiology = (
                "Radiology" in modules
            )

            obj.blood_bank = (
                "Blood Bank" in modules
            )

            obj.ambulance = (
                "Ambulance" in modules
            )

            obj.save()

            return JsonResponse({
                "success": True,
                "message": "Charge type saved successfully.",
                "id": obj.id
            })


        # =================================================
        # CHARGE CATEGORY
        # =================================================

        elif charge_type == "charge_category":

            name = request.POST.get(
                "category_name"
            )

            charge_type_id = request.POST.get(
                "charge_type"
            )

            description = request.POST.get(
                "description",
                ""
            )

            if not name:
                return JsonResponse({
                    "success": False,
                    "message": "Category name is required."
                })

            if not charge_type_id:
                return JsonResponse({
                    "success": False,
                    "message": "Charge type is required."
                })

            charge_type_obj = get_object_or_404(
                HospitalChargeType,
                id=charge_type_id
            )

            if item_id:

                obj = get_object_or_404(
                    HospitalChargeCategory,
                    id=item_id
                )

                obj.name = name
                obj.charge_type = charge_type_obj
                obj.description = description

                obj.save()

            else:

                obj = HospitalChargeCategory.objects.create(
                    name=name,
                    charge_type=charge_type_obj,
                    description=description
                )

            return JsonResponse({
                "success": True,
                "message": "Charge category saved successfully.",
                "id": obj.id
            })


        # =================================================
        # CHARGE
        # =================================================

        elif charge_type == "charge":

            name = request.POST.get(
                "charge_name"
            )

            charge_type_id = request.POST.get(
                "charge_type"
            )

            category_id = request.POST.get(
                "category"
            )

            unit_id = request.POST.get(
                "unit"
            )

            tax_id = request.POST.get(
                "tax"
            )

            standard_charge = request.POST.get(
                "standard_charge"
            )

            description = request.POST.get(
                "description",
                ""
            )

            tpa_charges_raw = request.POST.get(
                "tpa_charges",
                "{}"
            )

            if not name:
                return JsonResponse({
                    "success": False,
                    "message": "Charge name is required."
                })

            if not charge_type_id:
                return JsonResponse({
                    "success": False,
                    "message": "Charge type is required."
                })

            if not category_id:
                return JsonResponse({
                    "success": False,
                    "message": "Category is required."
                })

            if not unit_id:
                return JsonResponse({
                    "success": False,
                    "message": "Unit is required."
                })

            if not standard_charge:
                return JsonResponse({
                    "success": False,
                    "message": "Standard charge is required."
                })

            charge_type_obj = get_object_or_404(
                HospitalChargeType,
                id=charge_type_id
            )

            category_obj = get_object_or_404(
                HospitalChargeCategory,
                id=category_id
            )

            unit_obj = get_object_or_404(
                HospitalChargeUnit,
                id=unit_id
            )

            tax_obj = None

            if tax_id:
                tax_obj = get_object_or_404(
                    HospitalTax,
                    id=tax_id
                )

            try:

                tpa_charges = json.loads(
                    tpa_charges_raw
                )

            except (json.JSONDecodeError, TypeError):

                tpa_charges = {}

            with transaction.atomic():

                if item_id:

                    obj = get_object_or_404(
                        HospitalCharge,
                        id=item_id
                    )

                    obj.name = name
                    obj.charge_type = charge_type_obj
                    obj.category = category_obj
                    obj.unit = unit_obj
                    obj.tax = tax_obj
                    obj.standard_charge = standard_charge
                    obj.description = description

                    obj.save()

                else:

                    obj = HospitalCharge.objects.create(
                        name=name,
                        charge_type=charge_type_obj,
                        category=category_obj,
                        unit=unit_obj,
                        tax=tax_obj,
                        standard_charge=standard_charge,
                        description=description
                    )

                # =========================================
                # TPA CHARGES
                # =========================================

                HospitalChargeTPA.objects.filter(
                    charge=obj
                ).delete()

                for tpa_id, amount in tpa_charges.items():

                    if amount in [
                        "",
                        None
                    ]:
                        continue

                    try:

                        tpa = TPA.objects.get(
                            id=tpa_id
                        )

                    except TPA.DoesNotExist:

                        continue

                    HospitalChargeTPA.objects.create(
                        charge=obj,
                        tpa=tpa,
                        amount=amount
                    )

            return JsonResponse({
                "success": True,
                "message": "Charge saved successfully.",
                "id": obj.id
            })


        # =================================================
        # INVALID
        # =================================================

        return JsonResponse({
            "success": False,
            "message": "Invalid charge section."
        }, status=400)


    except IntegrityError as e:

        return JsonResponse({
            "success": False,
            "message": (
                "This record already exists or "
                "cannot be saved because it is being used."
            )
        }, status=400)


    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)


@require_GET
def get_hospital_charge(request, charge_id):

    try:

        charge = get_object_or_404(
            HospitalCharge,
            id=charge_id
        )

        # -----------------------------------------
        # TPA CHARGES
        # -----------------------------------------

        tpa_charges = []

        for item in HospitalChargeTPA.objects.filter(
            charge=charge
        ).select_related("tpa"):

            tpa_charges.append({
                "tpa_name": item.tpa.tpa_name,
                "amount": str(item.amount)
            })

        # -----------------------------------------
        # RESPONSE
        # -----------------------------------------

        return JsonResponse({

            "success": True,

            "charge": {

                "id": charge.id,

                "charge_name": charge.name,

                "charge_type": (
                    charge.charge_type.name
                    if charge.charge_type
                    else "-"
                ),

                "category": (
                    charge.category.name
                    if charge.category
                    else "-"
                ),

                "unit": (
                    charge.unit.name
                    if charge.unit
                    else "-"
                ),

                "tax": (
                    charge.tax.name
                    if charge.tax
                    else "No Tax"
                ),

                "tax_percentage": (
                    str(charge.tax.percentage)
                    if charge.tax
                    else "-"
                ),

                "standard_charge": str(
                    charge.standard_charge
                ),

                "description": (
                    charge.description
                    or "-"
                ),

                "tpa_charges": tpa_charges

            }

        })

    except Exception as e:

        return JsonResponse({

            "success": False,
            "message": str(e)

        }, status=500)

    
def hospital_charge_detail(request, charge_type, item_id):

    # =====================================================
    # UNIT
    # =====================================================

    if charge_type == "unit":

        obj = get_object_or_404(
            HospitalChargeUnit,
            id=item_id
        )

        return JsonResponse({
            "success": True,
            "item": {
                "id": obj.id,
                "name": obj.name,

                # Your current model doesn't have unit_type
                "unit_type": "",
                "unit_name": obj.name,
            }
        })


    # =====================================================
    # TAX
    # =====================================================

    elif charge_type == "tax":

        obj = get_object_or_404(
            HospitalTax,
            id=item_id
        )

        return JsonResponse({
            "success": True,
            "item": {
                "id": obj.id,
                "name": obj.name,
                "tax_name": obj.name,
                "percentage": str(obj.percentage),
            }
        })


    # =====================================================
    # CHARGE TYPE
    # =====================================================

    elif charge_type == "charge_type":

        obj = get_object_or_404(
            HospitalChargeType,
            id=item_id
        )

        modules = []

        if obj.appointment:
            modules.append("Appointment")

        if obj.opd:
            modules.append("OPD")

        if obj.ipd:
            modules.append("IPD")

        if obj.pathology:
            modules.append("Pathology")

        if obj.radiology:
            modules.append("Radiology")

        if obj.blood_bank:
            modules.append("Blood Bank")

        if obj.ambulance:
            modules.append("Ambulance")

        return JsonResponse({
            "success": True,
            "item": {
                "id": obj.id,
                "name": obj.name,
                "charge_type": obj.name,
                "modules": modules,
            }
        })


    # =====================================================
    # CATEGORY
    # =====================================================

    elif charge_type == "charge_category":

        obj = get_object_or_404(
            HospitalChargeCategory.objects
            .select_related("charge_type"),
            id=item_id
        )

        return JsonResponse({
            "success": True,
            "item": {
                "id": obj.id,
                "name": obj.name,
                "category_name": obj.name,

                "charge_type_id":
                    obj.charge_type_id,

                "charge_type":
                    obj.charge_type.name,

                "description":
                    obj.description or "",
            }
        })


    # =====================================================
    # CHARGE
    # =====================================================

    elif charge_type == "charge":

        obj = get_object_or_404(
            HospitalCharge.objects
            .select_related(
                "charge_type",
                "category",
                "unit",
                "tax"
            )
            .prefetch_related(
                "tpa_charges__tpa"
            ),
            id=item_id
        )

        tpa_charges = {}

        for tpa_charge in obj.tpa_charges.all():

            tpa_charges[
                str(tpa_charge.tpa_id)
            ] = str(
                tpa_charge.amount
            )

        return JsonResponse({
            "success": True,

            "item": {

                "id": obj.id,

                "name": obj.name,
                "charge_name": obj.name,

                "charge_type_id":
                    obj.charge_type_id,

                "charge_type":
                    obj.charge_type.name,

                "category_id":
                    obj.category_id,

                "category":
                    obj.category.name,

                "category_name":
                    obj.category.name,

                "unit_id":
                    obj.unit_id,

                "unit":
                    obj.unit.name,

                "unit_name":
                    obj.unit.name,

                "tax_id":
                    obj.tax_id,

                "tax":
                    obj.tax.name
                    if obj.tax
                    else "",

                "tax_name":
                    obj.tax.name
                    if obj.tax
                    else "",

                "standard_charge":
                    str(obj.standard_charge),

                "description":
                    obj.description or "",

                "tpa_charges":
                    tpa_charges,
            }
        })


    return JsonResponse({
        "success": False,
        "message": "Invalid charge section."
    }, status=400)


@require_http_methods(["POST"])
def delete_hospital_charge_item(
    request,
    charge_type,
    item_id
):

    try:

        if charge_type == "unit":

            obj = get_object_or_404(
                HospitalChargeUnit,
                id=item_id
            )

        elif charge_type == "tax":

            obj = get_object_or_404(
                HospitalTax,
                id=item_id
            )

        elif charge_type == "charge_type":

            obj = get_object_or_404(
                HospitalChargeType,
                id=item_id
            )

        elif charge_type == "charge_category":

            obj = get_object_or_404(
                HospitalChargeCategory,
                id=item_id
            )

        elif charge_type == "charge":

            obj = get_object_or_404(
                HospitalCharge,
                id=item_id
            )

        else:

            return JsonResponse({
                "success": False,
                "message": "Invalid charge type."
            }, status=400)

        obj.delete()

        return JsonResponse({
            "success": True,
            "message": "Deleted successfully."
        })

    except IntegrityError:

        return JsonResponse({
            "success": False,
            "message": (
                "This item cannot be deleted because "
                "it is being used by another record."
            )
        }, status=400)

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)


def tpa_data(request):

    tpas = TPA.objects.all().order_by(
        "tpa_name"
    )

    rows = []

    for tpa in tpas:

        rows.append({
            "id": tpa.id,
            "tpa_name": tpa.tpa_name,
            "name": tpa.tpa_name,
            "code": tpa.code,
            "contact_number": tpa.contact_number,
            "address": tpa.address,
            "contact_person": tpa.contact_person,
            "contact_person_mobile":
                tpa.contact_person_mobile,
        })

    return JsonResponse({
        "success": True,
        "rows": rows
    })
    
def manager_radiology(request):
    user_id=request.session.get('user_id')
    role=request.session.get('role')
    cat=RadiologyCategory.objects.filter(created_by_id=user_id)
    unit=RadiologyUnit.objects.filter(created_by_id=user_id)
    param=RadiologyParameter.objects.filter(created_by_id=user_id)
    if role == 'super_admin':
            base = 'super_admin_home.html'
    elif role == 'admin':
            base = 'admin_home.html'
    elif role == 'manager':
            base = 'manager_home.html'
    elif role == 'radiologist':
                base = 'dashboard.html'
  

    active_category=request.GET.get('category')
    manager = Registration.objects.get(
                id=user_id,
               
            )
    return render(request,'manager_radiology.html',{
    "user_id":user_id,
    "param":param,
    "role":role,
    "manager":manager,
    "cat":cat,
    "unit":unit,
    "base":base,
    
    "active_category":active_category,
        
    })
def manager_category(request):
      user_id=request.session.get('user_id')
      if request.method=='POST':
        desc=request.POST.get('desc')
        name= request.POST.get('name')

        

        
        
        
        RadiologyCategory.objects.create(
                title=name,description=desc,created_by_id=user_id,category='Category'
            )
        return JsonResponse({
          'title': name,
                    'description': desc,
                    
                    'success':True,   
                    'message':'Category  Added successfully'               
                   

    })
def manager_editcategory(request):
          user_id=request.session.get('user_id')
          if request.method=='POST':
            desc=request.POST.get('desc')
            name= request.POST.get('name')
            catid=request.POST.get('catid')
    
            
            
            
            cat=RadiologyCategory.objects.get(id=catid)
            cat.description=desc
            cat.title=name
            cat.save()
                   
                
            return JsonResponse({
              'title': name,
                        'description': desc,
                        
                        'success':True,   
                        'message':'Category  Updated successfully'               
                       
    
        })
def delete_radiocatgegory(request):
    id=request.POST.get('id')
    radio=RadiologyCategory.objects.get(id=id)
    radio.delete()
    return JsonResponse({
        'success':True
    })
def manager_unit(request):
    user_id=request.session.get('user_id')
    if request.method=='POST':
            desc=request.POST.get('desc')
            name= request.POST.get('name')
            
    
            
            
            
            RadiologyUnit.objects.create(
                    title=name,description=desc,created_by_id=user_id,category='Unit'
                )
            return JsonResponse({
              'title': name,
                        'description': desc,
                        
                        'success':True,   
                        'message':'Unit  Added successfully'               
                       
    
        })
def manager_editunit(request):
    if request.method=='POST':
                desc=request.POST.get('desc')
                name= request.POST.get('name')
                unitid=request.POST.get('unitid')
        
                
                
                
                cat=RadiologyUnit.objects.get(id=unitid)
                cat.description=desc
                cat.title=name
                cat.save()
                       
                    
                return JsonResponse({
                  'title': name,
                            'description': desc,
                            
                            'success':True,   
                            'message':'Unit  Updated successfully'               
                           
        
            })
def delete_radiounit(request):
    id=request.POST.get('id')
    radio=RadiologyUnit.objects.get(id=id)
    radio.delete()
    return JsonResponse({
        'success':True
    })
def manager_parameter(request):
    user_id=request.session.get('user_id')
    if request.method=='POST':
                desc=request.POST.get('desc')
                name= request.POST.get('name')
                unit_id=request.POST.get('unit')
                unit=RadiologyUnit.objects.get(id=unit_id)
                fromrange=request.POST.get('fromdate')
                torange=request.POST.get('todate')
                
                
                RadiologyParameter.objects.create(
                        title=name,description=desc,created_by_id=user_id,category='parameter',unit=unit,
                        fromrange=fromrange,torange=torange
                    )
                return JsonResponse({
                  'title': name,
                            'description': desc,
                            'unit':unit.title,
                            'fromrange':fromrange,
                            'torange':torange,
                            
                            'success':True,   
                            'message':'Unit  Added successfully'               
                           
        
            })
def manager_editparameter(request):
    if request.method=='POST':
                desc=request.POST.get('desc')
                name= request.POST.get('name')
                unit=request.POST.get('unit')
                paramid=request.POST.get('paramid')
                fromrange=request.POST.get('fromdate')
                torange=request.POST.get('todate')
        
                
                cat=RadiologyParameter.objects.get(id=paramid)
                cat.description=desc
                cat.title=name
                cat.fromrange=fromrange
                cat.torange=torange
                cat.unit_id=unit
                cat.save()
                       
                    
                return JsonResponse({
                  'title': name,
                            'description': desc,
                            
                            'success':True,   
                            'message':'Unit  Updated successfully'               
                           
        
            })
def delete_radioparameter(request):
    id=request.POST.get('id')
    radio=RadiologyParameter.objects.get(id=id)
    radio.delete()
    return JsonResponse({
        'success':True
    })

def pathologist_radiology(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    cat = PathologyCategory.objects.filter(created_by_id=user_id)
    unit = PathologyUnit.objects.filter(created_by_id=user_id)
    param = PathologyParameter.objects.filter(created_by_id=user_id)

    if role == 'super_admin':
        base = 'super_admin_home.html'
    elif role == 'admin':
        base = 'admin_home.html'
    elif role == 'manager':
        base = 'manager_home.html'
    elif role == 'radiologist':
        base = 'dashboard.html'
    elif role == 'pathenologist':
        base = 'pathenologist_home.html'

    active_category = request.GET.get('category')

    manager = Registration.objects.get(id=user_id)

    return render(request, 'pathologist_radiology.html', {
        "user_id": user_id,
        "param": param,
        "role": role,
        "manager": manager,
        "cat": cat,
        "unit": unit,
        "base": base,
        "active_category": active_category,
    })


def pathologist_category(request):
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        desc = request.POST.get('desc')
        name = request.POST.get('name')

        PathologyCategory.objects.create(
            title=name,
            description=desc,
            created_by_id=user_id,
            category='Category'
        )

        return JsonResponse({
            'title': name,
            'description': desc,
            'success': True,
            'message': 'Category Added successfully'
        })


def pathologist_editcategory(request):
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        desc = request.POST.get('desc')
        name = request.POST.get('name')
        catid = request.POST.get('catid')

        cat = PathologyCategory.objects.get(id=catid)
        cat.description = desc
        cat.title = name
        cat.save()

        return JsonResponse({
            'title': name,
            'description': desc,
            'success': True,
            'message': 'Category Updated successfully'
        })


def delete_pathologist_category(request):
    id = request.POST.get('id')

    radio = PathologyCategory.objects.get(id=id)
    radio.delete()

    return JsonResponse({
        'success': True
    })


def pathologist_unit(request):
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        desc = request.POST.get('desc')
        name = request.POST.get('name')

        PathologyUnit.objects.create(
            title=name,
            description=desc,
            created_by_id=user_id,
            category='Unit'
        )

        return JsonResponse({
            'title': name,
            'description': desc,
            'success': True,
            'message': 'Unit Added successfully'
        })


def pathologist_editunit(request):
    if request.method == 'POST':
        desc = request.POST.get('desc')
        name = request.POST.get('name')
        unitid = request.POST.get('unitid')

        cat = PathologyUnit.objects.get(id=unitid)
        cat.description = desc
        cat.title = name
        cat.save()

        return JsonResponse({
            'title': name,
            'description': desc,
            'success': True,
            'message': 'Unit Updated successfully'
        })


def delete_pathologist_unit(request):
    id = request.POST.get('id')

    radio = PathologyUnit.objects.get(id=id)
    radio.delete()

    return JsonResponse({
        'success': True
    })


def pathologist_parameter(request):
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        desc = request.POST.get('desc')
        name = request.POST.get('name')
        unit_id = request.POST.get('unit')
        fromrange=request.POST.get('fromdate')
        torange=request.POST.get('todate')

        unit = PathologyUnit.objects.get(id=unit_id)

        PathologyParameter.objects.create(
            title=name,
            description=desc,
            created_by_id=user_id,
            category='parameter',
            unit=unit,
            fromrange=fromrange,torange=torange
        )

        return JsonResponse({
            'title': name,
            'description': desc,
            'unit': unit.title,
            'success': True,
            "fromrange":fromrange,
            "torange":torange,
            'message': 'Parameter Added successfully'
        })


def pathologist_editparameter(request):
    if request.method == 'POST':
        desc = request.POST.get('desc')
        name = request.POST.get('name')
        unit = request.POST.get('unit')
        paramid = request.POST.get('paramid')
        fromrange=request.POST.get('fromdate')
        torange=request.POST.get('todate')

        cat = PathologyParameter.objects.get(id=paramid)
        cat.description = desc
        cat.title = name
        cat.unit_id = unit
        cat.fromrange=fromrange
        cat.torange=torange
        cat.save()

        return JsonResponse({
            'title': name,
            'description': desc,
            'success': True,
            'message': 'Parameter Updated successfully'
        })


def delete_pathologist_parameter(request):
    id = request.POST.get('id')

    radio = PathologyParameter.objects.get(id=id)
    radio.delete()

    return JsonResponse({
        'success': True
    })
    
# Ambulance Views
def ambulance_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    user_role = str(getattr(current_user, 'role', '')).lower()
    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    search_query = request.GET.get("q", "").strip()
    per_page = request.GET.get("per_page", "10").strip().lower()
    if per_page not in ['10', '50', '100', 'all']:
        per_page = '10'

    ambulances_qs = Ambulance.objects.all()
    if search_query:
        ambulances_qs = ambulances_qs.filter(
            Q(Driver_name__icontains=search_query) |
            Q(Vehicle_number__icontains=search_query) |
            Q(Vehicle_model__icontains=search_query) |
            Q(Driver_License__icontains=search_query) |
            Q(Contact_number__icontains=search_query) |
            Q(Vehicle_type__icontains=search_query) |
            Q(Year_Manufactor__icontains=search_query) |
            Q(Notes__icontains=search_query)
        )

    ambulances_qs = ambulances_qs.annotate(
        role_priority=Case(
            When(created_by__role='manager', then=Value(1)),
            When(created_by__role='super_admin', then=Value(2)),
            When(created_by__role='admin', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('role_priority', '-created_at')

    if per_page == 'all':
        per_page_int = max(1, ambulances_qs.count())
    else:
        per_page_int = int(per_page)

    paginator = Paginator(ambulances_qs, per_page_int)
    page_number = request.GET.get('page', 1)
    try:
        ambulances_page = paginator.page(page_number)
    except PageNotAnInteger:
        ambulances_page = paginator.page(1)
    except EmptyPage:
        ambulances_page = paginator.page(max(1, paginator.num_pages))

    context = {
        "base_template": base_template,
        "manager": current_user,
        "ambulances": ambulances_page,
        "page_obj": ambulances_page,
        "paginator": paginator,
        "search_query": search_query,
        "per_page": per_page,
    }

    return render(request, "ambulance.html", context)


def check_ambulance_vehicle_number(request):
    vehicle_number = request.GET.get("vehicle_number", "").strip()
    item_id = request.GET.get("item_id", "").strip()

    exists = False
    if vehicle_number:
        qs = Ambulance.objects.filter(Vehicle_number__iexact=vehicle_number)
        if item_id:
            qs = qs.exclude(id=item_id)
        exists = qs.exists()

    return JsonResponse({"exists": exists})


def save_ambulance(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        driver_name = request.POST.get('Driver_name', '').strip()
        vehicle_number = request.POST.get('Vehicle_number', '').strip().upper()
        vehicle_model = request.POST.get('Vehicle_model', '').strip()
        year_manufactor = request.POST.get('Year_Manufactor', '').strip()
        driver_license = request.POST.get('Driver_License', '').strip().upper()
        contact_number = request.POST.get('Contact_number', '').strip()
        vehicle_type = request.POST.get('Vehicle_type', '').strip()
        notes = request.POST.get('Notes', '').strip()

        if not driver_name or not vehicle_number or not vehicle_model or not notes:
            return JsonResponse({'status': 'error', 'message': 'Driver Name, Vehicle Number, Vehicle Model, and Notes are required fields.'}, status=400)

        # Check vehicle number uniqueness
        v_qs = Ambulance.objects.filter(Vehicle_number__iexact=vehicle_number)
        if item_id:
            v_qs = v_qs.exclude(id=item_id)
        if v_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'An ambulance with vehicle number "{vehicle_number}" already exists.'}, status=400)

        if len(contact_number) != 10 or not contact_number.isdigit():
            return JsonResponse({'status': 'error', 'message': 'Contact number must be exactly 10 digits.'}, status=400)

        if year_manufactor:
            if len(year_manufactor) != 4 or not year_manufactor.isdigit() or int(year_manufactor) < 1950 or int(year_manufactor) > 2027:
                return JsonResponse({'status': 'error', 'message': 'Year Manufactured must be a valid 4-digit year (1950 - 2026).'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        if item_id:
            ambulance = get_object_or_404(Ambulance, id=item_id)

            can_edit = False
            if current_user.role in ["manager", "super_admin", "admin"]:
                can_edit = True

            if not can_edit:
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this ambulance record.'}, status=403)

            ambulance.Driver_name = driver_name
            ambulance.Vehicle_number = vehicle_number
            ambulance.Vehicle_model = vehicle_model
            ambulance.Year_Manufactor = year_manufactor
            ambulance.Driver_License = driver_license
            ambulance.Contact_number = contact_number
            ambulance.Vehicle_type = vehicle_type
            ambulance.Notes = notes
            ambulance.save()
            messages.success(request, "Ambulance record updated successfully.")
        else:
            Ambulance.objects.create(
                Driver_name=driver_name,
                Vehicle_number=vehicle_number,
                Vehicle_model=vehicle_model,
                Year_Manufactor=year_manufactor,
                Driver_License=driver_license,
                Contact_number=contact_number,
                Vehicle_type=vehicle_type,
                Notes=notes,
                created_by=current_user
            )
            messages.success(request, "Ambulance record added successfully.")

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_ambulance(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

        current_user = get_object_or_404(Registration, id=user_id)
        ambulance = get_object_or_404(Ambulance, pk=pk)

        can_delete = False
        if current_user.role in ["manager", "super_admin", "admin"]:
            can_delete = True

        if not can_delete:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        ambulance.delete()
        messages.success(request, "Ambulance record deleted successfully.")
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
#End

def human_resource(request):

    # ==========================================
    # 1. SESSION AUTHENTICATION
    # ==========================================

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    # ==========================================
    # 2. GET CURRENT USER
    # ==========================================

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") |
            Q(role__iexact="admin") |
            Q(role__iexact="manager"),
            id=user_id
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    # ==========================================
    # 3. GET USER ROLE
    # ==========================================

    user_role = str(
        getattr(current_user, "role", "")
    ).lower().strip()

    # ==========================================
    # 4. SELECT BASE TEMPLATE
    # ==========================================

    if user_role == "super_admin":
        base_template = "super_admin_home.html"

    elif user_role == "admin":
        base_template = "admin_home.html"

    elif user_role == "manager":
        base_template = "manager_home.html"

    else:
        request.session.flush()
        return redirect("login_page")

    # ==========================================
    # 5. GET ACTIVE CATEGORY
    # ==========================================

    active_category = request.GET.get(
        "category",
        "leave_type"
    )

    # ==========================================
    # 6. VALID CATEGORIES
    # ==========================================

    valid_categories = [
        "leave_type",
        "department",
        "designation",
        "specialist"
    ]

    if active_category not in valid_categories:
        active_category = "leave_type"

    # ==========================================
    # 7. SEARCH
    # ==========================================

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    # ==========================================
    # 8. GET ONLY CURRENT USER'S RECORDS
    # ==========================================

    items = HumanResource.objects.filter(
        created_by=current_user,
        category=active_category
    )

    # ==========================================
    # 9. SEARCH
    # ==========================================

    if search_query:
        items = items.filter(
            name__icontains=search_query
        )

    # ==========================================
    # 10. ORDER
    # ==========================================

    items = items.order_by("-id")

    # ==========================================
    # 11. CONTEXT
    # ==========================================

    context = {
        "base_template": base_template,
        "manager": current_user,
        "active_category": active_category,
        "items": items,
        "search_query": search_query,
    }

    return render(
        request,
        "human_resource.html",
        context
    )

def save_human_resource(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method."
        }, status=405)

    # =====================================================
    # 1. GET LOGGED-IN USER FROM SESSION
    # =====================================================

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Authentication required."
        }, status=401)

    current_user = get_object_or_404(
        Registration,
        id=user_id
    )

    # =====================================================
    # 2. CHECK USER ROLE
    # =====================================================

    user_role = str(
        getattr(current_user, "role", "")
    ).lower().strip()

    allowed_roles = [
        "manager",
        "admin",
        "super_admin"
    ]

    if user_role not in allowed_roles:
        return JsonResponse({
            "status": "error",
            "message": "You do not have permission to perform this action."
        }, status=403)

    # =====================================================
    # 3. GET MODAL DATA
    # =====================================================

    item_id = request.POST.get("item_id")
    category = request.POST.get("category")
    title = request.POST.get("title", "").strip()

    # =====================================================
    # 4. VALIDATION
    # =====================================================

    valid_categories = [
        "leave_type",
        "department",
        "designation",
        "specialist"
    ]

    if category not in valid_categories:
        return JsonResponse({
            "status": "error",
            "message": "Invalid Human Resource category."
        }, status=400)

    if not title:
        return JsonResponse({
            "status": "error",
            "message": "Name is required."
        }, status=400)

    # =====================================================
    # 5. EDIT EXISTING RECORD
    # =====================================================

    if item_id:

        item = get_object_or_404(
            HumanResource,
            id=item_id
        )

        can_edit = False

        # -------------------------------------------------
        # MANAGER
        # Manager can edit all HR records
        # -------------------------------------------------

        if user_role == "manager":
            can_edit = True

        # -------------------------------------------------
        # SUPER ADMIN
        # Super Admin can edit Admin/Super Admin records
        # but cannot edit Manager records
        # -------------------------------------------------

        elif user_role == "super_admin":

            if (
                not item.created_by
                or str(item.created_by.role).lower().strip()
                != "manager"
            ):
                can_edit = True

        # -------------------------------------------------
        # ADMIN
        # Admin can edit only records created by himself
        # -------------------------------------------------

        elif user_role == "admin":

            if item.created_by == current_user:
                can_edit = True

        # -------------------------------------------------
        # PERMISSION DENIED
        # -------------------------------------------------

        if not can_edit:

            return JsonResponse({
                "status": "error",
                "message": "You do not have permission to edit this record."
            }, status=403)

        # =================================================
        # CHECK DUPLICATE DURING EDIT
        # =================================================

        duplicate = HumanResource.objects.filter(
            category=category,
            name__iexact=title
        ).exclude(
            id=item.id
        ).exists()

        if duplicate:

            category_name = category.replace(
                "_",
                " "
            ).title()

            return JsonResponse({
                "status": "error",
                "message": (
                    f"{title} already exists in "
                    f"{category_name}."
                )
            }, status=400)

        # =================================================
        # UPDATE RECORD
        # =================================================

        item.category = category
        item.name = title
        item.save()

        return JsonResponse({
            "status": "success",
            "message": "Human Resource record updated successfully."
        })

    # =====================================================
    # 6. CHECK DUPLICATE BEFORE CREATE
    # =====================================================

    duplicate = HumanResource.objects.filter(
        category=category,
        name__iexact=title
    ).exists()

    if duplicate:

        category_name = category.replace(
            "_",
            " "
        ).title()

        return JsonResponse({
            "status": "error",
            "message": (
                f"{title} already exists in "
                f"{category_name}."
            )
        }, status=400)

    # =====================================================
    # 7. CREATE NEW RECORD
    # =====================================================

    HumanResource.objects.create(
        category=category,
        name=title,
        created_by=current_user
    )

    return JsonResponse({
        "status": "success",
        "message": "Human Resource record added successfully."
    })

def delete_human_resource(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method."
        }, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Authentication required."
        }, status=401)

    current_user = get_object_or_404(
        Registration,
        id=user_id
    )

    user_role = str(
        getattr(current_user, "role", "")
    ).lower().strip()

    allowed_roles = [
        "manager",
        "admin",
        "super_admin"
    ]

    if user_role not in allowed_roles:
        return JsonResponse({
            "status": "error",
            "message": "You do not have permission to delete this record."
        }, status=403)

    item_id = request.POST.get("item_id")
    category = request.POST.get("category")

    valid_categories = [
        "leave_type",
        "department",
        "designation",
        "specialist"
    ]

    if category not in valid_categories:
        return JsonResponse({
            "status": "error",
            "message": "Invalid Human Resource category."
        }, status=400)

    item = get_object_or_404(
        HumanResource,
        id=item_id,
        category=category
    )

    can_delete = False

    # Manager can delete all records
    if user_role == "manager":

        can_delete = True

    # Super Admin cannot delete Manager-created records
    elif user_role == "super_admin":

        if (
            not item.created_by
            or str(item.created_by.role).lower().strip()
            != "manager"
        ):
            can_delete = True

    # Admin can delete only own records
    elif user_role == "admin":

        if item.created_by == current_user:
            can_delete = True

    if not can_delete:

        return JsonResponse({
            "status": "error",
            "message": "You do not have permission to delete this record."
        }, status=403)

    item.delete()

    return JsonResponse({
        "status": "success",
        "message": "Human Resource record deleted successfully."
    })
    
from .models import IncomeHead, ExpenseHead

def finance_view(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    user_role = str(getattr(current_user, 'role', '')).lower()

    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    income_heads = IncomeHead.objects.filter(created_by=current_user).order_by('-created_at')
    expense_heads = ExpenseHead.objects.filter(created_by=current_user).order_by('-created_at')

    context = {
        "base_template": base_template,
        "manager": current_user,
        "income_heads": income_heads,
        "expense_heads": expense_heads,
    }

    return render(request, 'finance.html', context)


def add_income_head(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':

        current_user = get_object_or_404(Registration, id=user_id)

        name = request.POST.get('name', '').strip()
        description = request.POST.get('description')

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Income Head name is required.'})

        if IncomeHead.objects.filter(created_by=current_user, name__iexact=name).exists():
            return JsonResponse({'status': 'error', 'message': 'This Income Head already exists.'})

        IncomeHead.objects.create(
            name=name,
            description=description,
            created_by=current_user,
        )
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def edit_income_head(request, pk):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':

        income_head = get_object_or_404(IncomeHead, pk=pk, created_by_id=user_id)

        name = request.POST.get('name', '').strip()
        description = request.POST.get('description')

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Income Head name is required.'})

        if IncomeHead.objects.filter(created_by_id=user_id, name__iexact=name).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': 'This Income Head already exists.'})

        income_head.name = name
        income_head.description = description
        income_head.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def delete_income_head(request, pk):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':
        income_head = get_object_or_404(IncomeHead, pk=pk, created_by_id=user_id)
        income_head.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})



def add_expense_head(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':

        current_user = get_object_or_404(Registration, id=user_id)

        name = request.POST.get('name', '').strip()
        description = request.POST.get('description')

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Expense Head name is required.'})

        if ExpenseHead.objects.filter(created_by=current_user, name__iexact=name).exists():
            return JsonResponse({'status': 'error', 'message': 'This Expense Head already exists.'})

        ExpenseHead.objects.create(
            name=name,
            description=description,
            created_by=current_user,
        )
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def edit_expense_head(request, pk):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':

        expense_head = get_object_or_404(ExpenseHead, pk=pk, created_by_id=user_id)

        name = request.POST.get('name', '').strip()
        description = request.POST.get('description')

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Expense Head name is required.'})

        if ExpenseHead.objects.filter(created_by_id=user_id, name__iexact=name).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': 'This Expense Head already exists.'})

        expense_head.name = name
        expense_head.description = description
        expense_head.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def delete_expense_head(request, pk):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':
        expense_head = get_object_or_404(ExpenseHead, pk=pk, created_by_id=user_id)
        expense_head.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


from .models import BloodProduct


def blood_bank_view(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    user_role = str(getattr(current_user, 'role', '')).lower()

    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    products = BloodProduct.objects.filter(created_by=current_user).order_by('-created_at')

    context = {
        "base_template": base_template,
        "manager": current_user,
        "products": products,
    }

    return render(request, 'blood_bank.html', context)


def add_blood_product(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':

        current_user = get_object_or_404(Registration, id=user_id)

        name = request.POST.get('name', '').strip()
        product_type = request.POST.get('type')

        if not name or not product_type:
            return JsonResponse({'status': 'error', 'message': 'Name and Type are required.'})

        if BloodProduct.objects.filter(created_by=current_user, name__iexact=name, type=product_type).exists():
            return JsonResponse({'status': 'error', 'message': 'This product already exists under the selected type.'})

        BloodProduct.objects.create(
            name=name,
            type=product_type,
            created_by=current_user,
        )
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def edit_blood_product(request, pk):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':

        product = get_object_or_404(BloodProduct, pk=pk, created_by_id=user_id)

        name = request.POST.get('name', '').strip()
        product_type = request.POST.get('type')

        if not name or not product_type:
            return JsonResponse({'status': 'error', 'message': 'Name and Type are required.'})

        if BloodProduct.objects.filter(created_by_id=user_id, name__iexact=name, type=product_type).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': 'This product already exists under the selected type.'})

        product.name = name
        product.type = product_type
        product.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def delete_blood_product(request, pk):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})

    if request.method == 'POST':
        product = get_object_or_404(BloodProduct, pk=pk, created_by_id=user_id)
        product.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})
    
PHARMACY_TAB_LABELS = {
    "medicine_category": "Medicine Category",
    "supplier": "Supplier",
    "medicine_dosage": "Medicine Dosage",
    "unit": "Unit",
    "dose_interval": "Dose Interval",
    "dose_duration": "Dose Duration",
    "company": "Company",
    "medicine_group": "Medicine Group",
}

PHARMACY_PAGE_SIZE_OPTIONS = ["10", "50", "100", "all"]

def get_pharmacy_logged_in_user(request):

    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id or not role:
        return None, None

    if role == "manager":
        base_template = "manager_home.html"

    elif role == "super_admin":
        base_template = "super_admin_home.html"

    elif role == "admin":
        base_template = "admin_home.html"

    else:
        return None, None

    try:
        user = Registration.objects.get(id=user_id, role=role)

    except Registration.DoesNotExist:
        return None, None

    return user, base_template


# -----------------------------------------------------------------
# MAIN PHARMACY SETUP PAGE (left tabs + right listing)
# -----------------------------------------------------------------

def pharmacy_view(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return redirect("login_page")

    active_tab = request.GET.get("tab", "medicine_category")

    if active_tab not in PHARMACY_TAB_LABELS:
        active_tab = "medicine_category"

    search_query = request.GET.get("q", "").strip()

    if active_tab == "medicine_category":

        items = MedicineCategory.objects.all()

        if search_query:
            items = items.filter(category_name__icontains=search_query)

    elif active_tab == "supplier":

        items = Supplier.objects.all()

        if search_query:
            items = items.filter(
                Q(supplier_name__icontains=search_query) |
                Q(contact_person_name__icontains=search_query) |
                Q(supplier_contact__icontains=search_query) |
                Q(drug_license_number__icontains=search_query)
            )

    elif active_tab == "medicine_dosage":

        items = MedicineDosage.objects.select_related("category", "unit").all()

        if search_query:
            items = items.filter(
                Q(category__category_name__icontains=search_query) |
                Q(dose__icontains=search_query) |
                Q(unit__unit_name__icontains=search_query)
            )

    elif active_tab == "unit":

        items = Unit.objects.all()

        if search_query:
            items = items.filter(unit_name__icontains=search_query)

    elif active_tab == "dose_interval":

        items = DoseInterval.objects.all()

        if search_query:
            items = items.filter(interval_name__icontains=search_query)

    elif active_tab == "dose_duration":

        items = DoseDuration.objects.all()

        if search_query:
            items = items.filter(duration_name__icontains=search_query)

    elif active_tab == "company":

        items = Company.objects.all()

        if search_query:
            items = items.filter(company_name__icontains=search_query)

    elif active_tab == "medicine_group":

        items = MedicineGroup.objects.all()

        if search_query:
            items = items.filter(group_name__icontains=search_query)

    else:

        items = MedicineCategory.objects.none()

    per_page_param = request.GET.get("per_page", "10")

    if per_page_param not in PHARMACY_PAGE_SIZE_OPTIONS:
        per_page_param = "10"

    if per_page_param == "all":
        total_count = items.count()
        per_page = total_count if total_count > 0 else 1
    else:
        per_page = int(per_page_param)

    paginator = Paginator(items, per_page)

    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)

    except PageNotAnInteger:
        page_obj = paginator.page(1)

    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages if paginator.num_pages else 1)

    context = {
        "base_template": base_template,
        "manager": user,
        "user": user,
        "active_tab": active_tab,
        "tab_labels": PHARMACY_TAB_LABELS,
        "tab_label": PHARMACY_TAB_LABELS.get(active_tab, ""),
        "search_query": search_query,
        "page_obj": page_obj,
        "paginator": paginator,
        "per_page": per_page_param,
        "page_size_options": PHARMACY_PAGE_SIZE_OPTIONS,
        "all_categories": MedicineCategory.objects.all(),
        "all_units": Unit.objects.all(),
    }

    return render(request, "pharmacy.html", context)


# -----------------------------------------------------------------
# MEDICINE CATEGORY
# -----------------------------------------------------------------

@require_POST
def save_medicine_category(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")
    category_name = request.POST.get("category_name", "").strip()

    if not category_name:
        return JsonResponse({"success": False, "message": "Category name is required."}, status=400)

    if item_id:

        item = get_object_or_404(MedicineCategory, id=item_id)

        if MedicineCategory.objects.exclude(id=item_id).filter(category_name__iexact=category_name).exists():
            return JsonResponse({"success": False, "message": "This category already exists."}, status=400)

        item.category_name = category_name
        item.save()

        message = "Medicine category updated successfully."

    else:

        if MedicineCategory.objects.filter(category_name__iexact=category_name).exists():
            return JsonResponse({"success": False, "message": "This category already exists."}, status=400)

        MedicineCategory.objects.create(category_name=category_name, created_by=user)

        message = "Medicine category added successfully."

    return JsonResponse({"success": True, "message": message})


@require_POST
def delete_medicine_category(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(MedicineCategory, pk=pk)

    if item.dosages.exists():
        return JsonResponse({
            "success": False,
            "message": "Cannot delete - this category is used in Medicine Dosage records."
        }, status=400)

    item.delete()

    return JsonResponse({"success": True, "message": "Medicine category deleted successfully."})


# -----------------------------------------------------------------
# SUPPLIER
# -----------------------------------------------------------------

@require_POST
def save_supplier(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")
    supplier_name = request.POST.get("supplier_name", "").strip()
    supplier_contact = request.POST.get("supplier_contact", "").strip()
    contact_person_name = request.POST.get("contact_person_name", "").strip()
    contact_person_phone = request.POST.get("contact_person_phone", "").strip()
    drug_license_number = request.POST.get("drug_license_number", "").strip()
    address = request.POST.get("address", "").strip()

    if not supplier_name:
        return JsonResponse({"success": False, "message": "Supplier name is required."}, status=400)

    if item_id:

        item = get_object_or_404(Supplier, id=item_id)

        item.supplier_name = supplier_name
        item.supplier_contact = supplier_contact or None
        item.contact_person_name = contact_person_name or None
        item.contact_person_phone = contact_person_phone or None
        item.drug_license_number = drug_license_number or None
        item.address = address or None
        item.save()

        message = "Supplier updated successfully."

    else:

        Supplier.objects.create(
            supplier_name=supplier_name,
            supplier_contact=supplier_contact or None,
            contact_person_name=contact_person_name or None,
            contact_person_phone=contact_person_phone or None,
            drug_license_number=drug_license_number or None,
            address=address or None,
            created_by=user
        )

        message = "Supplier added successfully."

    return JsonResponse({"success": True, "message": message})


@require_POST
def delete_supplier(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(Supplier, pk=pk)
    item.delete()

    return JsonResponse({"success": True, "message": "Supplier deleted successfully."})


# -----------------------------------------------------------------
# MEDICINE DOSAGE (supports adding several rows at once)
# -----------------------------------------------------------------

@require_POST
def save_medicine_dosage(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")

    if item_id:

        category_id = request.POST.get("category")
        dose = request.POST.get("dose", "").strip()
        unit_id = request.POST.get("unit")

        if not category_id or not dose or not unit_id:
            return JsonResponse({"success": False, "message": "Category, dose and unit are required."}, status=400)

        item = get_object_or_404(MedicineDosage, id=item_id)
        item.category_id = category_id
        item.dose = dose
        item.unit_id = unit_id
        item.save()

        return JsonResponse({"success": True, "message": "Medicine dosage updated successfully."})

    # Adding one or more new rows from the dynamic add-row modal
    categories = request.POST.getlist("category[]")
    doses = request.POST.getlist("dose[]")
    units = request.POST.getlist("unit[]")

    if not categories:
        return JsonResponse({"success": False, "message": "Add at least one dosage row."}, status=400)

    created_count = 0

    with transaction.atomic():

        for category_id, dose, unit_id in zip(categories, doses, units):

            category_id = (category_id or "").strip()
            dose = (dose or "").strip()
            unit_id = (unit_id or "").strip()

            if not category_id or not dose or not unit_id:
                continue

            MedicineDosage.objects.create(
                category_id=category_id,
                dose=dose,
                unit_id=unit_id,
                created_by=user
            )

            created_count += 1

    if created_count == 0:
        return JsonResponse({
            "success": False,
            "message": "Please fill category, dose and unit for at least one row."
        }, status=400)

    return JsonResponse({
        "success": True,
        "message": f"{created_count} medicine dosage row(s) added successfully."
    })


@require_POST
def delete_medicine_dosage(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(MedicineDosage, pk=pk)
    item.delete()

    return JsonResponse({"success": True, "message": "Medicine dosage deleted successfully."})


# -----------------------------------------------------------------
# UNIT
# -----------------------------------------------------------------

@require_POST
def save_unit(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")
    unit_name = request.POST.get("unit_name", "").strip()

    if not unit_name:
        return JsonResponse({"success": False, "message": "Unit name is required."}, status=400)

    if item_id:

        item = get_object_or_404(Unit, id=item_id)

        if Unit.objects.exclude(id=item_id).filter(unit_name__iexact=unit_name).exists():
            return JsonResponse({"success": False, "message": "This unit already exists."}, status=400)

        item.unit_name = unit_name
        item.save()

        message = "Unit updated successfully."

    else:

        if Unit.objects.filter(unit_name__iexact=unit_name).exists():
            return JsonResponse({"success": False, "message": "This unit already exists."}, status=400)

        Unit.objects.create(unit_name=unit_name, created_by=user)

        message = "Unit added successfully."

    return JsonResponse({"success": True, "message": message})


@require_POST
def delete_unit(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(Unit, pk=pk)

    if item.dosages.exists():
        return JsonResponse({
            "success": False,
            "message": "Cannot delete - this unit is used in Medicine Dosage records."
        }, status=400)

    item.delete()

    return JsonResponse({"success": True, "message": "Unit deleted successfully."})


# -----------------------------------------------------------------
# DOSE INTERVAL
# -----------------------------------------------------------------

@require_POST
def save_dose_interval(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")
    interval_name = request.POST.get("interval_name", "").strip()

    if not interval_name:
        return JsonResponse({"success": False, "message": "Interval is required."}, status=400)

    if item_id:

        item = get_object_or_404(DoseInterval, id=item_id)

        if DoseInterval.objects.exclude(id=item_id).filter(interval_name__iexact=interval_name).exists():
            return JsonResponse({"success": False, "message": "This interval already exists."}, status=400)

        item.interval_name = interval_name
        item.save()

        message = "Dose interval updated successfully."

    else:

        if DoseInterval.objects.filter(interval_name__iexact=interval_name).exists():
            return JsonResponse({"success": False, "message": "This interval already exists."}, status=400)

        DoseInterval.objects.create(interval_name=interval_name, created_by=user)

        message = "Dose interval added successfully."

    return JsonResponse({"success": True, "message": message})


@require_POST
def delete_dose_interval(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(DoseInterval, pk=pk)
    item.delete()

    return JsonResponse({"success": True, "message": "Dose interval deleted successfully."})


# -----------------------------------------------------------------
# DOSE DURATION
# -----------------------------------------------------------------

@require_POST
def save_dose_duration(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")
    duration_name = request.POST.get("duration_name", "").strip()

    if not duration_name:
        return JsonResponse({"success": False, "message": "Duration is required."}, status=400)

    if item_id:

        item = get_object_or_404(DoseDuration, id=item_id)

        if DoseDuration.objects.exclude(id=item_id).filter(duration_name__iexact=duration_name).exists():
            return JsonResponse({"success": False, "message": "This duration already exists."}, status=400)

        item.duration_name = duration_name
        item.save()

        message = "Dose duration updated successfully."

    else:

        if DoseDuration.objects.filter(duration_name__iexact=duration_name).exists():
            return JsonResponse({"success": False, "message": "This duration already exists."}, status=400)

        DoseDuration.objects.create(duration_name=duration_name, created_by=user)

        message = "Dose duration added successfully."

    return JsonResponse({"success": True, "message": message})


@require_POST
def delete_dose_duration(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(DoseDuration, pk=pk)
    item.delete()

    return JsonResponse({"success": True, "message": "Dose duration deleted successfully."})


# -----------------------------------------------------------------
# COMPANY
# -----------------------------------------------------------------

@require_POST
def save_company(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")
    company_name = request.POST.get("company_name", "").strip()

    if not company_name:
        return JsonResponse({"success": False, "message": "Company name is required."}, status=400)

    if item_id:

        item = get_object_or_404(Company, id=item_id)

        if Company.objects.exclude(id=item_id).filter(company_name__iexact=company_name).exists():
            return JsonResponse({"success": False, "message": "This company already exists."}, status=400)

        item.company_name = company_name
        item.save()

        message = "Company updated successfully."

    else:

        if Company.objects.filter(company_name__iexact=company_name).exists():
            return JsonResponse({"success": False, "message": "This company already exists."}, status=400)

        Company.objects.create(company_name=company_name, created_by=user)

        message = "Company added successfully."

    return JsonResponse({"success": True, "message": message})


@require_POST
def delete_company(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(Company, pk=pk)
    item.delete()

    return JsonResponse({"success": True, "message": "Company deleted successfully."})


# -----------------------------------------------------------------
# MEDICINE GROUP
# -----------------------------------------------------------------

@require_POST
def save_medicine_group(request):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item_id = request.POST.get("item_id")
    group_name = request.POST.get("group_name", "").strip()

    if not group_name:
        return JsonResponse({"success": False, "message": "Medicine group is required."}, status=400)

    if item_id:

        item = get_object_or_404(MedicineGroup, id=item_id)

        if MedicineGroup.objects.exclude(id=item_id).filter(group_name__iexact=group_name).exists():
            return JsonResponse({"success": False, "message": "This medicine group already exists."}, status=400)

        item.group_name = group_name
        item.save()

        message = "Medicine group updated successfully."

    else:

        if MedicineGroup.objects.filter(group_name__iexact=group_name).exists():
            return JsonResponse({"success": False, "message": "This medicine group already exists."}, status=400)

        MedicineGroup.objects.create(group_name=group_name, created_by=user)

        message = "Medicine group added successfully."

    return JsonResponse({"success": True, "message": message})


@require_POST
def delete_medicine_group(request, pk):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    item = get_object_or_404(MedicineGroup, pk=pk)
    item.delete()

    return JsonResponse({"success": True, "message": "Medicine group deleted successfully."})


# -----------------------------------------------------------------
# EXCEL EXPORT (one endpoint, driven by the active tab)
# -----------------------------------------------------------------

def export_pharmacy_excel(request, tab):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return redirect("login_page")

    if tab not in PHARMACY_TAB_LABELS:
        return redirect("pharmacy_view")

    search_query = request.GET.get("q", "").strip()

    from openpyxl.styles import Font, PatternFill, Alignment

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = PHARMACY_TAB_LABELS[tab][:31]

    def style_header(headers):

        sheet.append(headers)

        for cell in sheet[1]:

            cell.font = Font(bold=True, color="FFFFFF")

            cell.fill = PatternFill(
                start_color="14382F", end_color="14382F", fill_type="solid"
            )

            cell.alignment = Alignment(horizontal="center", vertical="center")

        sheet.freeze_panes = "A2"
        sheet.row_dimensions[1].height = 22

    if tab == "medicine_category":

        items = MedicineCategory.objects.all()

        if search_query:
            items = items.filter(category_name__icontains=search_query)

        style_header(["S.No", "Category Name"])

        for index, item in enumerate(items, start=1):
            sheet.append([index, item.category_name])

    elif tab == "supplier":

        items = Supplier.objects.all()

        if search_query:
            items = items.filter(
                Q(supplier_name__icontains=search_query) |
                Q(contact_person_name__icontains=search_query)
            )

        style_header([
            "S.No", "Supplier Name", "Supplier Contact",
            "Contact Person Name", "Contact Person Phone",
            "Drug License Number", "Address"
        ])

        for index, item in enumerate(items, start=1):
            sheet.append([
                index, item.supplier_name, item.supplier_contact or "",
                item.contact_person_name or "", item.contact_person_phone or "",
                item.drug_license_number or "", item.address or ""
            ])

    elif tab == "medicine_dosage":

        items = MedicineDosage.objects.select_related("category", "unit").all()

        if search_query:
            items = items.filter(
                Q(category__category_name__icontains=search_query) |
                Q(dose__icontains=search_query)
            )

        style_header(["S.No", "Category", "Dose", "Unit"])

        for index, item in enumerate(items, start=1):
            sheet.append([
                index, item.category.category_name, item.dose, item.unit.unit_name
            ])

    elif tab == "unit":

        items = Unit.objects.all()

        if search_query:
            items = items.filter(unit_name__icontains=search_query)

        style_header(["S.No", "Unit Name"])

        for index, item in enumerate(items, start=1):
            sheet.append([index, item.unit_name])

    elif tab == "dose_interval":

        items = DoseInterval.objects.all()

        if search_query:
            items = items.filter(interval_name__icontains=search_query)

        style_header(["S.No", "Interval"])

        for index, item in enumerate(items, start=1):
            sheet.append([index, item.interval_name])

    elif tab == "dose_duration":

        items = DoseDuration.objects.all()

        if search_query:
            items = items.filter(duration_name__icontains=search_query)

        style_header(["S.No", "Duration"])

        for index, item in enumerate(items, start=1):
            sheet.append([index, item.duration_name])

    elif tab == "company":

        items = Company.objects.all()

        if search_query:
            items = items.filter(company_name__icontains=search_query)

        style_header(["S.No", "Company Name"])

        for index, item in enumerate(items, start=1):
            sheet.append([index, item.company_name])

    elif tab == "medicine_group":

        items = MedicineGroup.objects.all()

        if search_query:
            items = items.filter(group_name__icontains=search_query)

        style_header(["S.No", "Medicine Group"])

        for index, item in enumerate(items, start=1):
            sheet.append([index, item.group_name])

    widths = [10] + [30] * (sheet.max_column - 1)

    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(index)].width = width

    sheet.auto_filter.ref = sheet.dimensions

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = f'attachment; filename="{tab}.xlsx"'

    workbook.save(response)

    return response
    
import io
def export_pharmacy_pdf(request, tab):

    user, base_template = get_pharmacy_logged_in_user(request)

    if not user:
        return redirect("login_page")

    if tab not in PHARMACY_TAB_LABELS:
        return redirect("pharmacy_view")

    search_query = request.GET.get("q", "").strip()

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    if tab == "medicine_category":
        items = MedicineCategory.objects.all()
        if search_query:
            items = items.filter(category_name__icontains=search_query)
        headers = ["S.No", "Category Name"]
        rows = [[str(i), item.category_name] for i, item in enumerate(items, start=1)]

    elif tab == "supplier":
        items = Supplier.objects.all()
        if search_query:
            items = items.filter(
                Q(supplier_name__icontains=search_query) |
                Q(contact_person_name__icontains=search_query)
            )
        headers = ["Supplier Name", "Contact", "Person Name", "Person Phone", "License No", "Address"]
        rows = [[
            item.supplier_name, item.supplier_contact or "-", item.contact_person_name or "-",
            item.contact_person_phone or "-", item.drug_license_number or "-", item.address or "-"
        ] for item in items]

    elif tab == "medicine_dosage":
        items = MedicineDosage.objects.select_related("category", "unit").all()
        if search_query:
            items = items.filter(
                Q(category__category_name__icontains=search_query) |
                Q(dose__icontains=search_query)
            )
        headers = ["Category", "Dose", "Unit"]
        rows = [[item.category.category_name, item.dose, item.unit.unit_name] for item in items]

    elif tab == "unit":
        items = Unit.objects.all()
        if search_query:
            items = items.filter(unit_name__icontains=search_query)
        headers = ["S.No", "Unit Name"]
        rows = [[str(i), item.unit_name] for i, item in enumerate(items, start=1)]

    elif tab == "dose_interval":
        items = DoseInterval.objects.all()
        if search_query:
            items = items.filter(interval_name__icontains=search_query)
        headers = ["Interval"]
        rows = [[item.interval_name] for item in items]

    elif tab == "dose_duration":
        items = DoseDuration.objects.all()
        if search_query:
            items = items.filter(duration_name__icontains=search_query)
        headers = ["Duration"]
        rows = [[item.duration_name] for item in items]

    elif tab == "company":
        items = Company.objects.all()
        if search_query:
            items = items.filter(company_name__icontains=search_query)
        headers = ["S.No", "Company Name"]
        rows = [[str(i), item.company_name] for i, item in enumerate(items, start=1)]

    elif tab == "medicine_group":
        items = MedicineGroup.objects.all()
        if search_query:
            items = items.filter(group_name__icontains=search_query)
        headers = ["S.No", "Medicine Group"]
        rows = [[str(i), item.group_name] for i, item in enumerate(items, start=1)]

    else:
        headers, rows = [], []

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=15 * mm, leftMargin=15 * mm, rightMargin=15 * mm
    )
    styles = getSampleStyleSheet()
    elements = [Paragraph(f"<b>{PHARMACY_TAB_LABELS[tab]}</b>", styles["Title"]), Spacer(1, 10)]

    if not rows:
        rows = [["No records found."] + [""] * (len(headers) - 1)]

    table = Table([headers] + rows, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14382f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d8e0dd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8faf9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{tab}.pdf"'
    return response
    
def symptoms_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")


    active_category = request.GET.get(
        "category",
        "symptom_type"
    )

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    page_size = request.GET.get(
        "page_size",
        "10"
    )

    try:
        page_size = int(page_size)

        if page_size not in [10, 50, 100, 200]:
            page_size = 10

    except (TypeError, ValueError):
        page_size = 10

    page_number = request.GET.get(
        "page",
        "1"
    )


    context = {
        "manager": manager,
        "active_category": active_category,
        "search_query": search_query,
        "page_size": page_size,
    }
    if active_category == "symptom_type":

        symptom_types = (
            SymptomType.objects
            .all()
            .order_by("id")
        )
        if search_query:

            symptom_types = symptom_types.filter(
                name__icontains=search_query
            )
        paginator = Paginator(
            symptom_types,
            page_size
        )

        page_obj = paginator.get_page(
            page_number
        )
        context["symptom_types"] = page_obj.object_list
        context["page_obj"] = page_obj

    elif active_category == "symptom_head":

        symptom_heads = (
            SymptomHead.objects
            .select_related("symptom_type")
            .all()
            .order_by("id")
        )

        if search_query:

            symptom_heads = symptom_heads.filter(
                name__icontains=search_query
            )

        paginator = Paginator(
            symptom_heads,
            page_size
        )

        page_obj = paginator.get_page(
            page_number
        )


        context["symptom_heads"] = page_obj.object_list
        context["page_obj"] = page_obj
        context["symptom_types"] = (
            SymptomType.objects
            .all()
            .order_by("name")
        )

    else:

        active_category = "symptom_type"

        context["active_category"] = active_category


        symptom_types = (
            SymptomType.objects
            .all()
            .order_by("id")
        )

        if search_query:

            symptom_types = symptom_types.filter(
                name__icontains=search_query
            )
        paginator = Paginator(
            symptom_types,
            page_size
        )

        page_obj = paginator.get_page(
            page_number
        )
        context["symptom_types"] = page_obj.object_list
        context["page_obj"] = page_obj

    return render(
        request,
        "symptoms_manager.html",
        context
    )


def save_symptom_type(request):

    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        })

    symptom_types = request.POST.getlist('symptom_type[]')
    item_id = request.POST.get('item_id', '').strip()
    symptom_types = [
        value.strip()
        for value in symptom_types
        if value.strip()
    ]

    if not symptom_types:
        return JsonResponse({
            'status': 'error',
            'message': 'Please enter at least one symptom type.'
        })

    if item_id:

        symptom = get_object_or_404(
            SymptomType,
            id=item_id
        )

        first_name = symptom_types[0]
        if SymptomType.objects.filter(
            name__iexact=first_name
        ).exclude(id=symptom.id).exists():

            return JsonResponse({
                'status': 'error',
                'message': f'"{first_name}" already exists.'
            })

        symptom.name = first_name
        symptom.save()

        created_count = 0
        duplicate_names = []

        for name in symptom_types[1:]:

            if SymptomType.objects.filter(
                name__iexact=name
            ).exists():

                duplicate_names.append(name)
                continue

            SymptomType.objects.create(
                name=name
            )

            created_count += 1

        if created_count > 0:

            return JsonResponse({
                'status': 'success',
                'message': (
                    f'Symptom type updated successfully. '
                    f'{created_count} additional symptom type(s) added.'
                )
            })

        return JsonResponse({
            'status': 'success',
            'message': 'Symptom type updated successfully.'
        })

    created_count = 0

    duplicate_names = []

    for name in symptom_types:

        if SymptomType.objects.filter(
            name__iexact=name
        ).exists():

            duplicate_names.append(name)
            continue

        SymptomType.objects.create(
            name=name
        )

        created_count += 1

    if created_count == 0:

        return JsonResponse({
            'status': 'error',
            'message': 'All entered symptom types already exist.'
        })

    return JsonResponse({
        'status': 'success',
        'message': f'{created_count} symptom type(s) saved successfully.'
    })

def delete_symptom_type(request, id):

    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        })

    symptom = get_object_or_404(
        SymptomType,
        id=id
    )

    symptom.delete()

    return JsonResponse({
        'status': 'success',
        'message': 'Symptom type deleted successfully.'
    })



def save_symptom_head(request):

    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        })

    item_id = request.POST.get('item_id', '').strip()
    name = request.POST.get('symptom_head_name', '').strip()
    symptom_type_id = request.POST.get('symptom_type', '').strip()
    description = request.POST.get('description', '').strip()

    if not name:
        return JsonResponse({
            'status': 'error',
            'message': 'Please enter symptom head name.'
        })

    if not symptom_type_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Please select symptom type.'
        })

    symptom_type = get_object_or_404(
        SymptomType,
        id=symptom_type_id
    )

    if item_id:

        symptom_head = get_object_or_404(
            SymptomHead,
            id=item_id
        )
        if SymptomHead.objects.filter(
            name__iexact=name,
            symptom_type=symptom_type
        ).exclude(
            id=symptom_head.id
        ).exists():

            return JsonResponse({
                'status': 'error',
                'message': 'This symptom head already exists for this symptom type.'
            })

        symptom_head.name = name
        symptom_head.symptom_type = symptom_type
        symptom_head.description = description

        symptom_head.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Symptom head updated successfully.'
        })

    if SymptomHead.objects.filter(
        name__iexact=name,
        symptom_type=symptom_type
    ).exists():

        return JsonResponse({
            'status': 'error',
            'message': 'This symptom head already exists for this symptom type.'
        })

    SymptomHead.objects.create(
        name=name,
        symptom_type=symptom_type,
        description=description
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Symptom head saved successfully.'
    })


def delete_symptom_head(request, id):

    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        })

    symptom_head = get_object_or_404(
        SymptomHead,
        id=id
    )

    symptom_head.delete()

    return JsonResponse({
        'status': 'success',
        'message': 'Symptom head deleted successfully.'
    })



def export_symptoms_excel(request):

    category = request.GET.get(
        "category",
        "symptom_type"
    )

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    workbook = Workbook()
    worksheet = workbook.active

    if category == "symptom_type":

        worksheet.title = "Symptom Types"

        worksheet.append([
            "Sl No",
            "Symptom Type"
        ])

        symptom_types = SymptomType.objects.all()

        if search_query:
            symptom_types = symptom_types.filter(
                name__icontains=search_query
            )

        for index, symptom in enumerate(
            symptom_types,
            start=1
        ):
            worksheet.append([
                index,
                symptom.name
            ])

        filename = "Symptom_Types.xlsx"

    else:

        worksheet.title = "Symptom Heads"

        worksheet.append([
            "Sl No",
            "Symptom Head",
            "Symptom Type",
            "Description"
        ])

        symptom_heads = SymptomHead.objects.select_related(
            "symptom_type"
        ).all()

        if search_query:
            symptom_heads = symptom_heads.filter(
                Q(name__icontains=search_query) |
                Q(symptom_type__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        for index, head in enumerate(
            symptom_heads,
            start=1
        ):
            worksheet.append([
                index,
                head.name,
                head.symptom_type.name,
                head.description or ""
            ])

        filename = "Symptom_Heads.xlsx"

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    workbook.save(response)

    return response





def export_symptoms_pdf(request):

    category = request.GET.get(
        "category",
        "symptom_type"
    )
    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    if category == "symptom_type":

        filename = "Symptom_Types.pdf"

        response = HttpResponse(
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )

        document = SimpleDocTemplate(
            response,
            pagesize=A4
        )

        data = [
            [
                "Sl No",
                "Symptom Type"
            ]
        ]

    
        symptom_types = SymptomType.objects.all()


        if search_query:

            symptom_types = symptom_types.filter(
                name__icontains=search_query
            )

        symptom_types = symptom_types.order_by("name")


        for index, symptom in enumerate(
            symptom_types,
            start=1
        ):

            data.append([
                index,
                symptom.name
            ])

        title = Paragraph(
            "Symptom Types",
            getSampleStyleSheet()["Title"]
        )



    else:

        filename = "Symptom_Heads.pdf"

        response = HttpResponse(
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )

        document = SimpleDocTemplate(
            response,
            pagesize=landscape(A4)
        )

        data = [
            [
                "Sl No",
                "Symptom Head",
                "Symptom Type",
                "Description"
            ]
        ]
        symptom_heads = SymptomHead.objects.select_related(
            "symptom_type"
        ).all()
        if search_query:

            symptom_heads = symptom_heads.filter(
                Q(name__icontains=search_query) |
                Q(symptom_type__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        symptom_heads = symptom_heads.order_by(
            "symptom_type__name",
            "name"
        )
        for index, head in enumerate(
            symptom_heads,
            start=1
        ):

            data.append([
                index,
                head.name,
                head.symptom_type.name,
                head.description or ""
            ])

        title = Paragraph(
            "Symptom Heads",
            getSampleStyleSheet()["Title"]
        )

    table = Table(
        data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0b3d2e")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "LEFT"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )


    document.build([
        title,
        table
    ])

    return response


def print_symptoms(request):

    category = request.GET.get(
        "category",
        "symptom_type"
    )

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    if category == "symptom_type":

        symptoms = SymptomType.objects.all()

        if search_query:
            symptoms = symptoms.filter(
                name__icontains=search_query
            )

        return render(
            request,
            "print_symptom_types.html",
            {
                "symptoms": symptoms,
                "search_query": search_query,
            }
        )

    else:

        symptom_heads = SymptomHead.objects.select_related(
            "symptom_type"
        ).all()

        if search_query:
            symptom_heads = symptom_heads.filter(
                Q(name__icontains=search_query) |
                Q(symptom_type__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return render(
            request,
            "print_symptom_heads.html",
            {
                "symptom_heads": symptom_heads,
                "search_query": search_query,
            }
        )



def vitals_manager(request):
    return render(request, 'vitals_manager.html')



def findings_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    active_category = request.GET.get(
        "category",
        "finding_category"
    )

    if active_category not in [
        "finding_category",
        "finding"
    ]:
        active_category = "finding_category"

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    try:

        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )

    except (ValueError, TypeError):

        page_size = 10

    if page_size not in [
        10,
        50,
        100,
        200
    ]:

        page_size = 10

    finding_categories = FindingCategory.objects.all().order_by(
        "name"
    )


    if active_category == "finding_category":

        categories = FindingCategory.objects.all().order_by(
            "id"
        )

        if search_query:

            categories = categories.filter(
                name__icontains=search_query
            )

        paginator = Paginator(
            categories,
            page_size
        )

        page_number = request.GET.get(
            "page",
            1
        )

        page_obj = paginator.get_page(
            page_number
        )

        context = {

            "manager": manager,

            "active_category":
                "finding_category",
            "finding_categories":
                page_obj.object_list,
            "finding_types":
                finding_categories,
            "finding_list":
                [],

            "page_obj":
                page_obj,

            "search_query":
                search_query,

            "page_size":
                page_size,
        }

    else:

        findings = Finding.objects.select_related(
            "category"
        ).all().order_by(
            "id"
        )
        if search_query:

            findings = findings.filter(

                Q(
                    name__icontains=search_query
                )

                |

                Q(
                    category__name__icontains=search_query
                )

                |

                Q(
                    description__icontains=search_query
                )

            )

        paginator = Paginator(
            findings,
            page_size
        )

        page_number = request.GET.get(
            "page",
            1
        )

        page_obj = paginator.get_page(
            page_number
        )

        context = {

            "manager": manager,

            "active_category":
                "finding",
            "finding_categories":
                finding_categories,

            "finding_types":
                finding_categories,
            "finding_list":
                page_obj.object_list,

            "page_obj":
                page_obj,

            "search_query":
                search_query,

            "page_size":
                page_size,
        }

    return render(
        request,
        "findings_manager.html",
        context
    )


@require_POST
def save_finding_category_manager(request):

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    names = request.POST.getlist(
        "finding_type[]"
    )
    names = [
        name.strip()
        for name in names
        if name.strip()
    ]

    if not names:
        return JsonResponse({
            "status": "error",
            "message": "Category name is required."
        })
    if item_id:

        category = get_object_or_404(
            FindingCategory,
            id=item_id
        )
        edit_name = names[0]
        if FindingCategory.objects.filter(
            name__iexact=edit_name
        ).exclude(
            id=category.id
        ).exists():

            return JsonResponse({
                "status": "error",
                "message": f"Category '{edit_name}' already exists."
            })

        category.name = edit_name
        category.save()

        created_count = 0

        for new_name in names[1:]:

            if FindingCategory.objects.filter(
                name__iexact=new_name
            ).exists():

                continue

            FindingCategory.objects.create(
                name=new_name
            )

            created_count += 1

        return JsonResponse({
            "status": "success",
            "message": "Category updated and new categories added successfully."
        })

    created_count = 0

    duplicate_names = []

    for name in names:

        if FindingCategory.objects.filter(
            name__iexact=name
        ).exists():

            duplicate_names.append(name)
            continue

        FindingCategory.objects.create(
            name=name
        )

        created_count += 1

    if created_count == 0:

        return JsonResponse({
            "status": "error",
            "message": "All entered categories already exist."
        })

    return JsonResponse({
        "status": "success",
        "message": f"{created_count} category(s) added successfully."
    })


@require_POST
def save_finding_manager(request):

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    name = request.POST.get(
        "finding_head_name",
        ""
    ).strip()

    category_id = request.POST.get(
        "category",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    if not name:

        return JsonResponse({
            "status": "error",
            "message": "Finding name is required."
        })

    if not category_id:

        return JsonResponse({
            "status": "error",
            "message": "Please select a category."
        })

    category = get_object_or_404(
        FindingCategory,
        id=category_id
    )


    if item_id:

        finding = get_object_or_404(
            Finding,
            id=item_id
        )
        duplicate = Finding.objects.filter(
            name__iexact=name,
            category=category
        ).exclude(
            id=finding.id
        ).exists()

        if duplicate:

            return JsonResponse({
                "status": "error",
                "message": "This finding already exists in this category."
            })

        finding.name = name
        finding.category = category
        finding.description = description

        finding.save()

        return JsonResponse({
            "status": "success",
            "message": "Finding updated successfully."
        })

    duplicate = Finding.objects.filter(
        name__iexact=name,
        category=category
    ).exists()

    if duplicate:

        return JsonResponse({
            "status": "error",
            "message": "This finding already exists in this category."
        })

    Finding.objects.create(
        name=name,
        category=category,
        description=description
    )

    return JsonResponse({
        "status": "success",
        "message": "Finding added successfully."
    })



@require_POST
def delete_finding_category_manager(request, id):

    category = get_object_or_404(
        FindingCategory,
        id=id
    )

    category.delete()

    return JsonResponse({
        "status": "success",
        "message": "Finding category deleted successfully."
    })




@require_POST
def delete_finding_manager(request, id):

    finding = get_object_or_404(
        Finding,
        id=id
    )

    finding.delete()

    return JsonResponse({
        "status": "success",
        "message": "Finding deleted successfully."
    })




def export_findings_excel(request):

    category = request.GET.get(
        "category",
        "finding_category"
    )

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    workbook = Workbook()

    worksheet = workbook.active


    if category == "finding_category":

        worksheet.title = "Categories"

        headers = [
            "Sl No",
            "Category"
        ]

        worksheet.append(headers)

        categories = FindingCategory.objects.all().order_by(
            "id"
        )

        if search_query:

            categories = categories.filter(
                name__icontains=search_query
            )

        for index, category_obj in enumerate(
            categories,
            start=1
        ):

            worksheet.append([
                index,
                category_obj.name
            ])

        filename = "categories.xlsx"


    else:

        worksheet.title = "Findings"

        headers = [
            "Sl No",
            "Finding",
            "Category",
            "Description"
        ]

        worksheet.append(headers)

        findings = Finding.objects.select_related(
            "category"
        ).all().order_by(
            "id"
        )

        if search_query:

            findings = findings.filter(

                Q(
                    name__icontains=search_query
                )

                |

                Q(
                    category__name__icontains=search_query
                )

                |

                Q(
                    description__icontains=search_query
                )

            )

        for index, finding in enumerate(
            findings,
            start=1
        ):

            worksheet.append([
                index,
                finding.name,
                finding.category.name
                if finding.category
                else "-",
                finding.description
                if finding.description
                else "-"
            ])

        filename = "findings.xlsx"

    header_fill = PatternFill(
        start_color="0B3D2E",
        end_color="0B3D2E",
        fill_type="solid"
    )

    header_font = Font(
        color="FFFFFF",
        bold=True
    )

    header_alignment = Alignment(
        horizontal="center",
        vertical="center"
    )

    for cell in worksheet[1]:

        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment



    for column_cells in worksheet.columns:

        max_length = 0

        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:

            if cell.value is not None:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 4,
            50
        )


    worksheet.freeze_panes = "A2"

    response = HttpResponse(
        content_type=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="{filename}"'
    )

    workbook.save(response)

    return response


def export_findings_pdf(request):

    category = request.GET.get(
        "category",
        "finding_category"
    )

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; filename="findings.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    title_style.alignment = TA_CENTER

    elements = []



    if category == "finding_category":

        filename = "finding_categories.pdf"

        response[
            "Content-Disposition"
        ] = (
            f'attachment; filename="{filename}"'
        )

        elements.append(
            Paragraph(
                "Finding Categories",
                title_style
            )
        )

        elements.append(
            Paragraph(
                "<br/>",
                styles["Normal"]
            )
        )

        data = [
            [
                "Sl No",
                "Category"
            ]
        ]

        categories = FindingCategory.objects.all().order_by(
            "id"
        )

        if search_query:

            categories = categories.filter(
                name__icontains=search_query
            )

        for index, category_obj in enumerate(
            categories,
            start=1
        ):

            data.append([
                index,
                category_obj.name
            ])

        table = Table(
            data,
            colWidths=[
                80,
                400
            ]
        )

    else:

        filename = "findings.pdf"

        response[
            "Content-Disposition"
        ] = (
            f'attachment; filename="{filename}"'
        )

        elements.append(
            Paragraph(
                "Findings",
                title_style
            )
        )

        elements.append(
            Paragraph(
                "<br/>",
                styles["Normal"]
            )
        )

        data = [
            [
                "Sl No",
                "Finding",
                "Category",
                "Description"
            ]
        ]

        findings = Finding.objects.select_related(
            "category"
        ).all().order_by(
            "id"
        )
        if search_query:

            findings = findings.filter(

                Q(
                    name__icontains=search_query
                )

                |

                Q(
                    category__name__icontains=search_query
                )

                |

                Q(
                    description__icontains=search_query
                )

            )

        for index, finding in enumerate(
            findings,
            start=1
        ):

            data.append([
                index,
                finding.name,
                finding.category.name
                if finding.category
                else "-",
                finding.description
                if finding.description
                else "-"
            ])

        table = Table(
            data,
            colWidths=[
                50,
                160,
                150,
                300
            ]
        )

    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0B3D2E")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, 0),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D8E7E0")
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F7FBF9")
                ]
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

        ])
    )

    elements.append(table)

    document.build(elements)

    return response


def print_findings(request):

    category = request.GET.get(
        "category",
        "finding_category"
    )

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    if category == "finding_category":

        finding_categories = FindingCategory.objects.all().order_by(
            "id"
        )

        if search_query:

            finding_categories = finding_categories.filter(
                name__icontains=search_query
            )

        context = {

            "category":
                category,

            "finding_categories":
                finding_categories,

            "search_query":
                search_query,

        }

    else:

        findings = Finding.objects.select_related(
            "category"
        ).all().order_by(
            "id"
        )

        if search_query:

            findings = findings.filter(

                Q(
                    name__icontains=search_query
                )

                |

                Q(
                    category__name__icontains=search_query
                )

                |

                Q(
                    description__icontains=search_query
                )

            )

        context = {

            "category":
                category,

            "findings":
                findings,

            "search_query":
                search_query,

        }

    return render(
        request,
        "findings_print.html",
        context
    )




def vital_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:

        manager = Registration.objects.get(
            id=user_id,
            role="manager"
        )

    except Registration.DoesNotExist:

        request.session.flush()
        return redirect("login_page")

 

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    vitals = (
        Vital.objects
        .all()
        .order_by("name")
    )

    if search_query:

        vitals = vitals.filter(
            Q(name__icontains=search_query) |
            Q(unit__icontains=search_query) |
            Q(from_value__icontains=search_query) |
            Q(to_value__icontains=search_query)
        )


    try:

        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )

    except (ValueError, TypeError):

        page_size = 10

    if page_size not in [
        10,
        50,
        100,
        200
    ]:

        page_size = 10

   

    paginator = Paginator(
        vitals,
        page_size
    )

    page_number = request.GET.get(
        "page",
        1
    )

    page_obj = paginator.get_page(
        page_number
    )


    context = {

        "manager": manager,

        "vitals": page_obj.object_list,

        "page_obj": page_obj,

        "search_query": search_query,

        "page_size": page_size,
    }

    return render(
        request,
        "vitals_manager.html",
        context
    )


def save_vital_manager(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request."
        })

    try:

        vital_id = request.POST.get(
            "item_id",
            ""
        ).strip()

        name = request.POST.get(
            "vital_name",
            ""
        ).strip()

        from_value = request.POST.get(
            "from_value",
            ""
        ).strip()

        to_value = request.POST.get(
            "to_value",
            ""
        ).strip()

        unit = request.POST.get(
            "unit",
            ""
        ).strip()

        if not name:
            return JsonResponse({
                "status": "error",
                "message": "Vital name is required."
            })

        if not from_value:
            return JsonResponse({
                "status": "error",
                "message": "From value is required."
            })

        if not to_value:
            return JsonResponse({
                "status": "error",
                "message": "To value is required."
            })

        if not unit:
            return JsonResponse({
                "status": "error",
                "message": "Unit is required."
            })

        try:

            from_decimal = Decimal(
                from_value
            )

            to_decimal = Decimal(
                to_value
            )

        except InvalidOperation:

            return JsonResponse({
                "status": "error",
                "message": "Please enter valid numeric values."
            })

        if from_decimal > to_decimal:

            return JsonResponse({
                "status": "error",
                "message": "From value cannot be greater than To value."
            })

        if vital_id:

            vital = get_object_or_404(
                Vital,
                id=vital_id
            )
            duplicate = Vital.objects.filter(
                name__iexact=name
            ).exclude(
                id=vital.id
            ).exists()

            if duplicate:

                return JsonResponse({
                    "status": "error",
                    "message": "This vital already exists."
                })

            vital.name = name
            vital.from_value = from_decimal
            vital.to_value = to_decimal
            vital.unit = unit

            vital.save()

            return JsonResponse({
                "status": "success",
                "message": "Vital updated successfully."
            })

        duplicate = Vital.objects.filter(
            name__iexact=name
        ).exists()

        if duplicate:

            return JsonResponse({
                "status": "error",
                "message": "This vital already exists."
            })

        Vital.objects.create(
            name=name,
            from_value=from_decimal,
            to_value=to_decimal,
            unit=unit
        )

        return JsonResponse({
            "status": "success",
            "message": "Vital added successfully."
        })

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })


def delete_vital_manager(request, id):

    if request.method != "POST":

        return JsonResponse({
            "status": "error",
            "message": "Invalid request."
        })

    vital = get_object_or_404(
        Vital,
        id=id
    )

    vital.delete()

    return JsonResponse({
        "status": "success",
        "message": "Vital deleted successfully."
    })


def export_vitals_excel(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        user = Registration.objects.get(
            id=user_id
        )

        if user.role not in ["manager", "admin", "super_admin"]:
            return redirect("login_page")

    except Registration.DoesNotExist:
        return redirect("login_page")

    search_query = request.GET.get("q", "").strip()

    vitals = Vital.objects.all().order_by("id")

    if search_query:
        vitals = vitals.filter(
            Q(name__icontains=search_query) |
            Q(unit__icontains=search_query) |
            Q(from_value__icontains=search_query) |
            Q(to_value__icontains=search_query)
        )


    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Vitals"

    worksheet.append([
        "Sl No",
        "Vital Name",
        "Reference Range",
        "Unit"
    ])

    for index, vital in enumerate(vitals, start=1):

        worksheet.append([
            index,
            vital.name,
            f"{vital.from_value} - {vital.to_value}",
            vital.unit
        ])



    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="vitals.xlsx"'
    )

    workbook.save(response)

    return response



def export_vitals_pdf(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        user = Registration.objects.get(
            id=user_id
        )

        if user.role not in ["manager", "admin","super_admin"]:
            return redirect("login_page")

    except Registration.DoesNotExist:
        return redirect("login_page")

    search_query = request.GET.get("q", "").strip()

    vitals = Vital.objects.all().order_by("id")

    if search_query:
        vitals = vitals.filter(
            Q(name__icontains=search_query) |
            Q(unit__icontains=search_query) |
            Q(from_value__icontains=search_query) |
            Q(to_value__icontains=search_query)
        )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="vitals.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "<b>Vitals</b>",
        styles["Title"]
    )

    elements.append(title)

    data = [
        [
            "Sl No",
            "Vital Name",
            "Reference Range",
            "Unit"
        ]
    ]

    for index, vital in enumerate(vitals, start=1):

        data.append([
            str(index),
            vital.name,
            f"{vital.from_value} - {vital.to_value}",
            vital.unit
        ])

    table = Table(
        data,
        colWidths=[50, 150, 180, 80]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0b3d2e")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    elements.append(table)

    document.build(elements)

    return response


def symptoms_superadmin(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    active_category = request.GET.get(
        "category",
        "symptom_type"
    )

    if active_category not in [
        "symptom_type",
        "symptom_head"
    ]:
        active_category = "symptom_type"

    search_query = request.GET.get(
        "q",
        ""
    ).strip()


    try:
        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )
    except (TypeError, ValueError):
        page_size = 10

    if page_size not in [
        10,
        50,
        100,
        200
    ]:
        page_size = 10

    page_number = request.GET.get(
        "page",
        1
    )

    symptom_types = (
        SymptomType.objects
        .all()
        .order_by("id")
    )

    if search_query:
        symptom_types = symptom_types.filter(
            name__icontains=search_query
        )

    symptom_heads = (
        SymptomHead.objects
        .select_related("symptom_type")
        .all()
        .order_by("id")
    )

    if search_query:
        symptom_heads = symptom_heads.filter(
            Q(name__icontains=search_query) |
            Q(symptom_type__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if active_category == "symptom_type":

        paginator = Paginator(
            symptom_types,
            page_size
        )

    else:

        paginator = Paginator(
            symptom_heads,
            page_size
        )

    page_obj = paginator.get_page(
        page_number
    )


    all_symptom_types = (
        SymptomType.objects
        .all()
        .order_by("name")
    )

    context = {
        "manager": super_admin,
        "superadmin": super_admin,

        "symptom_types": (
            page_obj.object_list
            if active_category == "symptom_type"
            else []
        ),

        "symptom_heads": (
            page_obj.object_list
            if active_category == "symptom_head"
            else []
        ),

        "all_symptom_types": all_symptom_types,

        "page_obj": page_obj,

        "active_category": active_category,

        "search_query": search_query,

        "page_size": page_size,
    }

    return render(
        request,
        "symptoms_superadmin.html",
        context
    )


@require_POST
def superadmin_save_symptom_type(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    symptom_types = request.POST.getlist(
        "symptom_type[]"
    )

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    symptom_types = [
        value.strip()
        for value in symptom_types
        if value.strip()
    ]

    if not symptom_types:
        return JsonResponse({
            "status": "error",
            "message": "Please enter at least one symptom type."
        })

    if item_id:

        symptom = get_object_or_404(
            SymptomType,
            id=item_id,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        )

        first_name = symptom_types[0]

        if SymptomType.objects.filter(
            name__iexact=first_name,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=symptom.id
        ).exists():

            return JsonResponse({
                "status": "error",
                "message": f'"{first_name}" already exists.'
            })

        symptom.name = first_name
        symptom.save()

        created_count = 0

        for name in symptom_types[1:]:

            if SymptomType.objects.filter(
                name__iexact=name,
                role=super_admin
            ).exists():

                continue

            SymptomType.objects.create(
                name=name,
                role=super_admin
            )

            created_count += 1

        return JsonResponse({
            "status": "success",
            "message": "Symptom type updated successfully."
        })

    created_count = 0

    for name in symptom_types:

        if SymptomType.objects.filter(
            name__iexact=name,
            role=super_admin
        ).exists():

            continue

        SymptomType.objects.create(
            name=name,
            role=super_admin
        )

        created_count += 1

    if created_count == 0:
        return JsonResponse({
            "status": "error",
            "message": "All entered symptom types already exist."
        })

    return JsonResponse({
        "status": "success",
        "message": (
            f"{created_count} symptom type(s) "
            "saved successfully."
        )
    })


@require_POST
def superadmin_delete_symptom_type(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    symptom = get_object_or_404(
        SymptomType,
        id=id,
        role=super_admin
    )

    symptom.delete()

    return JsonResponse({
        "status": "success",
        "message": "Symptom type deleted successfully."
    })


@require_POST
def superadmin_save_symptom_head(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    name = request.POST.get(
        "symptom_head_name",
        ""
    ).strip()

    symptom_type_id = request.POST.get(
        "symptom_type",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    if not name:
        return JsonResponse({
            "status": "error",
            "message": "Please enter symptom head name."
        })

    if not symptom_type_id:
        return JsonResponse({
            "status": "error",
            "message": "Please select symptom type."
        })

    symptom_type = get_object_or_404(
        SymptomType,
        id=symptom_type_id,
        role__role__in=[
            "manager",
            "admin",
            "super_admin"
        ]
    )


    if item_id:

        symptom_head = get_object_or_404(
            SymptomHead,
            id=item_id,
            role=super_admin
        )

        if SymptomHead.objects.filter(
            name__iexact=name,
            symptom_type=symptom_type,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=symptom_head.id
        ).exists():

            return JsonResponse({
                "status": "error",
                "message": (
                    "This symptom head already exists "
                    "for this symptom type."
                )
            })

        symptom_head.name = name
        symptom_head.symptom_type = symptom_type
        symptom_head.description = description

        symptom_head.save()

        return JsonResponse({
            "status": "success",
            "message": "Symptom head updated successfully."
        })

    if SymptomHead.objects.filter(
        name__iexact=name,
        symptom_type=symptom_type,
        role=super_admin
    ).exists():

        return JsonResponse({
            "status": "error",
            "message": (
                "This symptom head already exists "
                "for this symptom type."
            )
        })

    SymptomHead.objects.create(
        name=name,
        symptom_type=symptom_type,
        description=description,
        role=super_admin
    )

    return JsonResponse({
        "status": "success",
        "message": "Symptom head saved successfully."
    })



@require_POST
def superadmin_delete_symptom_head(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    symptom_head = get_object_or_404(
        SymptomHead,
        id=id,
        role=super_admin
    )

    symptom_head.delete()

    return JsonResponse({
        "status": "success",
        "message": "Symptom head deleted successfully."
    })



def findings_superadmin(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")


    active_category = request.GET.get(
        "category",
        "finding_category"
    )

    if active_category not in [
        "finding_category",
        "finding"
    ]:
        active_category = "finding_category"


    search_query = request.GET.get(
        "q",
        ""
    ).strip()


    try:

        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )

    except (ValueError, TypeError):

        page_size = 10


    if page_size not in [
        10,
        50,
        100,
        200
    ]:

        page_size = 10


    page_number = request.GET.get(
        "page",
        1
    )


    finding_categories = (
        FindingCategory.objects
        .all()
        .order_by("name")
    )


    if active_category == "finding_category":

        categories = (
            FindingCategory.objects
            .all()
            .order_by("id")
        )

        if search_query:

            categories = categories.filter(
                name__icontains=search_query
            )

        paginator = Paginator(
            categories,
            page_size
        )

        page_obj = paginator.get_page(
            page_number
        )


        context = {

            "manager": super_admin,

            "superadmin": super_admin,

            "active_category":
                "finding_category",

            "finding_categories":
                page_obj.object_list,

            "finding_types":
                finding_categories,

            "finding_list":
                [],

            "page_obj":
                page_obj,

            "search_query":
                search_query,

            "page_size":
                page_size,
        }


    else:

        findings = (
            Finding.objects
            .select_related("category")
            .all()
            .order_by("id")
        )

        if search_query:

            findings = findings.filter(

                Q(name__icontains=search_query) |

                Q(
                    category__name__icontains=
                    search_query
                ) |

                Q(
                    description__icontains=
                    search_query
                )

            )

        paginator = Paginator(
            findings,
            page_size
        )

        page_obj = paginator.get_page(
            page_number
        )


        context = {

            "manager": super_admin,

            "superadmin": super_admin,

            "active_category":
                "finding",

            "finding_categories":
                finding_categories,

            "finding_types":
                finding_categories,

            "finding_list":
                page_obj.object_list,

            "page_obj":
                page_obj,

            "search_query":
                search_query,

            "page_size":
                page_size,
        }

    return render(
        request,
        "findings_superadmin.html",
        context
    )


@require_POST
def superadmin_save_finding_category_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    names = request.POST.getlist(
        "finding_type[]"
    )

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    names = [
        name.strip()
        for name in names
        if name.strip()
    ]

    if not names:
        return JsonResponse({
            "status": "error",
            "message": "Category name is required."
        })


    if item_id:

        category = get_object_or_404(
            FindingCategory,
            id=item_id,
            role=super_admin
        )

        edit_name = names[0]

        if FindingCategory.objects.filter(
            name__iexact=edit_name,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=category.id
        ).exists():

            return JsonResponse({
                "status": "error",
                "message": (
                    f"Category '{edit_name}' already exists."
                )
            })

        category.name = edit_name
        category.save()

        for new_name in names[1:]:

            if FindingCategory.objects.filter(
                name__iexact=new_name,
                role=super_admin
            ).exists():

                continue

            FindingCategory.objects.create(
                name=new_name,
                role=super_admin
            )

        return JsonResponse({
            "status": "success",
            "message": "Category updated successfully."
        })


    created_count = 0

    for name in names:

        if FindingCategory.objects.filter(
            name__iexact=name,
            role=super_admin
        ).exists():

            continue

        FindingCategory.objects.create(
            name=name,
            role=super_admin
        )

        created_count += 1

    if created_count == 0:

        return JsonResponse({
            "status": "error",
            "message": "All entered categories already exist."
        })

    return JsonResponse({
        "status": "success",
        "message": (
            f"{created_count} category(s) "
            "added successfully."
        )
    })




@require_POST
def superadmin_save_finding_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    name = request.POST.get(
        "finding_head_name",
        ""
    ).strip()

    category_id = request.POST.get(
        "category",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    if not name:
        return JsonResponse({
            "status": "error",
            "message": "Finding name is required."
        })

    if not category_id:
        return JsonResponse({
            "status": "error",
            "message": "Please select a category."
        })

    category = get_object_or_404(
        FindingCategory,
        id=category_id,
        role__role__in=[
            "manager",
            "admin",
            "super_admin"
        ]
    )

    if item_id:

        finding = get_object_or_404(
            Finding,
            id=item_id,
            role=super_admin
        )

        duplicate = Finding.objects.filter(
            name__iexact=name,
            category=category,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=finding.id
        ).exists()

        if duplicate:
            return JsonResponse({
                "status": "error",
                "message": (
                    "This finding already exists "
                    "in this category."
                )
            })

        finding.name = name
        finding.category = category
        finding.description = description

        finding.save()

        return JsonResponse({
            "status": "success",
            "message": "Finding updated successfully."
        })


    if Finding.objects.filter(
        name__iexact=name,
        category=category,
        role=super_admin
    ).exists():

        return JsonResponse({
            "status": "error",
            "message": (
                "This finding already exists "
                "in this category."
            )
        })

    Finding.objects.create(
        name=name,
        category=category,
        description=description,
        role=super_admin
    )

    return JsonResponse({
        "status": "success",
        "message": "Finding added successfully."
    })


@require_POST
def superadmin_delete_finding_category_manager(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    category = get_object_or_404(
        FindingCategory,
        id=id,

    )

    category.delete()

    return JsonResponse({
        "status": "success",
        "message": "Finding category deleted successfully."
    })



@require_POST
def superadmin_delete_finding_manager(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    finding = get_object_or_404(
        Finding,
        id=id,

    )

    finding.delete()

    return JsonResponse({
        "status": "success",
        "message": "Finding deleted successfully."
    })


def vitals_superadmin(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )

    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    search_query = request.GET.get(
        "q",
        ""
    ).strip()


    vitals = (
        Vital.objects
        .all()
        .order_by("name")
    )


    if search_query:

        vitals = vitals.filter(

            Q(
                name__icontains=
                search_query
            )

            |

            Q(
                unit__icontains=
                search_query
            )

            |

            Q(
                from_value__icontains=
                search_query
            )

            |

            Q(
                to_value__icontains=
                search_query
            )

        )



    try:

        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )

    except (ValueError, TypeError):

        page_size = 10

    if page_size not in [
        10,
        50,
        100,
        200
    ]:

        page_size = 10

    page_number = request.GET.get(
        "page",
        1
    )


    paginator = Paginator(
        vitals,
        page_size
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "manager":
            super_admin,

        "superadmin":
            super_admin,

        "vitals":
            page_obj.object_list,

        "page_obj":
            page_obj,

        "search_query":
            search_query,

        "page_size":
            page_size,
    }

    return render(
        request,
        "vitals_superadmin.html",
        context
    )



@require_POST
def superadmin_save_vital_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:

        vital_id = request.POST.get(
            "item_id",
            ""
        ).strip()

        name = request.POST.get(
            "vital_name",
            ""
        ).strip()

        from_value = request.POST.get(
            "from_value",
            ""
        ).strip()

        to_value = request.POST.get(
            "to_value",
            ""
        ).strip()

        unit = request.POST.get(
            "unit",
            ""
        ).strip()

        if not name:
            return JsonResponse({
                "status": "error",
                "message": "Vital name is required."
            })

        if not from_value:
            return JsonResponse({
                "status": "error",
                "message": "From value is required."
            })

        if not to_value:
            return JsonResponse({
                "status": "error",
                "message": "To value is required."
            })

        if not unit:
            return JsonResponse({
                "status": "error",
                "message": "Unit is required."
            })

        try:

            from_decimal = Decimal(
                from_value
            )

            to_decimal = Decimal(
                to_value
            )

        except InvalidOperation:

            return JsonResponse({
                "status": "error",
                "message": (
                    "Please enter valid numeric values."
                )
            })

        if from_decimal > to_decimal:

            return JsonResponse({
                "status": "error",
                "message": (
                    "From value cannot be greater "
                    "than To value."
                )
            })



        if vital_id:

            vital = get_object_or_404(
                Vital,
                id=vital_id,
                role=super_admin
            )

            duplicate = Vital.objects.filter(
                name__iexact=name,
                role__role__in=[
                    "manager",
                    "admin",
                    "super_admin"
                ]
            ).exclude(
                id=vital.id
            ).exists()

            if duplicate:

                return JsonResponse({
                    "status": "error",
                    "message": "This vital already exists."
                })

            vital.name = name
            vital.from_value = from_decimal
            vital.to_value = to_decimal
            vital.unit = unit

            vital.save()

            return JsonResponse({
                "status": "success",
                "message": "Vital updated successfully."
            })


        if Vital.objects.filter(
            name__iexact=name,
            role=super_admin
        ).exists():

            return JsonResponse({
                "status": "error",
                "message": "This vital already exists."
            })

        Vital.objects.create(
            name=name,
            from_value=from_decimal,
            to_value=to_decimal,
            unit=unit,
            role=super_admin
        )

        return JsonResponse({
            "status": "success",
            "message": "Vital added successfully."
        })

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })




@require_POST
def superadmin_delete_vital_manager(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        super_admin = Registration.objects.get(
            id=user_id,
            role="super_admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    vital = get_object_or_404(
        Vital,
        id=id,
    )

    vital.delete()

    return JsonResponse({
        "status": "success",
        "message": "Vital deleted successfully."
    })




def symptoms_admin(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")


    active_category = request.GET.get(
        "category",
        "symptom_type"
    )

    if active_category not in [
        "symptom_type",
        "symptom_head"
    ]:
        active_category = "symptom_type"
    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    try:
        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )
    except (TypeError, ValueError):

        page_size = 10

    if page_size not in [
        10,
        50,
        100,
        200
    ]:
        page_size = 10

    page_number = request.GET.get(
        "page",
        1
    )
    symptom_types = (
        SymptomType.objects
        .order_by("id")
    )

    if search_query:

        symptom_types = symptom_types.filter(
            name__icontains=search_query
        )

    symptom_heads = (
        SymptomHead.objects
        .select_related(
            "symptom_type"
        )
        .order_by("id")
    )

    if search_query:

        symptom_heads = symptom_heads.filter(
            Q(name__icontains=search_query) |
            Q(
                symptom_type__name__icontains=
                search_query
            ) |
            Q(
                description__icontains=
                search_query
            )
        )



    if active_category == "symptom_type":

        paginator = Paginator(
            symptom_types,
            page_size
        )

    else:

        paginator = Paginator(
            symptom_heads,
            page_size
        )

    page_obj = paginator.get_page(
        page_number
    )

    all_symptom_types = (
        SymptomType.objects
        .order_by("name")
    )


    context = {

        "manager": admin,

        "admin": admin,

        "symptom_types": (
            page_obj.object_list
            if active_category == "symptom_type"
            else []
        ),

        "symptom_heads": (
            page_obj.object_list
            if active_category == "symptom_head"
            else []
        ),

        "all_symptom_types":
            all_symptom_types,

        "page_obj":
            page_obj,

        "active_category":
            active_category,

        "search_query":
            search_query,

        "page_size":
            page_size,
    }

    return render(
        request,
        "symptoms_admin.html",
        context
    )


@require_POST
def admin_save_symptom_type(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    symptom_types = request.POST.getlist(
        "symptom_type[]"
    )

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    symptom_types = [
        value.strip()
        for value in symptom_types
        if value.strip()
    ]

    if not symptom_types:

        return JsonResponse({
            "status": "error",
            "message": "Please enter at least one symptom type."
        })

  

    if item_id:

        symptom = get_object_or_404(
            SymptomType,
            id=item_id,
            role=admin
        )

        first_name = symptom_types[0]

        if SymptomType.objects.filter(
            name__iexact=first_name,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=symptom.id
        ).exists():

            return JsonResponse({
                "status": "error",
                "message":
                    f'"{first_name}" already exists.'
            })

        symptom.name = first_name
        symptom.save()

        for name in symptom_types[1:]:

            if SymptomType.objects.filter(
                name__iexact=name,
                role=admin
            ).exists():
                continue

            SymptomType.objects.create(
                name=name,
                role=admin
            )

        return JsonResponse({
            "status": "success",
            "message": "Symptom type updated successfully."
        })


    created_count = 0

    for name in symptom_types:

        if SymptomType.objects.filter(
            name__iexact=name,
            role=admin
        ).exists():
            continue

        SymptomType.objects.create(
            name=name,
            role=admin
        )

        created_count += 1

    if created_count == 0:

        return JsonResponse({
            "status": "error",
            "message": "All entered symptom types already exist."
        })

    return JsonResponse({
        "status": "success",
        "message":
            f"{created_count} symptom type(s) "
            "saved successfully."
    })



@require_POST
def admin_delete_symptom_type(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    symptom = get_object_or_404(
        SymptomType,
        id=id,

    )

    symptom.delete()

    return JsonResponse({
        "status": "success",
        "message": "Symptom type deleted successfully."
    })




@require_POST
def admin_save_symptom_head(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    name = request.POST.get(
        "symptom_head_name",
        ""
    ).strip()

    symptom_type_id = request.POST.get(
        "symptom_type",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    if not name:

        return JsonResponse({
            "status": "error",
            "message": "Please enter symptom head name."
        })

    if not symptom_type_id:

        return JsonResponse({
            "status": "error",
            "message": "Please select symptom type."
        })

    symptom_type = get_object_or_404(
        SymptomType,
        id=symptom_type_id,
        role__role__in=[
            "manager",
            "admin",
            "super_admin"
        ]
    )


    if item_id:

        symptom_head = get_object_or_404(
            SymptomHead,
            id=item_id,
            role=admin
        )

        if SymptomHead.objects.filter(
            name__iexact=name,
            symptom_type=symptom_type,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=symptom_head.id
        ).exists():

            return JsonResponse({
                "status": "error",
                "message":
                    "This symptom head already exists "
                    "for this symptom type."
            })

        symptom_head.name = name
        symptom_head.symptom_type = symptom_type
        symptom_head.description = description

        symptom_head.save()

        return JsonResponse({
            "status": "success",
            "message": "Symptom head updated successfully."
        })

    if SymptomHead.objects.filter(
        name__iexact=name,
        symptom_type=symptom_type,
        role=admin
    ).exists():

        return JsonResponse({
            "status": "error",
            "message":
                "This symptom head already exists "
                "for this symptom type."
        })

    SymptomHead.objects.create(
        name=name,
        symptom_type=symptom_type,
        description=description,
        role=admin
    )

    return JsonResponse({
        "status": "success",
        "message": "Symptom head saved successfully."
    })



@require_POST
def admin_delete_symptom_head(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    symptom_head = get_object_or_404(
        SymptomHead,
        id=id,
        role=admin
    )

    symptom_head.delete()

    return JsonResponse({
        "status": "success",
        "message": "Symptom head deleted successfully."
    })


def findings_admin(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()
        return redirect("login_page")

    active_category = request.GET.get(
        "category",
        "finding_category"
    )

    if active_category not in [
        "finding_category",
        "finding"
    ]:
        active_category = "finding_category"
    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    try:
        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )
    except (ValueError, TypeError):

        page_size = 10

    if page_size not in [
        10,
        50,
        100,
        200
    ]:
        page_size = 10

    page_number = request.GET.get(
        "page",
        1
    )


    finding_categories = (
        FindingCategory.objects
        .all()
        .order_by("name")
    )

    if active_category == "finding_category":

        categories = (
            FindingCategory.objects
            .all()
            .order_by("id")
        )

        if search_query:

            categories = categories.filter(
                name__icontains=search_query
            )

        paginator = Paginator(
            categories,
            page_size
        )

        page_obj = paginator.get_page(
            page_number
        )

        context = {

            "manager":
                admin,

            "admin":
                admin,

            "active_category":
                "finding_category",

            "finding_categories":
                page_obj.object_list,

            "finding_types":
                finding_categories,

            "finding_list":
                [],

            "page_obj":
                page_obj,

            "search_query":
                search_query,

            "page_size":
                page_size,
        }


    else:

        findings = (
            Finding.objects
            .select_related("category")
            .all()
            .order_by("id")
        )

        if search_query:

            findings = findings.filter(

                Q(
                    name__icontains=
                    search_query
                )

                |

                Q(
                    category__name__icontains=
                    search_query
                )

                |

                Q(
                    description__icontains=
                    search_query
                )
            )

        paginator = Paginator(
            findings,
            page_size
        )

        page_obj = paginator.get_page(
            page_number
        )

        context = {

            "manager":
                admin,

            "admin":
                admin,

            "active_category":
                "finding",

            "finding_categories":
                finding_categories,

            "finding_types":
                finding_categories,

            "finding_list":
                page_obj.object_list,

            "page_obj":
                page_obj,

            "search_query":
                search_query,

            "page_size":
                page_size,
        }

    return render(
        request,
        "findings_admin.html",
        context
    )




@require_POST
def admin_save_finding_category_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    names = request.POST.getlist(
        "finding_type[]"
    )

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    names = [
        name.strip()
        for name in names
        if name.strip()
    ]

    if not names:

        return JsonResponse({
            "status": "error",
            "message": "Category name is required."
        })



    if item_id:

        category = get_object_or_404(
            FindingCategory,
            id=item_id,
            role=admin
        )

        edit_name = names[0]

        if FindingCategory.objects.filter(
            name__iexact=edit_name,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=category.id
        ).exists():

            return JsonResponse({
                "status": "error",
                "message":
                    f"Category '{edit_name}' already exists."
            })

        category.name = edit_name
        category.save()

        for new_name in names[1:]:

            if FindingCategory.objects.filter(
                name__iexact=new_name,
                role=admin
            ).exists():
                continue

            FindingCategory.objects.create(
                name=new_name,
                role=admin
            )

        return JsonResponse({
            "status": "success",
            "message": "Category updated successfully."
        })

  

    created_count = 0

    for name in names:

        if FindingCategory.objects.filter(
            name__iexact=name,
            role=admin
        ).exists():
            continue

        FindingCategory.objects.create(
            name=name,
            role=admin
        )

        created_count += 1

    if created_count == 0:

        return JsonResponse({
            "status": "error",
            "message": "All entered categories already exist."
        })

    return JsonResponse({
        "status": "success",
        "message":
            f"{created_count} category(s) "
            "added successfully."
    })




@require_POST
def admin_save_finding_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    item_id = request.POST.get(
        "item_id",
        ""
    ).strip()

    name = request.POST.get(
        "finding_head_name",
        ""
    ).strip()

    category_id = request.POST.get(
        "category",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    if not name:

        return JsonResponse({
            "status": "error",
            "message": "Finding name is required."
        })

    if not category_id:

        return JsonResponse({
            "status": "error",
            "message": "Please select a category."
        })

    category = get_object_or_404(
        FindingCategory,
        id=category_id,
        role__role__in=[
            "manager",
            "admin",
            "super_admin"
        ]
    )



    if item_id:

        finding = get_object_or_404(
            Finding,
            id=item_id,
            role=admin
        )

        duplicate = Finding.objects.filter(
            name__iexact=name,
            category=category,
            role__role__in=[
                "manager",
                "admin",
                "super_admin"
            ]
        ).exclude(
            id=finding.id
        ).exists()

        if duplicate:

            return JsonResponse({
                "status": "error",
                "message":
                    "This finding already exists "
                    "in this category."
            })

        finding.name = name
        finding.category = category
        finding.description = description

        finding.save()

        return JsonResponse({
            "status": "success",
            "message": "Finding updated successfully."
        })

    if Finding.objects.filter(
        name__iexact=name,
        category=category,
        role=admin
    ).exists():

        return JsonResponse({
            "status": "error",
            "message":
                "This finding already exists "
                "in this category."
        })

    Finding.objects.create(
        name=name,
        category=category,
        description=description,
        role=admin
    )

    return JsonResponse({
        "status": "success",
        "message": "Finding added successfully."
    })



@require_POST
def admin_delete_finding_category_manager(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    category = get_object_or_404(
        FindingCategory,
        id=id,

    )

    category.delete()

    return JsonResponse({
        "status": "success",
        "message": "Finding category deleted successfully."
    })




@require_POST
def admin_delete_finding_manager(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    finding = get_object_or_404(
        Finding,
        id=id,

    )

    finding.delete()

    return JsonResponse({
        "status": "success",
        "message": "Finding deleted successfully."
    })


def vitals_admin(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login_page")

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()
        return redirect("login_page")


    search_query = request.GET.get(
        "q",
        ""
    ).strip()



    vitals = (
        Vital.objects
        .all()
        .order_by("name")
    )


    if search_query:

        vitals = vitals.filter(

            Q(
                name__icontains=
                search_query
            )

            |

            Q(
                unit__icontains=
                search_query
            )

            |

            Q(
                from_value__icontains=
                search_query
            )

            |

            Q(
                to_value__icontains=
                search_query
            )
        )

    try:

        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )

    except (ValueError, TypeError):

        page_size = 10

    if page_size not in [
        10,
        50,
        100,
        200
    ]:

        page_size = 10

    page_number = request.GET.get(
        "page",
        1
    )


    paginator = Paginator(
        vitals,
        page_size
    )

    page_obj = paginator.get_page(
        page_number
    )



    context = {

        "manager":
            admin,

        "admin":
            admin,

        "vitals":
            page_obj.object_list,

        "page_obj":
            page_obj,

        "search_query":
            search_query,

        "page_size":
            page_size,
    }

    return render(
        request,
        "vitals_admin.html",
        context
    )




@require_POST
def admin_save_vital_manager(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:

        vital_id = request.POST.get(
            "item_id",
            ""
        ).strip()

        name = request.POST.get(
            "vital_name",
            ""
        ).strip()

        from_value = request.POST.get(
            "from_value",
            ""
        ).strip()

        to_value = request.POST.get(
            "to_value",
            ""
        ).strip()

        unit = request.POST.get(
            "unit",
            ""
        ).strip()

        if not name:

            return JsonResponse({
                "status": "error",
                "message": "Vital name is required."
            })

        if not from_value:

            return JsonResponse({
                "status": "error",
                "message": "From value is required."
            })

        if not to_value:

            return JsonResponse({
                "status": "error",
                "message": "To value is required."
            })

        if not unit:

            return JsonResponse({
                "status": "error",
                "message": "Unit is required."
            })

        try:

            from_decimal = Decimal(
                from_value
            )

            to_decimal = Decimal(
                to_value
            )

        except InvalidOperation:

            return JsonResponse({
                "status": "error",
                "message":
                    "Please enter valid numeric values."
            })

        if from_decimal > to_decimal:

            return JsonResponse({
                "status": "error",
                "message":
                    "From value cannot be greater "
                    "than To value."
            })


        if vital_id:

            vital = get_object_or_404(
                Vital,
                id=vital_id,
                role=admin
            )

            duplicate = Vital.objects.filter(
                name__iexact=name,
                role__role__in=[
                    "manager",
                    "admin",
                    "super_admin"
                ]
            ).exclude(
                id=vital.id
            ).exists()

            if duplicate:

                return JsonResponse({
                    "status": "error",
                    "message":
                        "This vital already exists."
                })

            vital.name = name
            vital.from_value = from_decimal
            vital.to_value = to_decimal
            vital.unit = unit

            vital.save()

            return JsonResponse({
                "status": "success",
                "message":
                    "Vital updated successfully."
            })

     

        if Vital.objects.filter(
            name__iexact=name,
            role=admin
        ).exists():

            return JsonResponse({
                "status": "error",
                "message":
                    "This vital already exists."
            })

        Vital.objects.create(
            name=name,
            from_value=from_decimal,
            to_value=to_decimal,
            unit=unit,
            role=admin
        )

        return JsonResponse({
            "status": "success",
            "message":
                "Vital added successfully."
        })

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })



@require_POST
def admin_delete_vital_manager(request, id):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    try:
        admin = Registration.objects.get(
            id=user_id,
            role="admin"
        )
    except Registration.DoesNotExist:

        request.session.flush()

        return JsonResponse({
            "status": "error",
            "message": "Unauthorized access."
        }, status=403)

    vital = get_object_or_404(
        Vital,
        id=id,
    )

    vital.delete()

    return JsonResponse({
        "status": "success",
        "message": "Vital deleted successfully."
    })
    
# ==========================================
# SETUP: INVENTORY MODULE VIEWS
# ==========================================

def inventory_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    user_role = str(getattr(current_user, 'role', '')).lower()
    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    active_tab = request.GET.get("tab", "category")
    search_query = request.GET.get("q", "").strip()
    per_page_param = request.GET.get("per_page", "10")
    page_number = request.GET.get("page", 1)

    if active_tab == "store":
        qs = InventoryStore.objects.select_related('created_by').all()
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) | Q(code__icontains=search_query) | Q(description__icontains=search_query)
            )
    elif active_tab == "supplier":
        qs = InventorySupplier.objects.select_related('created_by').all()
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) | Q(phone__icontains=search_query) | Q(email__icontains=search_query) |
                Q(contact_person_name__icontains=search_query) | Q(address__icontains=search_query)
            )
    else:
        qs = InventoryCategory.objects.select_related('created_by').all()
        if search_query:
            qs = qs.filter(name__icontains=search_query)

    qs = qs.annotate(
        role_priority=Case(
            When(created_by__role='manager', then=Value(1)),
            When(created_by__role='super_admin', then=Value(2)),
            When(created_by__role='admin', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('role_priority', '-created_at')

    total_records = qs.count()

    if per_page_param.lower() == 'all':
        items_list = list(qs)
        page_obj = None
    else:
        try:
            per_page = int(per_page_param)
        except ValueError:
            per_page = 10
        paginator = Paginator(qs, per_page)
        try:
            page_obj = paginator.page(page_number)
        except Exception:
            page_obj = paginator.page(1)
        items_list = page_obj.object_list

    for item in items_list:
        item.can_edit = check_setup_permission(current_user, item)
        item.can_delete = check_setup_permission(current_user, item)

    context = {
        "base_template": base_template,
        "manager": current_user,
        "active_tab": active_tab,
        "search_query": search_query,
        "per_page": per_page_param,
        "items": items_list,
        "page_obj": page_obj,
        "total_records": total_records,
    }
    return render(request, "inventory.html", context)


def save_inventory_category(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        name = request.POST.get('name', '').strip()

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Category Name is required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        dup_qs = InventoryCategory.objects.filter(name__iexact=name)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'Inventory Category "{name}" already exists.'}, status=400)

        if item_id:
            category = get_object_or_404(InventoryCategory, id=item_id)
            if not check_setup_permission(current_user, category):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            category.name = name
            category.save()
        else:
            InventoryCategory.objects.create(name=name, created_by=current_user)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_inventory_category(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        category = get_object_or_404(InventoryCategory, pk=pk)

        if not check_setup_permission(current_user, category):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        category.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


def save_inventory_store(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()

        if not name or not code:
            return JsonResponse({'status': 'error', 'message': 'Store Name and Code are required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        dup_qs = InventoryStore.objects.filter(code__iexact=code)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'Store Code "{code}" already exists.'}, status=400)

        if item_id:
            store = get_object_or_404(InventoryStore, id=item_id)
            if not check_setup_permission(current_user, store):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            store.name = name
            store.code = code
            store.description = description
            store.save()
        else:
            InventoryStore.objects.create(name=name, code=code, description=description, created_by=current_user)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_inventory_store(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        store = get_object_or_404(InventoryStore, pk=pk)

        if not check_setup_permission(current_user, store):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        store.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


def save_inventory_supplier(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        contact_person_name = request.POST.get('contact_person_name', '').strip()
        contact_person_phone = request.POST.get('contact_person_phone', '').strip()
        contact_person_email = request.POST.get('contact_person_email', '').strip()
        address = request.POST.get('address', '').strip()
        description = request.POST.get('description', '').strip()

        if not name or not phone:
            return JsonResponse({'status': 'error', 'message': 'Supplier Name and Phone Number are required.'}, status=400)

        # Backend Pattern Validation: Phone must be 10 digits
        if not re.match(r'^\d{10}$', phone):
            return JsonResponse({'status': 'error', 'message': 'Supplier Phone Number must be exactly 10 digits.'}, status=400)

        if contact_person_phone and not re.match(r'^\d{10}$', contact_person_phone):
            return JsonResponse({'status': 'error', 'message': 'Contact Person Phone Number must be exactly 10 digits.'}, status=400)

        # Strict Email Domain and Format Validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        typo_domains = ['@gmil.com', '@gmal.com', '@yaho.com', '@hotmial.com', '@gamil.com', '@gnail.com']

        if email:
            if not re.match(email_regex, email) or any(email.lower().endswith(td) for td in typo_domains):
                return JsonResponse({'status': 'error', 'message': 'Invalid Supplier Email address format (e.g. user@gmail.com).'}, status=400)
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'status': 'error', 'message': 'Invalid Supplier Email address.'}, status=400)

        if contact_person_email:
            if not re.match(email_regex, contact_person_email) or any(contact_person_email.lower().endswith(td) for td in typo_domains):
                return JsonResponse({'status': 'error', 'message': 'Invalid Contact Person Email address format (e.g. user@gmail.com).'}, status=400)
            try:
                validate_email(contact_person_email)
            except ValidationError:
                return JsonResponse({'status': 'error', 'message': 'Invalid Contact Person Email address.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        dup_qs = InventorySupplier.objects.filter(name__iexact=name)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'Supplier "{name}" already exists.'}, status=400)

        if item_id:
            supplier = get_object_or_404(InventorySupplier, id=item_id)
            if not check_setup_permission(current_user, supplier):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            supplier.name = name
            supplier.phone = phone
            supplier.email = email
            supplier.contact_person_name = contact_person_name
            supplier.contact_person_phone = contact_person_phone
            supplier.contact_person_email = contact_person_email
            supplier.address = address
            supplier.description = description
            supplier.save()
        else:
            InventorySupplier.objects.create(
                name=name, phone=phone, email=email,
                contact_person_name=contact_person_name,
                contact_person_phone=contact_person_phone,
                contact_person_email=contact_person_email,
                address=address, description=description,
                created_by=current_user
            )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_inventory_supplier(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        supplier = get_object_or_404(InventorySupplier, pk=pk)

        if not check_setup_permission(current_user, supplier):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        supplier.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


# ==========================================
# SETUP: REFERRAL MODULE VIEWS
# ==========================================

def referral_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    try:
        current_user = Registration.objects.get(
            Q(role__iexact="super_admin") | Q(role__iexact="admin") | Q(role__iexact="manager"),
            id=user_id
        )
    except Registration.DoesNotExist:
        request.session.flush()
        return redirect("login_page")

    user_role = str(getattr(current_user, 'role', '')).lower()
    if user_role == 'super_admin':
        base_template = 'super_admin_home.html'
    elif user_role == 'admin':
        base_template = 'admin_home.html'
    else:
        base_template = 'manager_home.html'

    active_tab = request.GET.get("tab", "category")
    search_query = request.GET.get("q", "").strip()
    per_page_param = request.GET.get("per_page", "10")
    page_number = request.GET.get("page", 1)

    referral_categories = ReferralCategory.objects.all().order_by('name')

    if active_tab == "commission":
        qs = ReferralCommission.objects.select_related('category', 'created_by').all()
        if search_query:
            qs = qs.filter(category__name__icontains=search_query)
    else:
        qs = ReferralCategory.objects.select_related('created_by').all()
        if search_query:
            qs = qs.filter(name__icontains=search_query)

    qs = qs.annotate(
        role_priority=Case(
            When(created_by__role='manager', then=Value(1)),
            When(created_by__role='super_admin', then=Value(2)),
            When(created_by__role='admin', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('role_priority', '-created_at')

    total_records = qs.count()

    if per_page_param.lower() == 'all':
        items_list = list(qs)
        page_obj = None
    else:
        try:
            per_page = int(per_page_param)
        except ValueError:
            per_page = 10
        paginator = Paginator(qs, per_page)
        try:
            page_obj = paginator.page(page_number)
        except Exception:
            page_obj = paginator.page(1)
        items_list = page_obj.object_list

    for item in items_list:
        item.can_edit = check_setup_permission(current_user, item)
        item.can_delete = check_setup_permission(current_user, item)

    context = {
        "base_template": base_template,
        "manager": current_user,
        "active_tab": active_tab,
        "search_query": search_query,
        "per_page": per_page_param,
        "referral_categories": referral_categories,
        "items": items_list,
        "page_obj": page_obj,
        "total_records": total_records,
    }
    return render(request, "referral.html", context)


def save_referral_category(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)

        item_id = request.POST.get('item_id')
        name = request.POST.get('name', '').strip()
        names_json = request.POST.get('names_json')

        if item_id:
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Category Name is required.'}, status=400)
            category = get_object_or_404(ReferralCategory, id=item_id)
            if not check_setup_permission(current_user, category):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            dup_qs = ReferralCategory.objects.filter(name__iexact=name).exclude(id=item_id)
            if dup_qs.exists():
                return JsonResponse({'status': 'error', 'message': f'Referral Category "{name}" already exists.'}, status=400)
            category.name = name
            category.save()
            return JsonResponse({'status': 'success'})

        elif names_json:
            try:
                cat_names = json.loads(names_json)
            except Exception:
                return JsonResponse({'status': 'error', 'message': 'Invalid categories payload.'}, status=400)

            created_count = 0
            skipped_duplicates = []
            for cname in cat_names:
                cname_str = str(cname).strip()
                if cname_str:
                    if ReferralCategory.objects.filter(name__iexact=cname_str).exists():
                        skipped_duplicates.append(cname_str)
                    else:
                        ReferralCategory.objects.create(name=cname_str, created_by=current_user)
                        created_count += 1

            if created_count == 0 and skipped_duplicates:
                return JsonResponse({'status': 'error', 'message': f'Category(ies) already exist: {", ".join(skipped_duplicates)}'}, status=400)

            return JsonResponse({'status': 'success', 'created': created_count})

        elif name:
            dup_qs = ReferralCategory.objects.filter(name__iexact=name)
            if dup_qs.exists():
                return JsonResponse({'status': 'error', 'message': f'Referral Category "{name}" already exists.'}, status=400)
            ReferralCategory.objects.create(name=name, created_by=current_user)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'error', 'message': 'Category Name is required.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_referral_category(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        category = get_object_or_404(ReferralCategory, pk=pk)

        if not check_setup_permission(current_user, category):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        in_use_count = ReferralCommission.objects.filter(category=category).count()
        if in_use_count > 0:
            return JsonResponse({'status': 'error', 'message': f'Cannot delete category "{category.name}" because it is currently used by a commission rule.'}, status=400)

        category.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


def save_referral_commission(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        category_id = request.POST.get('category_id')
        standard_commission = request.POST.get('standard_commission', '0.00')
        opd_commission = request.POST.get('opd_commission', '0.00')
        ipd_commission = request.POST.get('ipd_commission', '0.00')
        pharmacy_commission = request.POST.get('pharmacy_commission', '0.00')
        pathology_commission = request.POST.get('pathology_commission', '0.00')
        radiology_commission = request.POST.get('radiology_commission', '0.00')
        ambulance_commission = request.POST.get('ambulance_commission', '0.00')
        blood_bank_commission = request.POST.get('blood_bank_commission', '0.00')

        if not category_id:
            return JsonResponse({'status': 'error', 'message': 'Referral Category is required.'}, status=400)

        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        category = get_object_or_404(ReferralCategory, id=category_id)

        dup_qs = ReferralCommission.objects.filter(category=category)
        if item_id:
            dup_qs = dup_qs.exclude(id=item_id)
        if dup_qs.exists():
            return JsonResponse({'status': 'error', 'message': f'Commission rule for "{category.name}" already exists.'}, status=400)

        if item_id:
            commission = get_object_or_404(ReferralCommission, id=item_id)
            if not check_setup_permission(current_user, commission):
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this record.'}, status=403)
            commission.category = category
            commission.standard_commission = standard_commission or 0
            commission.opd_commission = opd_commission or 0
            commission.ipd_commission = ipd_commission or 0
            commission.pharmacy_commission = pharmacy_commission or 0
            commission.pathology_commission = pathology_commission or 0
            commission.radiology_commission = radiology_commission or 0
            commission.ambulance_commission = ambulance_commission or 0
            commission.blood_bank_commission = blood_bank_commission or 0
            commission.save()
        else:
            ReferralCommission.objects.create(
                category=category,
                standard_commission=standard_commission or 0,
                opd_commission=opd_commission or 0,
                ipd_commission=ipd_commission or 0,
                pharmacy_commission=pharmacy_commission or 0,
                pathology_commission=pathology_commission or 0,
                radiology_commission=radiology_commission or 0,
                ambulance_commission=ambulance_commission or 0,
                blood_bank_commission=blood_bank_commission or 0,
                created_by=current_user
            )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_referral_commission(request, pk):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        current_user = get_object_or_404(Registration, id=user_id)
        commission = get_object_or_404(ReferralCommission, pk=pk)

        if not check_setup_permission(current_user, commission):
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this record.'}, status=403)

        commission.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)



def compound_list(request):
        user_id = request.session.get('user_id')
        role = request.session.get('role')
        bloodgroup=BloodProduct.objects.filter(type='blood_group',created_by_id=user_id)
        component=BloodProduct.objects.filter(type='component',created_by_id=user_id)
        component1=Component.objects.filter(created_by_id=user_id)
    
        
        if role == 'super_admin':
            base = 'super_admin_home.html'
        elif role == 'admin':
            base = 'admin_home.html'
        elif role == 'manager':
            base = 'manager_home.html'
      
    
        active_category = request.GET.get('category')
    
        manager = Registration.objects.get(id=user_id)
    
        return render(request, 'compound_list.html', {
            "user_id": user_id,
            "bloodgroup":bloodgroup,
            "component":component,
            "component1":component1,
        
            
            "role": role,
            "manager": manager,
           
            "base": base,
            "active_category": active_category,
        })
    
    
def save_component(request):
    
     user_id = request.session.get('user_id')

     if request.method == 'POST':
        name=request.POST.get('name')
        blood_id=request.POST.get('bloodgroup')
        bag=request.POST.get('bag')
        componentid = request.POST.getlist('componentid')
        bagnos = request.POST.getlist('bagno')
        volume = request.POST.getlist('volume')
        unit = request.POST.getlist('unit')
        lot = request.POST.getlist('lot')
        institutions = request.POST.getlist('insti')
        bloodgroup=BloodProduct.objects.get(id=blood_id)
        component=Component.objects.create(
            created_by_id=user_id,
                            bloodgroup=bloodgroup,
                            componentname=name,
                            bag=bag
                        )
        
        for i in range(len(componentid)):
         ComponentDetails.objects.create(
             component=component,
                blood_component_id=componentid[i],
                bag_no=bagnos[i],
                volume=volume[i],
                unit=unit[i],
                lot=lot[i],
                institution=institutions[i],
         )

        return JsonResponse({
              
            'success': True,
            'message': 'Component details saved successfully'
        })
def edit_component(request):
         user_id = request.session.get('user_id')
    
         if request.method == 'POST':
            id=request.POST.get('id')
            detailid=request.POST.getlist('detailid')
            name=request.POST.get('name')
            blood_id=request.POST.get('bloodgroup')
            bag=request.POST.get('bag')
            componentid = request.POST.getlist('componentid')
            bagnos = request.POST.getlist('bagno')
            volume = request.POST.getlist('volume')
            unit = request.POST.getlist('unit')
            lot = request.POST.getlist('lot')
            institutions = request.POST.getlist('insti')
            bloodgroup=BloodProduct.objects.get(id=blood_id)
            comp=Component.objects.get(id=id)
            comp.componentname=name
            comp.bloodgroup=bloodgroup
            comp.bag=bag
            comp.save()
            for i in range(len(detailid)):
                if detailid[i]:
                 detail=ComponentDetails.objects.get(id=detailid[i],component_id=comp)
                 detail.bag_no = bagnos[i]
                 detail.volume = volume[i]
                 detail.unit = unit[i]
                 detail.lot = lot[i]
                 detail.institution = institutions[i]

                 detail.blood_component_id = componentid[i]

                 detail.save()
                else:
                     ComponentDetails.objects.create(
                                 component=comp,
                                    blood_component_id=componentid[i],
                                    bag_no=bagnos[i],
                                    volume=volume[i],
                                    unit=unit[i],
                                    lot=lot[i],
                                    institution=institutions[i],
                             )

            
                           
            return JsonResponse({
                  
                'success': True,
                'message': 'Component details saved successfully'
            })

def delete_component(request):
        id=request.POST.get('id')
        radio=Component.objects.get(id=id)
        radio.delete()
        return JsonResponse({
            'success':True
        })

from openpyxl import load_workbook

def pharmacy_list(request):
            user_id = request.session.get('user_id')
            role = request.session.get('role')
            bloodgroup=MedicineCategory.objects.filter(created_by_id=user_id)
            company=Company.objects.filter(created_by_id=user_id)
            group=MedicineGroup.objects.filter(created_by_id=user_id)
            unit=Unit.objects.filter(created_by_id=user_id)
            medicine=Medicine.objects.filter(created_by_id=user_id)
        
            
            if role == 'super_admin':
                base = 'super_admin_home.html'
            elif role == 'admin':
                base = 'admin_home.html'
            elif role == 'manager':
                base = 'manager_home.html'
          
        
            active_category = request.GET.get('category')
        
            manager = Registration.objects.get(id=user_id)
        
            return render(request, 'pharmacy_list.html', {
                "user_id": user_id,
                "bloodgroup":bloodgroup,
                "company":company,
                "group":group,
            "unit":unit,
                
                "role": role,
                "manager": manager,
               "medicine":medicine,
                "base": base,
                "active_category": active_category,
            })
        
def save_medicine(request):
    user_id = request.session.get('user_id')

    if request.method == 'POST':

        name = request.POST.get('name')
        category_id = request.POST.get('category')
        company_id = request.POST.get('company')
        composition = request.POST.get('composition')
        group_id = request.POST.get('group')
        unit_id = request.POST.get('unit')
        medicine_level = request.POST.get('medicine_level')
        reorder_level = request.POST.get('reorder_level')
        tax = request.POST.get('tax')
        packing = request.POST.get('packing')
        vat = request.POST.get('vat')
        rac = request.POST.get('rac')
        note = request.POST.get('note')
        image = request.FILES.get('image')
        category=MedicineCategory.objects.get(id=category_id)
        company_obj = Company.objects.get(id=company_id)
        group_obj = MedicineGroup.objects.get(id=group_id)
        unit_obj = Unit.objects.get(id=unit_id)

        Medicine.objects.create(
            medicine_name=name,
            medicine_category=category,
            company=company_obj,
            medicine_composition=composition,
            medicine_group=group_obj,
            unit=unit_obj,
            medicine_level=medicine_level,
            reorder_level=reorder_level,
            tax=tax,
            packing=packing,
            vat=vat,
            rac=rac,
            note=note,
            image=image,
            created_by_id=user_id
        )
        return JsonResponse({
            'success': True,
            'message': 'Medicine saved successfully'
        })
def edit_medicine(request):

    id = request.POST.get('id')

    name = request.POST.get('name')
    category_id = request.POST.get('category')
    company_id = request.POST.get('company')
    composition = request.POST.get('composition')
    group_id = request.POST.get('group')
    unit_id = request.POST.get('unit')
    medicine_level = request.POST.get('medicine_level')
    reorder_level = request.POST.get('reorder_level')
    tax = request.POST.get('tax')
    packing = request.POST.get('packing')
    vat = request.POST.get('vat')
    rac = request.POST.get('rac')
    note = request.POST.get('note')

    image = request.FILES.get('image')

    category = MedicineCategory.objects.get(id=category_id)
    company_obj = Company.objects.get(id=company_id)
    group_obj = MedicineGroup.objects.get(id=group_id)
    unit_obj = Unit.objects.get(id=unit_id)

    comp = Medicine.objects.get(id=id)

    comp.medicine_name = name
    comp.medicine_category = category
    comp.company = company_obj
    comp.medicine_composition = composition
    comp.medicine_group = group_obj
    comp.unit = unit_obj
    comp.medicine_level = medicine_level
    comp.reorder_level = reorder_level
    comp.tax = tax
    comp.packing = packing
    comp.vat = vat
    comp.rac = rac
    comp.note = note

    if image:
        comp.image = image

    comp.save()

    return JsonResponse({'success': True})
def delete_medicine(request):
    id = request.POST.get('id')

    radio = Medicine.objects.get(id=id)
    radio.delete()

    return JsonResponse({
        'success': True
    })
def excel_save(request):
    if request.method == 'POST':

        excel = request.FILES.get('files')

       
        workbook = load_workbook(excel)
        sheet = workbook.active

        

        for row_no, row in enumerate(
            sheet.iter_rows(min_row=2, values_only=True),
            start=2
        ):

                medicine_name = row[0]
                category_name = row[1]
                company_name = row[2]
                composition = row[3]
                group_name = row[4]
                unit_name = row[5]
                medicine_level = row[6]
                reorder_level = row[7]
                tax = row[8]
                packing = row[9]
                vat = row[10]
                rac = row[11]
                note = row[12]

                category = MedicineCategory.objects.get(
                    category_name=category_name
                )

                company = Company.objects.get(
                    company_name=company_name
                )

                group = MedicineGroup.objects.get(
                    group_name=group_name
                )

                unit = Unit.objects.get(
                    unit_name=unit_name
                )

                Medicine.objects.create(
                    medicine_name=medicine_name,
                    medicine_category=category,
                    company=company,
                    medicine_composition=composition,
                    medicine_group=group,
                    unit=unit,
                    medicine_level=medicine_level,
                    reorder_level=reorder_level,
                    tax=tax,
                    packing=packing,
                    vat=vat,
                    rac=rac,
                    note=note
                )

           

        
        messages.success(
                request,
                'Medicines imported successfully.'
            )

        return redirect('pharmacy_list')

def purchase(request):
                user_id = request.session.get('user_id')
                role = request.session.get('role')
                bloodgroup=MedicineCategory.objects.filter(created_by_id=user_id)
                company=Company.objects.filter(created_by_id=user_id)
                group=MedicineGroup.objects.filter(created_by_id=user_id)
                supplier=Supplier.objects.filter(created_by_id=user_id)
                medicine=Medicine.objects.filter(created_by_id=user_id)
            
                
                if role == 'super_admin':
                    base = 'super_admin_home.html'
                elif role == 'admin':
                    base = 'admin_home.html'
                elif role == 'manager':
                    base = 'manager_home.html'
              
            
                active_category = request.GET.get('category')
            
                manager = Registration.objects.get(id=user_id)
            
                return render(request, 'purchase.html', {
                    "user_id": user_id,
                    "bloodgroup":bloodgroup,
                    "company":company,
                    "group":group,
                "supplier":supplier,
                    
                    "role": role,
                    "manager": manager,
                   "medicine":medicine,
                    "base": base,
                    "active_category": active_category,
                })









#RESTAPI
def medpage(request):
    return render(request,'medpage.html')
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import MedicineCategory
from .serializers import MedicineCategorySerializer

@api_view(['GET'])# "This API view accepts a GET request."
def medilist(request):
    cat=MedicineCategory.objects.all()
    seralizer=MedicineCategorySerializer(cat,many=True) #Converts those Django objects into API-friendly data.
    return Response(seralizer.data)# return it as json api response