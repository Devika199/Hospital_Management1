from .import views
from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve


urlpatterns = [
    path('',views.home_page,name='home_page'),
    path('login',views.login_page,name='login_page'),
    path('signup',views.signup_page,name='signup_page'),
    path('manager_home',views.manager_home,name='manager_home'),
    path('super_admin_approval',views.super_admin_approval,name='super_admin_approval'),
    path("super-admin-approval/<int:user_id>/approve/",views.approve_super_admin,name="approve_super_admin"),
    path("super-admin-approval/<int:user_id>/reject/",views.reject_super_admin,name="reject_super_admin"),
    path('logout/', views.logout_view, name='logout'),
    path('super_admin_home',views.super_admin_home,name='super_admin_home'),
    path('admin_approval',views.admin_approval,name='admin_approval'),
    path("admin-approval/<int:user_id>/approve/",views.approve_admin,name="approve_admin"),
    path("admin-approval/<int:user_id>/reject/",views.reject_admin,name="reject_admin"),
    path('admin_home',views.admin_home,name='admin_home'),
    path('user_approval',views.user_approval,name='user_approval'),
    path("user-approval/<int:user_id>/approve/",views.approve_user,name="approve_user"),
    path("user-approval/<int:user_id>/reject/",views.reject_user,name="reject_user"),
    path('dashboard',views.dashboard,name='dashboard'),
    
    path("check-registration-field/", views.check_registration_field, name="check_registration_field"),
    
    # Main Front Office page
    path('front-office', views.front_office_view, name='front_office'),
    
    # AJAX Action URLs
    path('front-office/save/', views.save_front_office, name='save_front_office'),
    path('front-office/delete/<int:pk>/', views.delete_front_office, name='delete_front_office'),
    
    path('list_patients',views.list_patients,name='list_patients'),
    path("patients/add/",views.add_patient,name="add_patient"),
    path("patients/check-phone/",views.check_patient_phone,name="check_patient_phone"),
    path("patients/check-alternative/",views.check_patient_alternative,name="check_patient_alternative"),
    path("patients/check-email/",views.check_patient_email,name="check_patient_email"),
    path("patients/check-aadhar/",views.check_patient_aadhar,name="check_patient_aadhar"),
    path("patients/delete/", views.delete_patients,name="delete_patients"),
    path("patients/disable/",views.disable_patient,name="disable_patient"),
    path("patients/edit/<int:user_id>/", views.edit_patient,name="edit_patient"),
    path('disable_patients',views.disable_patients,name='disable_patients'),
    path("patients/enable/",views.enable_patient,name="enable_patient"),
    path("patients/import/",views.import_patients,name="import_patients"), 
    path("patients/import/sample/",views.download_patient_sample,name="download_patient_sample"),
    
    # Operations routes
    path('operations', views.operations_view, name='operations'),
    path('operations/category/save/', views.save_operation_category, name='save_operation_category'),
    path('operations/category/delete/<int:pk>/', views.delete_operation_category, name='delete_operation_category'),
    path('operations/save/', views.save_operation, name='save_operation'),
    path('operations/delete/<int:pk>/', views.delete_operation, name='delete_operation'),
    
    # ICD routes
    path('icd', views.icd_view, name='icd_view'),
    path('icd/group/save/', views.save_icd_group, name='save_icd_group'),
    path('icd/group/delete/<int:pk>/', views.delete_icd_group, name='delete_icd_group'),
    path('icd/code/save/', views.save_icd_code, name='save_icd_code'),
    path('icd/code/delete/<int:pk>/', views.delete_icd_code, name='delete_icd_code'),
    
    # Live validation route
    path('setup/check-duplicate/', views.check_setup_field, name='check_setup_field'),
    
    path('bed_manager',views.bed_manager,name='bed_manager'),
    path('add-floor/', views.add_floor, name='add_floor'),
    path('add_bedgroup/', views.add_bedgroup, name='add_bedgroup'),
    path('add_bedtype/', views.add_bedtype, name='add_bedtype'),
    path('add_bed/', views.add_bed, name='add_bed'),
    path('delete_bed/<int:bed_id>/', views.delete_bed, name='delete_bed'),
    path('delete_bed_type/<int:id>/', views.delete_bed_type, name='delete_bed_type'),
    path('delete_bed_group/<int:id>/', views.delete_bed_group, name='delete_bed_group'),
    path('delete_floor/<int:id>/', views.delete_floor, name='delete_floor'),
    path('bed_superadmin',views.bed_superadmin,name='bed_superadmin'),
    path('add-floor1/', views.add_floor1, name='add_floor1'),
    path('add_bedgroup1/', views.add_bedgroup1, name='add_bedgroup1'),
    path('add_bedtype1/', views.add_bedtype1, name='add_bedtype1'),
    path('add_bed1/', views.add_bed1, name='add_bed1'),
    path('delete_bed1/<int:bed_id>/', views.delete_bed1, name='delete_bed1'),
    path('delete_bed_type1/<int:id>/', views.delete_bed_type1, name='delete_bed_type1'),
    path('delete_bed_group1/<int:id>/', views.delete_bed_group1, name='delete_bed_group1'),
    path('delete_floor1/<int:id>/', views.delete_floor1, name='delete_floor1'),
    path('bed_admin',views.bed_admin,name='bed_admin'),
    path('add-floor2/', views.add_floor2, name='add_floor2'),
    path('add_bedgroup2/', views.add_bedgroup2, name='add_bedgroup2'),
    path('add_bedtype2/', views.add_bedtype2, name='add_bedtype2'),
    path('add_bed2/', views.add_bed2, name='add_bed2'),
    path('delete_bed2/<int:bed_id>/', views.delete_bed2, name='delete_bed2'),
    path('delete_bed_type2/<int:id>/', views.delete_bed_type2, name='delete_bed_type2'),
    path('delete_bed_group2/<int:id>/', views.delete_bed_group2, name='delete_bed_group2'),
    path('delete_floor2/<int:id>/', views.delete_floor2, name='delete_floor2'),
    
    path("tpa_management/",views.tpa_management,name="tpa_management"),
    path("tpa/save/",views.save_tpa,name="save_tpa"),
    path("tpa/<int:tpa_id>/",views.get_tpa,name="get_tpa"),
    path("tpa/<int:tpa_id>/delete/",views.delete_tpa,name="delete_tpa"),
    path("hospital-charges/view/<int:charge_id>/",views.get_hospital_charge,name="get_hospital_charge"),
    path("hospital_charges/",views.hospital_charges,name="hospital_charges"),
    path("hospital-charges/data/<str:charge_type>/",views.hospital_charges_data,name="hospital_charges_data"),
    path("hospital-charges/delete/<str:charge_type>/<int:item_id>/",views.delete_hospital_charge_item,name="delete_hospital_charge_item"),
    path("hospital-charges/<str:charge_type>/<int:item_id>/",views.hospital_charge_detail,name="hospital_charge_detail"),
    path("hospital-charges/save/<str:charge_type>/",views.save_hospital_charge,name="save_hospital_charge"),
    path("tpa/data/",views.tpa_data,name="tpa_data"),
    
    path('manager_radiology',views.manager_radiology,name='manager_radiology'),
    path('manager_category',views.manager_category,name='manager_category'),
    path('manager_editcategory',views.manager_editcategory,name='manager_editcategory'),
    path('delete_radiocatgegory',views.delete_radiocatgegory,name='delete_radiocatgegory'),
    path('manager_unit',views.manager_unit,name='manager_unit'),
    path('manager_editunit',views.manager_editunit,name='manager_editunit'),
    path('delete_radiounit',views.delete_radiounit,name='delete_radiounit'),
    path('manager_parameter',views.manager_parameter,name='manager_parameter'),
    path('delete_radioparameter',views.delete_radioparameter,name='delete_radioparameter'),
    path('manager_editparameter',views.manager_editparameter,name='manager_editparameter'),
    path('pathologist_radiology', views.pathologist_radiology, name='pathologist_radiology'),

    path('pathologist_category', views.pathologist_category, name='pathologist_category'),
    path('pathologist_category/edit/', views.pathologist_editcategory, name='pathologist_editcategory'),
    path('pathologist_category/delete/', views.delete_pathologist_category, name='delete_pathologist_category'),
    
    path('pathologist_unit/', views.pathologist_unit, name='pathologist_unit'),
    path('pathologist_unit/edit', views.pathologist_editunit, name='pathologist_editunit'),
    path('pathologist_unit/delete', views.delete_pathologist_unit, name='delete_pathologist_unit'),
    
    path('pathologist-parameter/', views.pathologist_parameter, name='pathologist_parameter'),
    path('pathologist-parameter/edit', views.pathologist_editparameter, name='pathologist_editparameter'),
    path('pathologist-parameter/delete', views.delete_pathologist_parameter, name='delete_pathologist_parameter'),
    
    # Main Ambulance page
    path('ambulance', views.ambulance_view, name='ambulance'),
    path('ambulance/save/', views.save_ambulance, name='save_ambulance'),
    path('ambulance/delete/<int:pk>/', views.delete_ambulance, name='delete_ambulance'),
    path('ambulance/check-vehicle-number/', views.check_ambulance_vehicle_number, name='check_ambulance_vehicle_number'),
    
    path('human_resource/',views.human_resource,name='human_resource'),
    path('save_human_resource/',views.save_human_resource,name='save_human_resource'),
    path("delete_human_resource/",views.delete_human_resource,name="delete_human_resource"),
    
    path('finance', views.finance_view, name='finance'),
    path('finance/income-head/add/', views.add_income_head, name='add_income_head'),
    path('finance/income-head/edit/<int:pk>/', views.edit_income_head, name='edit_income_head'),
    path('finance/income-head/delete/<int:pk>/', views.delete_income_head, name='delete_income_head'),
    
    path('finance/expense-head/add/', views.add_expense_head, name='add_expense_head'),
    path('finance/expense-head/edit/<int:pk>/', views.edit_expense_head, name='edit_expense_head'),
    path('finance/expense-head/delete/<int:pk>/', views.delete_expense_head, name='delete_expense_head'),
    path('blood-bank', views.blood_bank_view, name='blood_bank'),
    path('blood-bank/add/', views.add_blood_product, name='add_blood_product'),
    path('blood-bank/edit/<int:pk>/', views.edit_blood_product, name='edit_blood_product'),
    path('blood-bank/delete/<int:pk>/', views.delete_blood_product, name='delete_blood_product'),
    
    path('pharmacy/', views.pharmacy_view, name='pharmacy_view'),
    path('pharmacy/supplier/save/', views.save_supplier, name='save_supplier'),
    path('pharmacy/supplier/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),
    path('pharmacy/medicine-category/save/', views.save_medicine_category, name='save_medicine_category'),
    path('pharmacy/medicine-category/delete/<int:pk>/', views.delete_medicine_category, name='delete_medicine_category'),
    path('pharmacy/dosage/save/', views.save_medicine_dosage, name='save_medicine_dosage'),
    path('pharmacy/dosage/delete/<int:pk>/', views.delete_medicine_dosage, name='delete_medicine_dosage'),
    
    path('pharmacy/unit/save/', views.save_unit, name='save_unit'),
    path('pharmacy/unit/delete/<int:pk>/', views.delete_unit, name='delete_unit'),
    
    path('pharmacy/interval/save/', views.save_dose_interval, name='save_dose_interval'),
    path('pharmacy/interval/delete/<int:pk>/', views.delete_dose_interval, name='delete_dose_interval'),
    
    path('pharmacy/duration/save/', views.save_dose_duration, name='save_dose_duration'),
    path('pharmacy/duration/delete/<int:pk>/', views.delete_dose_duration, name='delete_dose_duration'),
    
    path('pharmacy/company/save/', views.save_company, name='save_company'),
    path('pharmacy/company/delete/<int:pk>/', views.delete_company, name='delete_company'),
    
    path('pharmacy/medicine-group/save/', views.save_medicine_group, name='save_medicine_group'),
    path('pharmacy/medicine-group/delete/<int:pk>/', views.delete_medicine_group, name='delete_medicine_group'),
    
    path('pharmacy/export/excel/<str:tab>/', views.export_pharmacy_excel, name='export_pharmacy_excel'),
    
    path('pharmacy/export/pdf/<str:tab>/', views.export_pharmacy_pdf, name='export_pharmacy_pdf'),
    
    path('symptoms_manager/', views.symptoms_manager, name='symptoms_manager'),
    path('symptoms/delete/<int:id>/',views.delete_symptom_type,name='delete_symptom_type'),
    path('symptoms/save/',views.save_symptom_type,name='save_symptom_type'),
    path('symptoms/save-head/', views.save_symptom_head,name='save_symptom_head'),
    path('symptoms/head/delete/<int:id>/',views.delete_symptom_head,name='delete_symptom_head'),
    path("symptoms/export/excel/",views.export_symptoms_excel,name="export_symptoms_excel"),
    path("symptoms/export/pdf/",views.export_symptoms_pdf,name="export_symptoms_pdf"),
    path("symptoms/print/",views.print_symptoms,name="print_symptoms"),
    path('findings_manager/', views.findings_manager, name='findings_manager'),
    path("findings/category/save/",views.save_finding_category_manager,name="save_finding_category"),
    path("findings/save/",views.save_finding_manager,name="save_finding"),
    path("findings/category/delete/<int:id>/",views.delete_finding_category_manager,name="delete_finding_category"),
    path("findings/delete/<int:id>/",views.delete_finding_manager,name="delete_finding"),
    path("findings/export/excel/",views.export_findings_excel,name="export_findings_excel"),
    path("findings/export/pdf/",views.export_findings_pdf,name="export_findings_pdf"),
    path("findings/print/",views.print_findings,name="print_findings"),
    path("vitals/manager/",views.vital_manager,name="vitals_manager"),
    path("vitals/manager/save/",views.save_vital_manager,name="save_vital_manager"),
    path("vitals/manager/delete/<int:id>/",views.delete_vital_manager,name="delete_vital_manager"),
    path("vitals/export/excel/",views.export_vitals_excel,name="export_vitals_excel"),
    path("vitals/export/pdf/",views.export_vitals_pdf,name="export_vitals_pdf"),
    path('symptoms_superadmin/',views.symptoms_superadmin,name='symptoms_superadmin'),
    path('superadmin/symptoms/delete/<int:id>/',views.superadmin_delete_symptom_type,name='superadmin_delete_symptom_type'),
    path('superadmin/symptoms/save/',views.superadmin_save_symptom_type,name='superadmin_save_symptom_type'),
    path('superadmin/symptoms/save-head/',views.superadmin_save_symptom_head,name='superadmin_save_symptom_head'),
    path('superadmin/symptoms/head/delete/<int:id>/',views.superadmin_delete_symptom_head,name='superadmin_delete_symptom_head'),
    path('findings_superadmin/',views.findings_superadmin,name='findings_superadmin'),
    path('superadmin/findings/category/save/',views.superadmin_save_finding_category_manager,name='superadmin_save_finding_category'),
    path('superadmin/findings/save/',views.superadmin_save_finding_manager,name='superadmin_save_finding'),
    path('superadmin/findings/category/delete/<int:id>/',views.superadmin_delete_finding_category_manager,name='superadmin_delete_finding_category'),
    path('superadmin/findings/delete/<int:id>/',views.superadmin_delete_finding_manager,name='superadmin_delete_finding'),
    path('vitals_superadmin',views.vitals_superadmin,name='vitals_superadmin'),
    path('superadmin/vitals/manager/save/',views.superadmin_save_vital_manager,name='superadmin_save_vital_manager'),
    path('superadmin/vitals/manager/delete/<int:id>/',views.superadmin_delete_vital_manager,name='superadmin_delete_vital_manager'),
    path("symptoms_admin/",views.symptoms_admin,name="symptoms_admin"),
    path("admin_save_symptom_type/",views.admin_save_symptom_type,name="admin_save_symptom_type"),
    path("admin_delete_symptom_type/<int:id>/",views.admin_delete_symptom_type,name="admin_delete_symptom_type"),
    path("admin_save_symptom_head/",views.admin_save_symptom_head,name="admin_save_symptom_head"),
    path("admin_delete_symptom_head/<int:id>/",views.admin_delete_symptom_head,name="admin_delete_symptom_head"),
    path("findings_admin/",views.findings_admin,name="findings_admin"),
    path("admin_save_finding_category/",views.admin_save_finding_category_manager,name="admin_save_finding_category"),
    path("admin_save_finding/",views.admin_save_finding_manager,name="admin_save_finding"),
    path("admin_delete_finding_category/<int:id>/",views.admin_delete_finding_category_manager,name="admin_delete_finding_category"),
    path("admin_delete_finding/<int:id>/",views.admin_delete_finding_manager,name="admin_delete_finding"),
    path("vitals_admin/",views.vitals_admin,name="vitals_admin"),
    path("admin_save_vital/",views.admin_save_vital_manager,name="admin_save_vital"),
    path("admin_delete_vital/<int:id>/",views.admin_delete_vital_manager,name="admin_delete_vital"),
    
    # Inventory routes
    path('inventory', views.inventory_view, name='inventory'),
    path('inventory/category/save/', views.save_inventory_category, name='save_inventory_category'),
    path('inventory/category/delete/<int:pk>/', views.delete_inventory_category, name='delete_inventory_category'),
    path('inventory/store/save/', views.save_inventory_store, name='save_inventory_store'),
    path('inventory/store/delete/<int:pk>/', views.delete_inventory_store, name='delete_inventory_store'),
    path('inventory/supplier/save/', views.save_inventory_supplier, name='save_inventory_supplier'),
    path('inventory/supplier/delete/<int:pk>/', views.delete_inventory_supplier, name='delete_inventory_supplier'),
    
    # Referral routes
    path('referral', views.referral_view, name='referral_view'),
    path('referral/category/save/', views.save_referral_category, name='save_referral_category'),
    path('referral/category/delete/<int:pk>/', views.delete_referral_category, name='delete_referral_category'),
    path('referral/commission/save/', views.save_referral_commission, name='save_referral_commission'),
    path('referral/commission/delete/<int:pk>/', views.delete_referral_commission, name='delete_referral_commission'),

     
    

path('compound_list',views.compound_list,name='compound_list'),
path('save_component',views.save_component,name='save_component'),
path('edit_component',views.edit_component,name='edit_component'),
path('delete_component',views.delete_component,name='delete_component'),

path('pharmacy_list',views.pharmacy_list,name='pharmacy_list'),   
path('save_medicine',views.save_medicine,name='save_medicine'), 
path('edit_medicine',views.edit_medicine,name='edit_medicine'),
path('delete_medicine',views.delete_medicine,name='delete_medicine'),
path('excel_save',views.excel_save,name='excel_save'),
path('purchase',views.purchase,name='purchase'),


#restapi
path('medilist',views.medilist,name='medilist'),
path('medpage',views.medpage,name='medpage'),


     
     re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
     
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

