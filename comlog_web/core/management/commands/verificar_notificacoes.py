# core/management/commands/verificar_notificacoes.py
from django.core.management.base import BaseCommand
from core.models import InscricaoNotificacao, IntegracaoCargaPontual
from core.views import consultar_status_agendamento
import requests

class Command(BaseCommand):
    help = 'Verifica status de agendamentos e notifica motoristas se houver mudança'

    def handle(self, *args, **kwargs):
        print("\n🔍 Iniciando verificação de notificações...")

        inscricoes = InscricaoNotificacao.objects.filter(ativo=True)
        config = IntegracaoCargaPontual.objects.first()

        if not config:
            self.stdout.write(self.style.ERROR("❌ Configuração da API (IntegracaoCargaPontual) não encontrada."))
            return

        if not inscricoes.exists():
            self.stdout.write(self.style.WARNING("⚠️ Nenhuma inscrição de notificação ativa encontrada."))
            return

        print(f"📌 Total de inscrições ativas encontradas: {inscricoes.count()}")

        for insc in inscricoes:
            try:
                print(f"\n🔄 Verificando agendamento: {insc.agendamento_id} para número: {insc.numero}")

                dados = consultar_status_agendamento(config, insc.agendamento_id)
                print(f"🔎 Dados retornados: {dados}")

                novo_status = dados.get("status")
                if not novo_status:
                    self.stdout.write(self.style.WARNING(f"⚠️ Sem status para agendamento {insc.agendamento_id}"))
                    continue

                if novo_status != insc.status_atual:
                    mensagem = f"🔔 O status do seu agendamento {insc.agendamento_id} mudou para: {novo_status}"
                    print(f"📬 Enviando mensagem: {mensagem}")

                    envio = requests.post("http://127.0.0.1:3000/enviar", json={
                        "numero": insc.numero,
                        "mensagem": mensagem
                    })

                    if envio.status_code == 200:
                        self.stdout.write(self.style.SUCCESS(f"✔️ Notificado: {insc.numero} | Novo status: {novo_status}"))
                        insc.status_atual = novo_status
                        insc.save()
                    else:
                        self.stdout.write(self.style.ERROR(f"❌ Erro ao enviar para {insc.numero}: {envio.text}"))

                else:
                    print(f"✅ Status inalterado: {novo_status}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erro com agendamento {insc.agendamento_id}: {str(e)}"))
