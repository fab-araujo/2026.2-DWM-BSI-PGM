# ✅ Solução da Atividade 8 — "O painel que só o dono abre"

> **Esta pasta é a SOLUÇÃO da Atividade 8**, publicada pelo professor **depois do prazo** dela. Serve para duas coisas: conferir o que você fez, e dar um ponto de partida para a **Apostila 9** a quem não terminou a Apostila 8 ou a Atividade 8.
>
> Copiar esta solução agora **não vale nota** na Atividade 8 — o prazo dela já passou. Vale para você seguir o semestre sem ficar para trás.

## O que tem aqui

O projeto inteiro, do jeito que ele fica ao fim da Apostila 8 **mais** a Atividade 8:

| Arquivo | O que é |
|---|---|
| `contas/` | o cadastro, a entrada e a saída (Seção 5 da Apostila 8) |
| `catalogo/models.py`, `catalogo/migrations/0006_produtor_usuario.py` | o campo `Produtor.usuario` |
| `catalogo/management/commands/criar_usuarios_produtores.py` | o comando que cria as oito contas de produtor (só roda com `DEBUG` ligado) |
| `catalogo/forms.py`, `catalogo/views_painel.py` | o formulário de produto e o painel: produtos (apostila) e pedidos (Parte A da atividade) |
| `catalogo/tests.py` | os testes de autorização da apostila e os das Partes B e C |
| `templates/403.html`, `catalogo/templates/catalogo/painel/` | as páginas do painel |
| `agrofeira/settings.py`, `pedidos/`, `static/`, `servidor20/` | o que já vinha das aulas anteriores |

Fica de fora, porque não é código: a tabela de sabotagens (Parte D) e o parágrafo (Parte E). A pasta `padroes/` da Seção 9 da Apostila 8 também não vem aqui: são exemplos soltos de Python, que não fazem parte do projeto.

## Como usar esta solução para começar a Apostila 9

Só faça isto se o **seu** projeto não chegou ao fim da Apostila 8 e da Atividade 8 funcionando. Se chegou, siga direto para a Apostila 9.

1. Abra o codespace do seu repositório `agrofeira-servidor-<seu-usuário>`.
2. No terminal, na **raiz** do seu repositório (o comando `pwd` mostra `/workspaces/agrofeira-servidor-<seu-usuário>`), rode este comando — é uma linha só:

```bash
curl -fsSL https://github.com/fab-araujo/2026.2-DWM-BSI-PGM/archive/refs/heads/main.tar.gz | tar xz --strip-components=3 --exclude=README.md 2026.2-DWM-BSI-PGM-main/aula08/solucao_atividade08
```

   Ele extrai **só o conteúdo desta pasta** na raiz do seu repositório. Arquivos com os mesmos nomes que você já tinha são **substituídos**; arquivos seus com outros nomes ficam.

3. Instale o que o projeto pede e recrie o banco a partir do que veio, um comando de cada vez:

```bash
pip install -r requirements.txt
rm -f db.sqlite3
python manage.py migrate
python manage.py loaddata catalogo pedidos
python manage.py criar_usuarios_produtores
python manage.py createsuperuser
```

4. Confira: rode `python manage.py test` (tem que terminar em `OK`), suba o servidor (`python manage.py runserver 0.0.0.0:8000`) e abra `/produtos/`, `/entrar/` (com `tonico` e a senha da Apostila 8) e `/admin/`.
5. Salve no seu repositório pelo painel **Controle do Código-Fonte** (mensagem, **Confirmação**, **Sincronizar alterações**) e comece a Apostila 9 pela Seção 1.

---

*Os nomes de produtores, sítios e compradores usados nos dados são fictícios; a geografia é real.*
