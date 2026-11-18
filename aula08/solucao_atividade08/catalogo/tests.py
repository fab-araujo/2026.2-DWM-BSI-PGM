from decimal import Decimal

import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalogo.models import Categoria, JanelaSafra, Produto, Produtor, Propriedade, Unidade
from pedidos.models import ItemPedido, Pedido, PontoRetirada


class CatalogoBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        categoria = Categoria.objects.create(nome="Frutas", slug="frutas")
        unidade = Unidade.objects.create(nome="quilo", sigla="kg", fracionavel=True)
        produtor = Produtor.objects.create(nome="Família Oliveira", slug="familia-oliveira", caf="B1")
        cls.cupuacu = Produto.objects.create(
            nome="Cupuaçu", slug="cupuacu", categoria=categoria, produtor=produtor,
            unidade=unidade, preco_centavos=1200, estoque=Decimal("20"),
        )
        cls.banana = Produto.objects.create(
            nome="Banana", slug="banana", categoria=categoria, produtor=produtor,
            unidade=unidade, preco_centavos=500, estoque=Decimal("30"),
        )


class DisponiveisEmTests(CatalogoBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # a safra do cupuaçu vai de março a agosto
        JanelaSafra.objects.create(
            produto=cls.cupuacu, mes_inicio=3, mes_fim=8, situacao="pico"
        )
        # a banana dá o ano inteiro
        JanelaSafra.objects.create(
            produto=cls.banana, mes_inicio=1, mes_fim=12, situacao="disponivel"
        )

    def test_dentro_da_janela_inclusive_nos_extremos(self):
        for mes in (3, 5, 8):
            with self.subTest(mes=mes):
                self.assertIn(self.cupuacu, Produto.objects.disponiveis_em(mes))

    def test_fora_da_janela(self):
        for mes in (1, 2, 9, 12):
            with self.subTest(mes=mes):
                self.assertNotIn(self.cupuacu, Produto.objects.disponiveis_em(mes))

    def test_janela_do_ano_inteiro_vale_em_qualquer_mes(self):
        for mes in (1, 6, 12):
            with self.subTest(mes=mes):
                self.assertIn(self.banana, Produto.objects.disponiveis_em(mes))

    def test_entressafra_nao_conta_como_disponivel(self):
        JanelaSafra.objects.filter(produto=self.cupuacu).update(situacao="entressafra")
        self.assertNotIn(self.cupuacu, Produto.objects.disponiveis_em(5))


class PaginasTests(CatalogoBase):
    def test_home_responde_200(self):
        resposta = self.client.get(reverse("catalogo:home"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "catalogo/home.html")

    def test_lista_mostra_os_produtos(self):
        resposta = self.client.get(reverse("catalogo:produtos"))
        self.assertContains(resposta, "Cupuaçu")
        self.assertContains(resposta, "Banana")

    def test_busca_filtra_a_lista(self):
        resposta = self.client.get(reverse("catalogo:produtos"), {"q": "cupu"})
        self.assertContains(resposta, "Cupuaçu")
        self.assertNotContains(resposta, "Banana")

    def test_pagina_do_produto(self):
        resposta = self.client.get(reverse("catalogo:produto", args=["cupuacu"]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["produto"], self.cupuacu)

    def test_slug_inexistente_e_404(self):
        resposta = self.client.get(reverse("catalogo:produto", args=["nao-existe"]))
        self.assertEqual(resposta.status_code, 404)

    def test_endereco_antigo_redireciona_para_sempre(self):
        resposta = self.client.get("/catalogo/")
        self.assertRedirects(resposta, reverse("catalogo:produtos"), status_code=301)


class SafraQueAtravessaOAnoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        categoria = Categoria.objects.create(nome="Frutas", slug="frutas")
        unidade = Unidade.objects.create(nome="quilo", sigla="kg", fracionavel=True)
        produtor = Produtor.objects.create(nome="Família Oliveira", slug="familia-oliveira", caf="B1")
        base = dict(categoria=categoria, produtor=produtor, unidade=unidade, preco_centavos=100)
        cls.cupuacu = Produto.objects.create(nome="Cupuaçu", slug="cupuacu", **base)
        cls.natal = Produto.objects.create(nome="Panetone", slug="panetone", **base)
        JanelaSafra.objects.create(produto=cls.cupuacu, mes_inicio=11, mes_fim=2, situacao="pico")
        JanelaSafra.objects.create(produto=cls.natal, mes_inicio=12, mes_fim=12, situacao="pico")

    def test_novembro_a_fevereiro_vale_nos_quatro_meses(self):
        for mes in (11, 12, 1, 2):
            with self.subTest(mes=mes):
                self.assertIn(self.cupuacu, Produto.objects.disponiveis_em(mes))

    def test_novembro_a_fevereiro_nao_vale_no_resto_do_ano(self):
        for mes in (3, 6, 10):
            with self.subTest(mes=mes):
                self.assertNotIn(self.cupuacu, Produto.objects.disponiveis_em(mes))

    def test_janela_de_um_mes_so(self):
        self.assertIn(self.natal, Produto.objects.disponiveis_em(12))
        for mes in (11, 1):
            with self.subTest(mes=mes):
                self.assertNotIn(self.natal, Produto.objects.disponiveis_em(mes))


class PainelBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nome="Frutas", slug="frutas")
        cls.unidade = Unidade.objects.create(nome="quilo", sigla="kg", fracionavel=True)
        cls.ana = User.objects.create_user("ana", password="senha-da-ana-123")
        cls.bia = User.objects.create_user("bia", password="senha-da-bia-123")
        produtor_ana = Produtor.objects.create(
            nome="Sítio da Ana", slug="sitio-da-ana", caf="A1", usuario=cls.ana
        )
        Produtor.objects.create(
            nome="Sítio da Bia", slug="sitio-da-bia", caf="B1", usuario=cls.bia
        )
        cls.banana = Produto.objects.create(
            nome="Banana", slug="banana", categoria=cls.categoria, produtor=produtor_ana,
            unidade=cls.unidade, preco_centavos=500, estoque=Decimal("30"),
        )

    def dados_do_produto(self, **mudancas):
        dados = {
            "nome": "Banana", "slug": "banana", "categoria": self.categoria.pk,
            "unidade": self.unidade.pk, "preco_centavos": 600, "estoque": "30",
        }
        dados.update(mudancas)
        return dados


class EntradaTests(PainelBase):
    def test_login_com_a_senha_certa_e_com_a_errada(self):
        self.assertTrue(self.client.login(username="ana", password="senha-da-ana-123"))
        self.assertIn("_auth_user_id", self.client.session)
        self.client.logout()
        self.assertFalse(self.client.login(username="ana", password="errada"))
        self.assertNotIn("_auth_user_id", self.client.session)


class AutorizacaoTests(PainelBase):
    def test_anonimo_vai_para_a_entrada(self):
        url = reverse("catalogo:painel_produto_editar", args=[self.banana.pk])
        resposta = self.client.get(url)
        self.assertRedirects(resposta, f"{reverse('contas:entrar')}?next={url}")

    def test_outro_produtor_recebe_403_e_nada_muda(self):
        self.client.force_login(self.bia)
        url = reverse("catalogo:painel_produto_editar", args=[self.banana.pk])
        self.assertEqual(self.client.get(url).status_code, 403)
        resposta = self.client.post(url, self.dados_do_produto(preco_centavos=1))
        self.assertEqual(resposta.status_code, 403)
        self.banana.refresh_from_db()
        self.assertEqual(self.banana.preco_centavos, 500)

    def test_dono_edita_e_a_alteracao_fica_gravada(self):
        self.client.force_login(self.ana)
        url = reverse("catalogo:painel_produto_editar", args=[self.banana.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        resposta = self.client.post(url, self.dados_do_produto(preco_centavos=650))
        self.assertRedirects(resposta, reverse("catalogo:painel"))
        self.banana.refresh_from_db()
        self.assertEqual(self.banana.preco_centavos, 650)


class PedidosBase(PainelBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        produtor_ana = Produtor.objects.get(slug="sitio-da-ana")
        produtor_bia = Produtor.objects.get(slug="sitio-da-bia")
        cls.mamao = Produto.objects.create(
            nome="Mamão", slug="mamao", categoria=cls.categoria, produtor=produtor_ana,
            unidade=cls.unidade, preco_centavos=400, estoque=Decimal("30"),
        )
        cls.cupuacu = Produto.objects.create(
            nome="Cupuaçu", slug="cupuacu", categoria=cls.categoria, produtor=produtor_bia,
            unidade=cls.unidade, preco_centavos=1200, estoque=Decimal("20"),
        )
        ponto = PontoRetirada.objects.create(nome="Praça", endereco="Centro", horario="sáb 7h")
        # pedido misto: banana e mamão são da Ana (dois itens dela), o cupuaçu é da Bia
        cls.pedido_misto = cls.novo_pedido(
            "Cris", ponto, [(cls.banana, 2), (cls.mamao, 3), (cls.cupuacu, 1)]
        )
        # pedido só da Bia
        cls.pedido_da_bia = cls.novo_pedido("Dani", ponto, [(cls.cupuacu, 2)])

    @classmethod
    def novo_pedido(cls, comprador, ponto, linhas):
        pedido = Pedido.objects.create(comprador=comprador, telefone="9", ponto_retirada=ponto)
        for produto, quantidade in linhas:
            ItemPedido.objects.create(
                pedido=pedido, produto=produto, nome_produto=produto.nome,
                nome_produtor=produto.produtor.nome, nome_unidade="quilo",
                preco_unitario_centavos=produto.preco_centavos, quantidade=Decimal(quantidade),
            )
        return pedido


class PainelPedidosTests(PedidosBase):
    def test_lista_so_tem_os_pedidos_dele(self):
        self.client.force_login(self.ana)
        resposta = self.client.get(reverse("catalogo:painel_pedidos"))
        self.assertContains(resposta, "Cris")
        self.assertNotContains(resposta, "Dani")

    def test_um_pedido_uma_linha_com_a_contagem_dos_itens_dele(self):
        self.client.force_login(self.ana)
        resposta = self.client.get(reverse("catalogo:painel_pedidos"))
        pedidos = list(resposta.context["pedidos"])
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(pedidos[0].meus_itens, 2)

    def test_detalhe_so_mostra_os_itens_dele_e_o_total_dele(self):
        self.client.force_login(self.ana)
        resposta = self.client.get(reverse("catalogo:painel_pedido", args=[self.pedido_misto.codigo]))
        self.assertContains(resposta, "Banana")
        self.assertContains(resposta, "Mamão")
        self.assertNotContains(resposta, "Cupuaçu")
        self.assertEqual(resposta.context["total_centavos"], 2200)

    def test_pedido_alheio_e_pedido_inexistente_dao_404(self):
        self.client.force_login(self.ana)
        for nome, codigo in [("alheio", self.pedido_da_bia.codigo), ("inexistente", uuid.uuid4())]:
            with self.subTest(pedido=nome):
                resposta = self.client.get(reverse("catalogo:painel_pedido", args=[codigo]))
                self.assertEqual(resposta.status_code, 404)

    def test_sem_entrar_vai_para_a_entrada(self):
        rotas = [
            reverse("catalogo:painel_pedidos"),
            reverse("catalogo:painel_pedido", args=[self.pedido_misto.codigo]),
        ]
        for url in rotas:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f"{reverse('contas:entrar')}?next={url}")

    def test_quem_nao_e_produtor_recebe_403(self):
        curioso = User.objects.create_user("curioso", password="senha-do-curioso-123")
        self.client.force_login(curioso)
        rotas = [
            reverse("catalogo:painel_pedidos"),
            reverse("catalogo:painel_pedido", args=[self.pedido_misto.codigo]),
        ]
        for url in rotas:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)


class PainelProdutosAindaTests(PainelBase):
    def test_produto_novo_pertence_ao_usuario_logado_mesmo_se_o_form_forjar(self):
        bia = Produtor.objects.get(slug="sitio-da-bia")
        self.client.force_login(self.ana)
        dados = self.dados_do_produto(nome="Mamão", slug="mamao", produtor=bia.pk)
        resposta = self.client.post(reverse("catalogo:painel_produto_novo"), dados)
        self.assertRedirects(resposta, reverse("catalogo:painel"))
        self.assertEqual(Produto.objects.get(slug="mamao").produtor, Produtor.objects.get(slug="sitio-da-ana"))
        self.assertFalse(bia.produtos.filter(slug="mamao").exists())

    def test_editar_produto_inexistente_da_404_para_o_produtor_e_entrada_para_o_anonimo(self):
        url = reverse("catalogo:painel_produto_editar", args=[99999])
        self.assertRedirects(self.client.get(url), f"{reverse('contas:entrar')}?next={url}")
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_propriedade_de_outro_produtor_e_recusada(self):
        bia = Produtor.objects.get(slug="sitio-da-bia")
        alheia = Propriedade.objects.create(
            produtor=bia, nome="Roça da Bia", comunidade="Uraim", distancia_sede_km=12,
            area_total_ha=Decimal("6.0"), manejo="convencional", fonte_agua="igarapé",
        )
        self.client.force_login(self.ana)
        dados = self.dados_do_produto(nome="Mamão", slug="mamao", propriedade=alheia.pk)
        resposta = self.client.post(reverse("catalogo:painel_produto_novo"), dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Produto.objects.filter(slug="mamao").exists())
