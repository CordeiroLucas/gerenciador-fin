# Sistema de Controle Financeiro

Sistema web completo para controle financeiro desenvolvido com Django e PostgreSQL.

## Funcionalidades

- ✅ **Etapa 1** - Setup inicial do projeto
- ✅ **Etapa 2** - Cadastro de Produtos/Serviços
- ✅ **Etapa 3** - Precificação
- ✅ **Etapa 4** - Registro de Vendas
- ✅ **Etapa 5** - Relatórios de Receita e Lucro
- ✅ **Etapa 6** - Registro de Despesas
- ✅ **Etapa 7** - Dashboard financeiro
- ✅ **Etapa 8** - Segurança e melhorias

## Tecnologias

- **Backend**: Django 5.2.7
- **Banco de Dados**: PostgreSQL (com fallback para SQLite)
- **Frontend**: Django Templates + Bootstrap (preparado para evolução)

## Instalação

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o arquivo `.env` com suas configurações

4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

5. Crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```

6. Execute o servidor:
   ```bash
   python manage.py runserver
   ```

## Configuração do Banco de Dados

### SQLite (Desenvolvimento)
Por padrão, o projeto está configurado para usar SQLite. Mantenha `USE_SQLITE=True` no arquivo `.env`.

### PostgreSQL (Produção)
Para usar PostgreSQL, configure no arquivo `.env`:
```
USE_SQLITE=False
DB_NAME=controle_financeiro
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

## Acesso ao Admin

- URL: http://localhost:8000/admin/
- Usuário: admin
- Senha: admin123

## Estrutura do Projeto

```
controle_financeiro/
├── controle_financeiro/    # Configurações do projeto
├── financeiro/             # App principal
│   ├── models.py          # Modelos (Categoria, Produto)
│   ├── admin.py           # Configuração do admin
│   └── ...
├── templates/             # Templates HTML
├── static/               # Arquivos estáticos
├── .env                  # Configurações de ambiente
└── requirements.txt      # Dependências
```

## Modelos Implementados

### Categoria
- Nome (único)
- Descrição
- Status ativo/inativo
- Timestamps

### Produto
- Nome
- Descrição
- Custo base (com validação >= 0)
- Categoria (FK)
- Status ativo/inativo
- Timestamps

## Funcionalidades Implementadas

### Etapa 2 - Cadastro de Produtos/Serviços ✅
- CRUD completo para produtos e categorias
- Interface web responsiva com Bootstrap
- Filtros e busca avançada
- Paginação automática
- Validações de formulário
- Sistema de mensagens de feedback

### Etapa 3 - Precificação ✅
- Campo de margem de lucro nos produtos
- Cálculo automático do preço final
- Propriedades calculadas (preço final, valor do lucro)
- Simulador interativo de precificação
- Validações de margem (0-999.99%)
- Interface JavaScript para cálculo em tempo real
- Exibição de preços na listagem e detalhes

### Etapa 4 - Registro de Vendas ✅
- Modelo de Venda com relacionamento aos produtos
- Cálculos automáticos (total, custo, lucro, margem realizada)
- CRUD completo para vendas
- Interface inteligente com preenchimento automático
- Filtros avançados (produto, categoria, período)
- Análise de rentabilidade por venda
- Estatísticas em tempo real no dashboard
- API AJAX para busca de preços

### Etapa 5 - Relatórios de Receita e Lucro ✅
- Relatórios com filtros por período (dia, semana, mês, ano)
- Gráficos interativos com Chart.js (linha e pizza)
- Análise detalhada por produto e categoria
- Estatísticas de receita, lucro e margem média
- Relatório detalhado com filtros avançados
- Comparação de performance vs planejado
- Visualização de participação por categoria
- Evolução diária dos últimos 30 dias

### Etapa 6 - Registro de Despesas ✅
- Modelo de Despesa com 9 categorias predefinidas
- Sistema de status (Pago, Pendente, Vencido)
- Controle de vencimentos e pagamentos
- Despesas recorrentes e observações
- CRUD completo com filtros avançados
- Integração com dashboard (lucro líquido)
- Interface AJAX para marcar como pago
- Admin otimizado com ações em lote

### Etapa 7 - Dashboard Financeiro ✅
- Painel executivo com KPIs principais
- 4 gráficos interativos com Chart.js
- Análise de tendências vs período anterior
- Sistema de alertas inteligentes
- Filtros por período (30d, 90d, 6m, 12m)
- Fluxo de caixa diário (30 dias)
- Top 10 produtos por receita
- Ações rápidas integradas

### Etapa 8 - Segurança e Melhorias ✅
- Sistema de autenticação completo
- Controle de acesso por usuário
- Isolamento de dados por usuário
- Interface de login/registro profissional
- Perfil de usuário com estatísticas
- Configurações de segurança avançadas
- Middleware personalizado
- Proteção CSRF e XSS

## Sistema Completo

O sistema está **100% funcional** e pronto para uso em produção, incluindo:
- ✅ Gestão completa de produtos e categorias
- ✅ Sistema de precificação inteligente
- ✅ Controle de vendas e rentabilidade
- ✅ Gestão de despesas operacionais
- ✅ Relatórios e gráficos avançados
- ✅ Dashboard executivo
- ✅ Autenticação e segurança
