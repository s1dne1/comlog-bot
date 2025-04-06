# painel/forms.py
from django import forms
from core.models import RegraAutomatica
from core.models import FonteDeDados

class RegraAutomaticaForm(forms.ModelForm):
    class Meta:
        model = RegraAutomatica
        fields = [
            'texto_usuario',
            'tipo_comparacao',
            'contexto',
            'requisicao',
            'novo_contexto',
            'ordem',
        ]
        widgets = {
            'texto_usuario': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_comparacao': forms.Select(attrs={'class': 'form-select'}),
            'contexto': forms.TextInput(attrs={'class': 'form-control'}),
            'requisicao': forms.Select(attrs={'class': 'form-select'}),
            'novo_contexto': forms.TextInput(attrs={'class': 'form-control'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }




class FonteDeDadosForm(forms.ModelForm):
    class Meta:
        model = FonteDeDados
        fields = '__all__'


from core.models import RequisicaoAPI

class RequisicaoAPIForm(forms.ModelForm):
    class Meta:
        model = RequisicaoAPI
        fields = '__all__'

