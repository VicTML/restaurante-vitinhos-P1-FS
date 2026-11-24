# 🍽️ Restaurante Vitinho's — Cardápio Digital & Gestão Mini-SaaS (P1 + P2)

Sistema web full stack desenvolvido em **Django** para a disciplina de **Laboratório de Programação Full Stack** (Engenharia de Software — Universidade de Vassouras).

O projeto nasceu como um MVP de cardápio digital e controle de salão (P1) e evoluiu para uma arquitetura **Mini-SaaS Multi-Organização** (P2), permitindo que diferentes unidades ou restaurantes operem na mesma base de dados com isolamento total, painel gerencial com métricas em tempo real e API REST.

---

## 🎯 Como o Sistema Funciona no Contexto do Restaurante

Cada módulo do código espelha uma operação real do salão e da gerência do restaurante:

1. **Multi-Unidades (`Organizacao` e `Perfil`):** O sistema suporta múltiplas unidades (ex.: *Matriz* e *Filial Centro*). Cada funcionário ou gerente possui um `Perfil` vinculado a uma única `Organizacao`, garantindo que ninguém veja mesas, pratos ou faturamento de outro restaurante.
2. **Cardápio e Combos (`Prato` e `Combo`):** O restaurante gerencia pratos individuais por categoria (*Entrada*, *Prato Principal*, *Sobremesa* e *Bebida*) e monta combos promocionais agrupando vários pratos.
3. **Controle de Salão (`Mesa`):** Cada unidade cadastra suas mesas com numeração única por organização e capacidade de lugares, acompanhando em tempo real se estão **Livres** ou **Ocupadas**.
4. **Fluxo de Atendimento (`Comanda` e `Item`):**
   - Ao receber clientes em uma mesa livre, o atendente abre uma `Comanda`, alterando automaticamente o status da mesa para **Ocupada**.
   - Durante o atendimento, os pedidos entram como `Itens` vinculados à comanda, registrando pratos ou combos e suas quantidades.
   - No fechamento da conta, o back-end soma os valores de todos os itens, grava o `total` consolidado, encerra a comanda (`aberta=False`) e libera a mesa para o próximo atendimento.
5. **Gestão e Tomada de Decisão (`Dashboard` e Relatórios):** O gerente acompanha o movimento da unidade por período filtrado, visualizando total de comandas, contas em aberto, faturamento das comandas fechadas, ranking dos pratos mais pedidos, gráfico mensal de movimento e exportação em CSV.

---

## 🏗️ Arquitetura do Código (Como Cada Arquivo Se Encaixa)

O projeto é dividido em dois apps principais: **`core`** (estrutura transversal do SaaS) e **`pedidos`** (regras de negócio do restaurante).

### 1. App `core/` (Base Multi-Tenant)
- **`core/models.py`**:
  - `Organizacao`: Representa cada unidade/restaurante cliente do sistema.
  - `DaOrganizacao` (`abstract = True`): Classe base abstrata herdada pelos models de negócio (`Prato`, `Combo`, `Mesa`, `Comanda`), injetando automaticamente a `ForeignKey` de organização sem duplicar código.
  - `Perfil`: Estende o `User` nativo do Django via `OneToOneField`, amarrando o usuário logado à sua respectiva `Organizacao`.
- **`core/admin.py`**: Registra `Organizacao` e `Perfil` no Django Admin para cadastro administrativo de unidades e operadores.

### 2. App `pedidos/` (Operação do Restaurante, Dashboard e API)
- **`pedidos/models.py`**: Define o banco relacional (`Prato`, `Combo`, `Mesa`, `Comanda`, `Item`). Utiliza `DecimalField` para precisão financeira, `ManyToManyField` nos combos e `UniqueConstraint(fields=['organizacao', 'numero'])` nas mesas para que duas unidades diferentes possam ter uma "Mesa 1" sem conflito global.
- **`pedidos/forms.py`**:
  - Validações de negócio da P1 (`clean_preco`, `clean_numero`) levantando `forms.ValidationError` contra preços zerados/negativos ou mesas inválidas.
  - `PeriodoForm` e `filtrar_periodo()`: Valida datas recebidas via `GET` (`inicio` e `fim`) antes de filtrar o ORM, impedindo erros 500 caso parâmetros inválidos sejam digitados na URL.
- **`pedidos/dashboard.py`**: Isola as consultas analíticas do ORM:
  - **KPIs (`aggregate` + `Count`/`Sum` com `Q`):** Calcula em uma única consulta total de comandas, abertas, fechadas e faturamento.
  - **Ranking (`values` + `annotate` + `order_by`):** Lista o Top 5 pratos mais pedidos da unidade no período.
  - **Série Temporal (`TruncMonth`):** Agrupa comandas e receitas mês a mês em ordem cronológica para alimentar o gráfico.
  - **Distribuição:** Contabiliza a divisão de pratos por categoria do cardápio.
- **`pedidos/views.py`**:
  - Centraliza o isolamento de dados com `org_atual(request)` e `@login_required`.
  - Protege acessos diretos via URL com `get_object_or_404(..., organizacao=org)` (retornando `404` caso tentem acessar o ID de outra organização).
  - Implementa busca combinada no cardápio usando objetos `Q()` (nome + categoria), gerenciamento de comandas, renderização do dashboard e exportação de relatório em **CSV** respeitando os mesmos filtros de organização e período.
  - Evita o problema de consultas **$N+1$** utilizando `select_related('mesa')` e `select_related('prato', 'comanda')` nos relacionamentos `ForeignKey`.
- **`pedidos/serializers.py`, `pedidos/api_views.py` e `pedidos/api_urls.py`**:
  - Camada de **API REST** construída com **Django REST Framework (DRF)** sob o prefixo `/api/`, utilizando `ModelSerializer` (com validação de preço) e views genéricas (`ListCreateAPIView` e `RetrieveUpdateDestroyAPIView`) separadas das rotas HTML.
- **`pedidos/templates/`**:
  - Interfaces em HTML/CSS com identidade visual temática (vermelho e amarelo claro), utilizando `{% empty %}` para estados vazios e `json_script` + **Chart.js** para renderizar os gráficos do dashboard com segurança.

---

## ✨ Evolução das Entregas (P1 ➔ P2)

| Etapa | Recurso Implementado | Solução Técnica no Django |
| :--- | :--- | :--- |
| **P1** | Busca e Filtro no Cardápio | Filtros combinados via `request.GET` e consultas dinâmicas com `Q()` |
| **P1** | Validação de Integridade | `ModelForm` com métodos `clean_*` bloqueando valores $\le 0$ |
| **P2** | Multi-Organização (Isolamento) | App `core`, herança `DaOrganizacao`, `UniqueConstraint` por org e `get_object_or_404` |
| **P2** | Dashboard & Filtros de Período | `aggregate`, `annotate`, `TruncMonth`, `PeriodoForm`, `Chart.js` e exportação CSV |
| **P2** | Desempenho de Consultas | Uso de `select_related` para eliminar consultas $N+1$ em loops e relatórios |
| **P2** | API REST | Endpoints JSON em `/api/pratos/` com `PratoSerializer` e DRF Generics |

---

## 🧪 Roteiro de Testes de Isolamento e Dashboard

Para validar o funcionamento multi-tenant e as métricas:
1. **Isolamento de Dados:** Criar duas organizações no `/admin/` (*Unidade A* e *Unidade B*) e dois usuários com seus respectivos perfis. Cada usuário visualiza apenas suas mesas, pratos e indicadores no `/dashboard/`.
2. **Proteção de ID na URL:** Tentar abrir `/comanda/<id_da_unidade_b>/` logado na *Unidade A* retorna `404 Not Found`.
3. **Filtro por Período & Resiliência:** Filtrar datas em `/dashboard/?inicio=2026-01-01&fim=2026-12-31` atualiza os cartões, o gráfico e o arquivo gerado em **Exportar CSV**; parâmetros inválidos (ex.: `?inicio=abc`) são tratados pelo `PeriodoForm` sem quebrar a página.
