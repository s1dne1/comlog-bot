from django.urls import path
from . import views





urlpatterns = [
    path('', views.home, name='home'),
    path('enviar/', views.envio, name='envio'),
    path('api/resposta/', views.resposta_automatica, name='resposta_automatica'),
    path('api/token-carga-pontual/', views.token_carga_pontual, name='token_carga_pontual'),
    path('api/config-carga-pontual/', views.config_carga_pontual, name='config_carga_pontual'),
    path('api/resposta-agendamento/<int:age_id>/', views.resposta_agendamento, name='resposta_agendamento'),
    path('api/resposta-configurada/', views.resposta_configurada),
    path('api/agendamento-dados/<int:age_id>/', views.agendamento_dados_puros),
    path('api/menu/', views.menu_proximo),
    path('api/menu-texto/', views.menu_texto),
    path('api/historico/', views.registrar_historico),
    path("api/mensagem/", views.processar_mensagem),
    path('api/regras-automatizadas/', views.listar_regras, name='listar_regras'),
    path('api/inscrever-notificacao/', views.inscrever_notificacao),
    path('chegadas/', views.chegadas, name='chegadas'),
    path('api/confirmar-chegada/', views.confirmar_chegada, name='confirmar_chegada'),



]