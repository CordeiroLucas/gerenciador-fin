from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from decimal import Decimal
from .models import Produto, Categoria, Venda, Despesa
from .forms import ProdutoForm, CategoriaForm, VendaForm, DespesaForm


@login_required
def home(request):
    """View principal do sistema"""
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    total_produtos = Produto.objects.filter(ativo=True).count()
    total_categorias = Categoria.objects.filter(ativo=True).count()
    total_vendas = Venda.objects.count()
    total_despesas = Despesa.objects.count()
    
    # Estatísticas do mês atual
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    vendas_mes = Venda.objects.filter(data_venda__gte=inicio_mes)
    receita_mes = vendas_mes.aggregate(total=Sum('total'))['total'] or 0
    lucro_mes = vendas_mes.aggregate(total=Sum('lucro_total'))['total'] or 0
    
    despesas_mes = Despesa.objects.filter(data_despesa__gte=inicio_mes)
    despesas_total_mes = despesas_mes.aggregate(total=Sum('valor'))['total'] or 0
    despesas_pagas_mes = despesas_mes.filter(pago=True).aggregate(total=Sum('valor'))['total'] or 0
    despesas_pendentes_mes = despesas_mes.filter(pago=False).aggregate(total=Sum('valor'))['total'] or 0
    
    # Lucro líquido (receita - despesas pagas)
    lucro_liquido_mes = lucro_mes - despesas_pagas_mes
    
    produtos_recentes = Produto.objects.filter(ativo=True).order_by('-criado_em')[:5]
    vendas_recentes = Venda.objects.select_related('produto').order_by('-data_venda')[:5]
    despesas_recentes = Despesa.objects.order_by('-data_despesa')[:5]
    
    context = {
        'total_produtos': total_produtos,
        'total_categorias': total_categorias,
        'total_vendas': total_vendas,
        'total_despesas': total_despesas,
        'receita_mes': receita_mes,
        'lucro_mes': lucro_mes,
        'despesas_total_mes': despesas_total_mes,
        'despesas_pagas_mes': despesas_pagas_mes,
        'despesas_pendentes_mes': despesas_pendentes_mes,
        'lucro_liquido_mes': lucro_liquido_mes,
        'produtos_recentes': produtos_recentes,
        'vendas_recentes': vendas_recentes,
        'despesas_recentes': despesas_recentes,
    }
    return render(request, 'financeiro/home.html', context)


# Views para Produtos
@login_required
def produto_lista(request):
    """Lista todos os produtos com filtros e paginação"""
    produtos = Produto.objects.select_related('categoria').filter(ativo=True)
    
    # Filtro por categoria
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)
    
    # Filtro por busca
    busca = request.GET.get('busca')
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(produtos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categorias para o filtro
    categorias = Categoria.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_selecionada': categoria_id,
        'busca': busca,
    }
    return render(request, 'financeiro/produto_lista.html', context)


@login_required
def produto_detalhe(request, pk):
    """Exibe detalhes de um produto"""
    produto = get_object_or_404(Produto, pk=pk)
    return render(request, 'financeiro/produto_detalhe.html', {'produto': produto})


@login_required
def produto_criar(request):
    """Cria um novo produto"""
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.usuario = request.user
            produto.save()
            messages.success(request, f'Produto "{produto.nome}" criado com sucesso!')
            return redirect('produto_detalhe', pk=produto.pk)
    else:
        form = ProdutoForm()
    
    return render(request, 'financeiro/produto_form.html', {
        'form': form,
        'titulo': 'Criar Produto',
        'botao': 'Criar'
    })


@login_required
def produto_editar(request, pk):
    """Edita um produto existente"""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            produto = form.save()
            messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso!')
            return redirect('produto_detalhe', pk=produto.pk)
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'financeiro/produto_form.html', {
        'form': form,
        'produto': produto,
        'titulo': 'Editar Produto',
        'botao': 'Salvar'
    })


@login_required
def produto_excluir(request, pk):
    """Exclui (desativa) um produto"""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        produto.ativo = False
        produto.save()
        messages.success(request, f'Produto "{produto.nome}" excluído com sucesso!')
        return redirect('produto_lista')
    
    return render(request, 'financeiro/produto_confirmar_exclusao.html', {'produto': produto})


@login_required
def simulador_precificacao(request):
    """Simulador de precificação para produtos"""
    produtos = Produto.objects.filter(ativo=True).select_related('categoria')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)
    
    busca = request.GET.get('busca')
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(produtos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categorias para filtro
    categorias = Categoria.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_selecionada': categoria_id,
        'busca': busca,
    }
    return render(request, 'financeiro/simulador_precificacao.html', context)


@login_required
def simular_preco_ajax(request):
    """API para simular preço via AJAX"""
    if request.method == 'POST':
        try:
            produto_id = request.POST.get('produto_id')
            nova_margem = request.POST.get('nova_margem')
            
            produto = get_object_or_404(Produto, pk=produto_id)
            nova_margem_decimal = Decimal(str(nova_margem))
            
            # Calcular novo preço
            novo_preco = produto.simular_preco(nova_margem_decimal)
            novo_lucro = novo_preco - produto.custo_base
            
            return JsonResponse({
                'success': True,
                'novo_preco': float(novo_preco),
                'novo_lucro': float(novo_lucro),
                'nova_margem': float(nova_margem_decimal),
                'custo_base': float(produto.custo_base)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


# Views para Categorias
@login_required
def categoria_lista(request):
    """Lista todas as categorias"""
    categorias = Categoria.objects.filter(ativo=True).order_by('nome')
    
    # Filtro por busca
    busca = request.GET.get('busca')
    if busca:
        categorias = categorias.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(categorias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'busca': busca,
    }
    return render(request, 'financeiro/categoria_lista.html', context)


@login_required
def categoria_criar(request):
    """Cria uma nova categoria"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" criada com sucesso!')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()
    
    return render(request, 'financeiro/categoria_form.html', {
        'form': form,
        'titulo': 'Criar Categoria',
        'botao': 'Criar'
    })


@login_required
def categoria_editar(request, pk):
    """Edita uma categoria existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'financeiro/categoria_form.html', {
        'form': form,
        'categoria': categoria,
        'titulo': 'Editar Categoria',
        'botao': 'Salvar'
    })


@login_required
def categoria_excluir(request, pk):
    """Exclui (desativa) uma categoria"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    # Verificar se há produtos usando esta categoria
    produtos_vinculados = categoria.produtos.filter(ativo=True).count()
    
    if request.method == 'POST':
        if produtos_vinculados > 0:
            messages.error(request, f'Não é possível excluir a categoria "{categoria.nome}" pois há {produtos_vinculados} produto(s) vinculado(s).')
        else:
            categoria.ativo = False
            categoria.save()
            messages.success(request, f'Categoria "{categoria.nome}" excluída com sucesso!')
        return redirect('categoria_lista')
    
    context = {
        'categoria': categoria,
        'produtos_vinculados': produtos_vinculados,
    }
    return render(request, 'financeiro/categoria_confirmar_exclusao.html', context)



# Views para Vendas
@login_required
def venda_lista(request):
    """Lista todas as vendas com filtros e paginação"""
    vendas = Venda.objects.select_related('produto', 'produto__categoria').order_by('-data_venda')
    
    # Filtro por produto
    produto_id = request.GET.get('produto')
    if produto_id:
        vendas = vendas.filter(produto_id=produto_id)
    
    # Filtro por categoria
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        vendas = vendas.filter(produto__categoria_id=categoria_id)
    
    # Filtro por período
    periodo = request.GET.get('periodo')
    if periodo:
        from datetime import datetime, timedelta
        hoje = datetime.now()
        
        if periodo == 'hoje':
            vendas = vendas.filter(data_venda__date=hoje.date())
        elif periodo == 'semana':
            inicio_semana = hoje - timedelta(days=7)
            vendas = vendas.filter(data_venda__gte=inicio_semana)
        elif periodo == 'mes':
            inicio_mes = hoje.replace(day=1)
            vendas = vendas.filter(data_venda__gte=inicio_mes)
        elif periodo == 'ano':
            inicio_ano = hoje.replace(month=1, day=1)
            vendas = vendas.filter(data_venda__gte=inicio_ano)
    
    # Filtro por busca
    busca = request.GET.get('busca')
    if busca:
        vendas = vendas.filter(
            Q(produto__nome__icontains=busca) | 
            Q(observacoes__icontains=busca)
        )
    
    # Calcular totais
    from django.db.models import Sum
    totais = vendas.aggregate(
        total_vendas=Sum('total'),
        total_lucro=Sum('lucro_total'),
        total_custo=Sum('custo_total')
    )
    
    # Paginação
    paginator = Paginator(vendas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    produtos = Produto.objects.filter(ativo=True).order_by('nome')
    categorias = Categoria.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'produtos': produtos,
        'categorias': categorias,
        'produto_selecionado': produto_id,
        'categoria_selecionada': categoria_id,
        'periodo_selecionado': periodo,
        'busca': busca,
        'totais': totais,
    }
    return render(request, 'financeiro/venda_lista.html', context)


@login_required
def venda_detalhe(request, pk):
    """Exibe detalhes de uma venda"""
    venda = get_object_or_404(Venda, pk=pk)
    return render(request, 'financeiro/venda_detalhe.html', {'venda': venda})


@login_required
def venda_criar(request):
    """Cria uma nova venda"""
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.usuario = request.user
            venda.save()
            messages.success(request, f'Venda #{venda.pk} registrada com sucesso! Total: R$ {venda.total:.2f}')
            return redirect('venda_detalhe', pk=venda.pk)
    else:
        form = VendaForm()
        
        # Se há um produto especificado na URL, pré-selecionar
        produto_id = request.GET.get('produto')
        if produto_id:
            try:
                produto = Produto.objects.get(pk=produto_id, ativo=True)
                form.fields['produto'].initial = produto
                form.fields['valor_unitario'].initial = produto.preco_final
            except Produto.DoesNotExist:
                pass
    
    return render(request, 'financeiro/venda_form.html', {
        'form': form,
        'titulo': 'Registrar Venda',
        'botao': 'Registrar'
    })


@login_required
def venda_editar(request, pk):
    """Edita uma venda existente"""
    venda = get_object_or_404(Venda, pk=pk)
    
    if request.method == 'POST':
        form = VendaForm(request.POST, instance=venda)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.usuario = request.user
            venda.save()
            messages.success(request, f'Venda #{venda.pk} atualizada com sucesso!')
            return redirect('venda_detalhe', pk=venda.pk)
    else:
        form = VendaForm(instance=venda)
    
    return render(request, 'financeiro/venda_form.html', {
        'form': form,
        'venda': venda,
        'titulo': 'Editar Venda',
        'botao': 'Salvar'
    })


@login_required
def venda_excluir(request, pk):
    """Exclui uma venda"""
    venda = get_object_or_404(Venda, pk=pk)
    
    if request.method == 'POST':
        venda.delete()
        messages.success(request, f'Venda #{pk} excluída com sucesso!')
        return redirect('venda_lista')
    
    return render(request, 'financeiro/venda_confirmar_exclusao.html', {'venda': venda})


@login_required
def obter_preco_produto_ajax(request):
    """API para obter preço do produto via AJAX"""
    if request.method == 'GET':
        try:
            produto_id = request.GET.get('produto_id')
            produto = get_object_or_404(Produto, pk=produto_id, ativo=True)
            
            return JsonResponse({
                'success': True,
                'preco_final': float(produto.preco_final),
                'custo_base': float(produto.custo_base),
                'margem_lucro': float(produto.margem_lucro),
                'nome': produto.nome,
                'categoria': produto.categoria.nome
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


# Views para Relatórios
@login_required
def relatorios_receita_lucro(request):
    """Relatórios de receita e lucro com gráficos"""
    from django.db.models import Sum, Count, Avg
    from datetime import datetime, timedelta
    import json
    
    # Período selecionado
    periodo = request.GET.get('periodo', 'mes')
    
    hoje = datetime.now()
    
    if periodo == 'dia':
        inicio = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
        fim = inicio + timedelta(days=1)
        titulo_periodo = 'Hoje'
    elif periodo == 'semana':
        inicio = hoje - timedelta(days=hoje.weekday())
        inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fim = inicio + timedelta(days=7)
        titulo_periodo = 'Esta Semana'
    elif periodo == 'mes':
        inicio = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if inicio.month == 12:
            fim = inicio.replace(year=inicio.year + 1, month=1)
        else:
            fim = inicio.replace(month=inicio.month + 1)
        titulo_periodo = 'Este Mês'
    elif periodo == 'ano':
        inicio = hoje.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        fim = inicio.replace(year=inicio.year + 1)
        titulo_periodo = 'Este Ano'
    else:  # todos
        inicio = None
        fim = None
        titulo_periodo = 'Todos os Períodos'
    
    # Filtrar vendas
    vendas = Venda.objects.select_related('produto', 'produto__categoria')
    if inicio and fim:
        vendas = vendas.filter(data_venda__gte=inicio, data_venda__lt=fim)
    
    # Estatísticas gerais
    stats = vendas.aggregate(
        total_vendas=Count('id'),
        receita_total=Sum('total'),
        custo_total=Sum('custo_total'),
        lucro_total=Sum('lucro_total')
    )
    
    # Garantir que valores não sejam None
    for key, value in stats.items():
        if value is None:
            stats[key] = 0
    
    # Calcular margem média
    if stats['custo_total'] > 0:
        stats['margem_media'] = (stats['lucro_total'] / stats['custo_total']) * 100
    else:
        stats['margem_media'] = 0
    
    # Vendas por categoria
    vendas_categoria = vendas.values('produto__categoria__nome').annotate(
        total=Sum('total'),
        lucro=Sum('lucro_total'),
        quantidade=Count('id')
    ).order_by('-total')
    
    # Produtos mais vendidos
    produtos_top = vendas.values('produto__nome', 'produto__categoria__nome').annotate(
        total=Sum('total'),
        lucro=Sum('lucro_total'),
        quantidade=Sum('quantidade')
    ).order_by('-total')[:10]
    
    # Dados para gráficos (últimos 30 dias)
    ultimos_30_dias = hoje - timedelta(days=30)
    vendas_diarias = []
    
    for i in range(30):
        data = ultimos_30_dias + timedelta(days=i)
        vendas_dia = vendas.filter(
            data_venda__date=data.date()
        ).aggregate(
            receita=Sum('total') or 0,
            lucro=Sum('lucro_total') or 0
        )
        
        vendas_diarias.append({
            'data': data.strftime('%d/%m'),
            'receita': float(vendas_dia['receita'] or 0),
            'lucro': float(vendas_dia['lucro'] or 0)
        })
    
    # Dados para gráfico de pizza (categorias)
    dados_pizza = []
    for categoria in vendas_categoria:
        dados_pizza.append({
            'nome': categoria['produto__categoria__nome'],
            'valor': float(categoria['total'] or 0),
            'lucro': float(categoria['lucro'] or 0)
        })
    
    context = {
        'periodo': periodo,
        'titulo_periodo': titulo_periodo,
        'stats': stats,
        'vendas_categoria': vendas_categoria,
        'produtos_top': produtos_top,
        'vendas_diarias_json': json.dumps(vendas_diarias),
        'dados_pizza_json': json.dumps(dados_pizza),
    }
    
    return render(request, 'financeiro/relatorios_receita_lucro.html', context)


@login_required
def relatorio_detalhado(request):
    """Relatório detalhado com filtros avançados"""
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    
    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    categoria_id = request.GET.get('categoria')
    produto_id = request.GET.get('produto')
    
    # Base query
    vendas = Venda.objects.select_related('produto', 'produto__categoria')
    
    # Aplicar filtros
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            vendas = vendas.filter(data_venda__gte=data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            vendas = vendas.filter(data_venda__lt=data_fim_obj)
        except ValueError:
            pass
    
    if categoria_id:
        vendas = vendas.filter(produto__categoria_id=categoria_id)
    
    if produto_id:
        vendas = vendas.filter(produto_id=produto_id)
    
    # Estatísticas
    stats = vendas.aggregate(
        total_vendas=Count('id'),
        receita_total=Sum('total'),
        custo_total=Sum('custo_total'),
        lucro_total=Sum('lucro_total')
    )
    
    # Garantir que valores não sejam None
    for key, value in stats.items():
        if value is None:
            stats[key] = 0
    
    # Calcular margem média
    if stats['custo_total'] > 0:
        stats['margem_media'] = (stats['lucro_total'] / stats['custo_total']) * 100
    else:
        stats['margem_media'] = 0
    
    # Calcular margem média
    if stats['custo_total'] > 0:
        stats['margem_media'] = (stats['lucro_total'] / stats['custo_total']) * 100
    else:
        stats['margem_media'] = 0
    
    # Análise por produto
    analise_produtos = vendas.values(
        'produto__nome', 
        'produto__categoria__nome',
        'produto__custo_base',
        'produto__margem_lucro'
    ).annotate(
        total_vendido=Sum('quantidade'),
        receita=Sum('total'),
        custo=Sum('custo_total'),
        lucro=Sum('lucro_total'),
        num_vendas=Count('id')
    ).order_by('-receita')
    
    # Análise por categoria
    analise_categorias = vendas.values('produto__categoria__nome').annotate(
        total_vendido=Sum('quantidade'),
        receita=Sum('total'),
        custo=Sum('custo_total'),
        lucro=Sum('lucro_total'),
        num_vendas=Count('id'),
        num_produtos=Count('produto', distinct=True)
    ).order_by('-receita')
    
    # Dados para filtros
    categorias = Categoria.objects.filter(ativo=True).order_by('nome')
    produtos = Produto.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'stats': stats,
        'analise_produtos': analise_produtos,
        'analise_categorias': analise_categorias,
        'categorias': categorias,
        'produtos': produtos,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'categoria_selecionada': categoria_id,
        'produto_selecionado': produto_id,
    }
    
    return render(request, 'financeiro/relatorio_detalhado.html', context)


# Views para Despesas
@login_required
def despesa_lista(request):
    """Lista todas as despesas com filtros e paginação"""
    despesas = Despesa.objects.all().order_by('-data_despesa')
    
    # Filtro por categoria
    categoria = request.GET.get('categoria')
    if categoria:
        despesas = despesas.filter(categoria=categoria)
    
    # Filtro por status de pagamento
    status = request.GET.get('status')
    if status == 'pago':
        despesas = despesas.filter(pago=True)
    elif status == 'pendente':
        despesas = despesas.filter(pago=False)
    elif status == 'vencido':
        from datetime import date
        despesas = despesas.filter(pago=False, data_vencimento__lt=date.today())
    
    # Filtro por período
    periodo = request.GET.get('periodo')
    if periodo:
        from datetime import datetime, timedelta
        hoje = datetime.now()
        
        if periodo == 'hoje':
            despesas = despesas.filter(data_despesa__date=hoje.date())
        elif periodo == 'semana':
            inicio_semana = hoje - timedelta(days=7)
            despesas = despesas.filter(data_despesa__gte=inicio_semana)
        elif periodo == 'mes':
            inicio_mes = hoje.replace(day=1)
            despesas = despesas.filter(data_despesa__gte=inicio_mes)
        elif periodo == 'ano':
            inicio_ano = hoje.replace(month=1, day=1)
            despesas = despesas.filter(data_despesa__gte=inicio_ano)
    
    # Filtro por busca
    busca = request.GET.get('busca')
    if busca:
        despesas = despesas.filter(
            Q(descricao__icontains=busca) | 
            Q(observacoes__icontains=busca)
        )
    
    # Calcular totais
    from django.db.models import Sum, Count
    totais = despesas.aggregate(
        total_despesas=Sum('valor'),
        total_pagas=Sum('valor', filter=Q(pago=True)),
        total_pendentes=Sum('valor', filter=Q(pago=False)),
        count_despesas=Count('id')
    )
    
    # Garantir que valores não sejam None
    for key, value in totais.items():
        if value is None:
            totais[key] = 0
    
    # Paginação
    paginator = Paginator(despesas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    from .models import CategoriasDespesa
    categorias_choices = CategoriasDespesa.choices
    
    context = {
        'page_obj': page_obj,
        'categorias_choices': categorias_choices,
        'categoria_selecionada': categoria,
        'status_selecionado': status,
        'periodo_selecionado': periodo,
        'busca': busca,
        'totais': totais,
    }
    return render(request, 'financeiro/despesa_lista.html', context)


@login_required
def despesa_detalhe(request, pk):
    """Exibe detalhes de uma despesa"""
    despesa = get_object_or_404(Despesa, pk=pk)
    return render(request, 'financeiro/despesa_detalhe.html', {'despesa': despesa})


@login_required
def despesa_criar(request):
    """Cria uma nova despesa"""
    if request.method == 'POST':
        form = DespesaForm(request.POST)
        if form.is_valid():
            despesa = form.save(commit=False)
            despesa.usuario = request.user
            despesa.save()
            messages.success(request, f'Despesa "{despesa.descricao}" registrada com sucesso! Valor: R$ {despesa.valor:.2f}')
            return redirect('despesa_detalhe', pk=despesa.pk)
    else:
        form = DespesaForm()
    
    return render(request, 'financeiro/despesa_form.html', {
        'form': form,
        'titulo': 'Registrar Despesa',
        'botao': 'Registrar'
    })


@login_required
def despesa_editar(request, pk):
    """Edita uma despesa existente"""
    despesa = get_object_or_404(Despesa, pk=pk)
    
    if request.method == 'POST':
        form = DespesaForm(request.POST, instance=despesa)
        if form.is_valid():
            despesa = form.save(commit=False)
            despesa.usuario = request.user
            despesa.save()
            messages.success(request, f'Despesa "{despesa.descricao}" atualizada com sucesso!')
            return redirect('despesa_detalhe', pk=despesa.pk)
    else:
        form = DespesaForm(instance=despesa)
    
    return render(request, 'financeiro/despesa_form.html', {
        'form': form,
        'despesa': despesa,
        'titulo': 'Editar Despesa',
        'botao': 'Salvar'
    })


@login_required
def despesa_excluir(request, pk):
    """Exclui uma despesa"""
    despesa = get_object_or_404(Despesa, pk=pk)
    
    if request.method == 'POST':
        despesa.delete()
        messages.success(request, f'Despesa "{despesa.descricao}" excluída com sucesso!')
        return redirect('despesa_lista')
    
    return render(request, 'financeiro/despesa_confirmar_exclusao.html', {'despesa': despesa})


@login_required
def despesa_marcar_pago(request, pk):
    """Marca uma despesa como paga via AJAX"""
    if request.method == 'POST':
        try:
            despesa = get_object_or_404(Despesa, pk=pk)
            despesa.marcar_como_pago()
            
            return JsonResponse({
                'success': True,
                'message': f'Despesa "{despesa.descricao}" marcada como paga!',
                'data_pagamento': despesa.data_pagamento.strftime('%d/%m/%Y %H:%M') if despesa.data_pagamento else None
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


# Dashboard Financeiro
@login_required
def dashboard_financeiro(request):
    """Dashboard executivo com KPIs e análises financeiras"""
    from django.db.models import Sum, Count, Avg
    from datetime import datetime, timedelta
    import json
    
    hoje = datetime.now()
    
    # Período padrão: últimos 12 meses
    periodo = request.GET.get('periodo', '12_meses')
    
    if periodo == '30_dias':
        inicio_periodo = hoje - timedelta(days=30)
        titulo_periodo = "Últimos 30 dias"
    elif periodo == '90_dias':
        inicio_periodo = hoje - timedelta(days=90)
        titulo_periodo = "Últimos 90 dias"
    elif periodo == '6_meses':
        inicio_periodo = hoje - timedelta(days=180)
        titulo_periodo = "Últimos 6 meses"
    elif periodo == '12_meses':
        inicio_periodo = hoje - timedelta(days=365)
        titulo_periodo = "Últimos 12 meses"
    else:
        inicio_periodo = hoje - timedelta(days=365)
        titulo_periodo = "Últimos 12 meses"
    
    # KPIs Principais
    vendas_periodo = Venda.objects.filter(data_venda__gte=inicio_periodo)
    despesas_periodo = Despesa.objects.filter(data_despesa__gte=inicio_periodo)
    
    kpis = {
        'receita_total': vendas_periodo.aggregate(total=Sum('total'))['total'] or 0,
        'lucro_bruto': vendas_periodo.aggregate(total=Sum('lucro_total'))['total'] or 0,
        'despesas_total': despesas_periodo.aggregate(total=Sum('valor'))['total'] or 0,
        'despesas_pagas': despesas_periodo.filter(pago=True).aggregate(total=Sum('valor'))['total'] or 0,
        'total_vendas': vendas_periodo.count(),
        'ticket_medio': 0,
        'margem_media': 0,
        'lucro_liquido': 0
    }
    
    # Cálculos derivados
    if kpis['total_vendas'] > 0:
        kpis['ticket_medio'] = kpis['receita_total'] / kpis['total_vendas']
    
    if kpis['receita_total'] > 0:
        kpis['margem_media'] = (kpis['lucro_bruto'] / kpis['receita_total']) * 100
    
    kpis['lucro_liquido'] = kpis['lucro_bruto'] - kpis['despesas_pagas']
    
    # Evolução mensal (últimos 12 meses)
    evolucao_mensal = []
    for i in range(12):
        mes_inicio = (hoje.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        mes_fim = (mes_inicio.replace(month=mes_inicio.month % 12 + 1) if mes_inicio.month < 12 
                  else mes_inicio.replace(year=mes_inicio.year + 1, month=1))
        
        vendas_mes = Venda.objects.filter(
            data_venda__gte=mes_inicio,
            data_venda__lt=mes_fim
        )
        despesas_mes = Despesa.objects.filter(
            data_despesa__gte=mes_inicio,
            data_despesa__lt=mes_fim,
            pago=True
        )
        
        receita_mes = vendas_mes.aggregate(total=Sum('total'))['total'] or 0
        lucro_bruto_mes = vendas_mes.aggregate(total=Sum('lucro_total'))['total'] or 0
        despesas_mes_total = despesas_mes.aggregate(total=Sum('valor'))['total'] or 0
        lucro_liquido_mes = lucro_bruto_mes - despesas_mes_total
        
        evolucao_mensal.insert(0, {
            'mes': mes_inicio.strftime('%b/%Y'),
            'receita': float(receita_mes),
            'lucro_bruto': float(lucro_bruto_mes),
            'despesas': float(despesas_mes_total),
            'lucro_liquido': float(lucro_liquido_mes)
        })
    
    # Top produtos por receita
    top_produtos = vendas_periodo.values(
        'produto__nome',
        'produto__categoria__nome'
    ).annotate(
        receita=Sum('total'),
        quantidade=Sum('quantidade'),
        lucro=Sum('lucro_total')
    ).order_by('-receita')[:10]
    
    # Despesas por categoria
    despesas_categoria = despesas_periodo.values(
        'categoria'
    ).annotate(
        total=Sum('valor'),
        count=Count('id')
    ).order_by('-total')
    
    # Converter para formato amigável
    despesas_categoria_formatada = []
    for item in despesas_categoria:
        categoria_display = dict(Despesa._meta.get_field('categoria').choices).get(
            item['categoria'], item['categoria']
        )
        despesas_categoria_formatada.append({
            'categoria': categoria_display,
            'total': float(item['total']),
            'count': item['count']
        })
    
    # Fluxo de caixa diário (últimos 30 dias)
    fluxo_caixa = []
    for i in range(30):
        data = hoje.date() - timedelta(days=29-i)
        
        receita_dia = Venda.objects.filter(
            data_venda__date=data
        ).aggregate(total=Sum('total'))['total'] or 0
        
        despesas_dia = Despesa.objects.filter(
            data_despesa__date=data,
            pago=True
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        fluxo_caixa.append({
            'data': data.strftime('%d/%m'),
            'receita': float(receita_dia),
            'despesas': float(despesas_dia),
            'saldo': float(receita_dia - despesas_dia)
        })
    
    # Análise de tendências
    # Comparar com período anterior
    inicio_anterior = inicio_periodo - (hoje - inicio_periodo)
    vendas_anterior = Venda.objects.filter(
        data_venda__gte=inicio_anterior,
        data_venda__lt=inicio_periodo
    )
    despesas_anterior = Despesa.objects.filter(
        data_despesa__gte=inicio_anterior,
        data_despesa__lt=inicio_periodo,
        pago=True
    )
    
    receita_anterior = vendas_anterior.aggregate(total=Sum('total'))['total'] or 0
    despesas_anterior_total = despesas_anterior.aggregate(total=Sum('valor'))['total'] or 0
    
    tendencias = {
        'receita_crescimento': 0,
        'despesas_crescimento': 0,
        'lucro_crescimento': 0
    }
    
    if receita_anterior > 0:
        tendencias['receita_crescimento'] = ((kpis['receita_total'] - receita_anterior) / receita_anterior) * 100
    
    if despesas_anterior_total > 0:
        tendencias['despesas_crescimento'] = ((kpis['despesas_pagas'] - despesas_anterior_total) / despesas_anterior_total) * 100
    
    lucro_anterior = (vendas_anterior.aggregate(total=Sum('lucro_total'))['total'] or 0) - despesas_anterior_total
    if lucro_anterior != 0:
        tendencias['lucro_crescimento'] = ((kpis['lucro_liquido'] - lucro_anterior) / abs(lucro_anterior)) * 100
    
    # Metas e alertas
    alertas = []
    
    # Alerta de despesas vencidas
    despesas_vencidas = Despesa.objects.filter(
        pago=False,
        data_vencimento__lt=hoje.date()
    ).count()
    
    if despesas_vencidas > 0:
        alertas.append({
            'tipo': 'danger',
            'titulo': 'Despesas Vencidas',
            'mensagem': f'{despesas_vencidas} despesa(s) vencida(s) precisam de atenção',
            'link': '/despesas/?status=vencido'
        })
    
    # Alerta de margem baixa
    if kpis['margem_media'] < 20 and kpis['receita_total'] > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'Margem Baixa',
            'mensagem': f'Margem média de {kpis["margem_media"]:.1f}% está abaixo do recomendado (20%)',
            'link': '/relatorios/detalhado/'
        })
    
    # Alerta de crescimento negativo
    if tendencias['receita_crescimento'] < -10:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'Queda na Receita',
            'mensagem': f'Receita caiu {abs(tendencias["receita_crescimento"]):.1f}% em relação ao período anterior',
            'link': '/relatorios/'
        })
    
    context = {
        'periodo': periodo,
        'titulo_periodo': titulo_periodo,
        'kpis': kpis,
        'evolucao_mensal': json.dumps(evolucao_mensal),
        'top_produtos': top_produtos,
        'despesas_categoria': despesas_categoria_formatada,
        'fluxo_caixa': json.dumps(fluxo_caixa),
        'tendencias': tendencias,
        'alertas': alertas,
        'despesas_categoria_json': json.dumps(despesas_categoria_formatada)
    }
    
    return render(request, 'financeiro/dashboard_financeiro.html', context)
