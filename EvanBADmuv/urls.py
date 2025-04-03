from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login', views.login, name='login'),
    path('create_Request/<int:pk>/', views.create_Request, name='create_Request'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('login', views.login, name='login'),
    path('rform/<int:pk>/', views.rform, name='rform'),
    path('rformtable/<int:pk>/', views.rformtable, name='rformtable'),
    path('logout_view', views.logout_view, name='logout_view'),
    path('scholar/<int:pk>/', views.scholar, name='scholar'),
    path('scholar_opp_details/<int:pk>/<int:pk2>', views.scholar_opp_details, name='scholar_opp_details'),

    #path('scholar_breakdown/<int:pk>/<int:pk2>', views.scholar_breakdown, name='scholar_breakdown'),
    path('scholar_breakdown/<int:pk>', views.scholar_breakdown, name='scholar_breakdown'),
    path('oaa_rformtable/<int:pk>/', views.oaa_rformtable, name='oaa_rformtable'),
    path('oaa_opp_details/<int:pk>/<int:pk2>', views.oaa_opp_details, name='oaa_opp_details'),
    path('opp_details/<int:pk>/<int:pk2>', views.opp_details, name='opp_details'),
    path('enlisted_scholars_table/<int:pk>/<int:pk2>/<int:pk3>', views.enlisted_scholars_table, name='enlisted_scholars_table'),
    #path('delete_enlisted_scholar/<int:pk>/<int:pk2>/<int:pk3>', views.delete_enlisted_scholar, name='delete_enlisted_scholar'),
    path('oaa_upkeep/<int:pk>', views.oaa_upkeep, name='oaa_upkeep'),
    path('bulkdelete', views.bulkdelete, name='bulkdelete'),
    path('oaa_manage_users/<int:pk>', views.oaa_manage_users, name='oaa_manage_users'),
    path('oaa_create_scholar/<int:pk>', views.oaa_create_scholar, name='oaa_create_scholar'),
    path('oaa_create_office/<int:pk>', views.oaa_create_office, name='oaa_create_office'),
    path('oaa_delete_office/<int:pk>', views.oaa_delete_office, name='oaa_delete_office'),
    path('oaa_delete_scholar/<int:pk>', views.oaa_delete_scholar, name='oaa_delete_scholar'),
    path('oaa_office_user/<int:pk>', views.oaa_office_user, name='oaa_office_user'),
    path('add_scholar/<int:pk>/<int:pk2>/<int:pk3>', views.add_scholar, name='add_scholar'),
    path('oaa_scholar_status/<int:pk>', views.oaa_scholar_status, name='oaa_scholar_status'),
    path('scholar_update_details/<int:pk>/', views.scholar_update_details, name='scholar_update_details'),    
    path('update_contact_details/<int:pk>', views.update_contact_details, name='update_contact_details'),
    path('change_password/<int:pk>/', views.change_password, name='change_password'),
    path('check_credentials/', views.check_credentials, name='check_credentials'),
    path('upload_scholar/', views.upload_scholar, name='upload_scholar'),

]


