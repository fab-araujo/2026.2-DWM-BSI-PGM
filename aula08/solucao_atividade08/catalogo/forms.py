from django import forms
from django.core.exceptions import ValidationError

from .models import Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            "nome", "slug", "variedade", "descricao", "categoria", "propriedade",
            "unidade", "preco_centavos", "estoque", "destaque", "conservacao",
            "validade",
        ]
        labels = {
            "descricao": "Descrição", "preco_centavos": "Preço (em centavos)",
            "propriedade": "Propriedade", "conservacao": "Conservação",
        }
        widgets = {"validade": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, produtor, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["propriedade"].queryset = produtor.propriedades.all()
        self.fields["propriedade"].empty_label = "(nenhuma)"

    def clean_preco_centavos(self):
        preco = self.cleaned_data["preco_centavos"]
        if preco < 1:
            raise ValidationError("O preço precisa ser maior que zero.")
        return preco

    def clean_estoque(self):
        estoque = self.cleaned_data["estoque"]
        if estoque < 0:
            raise ValidationError("O estoque não pode ser negativo.")
        return estoque
