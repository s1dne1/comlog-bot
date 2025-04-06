from django.contrib import admin
from .models import RespostaAutomatica, IntegracaoCargaPontual, InscricaoNotificacao
from .models import HistoricoMensagem, MenuBot, FonteDeDados,RequisicaoAPI,VariavelDisponivel,RegraAutomatica,AcaoAutomatizada
from import_export.admin import ExportMixin, ImportExportModelAdmin
from django.contrib import messages
import requests

# ✅ Registro correto, sem duplicidade
admin.site.register(IntegracaoCargaPontual)
admin.site.register(HistoricoMensagem)
# admin.site.register(FonteDeDados)    
# admin.site.register(RequisicaoAPI)    
admin.site.register(VariavelDisponivel)     
# admin.site.register(RegraAutomatica)  
admin.site.register(InscricaoNotificacao)



@admin.register(RespostaAutomatica)
class RespostaAutomaticaAdmin(admin.ModelAdmin):
    list_display = ['palavra_chave', 'pergunta_sequencial', 'ativo']
    actions = ['preencher_variaveis_disponiveis']

    def preencher_variaveis_disponiveis(self, request, queryset):
        for obj in queryset:
            if not obj.id_exemplo:
                self.message_user(request, f"❗ Preencha o ID de exemplo para {obj.palavra_chave}", level=messages.WARNING)
                continue

            try:
                url = f"http://127.0.0.1:8001/api/agendamento-dados/{obj.id_exemplo}"
                response = requests.get(url)
                dados = response.json()

                # Extrai as chaves como variáveis
                variaveis = [f"{{{{{k}}}}}" for k in dados.keys()]
                obj.variaveis_disponiveis = ", ".join(variaveis)
                obj.save()

                self.message_user(request, f"✅ Variáveis preenchidas para {obj.palavra_chave}", level=messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"Erro ao consultar API para {obj.palavra_chave}: {str(e)}", level=messages.ERROR)

    preencher_variaveis_disponiveis.short_description = "🔄 Preencher variáveis disponíveis a partir da API"
@admin.register(MenuBot)
class MenuBotAdmin(ImportExportModelAdmin, ExportMixin, admin.ModelAdmin):
    list_display = ['id_menu', 'opcao_usuario', 'proximo', 'ativo']
    search_fields = ['id_menu', 'proximo']
    list_filter = ['ativo']

# @admin.register(AcaoAutomatizada)
# class AcaoAutomatizadaAdmin(admin.ModelAdmin):
#     list_display = ['id', 'nome', 'metodo', 'endpoint_api']
#     search_fields = ['nome']
    
