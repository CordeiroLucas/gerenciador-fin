from django import forms
from .models import Produto, Categoria, Venda, Despesa


class CategoriaForm(forms.ModelForm):
    """Formulário para Categoria"""
    
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da categoria'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da categoria (opcional)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'ativo': 'Ativo'
        }
        help_texts = {
            'nome': 'Nome único para identificar a categoria',
            'descricao': 'Descrição opcional da categoria',
            'ativo': 'Marque para manter a categoria ativa'
        }

    def clean_nome(self):
        """Validação customizada para o nome"""
        nome = self.cleaned_data.get('nome')
        if nome:
            nome = nome.strip().title()
            
            # Verificar se já existe uma categoria com este nome (exceto a atual)
            qs = Categoria.objects.filter(nome__iexact=nome)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise forms.ValidationError('Já existe uma categoria com este nome.')
        
        return nome


class ProdutoForm(forms.ModelForm):
    """Formulário para Produto"""
    
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'custo_base', 'margem_lucro', 'categoria', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do produto/serviço'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do produto/serviço (opcional)'
            }),
            'custo_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'margem_lucro': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '999.99',
                'placeholder': '30.00'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'custo_base': 'Custo Base (R$)',
            'margem_lucro': 'Margem de Lucro (%)',
            'categoria': 'Categoria',
            'ativo': 'Ativo'
        }
        help_texts = {
            'nome': 'Nome do produto ou serviço',
            'descricao': 'Descrição detalhada (opcional)',
            'custo_base': 'Custo base em reais (deve ser >= 0)',
            'margem_lucro': 'Margem de lucro em percentual (ex: 30.00 para 30%)',
            'categoria': 'Selecione a categoria do produto',
            'ativo': 'Marque para manter o produto ativo'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas categorias ativas
        self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True).order_by('nome')
        
        # Adicionar opção vazia se não há categoria selecionada
        if not self.instance.pk:
            self.fields['categoria'].empty_label = "Selecione uma categoria"

    def clean_nome(self):
        """Validação customizada para o nome"""
        nome = self.cleaned_data.get('nome')
        if nome:
            nome = nome.strip().title()
        return nome

    def clean_custo_base(self):
        """Validação customizada para o custo base"""
        custo_base = self.cleaned_data.get('custo_base')
        if custo_base is not None and custo_base < 0:
            raise forms.ValidationError('O custo base deve ser maior ou igual a zero.')
        return custo_base

    def clean_margem_lucro(self):
        """Validação customizada para a margem de lucro"""
        margem_lucro = self.cleaned_data.get('margem_lucro')
        if margem_lucro is not None and margem_lucro < 0:
            raise forms.ValidationError('A margem de lucro deve ser maior ou igual a zero.')
        if margem_lucro is not None and margem_lucro > 999.99:
            raise forms.ValidationError('A margem de lucro não pode ser superior a 999.99%.')
        return margem_lucro

    def clean(self):
        """Validações que envolvem múltiplos campos"""
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        
        # Verificar se a categoria está ativa
        if categoria and not categoria.ativo:
            raise forms.ValidationError({
                'categoria': 'A categoria selecionada não está ativa.'
            })
        
        return cleaned_data


class VendaForm(forms.ModelForm):
    """Formulário para Venda"""
    
    class Meta:
        model = Venda
        fields = ['produto', 'quantidade', 'valor_unitario', 'observacoes']
        widgets = {
            'produto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '1.00'
            }),
            'valor_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a venda (opcional)'
            })
        }
        labels = {
            'produto': 'Produto/Serviço',
            'quantidade': 'Quantidade',
            'valor_unitario': 'Valor Unitário (R$)',
            'observacoes': 'Observações'
        }
        help_texts = {
            'produto': 'Selecione o produto ou serviço vendido',
            'quantidade': 'Quantidade vendida (deve ser > 0)',
            'valor_unitario': 'Valor unitário praticado na venda',
            'observacoes': 'Informações adicionais sobre a venda'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas produtos ativos
        self.fields['produto'].queryset = Produto.objects.filter(ativo=True).select_related('categoria').order_by('nome')
        
        # Adicionar opção vazia
        self.fields['produto'].empty_label = "Selecione um produto"
        
        # Se há um produto selecionado, pré-preencher o valor unitário com o preço final
        if self.instance.pk and self.instance.produto:
            self.fields['valor_unitario'].widget.attrs['data-preco-sugerido'] = str(self.instance.produto.preco_final)

    def clean_quantidade(self):
        """Validação customizada para quantidade"""
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is not None and quantidade <= 0:
            raise forms.ValidationError('A quantidade deve ser maior que zero.')
        return quantidade

    def clean_valor_unitario(self):
        """Validação customizada para valor unitário"""
        valor_unitario = self.cleaned_data.get('valor_unitario')
        if valor_unitario is not None and valor_unitario <= 0:
            raise forms.ValidationError('O valor unitário deve ser maior que zero.')
        return valor_unitario

    def clean(self):
        """Validações que envolvem múltiplos campos"""
        cleaned_data = super().clean()
        produto = cleaned_data.get('produto')
        
        # Verificar se o produto está ativo
        if produto and not produto.ativo:
            raise forms.ValidationError({
                'produto': 'O produto selecionado não está ativo.'
            })
        
        return cleaned_data


class DespesaForm(forms.ModelForm):
    """Formulário para Despesa"""
    
    class Meta:
        model = Despesa
        fields = [
            'descricao', 
            'categoria', 
            'valor', 
            'data_vencimento', 
            'pago',
            'recorrente', 
            'observacoes'
        ]
        
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Aluguel do escritório'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0,00'
            }),
            'data_vencimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'pago': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'recorrente': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais (opcional)'
            })
        }
        
        help_texts = {
            'descricao': 'Descreva brevemente a despesa',
            'categoria': 'Selecione a categoria que melhor se adequa',
            'valor': 'Valor em reais (R$)',
            'data_vencimento': 'Data de vencimento (opcional)',
            'pago': 'Marque se a despesa já foi paga',
            'recorrente': 'Marque se é uma despesa que se repete mensalmente',
            'observacoes': 'Informações adicionais sobre a despesa'
        }
    
    def clean_valor(self):
        """Validação customizada para o valor"""
        valor = self.cleaned_data.get('valor')
        if valor and valor <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return valor
    
    def clean(self):
        """Validações gerais do formulário"""
        cleaned_data = super().clean()
        pago = cleaned_data.get('pago')
        data_vencimento = cleaned_data.get('data_vencimento')
        
        # Se está marcado como pago, não precisa de data de vencimento
        if pago and data_vencimento:
            from datetime import date
            if data_vencimento > date.today():
                raise forms.ValidationError(
                    "Uma despesa não pode estar paga e ter vencimento futuro."
                )
        
        return cleaned_data
