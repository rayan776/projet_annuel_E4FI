"""
URL configuration for announces application

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.index, name='accounts'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('viewProfile/<str:login>', views.view_profile, name='viewProfile'),
    path('getBlockedList/', views.getBlockedList, name=''),
    path('resetPassword', views.resetPassword, name='resetPassword'),
    path('checkUsername/', views.checkUsername, name='checkUsername'),
    path('checkSecretAnswer/', views.checkSecretAnswer, name='checkSecretAnswer'),
    path('showSecretAnswer/', views.showSecretAnswer, name='showSecretAnswer')
]