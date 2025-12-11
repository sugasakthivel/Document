from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload_file'),
    path('file/<str:token>/', views.file_detail, name='file_detail'),
    path('file/<str:token>/delete/', views.delete_file, name='delete_file'),
    path('file/<str:token>/toggle/', views.toggle_file_status, name='toggle_file_status'),
    path('download/<str:token>/', views.download_file, name='download_file'),
]




