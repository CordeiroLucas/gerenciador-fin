from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # URLs para Produtos
    path('produtos/', views.produto_lista, name='produto_lista'),
    path('produtos/<int:pk>/', views.produto_detalhe, name='produto_detalhe'),
    path('produtos/criar/', views.produto_criar, name='produto_criar'),
    path('produtos/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('produtos/<int:pk>/excluir/', views.produto_excluir, name='produto_excluir'),
    
    # URLs para Precificação
    path('precificacao/', views.simulador_precificacao, name='simulador_precificacao'),
    path('api/simular-preco/', views.simular_preco_ajax, name='simular_preco_ajax'),
    
    # URLs para Vendas
    path('vendas/', views.venda_lista, name='venda_lista'),
    path('vendas/<int:pk>/', views.venda_detalhe, name='venda_detalhe'),
    path('vendas/criar/', views.venda_criar, name='venda_criar'),
    path('vendas/<int:pk>/editar/', views.venda_editar, name='venda_editar'),
    path('vendas/<int:pk>/excluir/', views.venda_excluir, name='venda_excluir'),
    path('api/preco-produto/', views.obter_preco_produto_ajax, name='obter_preco_produto_ajax'),
    
    # URLs para Dashboard
    path('dashboard/', views.dashboard_financeiro, name='dashboard_financeiro'),
    
    # URLs para Relatórios
    path('relatorios/', views.relatorios_receita_lucro, name='relatorios_receita_lucro'),
    path('relatorios/detalhado/', views.relatorio_detalhado, name='relatorio_detalhado'),
    
    # URLs para Despesas
    path('despesas/', views.despesa_lista, name='despesa_lista'),
    path('despesas/<int:pk>/', views.despesa_detalhe, name='despesa_detalhe'),
    path('despesas/criar/', views.despesa_criar, name='despesa_criar'),
    path('despesas/<int:pk>/editar/', views.despesa_editar, name='despesa_editar'),
    path('despesas/<int:pk>/excluir/', views.despesa_excluir, name='despesa_excluir'),
    path('despesas/<int:pk>/marcar-pago/', views.despesa_marcar_pago, name='despesa_marcar_pago'),
    
    # URLs para Categorias
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/criar/', views.categoria_criar, name='categoria_criar'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/excluir/', views.categoria_excluir, name='categoria_excluir'),
]
