from django.contrib import admin
from .models import Categoria, Produto, Venda, Despesa


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo']
    ordering = ['nome']
    
    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Informações de Data', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'custo_base', 'margem_lucro', 'preco_final_display', 'ativo', 'criado_em']
    list_filter = ['categoria', 'ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo', 'margem_lucro']
    ordering = ['nome']
    
    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'categoria', 'ativo')
        }),
        ('Precificação', {
            'fields': ('custo_base', 'margem_lucro', 'preco_final_display', 'valor_lucro_display'),
            'description': 'Configure os custos e margem de lucro do produto'
        }),
        ('Informações de Data', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['criado_em', 'atualizado_em', 'preco_final_display', 'valor_lucro_display']
    
    def preco_final_display(self, obj):
        """Exibe o preço final formatado"""
        return f"R$ {obj.preco_final:.2f}"
    preco_final_display.short_description = 'Preço Final'
    
    def valor_lucro_display(self, obj):
        """Exibe o valor do lucro formatado"""
        return f"R$ {obj.valor_lucro:.2f}"
    valor_lucro_display.short_description = 'Valor do Lucro'
    
    def get_queryset(self, request):
        """Otimizar consultas incluindo categoria"""
        return super().get_queryset(request).select_related('categoria')



@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'produto', 'quantidade', 'valor_unitario', 'total_display', 'lucro_total_display', 'margem_realizada_display', 'data_venda']
    list_filter = ['data_venda', 'produto__categoria']
    search_fields = ['produto__nome', 'observacoes']
    ordering = ['-data_venda']
    date_hierarchy = 'data_venda'
    
    fieldsets = (
        (None, {
            'fields': ('produto', 'quantidade', 'valor_unitario', 'observacoes')
        }),
        ('Valores Calculados', {
            'fields': ('total_display', 'custo_total_display', 'lucro_total_display', 'margem_realizada_display'),
            'classes': ('collapse',),
            'description': 'Valores calculados automaticamente'
        }),
        ('Informações de Data', {
            'fields': ('data_venda',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['total_display', 'custo_total_display', 'lucro_total_display', 'margem_realizada_display', 'data_venda']
    
    def total_display(self, obj):
        """Exibe o total formatado"""
        return f"R$ {obj.total:.2f}"
    total_display.short_description = 'Total da Venda'
    
    def custo_total_display(self, obj):
        """Exibe o custo total formatado"""
        return f"R$ {obj.custo_total:.2f}"
    custo_total_display.short_description = 'Custo Total'
    
    def lucro_total_display(self, obj):
        """Exibe o lucro total formatado"""
        return f"R$ {obj.lucro_total:.2f}"
    lucro_total_display.short_description = 'Lucro Total'
    
    def margem_realizada_display(self, obj):
        """Exibe a margem realizada formatada"""
        return obj.margem_realizada_formatada
    margem_realizada_display.short_description = 'Margem Realizada'
    
    def get_queryset(self, request):
        """Otimizar consultas incluindo produto e categoria"""
        return super().get_queryset(request).select_related('produto', 'produto__categoria')



@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = [
        'descricao', 
        'categoria_display', 
        'valor_formatado', 
        'status_pagamento', 
        'data_despesa',
        'data_vencimento',
        'pago',
        'recorrente'
    ]
    list_filter = [
        'categoria', 
        'pago', 
        'recorrente', 
        'data_despesa',
        'data_vencimento'
    ]
    search_fields = ['descricao', 'observacoes']
    list_editable = ['pago']
    date_hierarchy = 'data_despesa'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'categoria', 'valor')
        }),
        ('Datas', {
            'fields': ('data_vencimento', 'pago', 'data_pagamento')
        }),
        ('Configurações', {
            'fields': ('recorrente', 'observacoes'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['data_pagamento']
    
    actions = ['marcar_como_pago', 'marcar_como_pendente']
    
    def marcar_como_pago(self, request, queryset):
        """Ação para marcar despesas como pagas"""
        count = 0
        for despesa in queryset:
            if not despesa.pago:
                despesa.marcar_como_pago()
                count += 1
        
        self.message_user(
            request,
            f'{count} despesa(s) marcada(s) como paga(s).'
        )
    marcar_como_pago.short_description = "Marcar como pago"
    
    def marcar_como_pendente(self, request, queryset):
        """Ação para marcar despesas como pendentes"""
        count = queryset.filter(pago=True).update(
            pago=False,
            data_pagamento=None
        )
        
        self.message_user(
            request,
            f'{count} despesa(s) marcada(s) como pendente(s).'
        )
    marcar_como_pendente.short_description = "Marcar como pendente"
    
    def get_queryset(self, request):
        """Otimizar consultas"""
        return super().get_queryset(request).select_related()
