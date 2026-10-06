# 🍽️ Cardápio Digital - Restaurante Vitinho's (P1)

Projeto desenvolvido para a disciplina de Laboratório de Programação Full Stack (Engenharia de Software). Este sistema implementa o back-end e front-end de um Cardápio Digital gerenciador de salão usando o framework Django.

## 🎯 Como o Sistema Funciona no Contexto do Restaurante
O fluxo do código foi desenhado para espelhar as regras de negócio de um ambiente real de restaurante:
1. **Gestão do Salão:** As `Mesas` possuem numeração e capacidade. O sistema controla o status de ocupação booleano (Livre/Ocupada).
2. **Atendimento:** Quando os clientes chegam, o sistema "Abre uma Comanda", vinculando-a àquela `Mesa` específica. A mesa muda automaticamente seu status para "Ocupada".
3. **Pedidos:** Através do painel da comanda, o usuário adiciona `Itens`. Cada Item faz referência a um `Prato` ou `Combo` cadastrado no banco de dados e registra a quantidade pedida daquele produto.
4. **Fechamento de Conta:** A view itera sobre os Itens da Comanda ativa, multiplica o preço pela quantidade, atualiza o valor total, "baixa" a comanda e libera a mesa para o próximo cliente.

## ⚙️️ Explicação da Estrutura do Código (Padrão MTV do Django)
- **Models (`models.py`):** Define o esquema relacional do banco de dados. Utiliza campos como `DecimalField` para valores financeiros e relacionamentos cruciais como `ForeignKey` (ligando as Comandas às Mesas, e os Itens às Comandas/Pratos) e `ManyToManyField` (para agrupar múltiplos pratos em um único Combo).
- **Views (`views.py`):** Contém a lógica de negócio do restaurante. Processa as requisições, faz o cálculo matemático da conta interagindo com o ORM do Django, processa submissões (`request.POST`) e retorna as telas.
- **Forms (`forms.py`):** Utiliza `ModelForm` para gerar formulários dinâmicos e aplicar validações no back-end antes de salvar as interações no banco.
- **Templates (`templates/`):** A interface de usuário (com temática e estilização própria). Utiliza as *template tags* do Django (`{% for %}`, `{% if %}`) para renderizar o salão de mesas, status e o cardápio de forma dinâmica de acordo com o contexto injetado pelas views.

## ✨ Features Obrigatórias (P1) e Justificativas de Decisão

**Feature 1: Busca e Filtro na Listagem**
Optei por implementar a busca por texto no nome do prato e o filtro por categoria (Entrada, Principal, Sobremesa, Bebida). Essa escolha se justifica porque, em um cenário real de Cardápio Digital, o usuário precisa ter agilidade para encontrar um prato específico pelo nome ou explorar as opções disponíveis filtrando apenas o que deseja comer no momento.
*Detalhe técnico:* Utilizei `request.GET.get` na view e o objeto `Q()` do Django para permitir combinar a busca de texto e o filtro de categoria na mesma consulta (Desafio Extra).

**Feature 2: Validação Customizada no Formulário**
Apliquei uma regra de validação no formulário de cadastro de Pratos que impede a inserção de preços menores ou iguais a zero. Isso protege a integridade e a regra de negócio do sistema, evitando que itens com valores negativos ou gratuitos sejam cadastrados e quebrem a lógica financeira do fechamento de contas da comanda.
*Detalhe técnico:* Sobrescrevi o método de limpeza de dados (`clean_preco` e `clean_numero`) no `forms.py` para levantar exceções `forms.ValidationError` em casos de valores negativos no preço do prato ou na numeração e capacidade das mesas.

## 🚀 Como Rodar o Projeto Localmente
1. Clone este repositório.
2. Ative um ambiente virtual.
3. Instale o Django (`pip install django`).
4. Aplique as migrações: `python manage.py makemigrations` e `python manage.py migrate`.
5. Inicie o servidor: `python manage.py runserver`.
6. Acesse `http://127.0.0.1:8000/`.

