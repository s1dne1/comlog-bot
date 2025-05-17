# verificar_notificacoes_loop.py
import os
import django
import time
from django.core.management import call_command

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comlog_web.settings')
django.setup()

# Loop de execução
while True:
    print("🔁 Rodando verificar_notificacoes...")
    try:
        call_command('verificar_notificacoes')
    except Exception as e:
        print(f"❌ Erro: {e}")
    time.sleep(10)  # ⏱ Ajuste o tempo aqui (segundos)
