import requests

def obter_token(config):
    token_payload = {
        "tokenCombinado": config.token_combinado,
        "identificadorEmpresa": config.identificador_empresa,
        "loginUsuario": config.login_usuario,
        "loginUsuarioSenha": config.senha_usuario
    }

    response = requests.post(
        f"{config.url_base}:{config.porta}/sistema/Integracao/strada_rest_v_100/servidor/v100/autenticacao/token/",
        json=token_payload,
        headers={"Content-Type": "application/json"}
    )

    return response.json()["retorno"]["conteudo"]["token"]


def consultar_status_agendamento(config, age_id):
    token = obter_token(config)

    url = f"{config.url_base}:{config.porta}{config.rota_agendamento}{age_id}"

    response = requests.get(url, headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "tokenCombinado": token
    })

    dados_completos = response.json()["retorno"]["conteudo"]["conteudo"]

    # Verifica se a lista está vazia
    if not dados_completos:
        raise Exception("Nenhum dado de agendamento encontrado.")

    # Usa o primeiro item (índice 0), que geralmente já tem os dados principais
    return dados_completos[0]

import requests

def motorista_avisa_que_chegou(config, age_id):
    token = obter_token(config)

    url = "https://maringaferroliga.cargapontual.com:443/sistema/Integracao/strada_rest_v_100/servidor/v100/agendamento/agendamentoprodutodocaitem/statusauxiliar100/"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "tokenCombinado": token
    }

    payload = {
        "agendamentoprodutodocaitemstatus": [
            {
                "condicao": "1",
                "age_id": age_id,
                "statusDestino": 2
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Erro ao atualizar status: {response.status_code} - {response.text}")

    return True

from django.http import JsonResponse
from core.models import IntegracaoCargaPontual
from core.utils import consultar_status_agendamento

def ultimo_status(request):
    numero = request.GET.get("numero")
    if not numero:
        return JsonResponse({"erro": "Número não fornecido"}, status=400)

    try:
        config = IntegracaoCargaPontual.objects.first()
        dados = consultar_status_agendamento(config, numero)
        return JsonResponse({"status": dados.get("status")})
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
    

import requests

def consultar_agendamentos_geral(config, data_agendamento):
    token = obter_token(config)
    
    # Monta a URL conforme o VBA
    filtro = f"dataagendamento='{data_agendamento}'"
    #caminho = "https://maringaferroliga.cargapontual.com.br:443/sistema/Integracao/strada_rest_v_100/servidor/v100/agendamento/agendamentoauxiliar106/"
    caminho = "https://maringaferroliga.cargapontual.com.br:443/sistema/Integracao/strada_rest_v_100/servidor/v100/agendamento/agendamentoauxiliar106/"
    url = f"{caminho}{filtro}"
    

    #https://maringaferroliga.cargapontual.com.br:443/sistema/Integracao/strada_rest_v_100/servidor/v100/agendamento/agendamentoauxiliar106/dataagendamento='2025-04-11'

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "tokenCombinado": token
    }

    response = requests.get(url, headers=headers)
    #response.raise_for_status()  # Garante erro se falhar

    dados = response.json()["retorno"]["conteudo"]["conteudo"]

      # Verifica se a lista está vazia
    if not dados:
        raise Exception("Nenhum dado de agendamento encontrado.")

    # Usa o primeiro item (índice 0), que geralmente já tem os dados principais
    return dados


    