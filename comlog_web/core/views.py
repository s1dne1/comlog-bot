# Importações necessárias para a aplicação Django:
from django.shortcuts import render
from django.http import JsonResponse
import requests  # Utilizado para chamadas externas, por exemplo, para o bot
import json
from django.template import Template, Context
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now

# Importa os modelos utilizados na aplicação:
from .models import RespostaAutomatica, IntegracaoCargaPontual, HistoricoMensagem, MenuBot
from core.models import RegraAutomatica, RespostaAutomatica, VariavelDisponivel

# Importa a função utilitária para consultar status de agendamento
from .utils import consultar_status_agendamento


# =============================================================================
# Funções que renderizam templates HTML
# =============================================================================

def home(request):
    """
    Renderiza a página inicial da aplicação.
    """
    return render(request, 'core/home.html')


import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

@csrf_protect
@require_http_methods(["GET", "POST"])
def envio(request):
    """
    Se GET: renderiza o form.
    Se POST: recebe JSON ou form-data com:
      - numero (string) ou numeros (lista de strings)
      - mensagem (string)
    Envia cada mensagem ao bot Node em http://localhost:3000/enviar
    e retorna um JSON com o status de cada número.
    """
    if request.method == 'POST':
        # 1) Detecta JSON ou form-data
        if request.content_type.startswith('application/json'):
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'JSON inválido'}, status=400)
            numeros = payload.get('numeros') or [payload.get('numero')]
            mensagem = payload.get('mensagem')
        else:
            # form-encoded ou multipart/form-data
            numeros = request.POST.getlist('numeros') or [request.POST.get('numero')]
            mensagem = request.POST.get('mensagem')

        # 2) Valida dados mínimos
        if not mensagem or not numeros or any(n is None for n in numeros):
            return JsonResponse({'error': 'Campos "numero(s)" e "mensagem" são obrigatórios.'}, status=400)

        resultados = []
        for numero in numeros:
            try:
                resp = requests.post(
                    'http://localhost:3000/enviar',
                    json={'numero': numero, 'mensagem': mensagem},
                    timeout=5
                )
                if resp.status_code == 200:
                    resultados.append({'numero': numero, 'status': 'ok'})
                else:
                    resultados.append({
                        'numero': numero,
                        'status': 'erro',
                        'http_code': resp.status_code,
                        'detail': resp.text
                    })
            except Exception as e:
                resultados.append({'numero': numero, 'status': 'exception', 'detail': str(e)})

        return JsonResponse({'resultados': resultados})

    # GET
    return render(request, 'core/envio.html')


# =============================================================================
# Funções para respostas automáticas
# =============================================================================

def resposta_automatica(request):
    """
    Retorna uma resposta automática com base na palavra-chave enviada via parâmetro 'q'.
    Caso não seja informada a palavra-chave ou não exista resposta, retorna mensagem padrão.
    """
    termo = request.GET.get('q', '').strip().lower()

    if not termo:
        return JsonResponse({'erro': 'Parâmetro "q" é obrigatório.'}, status=400)

    resposta = RespostaAutomatica.objects.filter(palavra_chave__iexact=termo).first()

    if resposta:
        contexto = resposta.id_exemplo
        return JsonResponse({'resposta': resposta.resposta,
                             'contexto':contexto})
    else:
        return JsonResponse({'resposta': '🤖 Nenhuma resposta automática encontrada.',
                             'contexto':contexto})


# =============================================================================
# Funções para integração com a Carga Pontual
# =============================================================================

def config_carga_pontual(request):
    """
    Retorna a configuração da integração com a Carga Pontual, 
    incluindo URL base, rota de agendamento e porta.
    """
    try:
        config = IntegracaoCargaPontual.objects.first()
        data = {
            "url_base": config.url_base,
            "rota_agendamento": config.rota_agendamento,
            "porta": config.porta
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def token_carga_pontual(request):
    """
    Realiza a autenticação na API da Carga Pontual para obter um token de acesso.
    """
    try:
        config = IntegracaoCargaPontual.objects.first()

        # URL para obtenção do token
        url = "https://maringaferroliga.cargapontual.com:443/sistema/Integracao/strada_rest_v_100/servidor/v100/autenticacao/token/"
        payload = {
            "tokenCombinado": config.token_combinado,
            "identificadorEmpresa": config.identificador_empresa,
            "loginUsuario": config.login_usuario,
            "loginUsuarioSenha": config.senha_usuario
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            token = data["retorno"]["conteudo"]["token"]
            return JsonResponse({"token": token})
        else:
            return JsonResponse({"erro": "Erro ao obter token", "status": response.status_code}, status=500)

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def resposta_agendamento(request, age_id):
    """
    Consulta o status de um agendamento específico (através do ID) e utiliza
    um template para formatar a resposta automática com base nos dados retornados.
    """
    
    try:
        # Recupera a configuração da integração
        config = IntegracaoCargaPontual.objects.first()
        # Busca o modelo de resposta para agendamento
        modelo = RespostaAutomatica.objects.filter(palavra_chave__iexact='agendamento').first()
        if not modelo:
            return JsonResponse({'erro': 'Modelo de resposta não encontrado'}, status=404)

        # Consulta os dados de status do agendamento (Consumo da API do Carga Pontual)
        if age_id:
            dados = consultar_status_agendamento(config, age_id)

        # 🧠 Aplica substituição de variáveis usando o template do Django
        template = Template(modelo.resposta)
        context = Context(dados)
        resposta_final = template.render(context)
        
        
        

        return JsonResponse({'resposta': resposta_final,
                             'contexto':"notificacao_esperando_confirmacao"})

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


# =============================================================================
# Função para registrar o histórico de mensagens (usada externamente)
# =============================================================================

@csrf_exempt
def registrar_historico(request):
    """
    Registra no banco de dados o histórico de mensagens enviadas e recebidas.
    Aceita apenas requisições POST contendo os dados no corpo em JSON.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        HistoricoMensagem.objects.create(
            numero=data['numero'],
            mensagem_recebida=data['mensagem_recebida'],
            mensagem_enviada=data['mensagem_enviada']
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'erro': 'método inválido'}, status=400)


# =============================================================================
# Outras funções de respostas e menus
# =============================================================================

def resposta_configurada(request):
    """
    Retorna uma resposta configurada com base na palavra-chave informada via parâmetro 'q'.
    Somente retorna respostas ativas.
    """
    chave = request.GET.get('q', '').strip().lower()
    obj = RespostaAutomatica.objects.filter(palavra_chave__iexact=chave, ativo=True).first()
    
    if not obj:
        return JsonResponse({'erro': 'Palavra-chave não encontrada'}, status=404)
    
    return JsonResponse({
        'palavra_chave': obj.palavra_chave,
        'pergunta_sequencial': obj.pergunta_sequencial,
        'resposta': obj.resposta
    })


@csrf_exempt
def agendamento_dados_puros(request, age_id):
    """
    Retorna os dados brutos do status do agendamento (sem template),
    consultando a API da Carga Pontual.
    """
    try:
        config = IntegracaoCargaPontual.objects.first()
        dados = consultar_status_agendamento(config, age_id)
        return JsonResponse(dados)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)


def menu_proximo(request):
    """
    Retorna o próximo menu disponível com base no id_menu e na opção selecionada pelo usuário.
    """
    id_menu = request.GET.get('id_menu')
    opcao = request.GET.get('opcao', '')

    # Busca o item de menu que corresponda ao id_menu, opção e que esteja ativo
    item = MenuBot.objects.filter(
        id_menu=id_menu,
        opcao_usuario=opcao,
        ativo=True
    ).first()

    if item:
            return JsonResponse({'proximo': item.proximo})
    return JsonResponse({'erro': 'Opção não encontrada'}, status=404)


def menu_texto(request):
    """
    Retorna o texto do menu baseado no id_menu informado.
    """
    id_menu = request.GET.get('id_menu')
    item = MenuBot.objects.filter(id_menu=id_menu, ativo=True).first()

    if item:
        return JsonResponse({'texto': item.texto})
    return JsonResponse({'erro': 'Menu não encontrado'}, status=404)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import InscricaoNotificacao

@csrf_exempt
def inscrever_notificacao(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        body = json.loads(request.body)
        numero = body.get('numero')
        agendamento_id = body.get('agendamento_id')

        if numero and agendamento_id:
            insc, criado = InscricaoNotificacao.objects.update_or_create(
                numero=numero,
                agendamento_id=agendamento_id,
                defaults={"ativo": True}
            )
            print(f"✅ Inscrição salva: {numero} | agendamento {agendamento_id} | novo={criado}")
            return JsonResponse({"status": "inscrito com sucesso"})

        return JsonResponse({"erro": "Dados incompletos"}, status=400)

    except Exception as e:
        print(f"❌ Erro ao inscrever: {str(e)}")
        return JsonResponse({"erro": str(e)}, status=500)

# core/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from core.models import ChegadaMotorista  # você pode ajustar o nome
from datetime import datetime


# =============================================================================
# Função para avisar que chegou na planta 
# =============================================================================




from core.utils import motorista_avisa_que_chegou


# @csrf_exempt
# def confirmar_chegada_antiga(request):
#     if request.method != "POST":
#         return JsonResponse({"erro": "Método não permitido."}, status=405)

#     try:
#         data = json.loads(request.body)
#         numero = data.get("numero")
#         lat = data.get("latitude")
#         lng = data.get("longitude")
#         ordem = data.get("ordem_carregamento")
       

#         if not numero or lat is None or lng is None or not ordem:
#             return JsonResponse({"erro": "Campos obrigatórios: numero, latitude, longitude, ordem_carregamento"}, status=400)
        
        




#         # Atualizar status via integração Carga Pontual
#         config = IntegracaoCargaPontual.objects.first()
#         if config:
#             try:

#                 dadosagend = consultar_status_agendamento(config,ordem)

#                 # Registrar no banco
#                 ChegadaMotorista.objects.create(
#                     numero=numero,
#                     latitude=lat,
#                     longitude=lng,
#                     ordem_carregamento=ordem,
#                     # status_ordem_atual= dadosagend.get("status"),
#                     status_ordem_atual= '2 | CHEGOU NA PLANTA',
#                     tipo = dadosagend.get("age_tipooperacao"),
#                     parceiro = dadosagend.get("nomeparceiro"),
#                     transportadora = dadosagend.get("nometransportador"),
#                     periodo = dadosagend.get("periodoinicialfinal"),
#                     motorista = dadosagend.get("nomemotorista")
#                 )



#                 resultado = motorista_avisa_que_chegou(config, ordem)
#             except Exception as e:
#                 return JsonResponse({"erro": f"Erro ao atualizar status na Carga Pontual: {str(e)}"}, status=500)

#         return JsonResponse({"status": "✅ Chegada registrada e status atualizado com sucesso."})

#     except Exception as e:
#         return JsonResponse({"erro": str(e)}, status=500)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import ChegadaMotorista, IntegracaoCargaPontual
from .utils import consultar_status_agendamento, motorista_avisa_que_chegou

@csrf_exempt
def confirmar_chegada(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido. Use POST."}, status=405)

    try:
        data = json.loads(request.body)
        numero = data.get("numero")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        ordem = data.get("ordem_carregamento")

        # Verifica campos obrigatórios
        if not all([numero, latitude is not None, longitude is not None, ordem]):
            return JsonResponse({
                "erro": "Campos obrigatórios: numero, latitude, longitude, ordem_carregamento"
            }, status=400)

        # Verifica se há configuração
        config = IntegracaoCargaPontual.objects.first()
        if not config:
            return JsonResponse({"erro": "Configuração de integração não encontrada."}, status=500)

        # Busca chegada
        chegada = ChegadaMotorista.objects.filter(ordem_carregamento=ordem).first()
        if not chegada:
            return JsonResponse({"erro": f"Registro com número '{ordem}' não encontrado."}, status=404)

        # Atualiza dados da chegada
        chegada.numero = numero
        chegada.latitude = latitude
        chegada.longitude = longitude
        chegada.status_ordem_atual = "2 | CHEGOU NA PLANTA"
        chegada.chegou = True
        chegada.save()

        # Notifica via integração
        resultado = motorista_avisa_que_chegou(config, ordem)

        return JsonResponse({
            "status": "✅ Chegada confirmada e status atualizado.",
            "Numero": numero,
            "status_ordem": chegada.status_ordem_atual,
            "latitude": latitude,
            "longitude": longitude,
            "resultado_integracao": resultado
        })

    except json.JSONDecodeError:
        return JsonResponse({"erro": "JSON inválido."}, status=400)
    except Exception as e:
        return JsonResponse({"erro": f"Erro interno: {str(e)}"}, status=500)




from django.contrib import messages
from django.shortcuts import redirect
from .models import ChegadaMotorista  # ajuste se o nome do model for diferente
from .utils import consultar_agendamentos_geral
from datetime import date


from django.db.models import Q

def sincronizar_chegadas_api(request):
    config = IntegracaoCargaPontual.objects.first()
    data = request.GET.get("data") #or date.today().isoformat()

    try:
        dados_api = consultar_agendamentos_geral(config, data)

        for item in dados_api:
            if not isinstance(item, dict):
                continue

            ordem_carregamento = item.get("age_id")

            # Verifica se já existe
            chegada, created = ChegadaMotorista.objects.update_or_create(
                ordem_carregamento=ordem_carregamento,
                defaults={
                    "periodo": item.get("periodoinicialfinal"),
                    "motorista": item.get("nomemotorista"),
                    "parceiro": item.get("nomeparceiro"),
                    "numero": item.get("numero"),
                    "status_ordem_atual": item.get("status"),
                    "tipo": item.get("age_tipooperacao"),
                    "confirmado_em": data,
                },
            )

            # Só atualiza latitude/longitude se já existe ou se os dados estiverem presentes
            latitude = item.get("latitude")
            longitude = item.get("longitude")

            if latitude is not None and longitude is not None:
                chegada.latitude = latitude
                chegada.longitude = longitude
                chegada.save()

        messages.success(request, "✅ Chegadas atualizadas com sucesso.")
    except Exception as e:
        messages.error(request, f"❌ Erro ao sincronizar dados: {e}")
    
    return redirect("painel:chegadas")





   
# core/views.py
from django.http import JsonResponse
from core.models import IntegracaoCargaPontual, ChegadaMotorista


def ultimo_status(request):
    ordem = request.GET.get("numero")
    if not ordem:
        return JsonResponse({"erro": "Número não fornecido"}, status=400)

    try:
        # Consulta o status atual via API externa
        config = IntegracaoCargaPontual.objects.first()
        dados = consultar_status_agendamento(config, ordem)
        status = dados.get("status")

        if not status:
            return JsonResponse({"erro": "Status não encontrado na resposta"}, status=404)

        # Atualiza o campo status_ordem_atual no último registro do número
        ChegadaMotorista.objects.filter(ordem_carregamento=ordem).update(status_ordem_atual = status)
     

        return JsonResponse({"status": status})
    
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)




# =============================================================================
# Função para processamento de mensagens (usada via API REST)
# =============================================================================
@api_view(['POST'])
def processar_mensagem(request):
    """
    Processa a mensagem recebida, utilizando regras automáticas para determinar
    a resposta apropriada.
    Se a regra envolver uma requisição à API que requeira um número, o sistema
    solicitará que o usuário informe o número caso não o tenha enviado.
    """
    texto = request.data.get("texto", "").lower()
    numero = request.data.get("numero")
    contexto = request.data.get("contexto", "")
    mensagem_anterior = request.data.get("mensagem_anterior", "")

    # Busca todas as regras automáticas aplicáveis para o contexto atual, ordenando por "ordem"
    regras = RegraAutomatica.objects.filter(contexto=contexto).order_by("ordem")

    # Itera sobre cada regra para verificar se alguma se aplica à mensagem do usuário
    for regra in regras:
        compara = regra.texto_usuario.lower()

        # Verifica a comparação: se for "igual" ou se o texto "contém" a palavra-chave
        if (regra.tipo_comparacao == "igual" and texto == compara) or \
           (regra.tipo_comparacao == "contem" and compara in texto):

            # Obtém a resposta automática associada à regra, se existir
            resposta_obj = RespostaAutomatica.objects.filter(regra=regra).first()
            mensagem = resposta_obj.mensagem if resposta_obj else "Mensagem automática."
            variaveis = {}  # Dicionário para armazenar variáveis a serem substituídas

            # Se a regra definir uma requisição externa, faz a chamada à API configurada
            if regra.requisicao:
                try:
                    # Constrói a URL de chamada com base na configuração da fonte
                    url = regra.requisicao.fonte.url_base + regra.requisicao.endpoint

                    # Substitui os parâmetros na URL:
                    # - Se o valor for "{{texto}}", utiliza o texto do usuário;
                    # - Se for "{{numero}}", utiliza o número informado (ou solicita se não houver).
                    for k, v in regra.requisicao.parametros.items():
                        if v == "{{texto}}":
                            valor = texto
                        elif v == "{{numero}}":
                            if numero is None:
                                return Response({
                                    "resposta": "Por favor, informe o número.",
                                    "contexto": contexto
                                })
                            valor = str(numero)
                        else:
                            valor = v
                        url = url.replace(f"{{{{{k}}}}}", valor)

                    # Configura os headers adicionais para a requisição
                    headers = regra.requisicao.fonte.headers_extras or {}
                    if regra.requisicao.fonte.tipo_autenticacao == 'token':
                        headers['Authorization'] = f"Bearer {regra.requisicao.fonte.token}"

                    # Realiza a requisição de acordo com o método definido (GET ou POST)
                    if regra.requisicao.metodo == "GET":
                        api_resp = requests.get(url, headers=headers)
                    else:
                        api_resp = requests.post(url, headers=headers)

                    # Converte a resposta em JSON
                    dados = api_resp.json()

                    # Mapeia as variáveis disponíveis com base na resposta da API
                    variaveis_map = VariavelDisponivel.objects.filter(requisicao=regra.requisicao)
                    for var in variaveis_map:
                        partes = var.caminho.split(".")
                        valor = dados
                        for p in partes:
                            valor = valor.get(p, {})
                        # Se o valor for um dicionário, substitui por string vazia
                        variaveis[var.nome] = valor if not isinstance(valor, dict) else ""

                except Exception as e:
                    # Em caso de erro na requisição, retorna a última mensagem e mantém o contexto
                    return Response({
                        "resposta": f"⚠️ Erro ao consultar API. Retornando à última resposta: {mensagem_anterior}",
                        "contexto": contexto
                    })

            # Realiza a substituição das variáveis na mensagem, se configurado para isso
            if resposta_obj and resposta_obj.usar_variaveis:
                for nome, valor in variaveis.items():
                    mensagem = mensagem.replace(f"{{{{{nome}}}}}", str(valor))

            # Retorna a resposta final e atualiza o contexto, se aplicável
            return Response({
                "resposta": f"[{contexto}] {mensagem}",
                "contexto": regra.novo_contexto or contexto
            })

    # Caso nenhuma regra seja aplicada, retorna uma resposta padrão informando que não foi encontrada resposta
    return Response({
        "resposta": f"[{contexto}] 🤖 Nenhuma resposta automática encontrada.",
        "contexto": contexto
    })


def listar_regras(request):
    """
    Lista todas as regras automáticas cadastradas, retornando informações resumidas sobre cada uma.
    """
    regras = RegraAutomatica.objects.all().order_by('ordem')
    lista = []
    for regra in regras:
        lista.append({
            'id': regra.id,
            'texto_usuario': regra.texto_usuario,
            'tipo_comparacao': regra.tipo_comparacao,
            'contexto': regra.contexto,
            'novo_contexto': regra.novo_contexto,
            'requisicao': regra.requisicao.nome if regra.requisicao else None
        })
    return JsonResponse({'regras': lista})



from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('painel:index')  # redireciona para o painel ou home
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
    



