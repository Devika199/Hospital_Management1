from django.db import models
from datetime import date, datetime

class Registration(models.Model):

    ROLE_CHOICES = [
        ("manager", "Manager"),
        ("super_admin", "Super Admin"),
        ("admin", "Admin"),
        ("doctor", "Doctor"),
        ("accountant", "Accountant"),
        ("receptionist", "Receptionist"),
        ("pharmacist", "Pharmacist"),
        ("pathologist", "Pathologist"),
        ("radiologist", "Radiologist"),
        ("head_nurse", "Head Nurse"),
        ("nurse", "Nurse"),
        ("billing_executive", "Billing Executive"),
        ("patient", "Patient"),
    ]

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    # Personal details
    aadhar_number = models.CharField(
        max_length=12,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    email = models.EmailField(
        unique=True
    )

    username = models.CharField(
        max_length=100,
        unique=True
    )

    phone = models.CharField(
        max_length=10,
        unique=True
    )

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    guardian_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    # Password
    password = models.CharField(
        max_length=128
    )

    # Approval
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("disabled", "Disabled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    age = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    is_dead = models.BooleanField(
    default=False
    )

    blood_group = models.CharField(
    max_length=5,
    blank=True,
    null=True
    )

    marital_status = models.CharField(
    max_length=30,
    blank=True,
    null=True
    )

    alternative_number = models.CharField(
    max_length=10,
    unique=True,
    blank=True,
    null=True
    )

    remarks = models.TextField(
    blank=True,
    null=True
    )

    allergies = models.TextField(
    blank=True,
    null=True
    )

    tpa = models.CharField(
    max_length=150,
    blank=True,
    null=True
    )

    tpa_id = models.CharField(
    max_length=100,
    blank=True,
    null=True
    )

    tpa_validity = models.DateField(
    blank=True,
    null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        # Calculate age only if age is empty
        if self.age is None and self.date_of_birth:

            dob = self.date_of_birth

            # If DOB is received as string
            if isinstance(dob, str):
                dob = datetime.strptime(
                    dob, "%Y-%m-%d"
                ).date()

                self.date_of_birth = dob

            today = date.today()

            self.age = (
                today.year
                - dob.year
                - (
                    (today.month, today.day)
                    < (dob.month, dob.day)
                )
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role}"
        
class FrontOffice(models.Model):
    CATEGORY_CHOICES = (
        ('purpose', 'Purpose'),
        ('complaint', 'Complaint'),
        ('source', 'Source'),
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='front_office_records')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"

# Operations

class OperationCategory(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='operation_categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Operation(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(OperationCategory, on_delete=models.CASCADE, related_name='operations')
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='operations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# ICD

class ICDGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='icd_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ICDCode(models.Model):
    code = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey(ICDGroup, on_delete=models.CASCADE, related_name='icd_codes')
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='icd_codes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.group.name}"
    
class Floor(models.Model):
    role = models.ForeignKey(Registration, on_delete=models.CASCADE)
    floor_name=models.CharField(max_length=50, null=True, blank=True)
    description=models.CharField(max_length=50, null=True, blank=True)
class Bedgroup(models.Model):
    role = models.ForeignKey(Registration, on_delete=models.CASCADE)
    floor = models.ForeignKey(Floor,on_delete=models.SET_NULL,null=True,blank=True)
    group_name=models.CharField(max_length=50, null=True, blank=True)
    colour=models.CharField(max_length=50, null=True, blank=True)
    description=models.CharField(max_length=50, null=True, blank=True)
class Bedtype(models.Model):
    role = models.ForeignKey(Registration, on_delete=models.CASCADE)
    type_name=models.CharField(max_length=50, null=True, blank=True)
class Bed(models.Model):
    role = models.ForeignKey(Registration, on_delete=models.CASCADE)
    floor = models.ForeignKey(Floor,on_delete=models.SET_NULL,null=True,blank=True)
    bedtype = models.ForeignKey(Bedtype,on_delete=models.SET_NULL,null=True,blank=True)
    bedgroup = models.ForeignKey(Bedgroup,on_delete=models.SET_NULL,null=True,blank=True)
    bed_name=models.CharField(max_length=50, null=True, blank=True)
    description=models.CharField(max_length=50, null=True, blank=True)
    not_available = models.BooleanField(default=False)
    status =models.CharField(max_length=50, null=True, blank=True)
    
class TPA(models.Model):

    tpa_name = models.CharField(max_length=200)
    code = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
    contact_person = models.CharField(max_length=200)
    contact_person_mobile = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tpa_name

    class Meta:
        ordering = ["tpa_name"]



class HospitalChargeUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class HospitalTax(models.Model):
    name = models.CharField(max_length=100, unique=True)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    def __str__(self):
        return self.name


class HospitalChargeType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    appointment = models.BooleanField(default=False)
    opd = models.BooleanField(default=False)
    ipd = models.BooleanField(default=False)
    pathology = models.BooleanField(default=False)
    radiology = models.BooleanField(default=False)
    blood_bank = models.BooleanField(default=False)
    ambulance = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class HospitalChargeCategory(models.Model):
    name = models.CharField(max_length=100)

    charge_type = models.ForeignKey(
        HospitalChargeType,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class HospitalCharge(models.Model):

    name = models.CharField(max_length=200)

    charge_type = models.ForeignKey(
        HospitalChargeType,
        on_delete=models.PROTECT
    )

    category = models.ForeignKey(
        HospitalChargeCategory,
        on_delete=models.PROTECT
    )

    unit = models.ForeignKey(
        HospitalChargeUnit,
        on_delete=models.PROTECT
    )

    tax = models.ForeignKey(
        HospitalTax,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    standard_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class HospitalChargeTPA(models.Model):

    charge = models.ForeignKey(
        HospitalCharge,
        on_delete=models.CASCADE,
        related_name="tpa_charges"
    )

    tpa = models.ForeignKey(
        "TPA",
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ("charge", "tpa")
        
class RadiologyCategory(models.Model):
    CATEGORY_CHOICES = (
        ('category', 'Category'),
        ('Unit', 'unit'),
        ('Parameter', 'parameter'),
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
class RadiologyUnit(models.Model):
    CATEGORY_CHOICES = (
        ('category', 'Category'),
        ('Unit', 'unit'),
        ('Parameter', 'parameter'),
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"

class RadiologyParameter(models.Model):
    CATEGORY_CHOICES = (
        ('category', 'Category'),
        ('Unit', 'unit'),
        ('Parameter', 'parameter'),
    )
    unit = models.ForeignKey(RadiologyUnit, on_delete=models.SET_NULL, null=True, blank=True, )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    fromrange = models.CharField(max_length=100, null=True, blank=True)
    torange = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"


class PathologyCategory(models.Model):
    CATEGORY_CHOICES = (
        ('category', 'Category'),
        ('Unit', 'unit'),
        ('Parameter', 'parameter'),
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
class PathologyUnit(models.Model):
    CATEGORY_CHOICES = (
        ('category', 'Category'),
        ('Unit', 'unit'),
        ('Parameter', 'parameter'),
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"

class PathologyParameter(models.Model):
    CATEGORY_CHOICES = (
        ('category', 'Category'),
        ('Unit', 'unit'),
        ('Parameter', 'parameter'),
    )
    unit = models.ForeignKey(PathologyUnit, on_delete=models.SET_NULL, null=True, blank=True, )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    fromrange = models.CharField(max_length=100, null=True, blank=True)
    torange = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
        
#Ambulance

class Ambulance(models.Model):
    TYPE_CHOICES = (
        ('contract', 'Contract'),
        ('owned', 'Owned'),
    )


    Driver_name = models.CharField(max_length=100)
    Vehicle_number = models.CharField(max_length=50)
    Vehicle_model = models.CharField(max_length=100)
    Year_Manufactor = models.CharField(max_length=25)
    Driver_License = models.CharField(max_length=50)
    Contact_number = models.CharField(max_length=25)
    Vehicle_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    Notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='ambulances')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.Vehicle_number} - {self.Driver_name}"

    @property
    def driver_name(self):
        return self.Driver_name

    @property
    def vehicle_number(self):
        return self.Vehicle_number

    @property
    def vehicle_model(self):
        return self.Vehicle_model

    @property
    def year_manufactor(self):
        return self.Year_Manufactor

    @property
    def driver_license(self):
        return self.Driver_License

    @property
    def contact_number(self):
        return self.Contact_number

    @property
    def vehicle_type(self):
        return self.Vehicle_type

    @property
    def notes(self):
        return self.Notes
#End

class HumanResource(models.Model):

    CATEGORY_CHOICES = (
        ('leave_type', 'Leave Type'),
        ('department', 'Department'),
        ('designation', 'Designation'),
        ('specialist', 'Specialist'),
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    name = models.CharField(max_length=150)

    created_by = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='human_resource_records'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"
        
class IncomeHead(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='income_heads'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ExpenseHead(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expense_heads'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BloodProduct(models.Model):

    TYPE_CHOICES = [
        ('component', 'Component'),
        ('blood_group', 'Blood Group'),
    ]

    name = models.CharField(max_length=200)

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    created_by = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blood_products'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MedicineCategory(models.Model):

    category_name = models.CharField(max_length=150, unique=True)

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="medicine_categories"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name


class Unit(models.Model):

    unit_name = models.CharField(max_length=100, unique=True)

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pharmacy_units"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["unit_name"]

    def __str__(self):
        return self.unit_name


class DoseInterval(models.Model):

    interval_name = models.CharField(max_length=100, unique=True)

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="dose_intervals"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["interval_name"]

    def __str__(self):
        return self.interval_name


class DoseDuration(models.Model):

    duration_name = models.CharField(max_length=100, unique=True)

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="dose_durations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["duration_name"]

    def __str__(self):
        return self.duration_name


class Company(models.Model):

    company_name = models.CharField(max_length=150, unique=True)

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pharmacy_companies"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class MedicineGroup(models.Model):

    group_name = models.CharField(max_length=150, unique=True)

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="medicine_groups"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["group_name"]

    def __str__(self):
        return self.group_name


class Supplier(models.Model):

    supplier_name = models.CharField(max_length=150)

    supplier_contact = models.CharField(max_length=20, blank=True, null=True)

    contact_person_name = models.CharField(max_length=150, blank=True, null=True)

    contact_person_phone = models.CharField(max_length=20, blank=True, null=True)

    drug_license_number = models.CharField(max_length=100, blank=True, null=True)

    address = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="suppliers"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.supplier_name


class MedicineDosage(models.Model):

    category = models.ForeignKey(
        MedicineCategory, on_delete=models.CASCADE, related_name="dosages"
    )

    dose = models.CharField(max_length=50)

    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="dosages"
    )

    created_by = models.ForeignKey(
        Registration, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="medicine_dosages"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.category.category_name} - {self.dose} {self.unit.unit_name}"
        
class SymptomType(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SymptomHead(models.Model):
    name = models.CharField(max_length=200)
    symptom_type = models.ForeignKey(SymptomType,on_delete=models.CASCADE,related_name='symptom_heads')
    description = models.TextField(blank=True,null=True)
    def __str__(self):
        return self.name

class FindingCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Finding(models.Model):
    category = models.ForeignKey(FindingCategory,on_delete=models.CASCADE,related_name='findings')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Vital(models.Model):
    name = models.CharField(max_length=100)
    from_value = models.DecimalField(max_digits=10,decimal_places=2)
    to_value = models.DecimalField(max_digits=10,decimal_places=2)
    unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
        
class InventoryCategory(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class InventoryStore(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_stores')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class InventorySupplier(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_suppliers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==========================================
# REFERRAL SETUP MODULE MODELS
# ==========================================

class ReferralCategory(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='referral_categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ReferralCommission(models.Model):
    category = models.ForeignKey(ReferralCategory, on_delete=models.CASCADE, related_name='commissions')
    standard_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    opd_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ipd_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pharmacy_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pathology_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    radiology_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ambulance_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    blood_bank_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='referral_commissions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commission for {self.category.name}"

class Component(models.Model):
    componentname=models.CharField(max_length=100, blank=True, null=True)
    bag=models.CharField(max_length=100, blank=True, null=True)
   
    bloodgroup=models.ForeignKey(
        BloodProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    

    created_by = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.component} - {self.bag_no}"

class ComponentDetails(models.Model):
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE
    )
    blood_component = models.ForeignKey(
        BloodProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='component_entries'
    )
    

    bag_no = models.CharField(max_length=100, blank=True, null=True)
    volume = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=100, blank=True, null=True)
    lot = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=255, blank=True, null=True)

   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.component} - {self.bag_no}"

class Medicine(models.Model):

    medicine_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    medicine_category = models.ForeignKey(
        MedicineCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    medicine_composition = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    medicine_group = models.ForeignKey(
        MedicineGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    medicine_level = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    reorder_level = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    tax = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    packing = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    vat = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    rac = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    note = models.TextField(
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='medicine/',
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.medicine_name or ''