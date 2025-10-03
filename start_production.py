#!/usr/bin/env python3
"""
Script de inicialização para produção do sistema de controle financeiro
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_production():
    """Configura o ambiente de produção"""
    # Configurar settings de produção
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controle_financeiro.settings_production')
    
    # Configurar Django
    django.setup()
    
    print("🚀 Iniciando sistema de controle financeiro em produção...")
    
    # Executar migrações
    print("📦 Aplicando migrações...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Coletar arquivos estáticos
    print("📁 Coletando arquivos estáticos...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Criar superusuário se não existir
    print("👤 Verificando superusuário...")
    from django.contrib.auth.models import User
    if not User.objects.filter(is_superuser=True).exists():
        print("Criando superusuário padrão...")
        User.objects.create_superuser(
            username='admin',
            email='admin@controle-financeiro.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        print("✅ Superusuário criado: admin/admin123")
    else:
        print("✅ Superusuário já existe")
    
    print("🎉 Sistema configurado e pronto para produção!")
    print("📊 Acesse o sistema em: https://seu-dominio.com")
    print("🔧 Admin em: https://seu-dominio.com/admin/")

if __name__ == '__main__':
    setup_production()
