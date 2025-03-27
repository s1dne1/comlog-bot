from django.shortcuts import render
from django.http import JsonResponse
import requests  # opcional para chamadas externas (ex: para o bot)

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def envio(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        mensagem = request.POST.get('mensagem')

        try:
            response = requests.post(
                'http://localhost:3000/enviar',
                json={'numero': numero, 'mensagem': mensagem},
                timeout=5
            )
            if response.status_code == 200:
                return JsonResponse({'status': 'Mensagem enviada com sucesso!'})
            else:
                return JsonResponse({'status': 'Erro ao enviar a mensagem.', 'erro': response.text}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'Erro na conexão com o bot.', 'erro': str(e)}, status=500)

    return render(request, 'core/envio.html')