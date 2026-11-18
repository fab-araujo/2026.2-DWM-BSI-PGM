from django.urls import path

from . import views, views_painel

app_name = "catalogo"

urlpatterns = [
    path("", views.home, name="home"),
    path("produtos/", views.produtos, name="produtos"),
    path("produtos/<slug:slug>/", views.produto, name="produto"),
    path("catalogo/", views.catalogo_antigo),
    path("produtores/", views.produtores, name="produtores"),
    path("produtores/<slug:slug>/", views.produtor, name="produtor"),
    path("painel/", views_painel.ProdutosDoProdutor.as_view(), name="painel"),
    path("painel/produtos/novo/", views_painel.ProdutoNovo.as_view(), name="painel_produto_novo"),
    path("painel/produtos/<int:pk>/editar/", views_painel.ProdutoEditar.as_view(), name="painel_produto_editar"),
    path("painel/pedidos/", views_painel.PedidosDoProdutor.as_view(), name="painel_pedidos"),
    path("painel/pedidos/<uuid:codigo>/", views_painel.PedidoDoProdutor.as_view(), name="painel_pedido"),
]
