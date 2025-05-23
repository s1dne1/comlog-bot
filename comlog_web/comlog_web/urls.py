"""
URL configuration for comlog_web project.

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
from django.urls import path, include

from core.views import login_view, logout_view  # ou onde estiver sua view





urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # ← adiciona o app core aqui

 # 👇 Adicione isso:
    path('painel/', include('painel.urls')),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

]

# Celery com Redis (usando localhost:6379)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
