from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard & Root
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Transaction Management (CRUD)
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/add/', views.transaction_create_view, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_update_view, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete_view, name='transaction_delete'),

    # Monthly Summary & Analytics
    path('monthly-summary/', views.monthly_summary_view, name='monthly_summary'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
