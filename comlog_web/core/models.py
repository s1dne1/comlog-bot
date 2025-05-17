from django.db import models

# Create your models here.

    

class IntegracaoCargaPontual(models.Model):
    nome_configuracao = models.CharField(max_length=100, default='default')
    token_combinado = models.CharField(max_length=100)
    identificador_empresa = models.IntegerField()
    login_usuario = models.CharField(max_length=100)
    senha_usuario = models.CharField(max_length=100)
    url_base = models.CharField(max_length=200, default="https://maringaferroliga.cargapontual.com")
    rota_agendamento = models.CharField(max_length=200, default="/sistema/Integracao/strada_rest_v_100/servidor/v100/agendamento/agendamentoauxiliar100/age_id=")
    porta = models.CharField(max_length=10, default="443")

class HistoricoMensagem(models.Model):
    numero = models.CharField(max_length=20)
    mensagem_recebida = models.TextField()
    mensagem_enviada = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.numero} - {self.data.strftime('%d/%m/%Y %H:%M')}"
    
class MenuBot(models.Model):
    id_menu = models.CharField(max_length=100, help_text="Ex: menu_principal")
    texto = models.TextField(help_text="Texto exibido ao usuário")
    opcao_usuario = models.CharField(
        max_length=20,
        blank=True,
        help_text="Ex: 1, 2... ou vazio para menu direto"
    )
    proximo = models.CharField(max_length=100, help_text="Ex: outro ID de menu, ou acao:nome_da_acao")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id_menu} | {self.opcao_usuario or '[entrada]'} → {self.proximo}"
    

class FonteDeDados(models.Model):
    nome = models.CharField(max_length=100)
    url_base = models.URLField()
    tipo_autenticacao = models.CharField(max_length=20, choices=[
        ('token', 'Token'), ('basic', 'Basic Auth'), ('nenhuma', 'Nenhuma')
    ], default='nenhuma')
    token = models.CharField(max_length=200, blank=True, null=True)
    usuario = models.CharField(max_length=100, blank=True, null=True)
    senha = models.CharField(max_length=100, blank=True, null=True)
    headers_extras = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.nome


class RequisicaoAPI(models.Model):
    fonte = models.ForeignKey(FonteDeDados, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    metodo = models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST')])
    endpoint = models.CharField(max_length=200)  # Ex: /agendamento/{{id}}
    parametros = models.JSONField(default=dict, blank=True)  # Ex: {"id": "{{texto}}"}

    retorno_exemplo = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.fonte.nome} - {self.nome}"


class VariavelDisponivel(models.Model):
    requisicao = models.ForeignKey(RequisicaoAPI, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)  # Ex: age_id
    caminho = models.CharField(max_length=200)  # Ex: retorno.conteudo.age_id
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome



class RegraAutomatica(models.Model):
    # ... já existentes
    texto_usuario = models.CharField(max_length=255)
    tipo_comparacao = models.CharField(max_length=20, choices=[('igual', 'Igual'), ('contém', 'Contém')])
    contexto = models.CharField(max_length=100, blank=True, null=True)
    novo_contexto = models.CharField(max_length=100, blank=True, null=True)
    resposta_padrao = models.TextField(blank=True, null=True)
    ordem = models.IntegerField(default=1)
    requisicao = models.ForeignKey(RequisicaoAPI, on_delete=models.SET_NULL, null=True, blank=True)

    acao = models.ForeignKey('AcaoAutomatizada', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.texto_usuario} ({self.contexto or 'sem contexto'})"





class RespostaAutomatica(models.Model):
    palavra_chave = models.CharField(max_length=100)
    pergunta_sequencial = models.CharField(max_length=200, blank=True, null=True)
    resposta = models.TextField(help_text="Use {{variavel}} para montar a resposta.")
    variaveis_disponiveis = models.TextField(blank=True)
    id_exemplo = models.CharField(max_length=20, blank=True, help_text="Ex: 84427, usado para consultar exemplo real")
    ativo = models.BooleanField(default=True)

   
    
    
class AcaoAutomatizada(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    endpoint_api = models.URLField(blank=True, null=True)
    metodo = models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST')], default='GET')
    payload_padrao = models.TextField(blank=True, null=True)  # JSON para POST se necessário

    def __str__(self):
        return self.nome   

# core/models.py


class InscricaoNotificacao(models.Model):
    numero = models.CharField(max_length=50)  # Número do WhatsApp com @c.us
    agendamento_id = models.CharField(max_length=50)
    status_atual = models.CharField(max_length=100, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_inscricao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.numero} - {self.agendamento_id}"

    class Meta:
        verbose_name = "Inscrição de Notificação"
        verbose_name_plural = "Inscrições de Notificação"
    
from django.utils import timezone

class ChegadaMotorista(models.Model):
    numero = models.CharField(max_length=30,null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,null=True, blank=True)
    confirmado_em = models.DateTimeField(default=timezone.now)
    ordem_carregamento = models.CharField(max_length=30) 
    status_ordem = models.CharField(max_length=100, blank=True, null=True)
    status_ordem_atual = models.CharField(max_length=100, blank=True, null=True) 
    motorista = models.CharField(max_length=100, blank=True, null=True)  
    parceiro = models.CharField(max_length=100, blank=True, null=True)
    tipo =  models.CharField(max_length=100, blank=True, null=True)
    transportadora = models.CharField(max_length=100, blank=True, null=True)  
    periodo = models.CharField(max_length=100, blank=True, null=True)  
    chegou = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.ordem_carregamento} - {self.confirmado_em.strftime('%d/%m/%Y %H:%M')}"

