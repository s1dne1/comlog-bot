# painel/urls.py
from django.urls import path
from . import views

app_name = 'painel'

urlpatterns = [
    path('', views.index, name='index'),
    path('regras/', views.regras, name='tela_regras'),
    path('regras/nova/', views.nova_regra, name='nova_regra'),
    path('regras/editar/<int:pk>/', views.editar_regra, name='editar_regra'),
    path('regras/excluir/<int:pk>/', views.excluir_regra, name='excluir_regra'),

    # URLs para Fonte API (já implementadas)
    path('fontes/', views.fonte_api_list, name='fonte_api_list'),
    path('fontes/nova/', views.fonte_api_form, name='fonte_api_form'),
    path('fontes/editar/<int:pk>/', views.editar_fonte_api, name='editar_fonte_api'),
    path('fontes/excluir/<int:pk>/', views.excluir_regra, name='excluir_fonte_api'),
    

    # URLs para Requisições (já implementadas)
    path('requisicoes/', views.requisicao_list, name='requisicao_list'),
    path('requisicoes/nova/', views.requisicao_form, name='requisicao_form'),
    path('requisicoes/editar/<int:pk>/', views.editar_requisicao_api, name='editar_requisicao_api'),
    path('requisicoes/excluir/<int:pk>/', views.excluir_requisicao, name='excluir_requisicao_api'),



     path('requisicoes/<int:pk>/variaveis/', views.capturar_variaveis, name='capturar_variaveis'),



]
