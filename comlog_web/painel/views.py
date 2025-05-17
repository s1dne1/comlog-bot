# painel/views.py


from core.models import MenuBot
from .forms import MenuBotForm
from .forms import RespostaAutomaticaForm
from django.shortcuts import render, redirect, get_object_or_404
from core.models import RespostaAutomatica

from core.models import RequisicaoAPI
from .forms import RequisicaoAPIForm  # crie esse formulário se ainda não existir
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'painel/index.html')


@login_required
def config(request):
    return render(request, 'painel/config.html')


@login_required
def home(request):
    return render(request, 'painel/home.html')


# Listar menus cadastrados
def listar_menus(request):
    context = {
        'menus': MenuBot.objects.all()
    }
    return render(request, 'painel/menu.html', context)

# Adicionar novo menu
@login_required
def novo_menu(request):
    if request.method == 'POST':
        form = MenuBotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('painel:tela_menu')  # 'tela_menu' deve apontar para listar_menus
    else:
        form = MenuBotForm()

    return render(request, 'painel/novo_menu.html', {'form': form})

# Editar menu existente
@login_required
def editar_menu(request, pk):
    menu = get_object_or_404(MenuBot, pk=pk)
    if request.method == 'POST':
        form = MenuBotForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('painel:tela_menu')
    else:
        form = MenuBotForm(instance=menu)

    return render(request, 'painel/novo_menu.html', {'form': form})

# Excluir menu existente
@login_required
def excluir_menu(request, pk):
    menu = get_object_or_404(MenuBot, pk=pk)
    menu.delete()
    return redirect('painel:tela_menu')




@login_required
def resposta_automatica_list(request):
    context = {'resposta_automatica': RespostaAutomatica.objects.all()
    }
    return render(request, 'painel/resposta_automatica_list.html',context)


@login_required
def resposta_automatica_form(request):
    if request.method == 'POST':
        form = RespostaAutomaticaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('painel:resposta_automatica_list')
    else:
        form = RespostaAutomaticaForm()
    return render(request, 'painel/resposta_automatica_form.html', {'form': form})

@login_required
def editar_resposta_automatica(request, pk):
    resposta_automatica = get_object_or_404(RespostaAutomatica, pk=pk)

    if request.method == 'POST':
        form = RespostaAutomaticaForm(request.POST, instance=resposta_automatica)
        if form.is_valid():
            form.save()
            return redirect('painel:resposta_automatica_list')
    else:
        form = RespostaAutomaticaForm(instance=resposta_automatica)

    return render(request, 'painel/resposta_automatica_form.html', {'form': form, 'resposta_automatica': resposta_automatica})


# Excluir regra existente (opcional)
def excluir_resposta_automatica(request, pk):
    resposta_automatica = get_object_or_404(RespostaAutomatica, pk=pk)
    resposta_automatica.delete()
    return redirect('painel:resposta_automatica_list')


@login_required
def requisicao_list(request):
    requisicoes = RequisicaoAPI.objects.all()
    return render(request, 'painel/requisicao_list.html', {'requisicoes': requisicoes})

def requisicao_form(request):
    if request.method == 'POST':
        form = RequisicaoAPIForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('painel:requisicao_list')
    else:
        form = RequisicaoAPIForm()
    return render(request, 'painel/requisicao_form.html', {'form': form})


def editar_requisicao_api(request, pk):
    requisicao = get_object_or_404(RequisicaoAPI, pk=pk)

    if request.method == 'POST':
        form = RequisicaoAPIForm(request.POST, instance=requisicao)
        if form.is_valid():
            form.save()
            return redirect('painel:requisicao_list')
    else:
        form = RequisicaoAPIForm(instance=requisicao)

    return render(request, 'painel/requisicao_form.html', {'form': form, 'fonte': requisicao})


# Excluir regra existente (opcional)
def excluir_requisicao(request, pk):
    fonte = get_object_or_404(RequisicaoAPI, pk=pk)
    fonte.delete()
    return redirect('painel:requisicao_list')

from core.models import RequisicaoAPI  # ou o nome do seu model correto
from django.shortcuts import get_object_or_404, render

def capturar_variaveis(request, pk):
    requisicao = get_object_or_404(RequisicaoAPI, pk=pk)

    # Aqui você pode extrair ou simular variáveis da requisição, por enquanto usaremos exemplo:
    variaveis = {
        "produto": "Minério de Ferro",
        "status": "Liberado",
        "motorista": "João"
    }

    return render(request, 'painel/variaveis_requisicao.html', {
        'requisicao': requisicao,
        'variaveis': variaveis
    })


from core.models import ChegadaMotorista

from django.db.models import Q
from datetime import datetime,date

@login_required
def chegadas(request):
    nome = request.GET.get("nome")
    numero = request.GET.get("numero")
    parceiro = request.GET.get("parceiro")
    status = request.GET.get("status")
    data = request.GET.get("data") or date.today().isoformat()
    tipo =  request.GET.get("tipo")

    chegadas = ChegadaMotorista.objects.all()

    if nome:
        chegadas = chegadas.filter( motorista__icontains=nome)

    if numero:
        chegadas = chegadas.filter(numero__icontains=numero)

    if parceiro:
        chegadas = chegadas.filter(parceiro__icontains=parceiro)

    if status:
        chegadas = chegadas.filter(status_ordem_atual__icontains=status)

    if tipo:
        chegadas = chegadas.filter(tipo__icontains=tipo)    



    if data:
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d")
            chegadas = chegadas.filter(confirmado_em__date=data_obj.date())
        except:
            pass

    hoje = date.today().isoformat()
    #chegadas = ChegadaMotorista.objects.all()  # ou com filtros   
    #chegadas = chegadas.order_by("-confirmado_em")
    return render(request, 'painel/chegadas.html', {
        'chegadas': chegadas,
        'today_str': hoje,
        # outros filtros se quiser
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from core.utils import consultar_agendamentos_geral  # ajuste o import conforme a estrutura do seu projeto
from core.models import IntegracaoCargaPontual

@login_required
def chegadas_new_nao_usada(request):
    nome = request.GET.get("nome")
    numero = request.GET.get("numero")
    parceiro = request.GET.get("parceiro")
    status = request.GET.get("status")
    data = request.GET.get("data") or date.today().isoformat()
    tipo = request.GET.get("tipo") or "1"  # valor default como no script VBA

    try:
        config = IntegracaoCargaPontual.objects.first()
        dados_api = consultar_agendamentos_geral(config, data)
        if isinstance(dados_api, str):
            import json
            dados_api = json.loads(dados_api)
    except Exception as e:
        dados_api = []
        print(f"Erro ao consultar API: {e}")

    print("Tipo de dados_api:", type(dados_api))
    print("Conteúdo de dados_api:", dados_api)

    # Aplica filtros nos dados retornados da API
    chegadas_filtradas = []

    for item in dados_api:
        if nome and nome.lower() not in (item.get("nomemotorista") or "").lower():
            continue
        if numero and numero not in (item.get("age_id") or ""):
            continue
        if parceiro and parceiro.lower() not in (item.get("nomeparceiro") or "").lower():
            continue
        if status and status.lower() not in (item.get("age_status") or "").lower():
            continue
        #if tipo and str(tipo) != str(item.get("age_tipooperacao")):
         #   continue

        chegadas_filtradas.append(item)

    # Renderiza a página com os dados da API
    return render(request, 'painel/chegadas.html', {
        'chegadas': chegadas_filtradas,
        'filtros': {
            'nome': nome,
            'numero': numero,
            'parceiro': parceiro,
            'status': status,
            'data': data,
            'tipo': tipo
        }
    })

