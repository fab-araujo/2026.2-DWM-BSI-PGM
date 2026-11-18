from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from pedidos.carrinho import subtotal_centavos
from pedidos.models import Pedido

from .forms import ProdutoForm
from .models import Produto


class ProdutorLogado(LoginRequiredMixin):
    """Quem não entrou vai para a página de entrada; quem entrou mas não é produtor leva 403."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not hasattr(request.user, "produtor"):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ProdutosDoProdutor(ProdutorLogado, ListView):
    template_name = "catalogo/painel/produtos.html"
    context_object_name = "produtos"

    def get_queryset(self):
        return Produto.objects.filter(produtor__usuario=self.request.user).select_related(
            "unidade"
        )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["produtor"] = self.request.user.produtor
        contexto["sem_estoque"] = self.object_list.filter(estoque=0).count()
        return contexto


class ProdutoNovo(ProdutorLogado, CreateView):
    form_class = ProdutoForm
    template_name = "catalogo/painel/produto_form.html"
    success_url = reverse_lazy("catalogo:painel")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["produtor"] = self.request.user.produtor
        return kwargs

    def form_valid(self, form):
        form.instance.produtor = self.request.user.produtor
        messages.success(self.request, f"“{form.instance.nome}” foi cadastrado.")
        return super().form_valid(form)


class ProdutoEditar(ProdutorLogado, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "catalogo/painel/produto_form.html"
    success_url = reverse_lazy("catalogo:painel")

    def get_object(self, queryset=None):
        produto = super().get_object(queryset)
        if produto.produtor_id != self.request.user.produtor.id:
            raise PermissionDenied
        return produto

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["produtor"] = self.request.user.produtor
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"“{form.instance.nome}” foi atualizado.")
        return super().form_valid(form)


class PedidosDoProdutor(ProdutorLogado, ListView):
    template_name = "catalogo/painel/pedidos.html"
    context_object_name = "pedidos"

    def get_queryset(self):
        meus = Q(itens__produto__produtor__usuario=self.request.user)
        return (
            Pedido.objects.filter(meus)
            .select_related("ponto_retirada")
            .annotate(meus_itens=Count("itens", filter=meus))
        )


class PedidoDoProdutor(ProdutorLogado, DetailView):
    template_name = "catalogo/painel/pedido.html"
    context_object_name = "pedido"
    slug_field = "codigo"
    slug_url_kwarg = "codigo"

    def get_queryset(self):
        return Pedido.objects.filter(
            itens__produto__produtor__usuario=self.request.user
        ).distinct()

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        meus = self.object.itens.filter(produto__produtor__usuario=self.request.user)
        itens = [
            {"item": item, "subtotal": subtotal_centavos(item.preco_unitario_centavos, item.quantidade)}
            for item in meus
        ]
        contexto["itens"] = itens
        contexto["total_centavos"] = sum(i["subtotal"] for i in itens)
        return contexto
