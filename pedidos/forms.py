from django import forms
from .models import Prato, Combo, Mesa, Comanda, Item

class PratoForm(forms.ModelForm):
    class Meta:
        model = Prato
        fields = ['nome', 'ingredientes', 'preco', 'categoria']

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco <= 0:
            # Levanta o erro se o preço for zero ou negativo
            raise forms.ValidationError("O preço do prato deve ser maior que zero.") #
        return preco

class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        fields = ['nome', 'pratos', 'preco']

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero', 'capacidade']

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero is not None and numero <= 0:
            raise forms.ValidationError("O número da mesa deve ser 1 ou maior.")
        return numero
        
    def clean_capacidade(self):
        capacidade = self.cleaned_data.get('capacidade')
        if capacidade is not None and capacidade <= 0:
            raise forms.ValidationError("A capacidade da mesa deve ser de pelo menos 1 pessoa.")
        return capacidade

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['prato', 'combo', 'quantidade']