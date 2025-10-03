from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Categoria(models.Model):
    """Modelo para categorizar produtos/serviços"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """Modelo para produtos/serviços"""
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    custo_base = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Custo base do produto/serviço"
    )
    margem_lucro = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('30.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Margem de lucro em percentual (ex: 30.00 para 30%)"
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT,
        related_name='produtos'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='produtos',
        default=1,
        help_text="Usuário que criou o produto"
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - R$ {self.preco_final}"

    @property
    def preco_final(self):
        """Calcula o preço final com base no custo base e margem de lucro"""
        if self.custo_base and self.margem_lucro is not None:
            margem_decimal = self.margem_lucro / 100
            return self.custo_base * (1 + margem_decimal)
        return self.custo_base

    @property
    def valor_lucro(self):
        """Calcula o valor absoluto do lucro"""
        return self.preco_final - self.custo_base

    @property
    def margem_lucro_formatada(self):
        """Retorna a margem de lucro formatada como percentual"""
        return f"{self.margem_lucro}%"

    def simular_preco(self, nova_margem):
        """Simula o preço com uma nova margem de lucro"""
        margem_decimal = Decimal(str(nova_margem)) / 100
        return self.custo_base * (1 + margem_decimal)

    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError
        
        if self.custo_base < 0:
            raise ValidationError({'custo_base': 'O custo base deve ser maior ou igual a zero.'})
        
        if self.margem_lucro is not None and self.margem_lucro < 0:
            raise ValidationError({'margem_lucro': 'A margem de lucro deve ser maior ou igual a zero.'})



class Venda(models.Model):
    """Modelo para registrar vendas de produtos/serviços"""
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='vendas'
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantidade vendida"
    )
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Valor unitário no momento da venda"
    )
    data_venda = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora da venda"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vendas',
        default=1,
        help_text="Usuário que registrou a venda"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações sobre a venda"
    )
    
    # Campos calculados automaticamente
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Valor total da venda (quantidade × valor unitário)"
    )
    custo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Custo total dos produtos vendidos"
    )
    lucro_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Lucro total da venda"
    )
    
    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda']

    def __str__(self):
        return f"Venda #{self.pk} - {self.produto.nome} - R$ {self.total}"

    def save(self, *args, **kwargs):
        """Calcular valores automaticamente antes de salvar"""
        # Calcular total
        self.total = self.quantidade * self.valor_unitario
        
        # Calcular custo total baseado no custo base do produto
        self.custo_total = self.quantidade * self.produto.custo_base
        
        # Calcular lucro total
        self.lucro_total = self.total - self.custo_total
        
        super().save(*args, **kwargs)

    @property
    def margem_realizada(self):
        """Calcula a margem de lucro realizada na venda"""
        if self.custo_total > 0:
            return ((self.lucro_total / self.custo_total) * 100)
        return Decimal('0.00')

    @property
    def margem_realizada_formatada(self):
        """Retorna a margem realizada formatada como percentual"""
        return f"{self.margem_realizada:.2f}%"

    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError
        
        if self.quantidade <= 0:
            raise ValidationError({'quantidade': 'A quantidade deve ser maior que zero.'})
        
        if self.valor_unitario <= 0:
            raise ValidationError({'valor_unitario': 'O valor unitário deve ser maior que zero.'})
        
        # Verificar se o produto está ativo
        if self.produto and not self.produto.ativo:
            raise ValidationError({'produto': 'Não é possível vender um produto inativo.'})



class CategoriasDespesa(models.TextChoices):
    """Categorias predefinidas para despesas"""
    OPERACIONAL = 'operacional', 'Operacional'
    MARKETING = 'marketing', 'Marketing'
    ADMINISTRATIVO = 'administrativo', 'Administrativo'
    TECNOLOGIA = 'tecnologia', 'Tecnologia'
    RECURSOS_HUMANOS = 'recursos_humanos', 'Recursos Humanos'
    FINANCEIRO = 'financeiro', 'Financeiro'
    JURIDICO = 'juridico', 'Jurídico'
    INFRAESTRUTURA = 'infraestrutura', 'Infraestrutura'
    OUTROS = 'outros', 'Outros'


class Despesa(models.Model):
    """Modelo para registrar despesas do negócio"""
    descricao = models.CharField(max_length=200, help_text="Descrição da despesa")
    categoria = models.CharField(
        max_length=50,
        choices=CategoriasDespesa.choices,
        default=CategoriasDespesa.OPERACIONAL,
        help_text="Categoria da despesa"
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Valor da despesa em reais"
    )
    data_despesa = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora da despesa"
    )
    data_vencimento = models.DateField(
        blank=True,
        null=True,
        help_text="Data de vencimento (opcional)"
    )
    pago = models.BooleanField(
        default=False,
        help_text="Indica se a despesa foi paga"
    )
    data_pagamento = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Data e hora do pagamento"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações adicionais sobre a despesa"
    )
    recorrente = models.BooleanField(
        default=False,
        help_text="Indica se é uma despesa recorrente"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='despesas',
        default=1,
        help_text="Usuário que registrou a despesa"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_despesa']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

    @property
    def valor_formatado(self):
        """Retorna o valor formatado em reais"""
        return f"R$ {self.valor:.2f}"

    @property
    def categoria_display(self):
        """Retorna o nome da categoria formatado"""
        return self.get_categoria_display()

    @property
    def status_pagamento(self):
        """Retorna o status do pagamento"""
        if self.pago:
            return "Pago"
        elif self.data_vencimento:
            from datetime import date
            if self.data_vencimento < date.today():
                return "Vencido"
            else:
                return "Pendente"
        else:
            return "Pendente"

    @property
    def status_pagamento_class(self):
        """Retorna a classe CSS baseada no status"""
        status = self.status_pagamento
        if status == "Pago":
            return "success"
        elif status == "Vencido":
            return "danger"
        else:
            return "warning"

    def marcar_como_pago(self):
        """Marca a despesa como paga"""
        from django.utils import timezone
        self.pago = True
        self.data_pagamento = timezone.now()
        self.save()

    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        if self.pago and not self.data_pagamento:
            self.data_pagamento = timezone.now()
        
        if not self.pago and self.data_pagamento:
            raise ValidationError("Não é possível ter data de pagamento sem marcar como pago")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
