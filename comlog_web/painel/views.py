# painel/views.py

from django.shortcuts import render, redirect, get_object_or_404
from core.models import RegraAutomatica
from .forms import RegraAutomaticaForm
from django.shortcuts import render, redirect, get_object_or_404
from core.models import FonteDeDados
from .forms import FonteDeDadosForm
from core.models import RequisicaoAPI
from .forms import RequisicaoAPIForm  # crie esse formulário se ainda não existir


def index(request):
    return render(request, 'painel/index.html')

# Listar regras automáticas
def regras(request):
    context = {
        'regras': RegraAutomatica.objects.all()
    }
    return render(request, 'painel/regras.html', context)

# Adicionar nova regra
def nova_regra(request):
    if request.method == 'POST':
        form = RegraAutomaticaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('painel:tela_regras')
    else:
        form = RegraAutomaticaForm()

    return render(request, 'painel/nova_regra.html', {'form': form})

# Editar regra existente (opcional, mas recomendado)
def editar_regra(request, pk):
    regra = get_object_or_404(RegraAutomatica, pk=pk)
    if request.method == 'POST':
        form = RegraAutomaticaForm(request.POST, instance=regra)
        if form.is_valid():
            form.save()
            return redirect('painel:tela_regras')
    else:
        form = RegraAutomaticaForm(instance=regra)

    return render(request, 'painel/nova_regra.html', {'form': form})

# Excluir regra existente (opcional)
def excluir_regra(request, pk):
    regra = get_object_or_404(RegraAutomatica, pk=pk)
    regra.delete()
    return redirect('painel:tela_regras')




def fonte_api_list(request):
    fontes = FonteDeDados.objects.all()
    return render(request, 'painel/fonte_list.html',{'fontes': fontes})



def fonte_api_form(request):
    if request.method == 'POST':
        form = FonteDeDadosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('painel:fonte_api_list')
    else:
        form = FonteDeDadosForm()
    return render(request, 'painel/fonte_form.html', {'form': form})

def editar_fonte_api(request, pk):
    fonte = get_object_or_404(FonteDeDados, pk=pk)

    if request.method == 'POST':
        form = FonteDeDadosForm(request.POST, instance=fonte)
        if form.is_valid():
            form.save()
            return redirect('painel:fonte_api_list')
    else:
        form = FonteDeDadosForm(instance=fonte)

    return render(request, 'painel/fonte_form.html', {'form': form, 'fonte': fonte})


# Excluir regra existente (opcional)
def excluir_fonte_api(request, pk):
    fonte = get_object_or_404(FonteDeDados, pk=pk)
    fonte.delete()
    return redirect('painel:fonte_api_list')



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


