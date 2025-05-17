# painel/forms.py
from django import forms
from core.models import MenuBot
from core.models import RespostaAutomatica

class MenuBotForm(forms.ModelForm):
    class Meta:
        model = MenuBot
        fields = [
            'id_menu',
            'texto',
            'opcao_usuario',
            'proximo',
            'ativo',
       
        ]
        widgets = {
            'id_menu': forms.TextInput(attrs={'class': 'form-control'}),
            'texto': forms.Textarea(attrs={'rows': 12, 'class': 'form-control'}),
            'opcao_usuario': forms.TextInput(attrs={'class': 'form-control'}),
            'proximo': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
  
        }




class RespostaAutomaticaForm(forms.ModelForm):
    class Meta:
        model = RespostaAutomatica
        fields = ['palavra_chave', 'pergunta_sequencial', 'resposta', 'variaveis_disponiveis', 'id_exemplo', 'ativo']
        widgets = {
            'resposta': forms.Textarea(attrs={'class': 'form-control', 'rows': 12}),
            'palavra_chave': forms.TextInput(attrs={'class': 'form-control'}),
            'pergunta_sequencial': forms.TextInput(attrs={'class': 'form-control'}),
            'variaveis_disponiveis': forms.Textarea(attrs={'class': 'form-control','rows':5}),
            'id_exemplo': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


from core.models import RequisicaoAPI

class RequisicaoAPIForm(forms.ModelForm):
    class Meta:
        model = RequisicaoAPI
        fields = '__all__'

