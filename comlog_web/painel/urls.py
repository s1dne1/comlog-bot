# painel/urls.py
from django.urls import path
from . import views
app_name = 'painel'

urlpatterns = [
    path('', views.index, name='index'),
    path('config/', views.config, name='config'),
    path('home/', views.home, name='home'),
    path('menu/', views.listar_menus, name='tela_menu'),
    path('menu/novo/', views.novo_menu, name='novo_menu'),
    path('menu/editar/<int:pk>/', views.editar_menu, name='editar_menu'),
    path('menu/excluir/<int:pk>/', views.excluir_menu, name='excluir_menu'),

    # URLs para Fonte API (já implementadas)
    path('resposta_automatica/', views.resposta_automatica_list, name='resposta_automatica_list'),
    path('resposta_automatica/nova/', views.resposta_automatica_form, name='resposta_automatica_form'),
    path('resposta_automatica/editar/<int:pk>/', views.editar_resposta_automatica, name='editar_resposta_automatica'),
    path('resposta_automatica/excluir/<int:pk>/', views.excluir_resposta_automatica, name='excluir_resposta_automatica'),
    

    # URLs para Requisições (já implementadas)
    path('requisicoes/', views.requisicao_list, name='requisicao_list'),
    path('requisicoes/nova/', views.requisicao_form, name='requisicao_form'),
    path('requisicoes/editar/<int:pk>/', views.editar_requisicao_api, name='editar_requisicao_api'),
    path('requisicoes/excluir/<int:pk>/', views.excluir_requisicao, name='excluir_requisicao_api'),



    path('requisicoes/<int:pk>/variaveis/', views.capturar_variaveis, name='capturar_variaveis'),
    path('chegadas/', views.chegadas, name='chegadas'),


     
      



]
