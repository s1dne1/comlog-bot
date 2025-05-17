# core/tasks.py

from celery import shared_task
from core.management.commands.verificar_notificacoes import Command as Verifica

@shared_task
def verificar_notificacoes_task():
    print("🔔 Executando verificação via Celery...")
    Verifica().handle()
