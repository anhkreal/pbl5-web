"""
URL configuration for fe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from app import view_account
from app import view_detection

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('thu-vien-con-trung/', views.thu_vien_con_trung, name='thu_vien_con_trung'),
    path('login/', view_account.login_view, name='login'),
    path('register/', view_account.register, name='register'),
    path('logout/', view_account.logout_view, name='logout'),
    path('account-info/', view_account.account_info, name='account_info'),
    path('livefeed/', views.livefeed, name='livefeed'),
    path('insect/<int:id>/', views.insect_detail, name='insect_detail'),
    path('api/detect_insect', view_detection.detect_insect_from_frame, name='api_detect_insect'),
    path('history/', views.history, name='history'),
]
