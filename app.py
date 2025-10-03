#!/usr/bin/env python3
"""
Servidor Flask para servir a aplicação Django em produção
"""

import os
import sys
import subprocess
from flask import Flask, request, Response
import requests
from threading import Thread
import time

app = Flask(__name__)

# Configurações
DJANGO_PORT = 8001
DJANGO_URL = f"http://127.0.0.1:{DJANGO_PORT}"

def start_django():
    """Inicia o servidor Django"""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'controle_financeiro.settings_production'
    
    # Executar setup de produção
    subprocess.run([sys.executable, 'start_production.py'], check=True)
    
    # Iniciar servidor Django
    subprocess.run([
        sys.executable, 'manage.py', 'runserver', 
        f'127.0.0.1:{DJANGO_PORT}', '--noreload'
    ])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy para o servidor Django"""
    try:
        # Construir URL completa
        url = f"{DJANGO_URL}/{path}"
        if request.query_string:
            url += f"?{request.query_string.decode()}"
        
        # Fazer requisição para Django
        if request.method == 'GET':
            resp = requests.get(url, headers=dict(request.headers))
        elif request.method == 'POST':
            resp = requests.post(url, 
                               data=request.form, 
                               files=request.files,
                               headers=dict(request.headers))
        elif request.method == 'PUT':
            resp = requests.put(url, 
                              data=request.get_data(),
                              headers=dict(request.headers))
        elif request.method == 'DELETE':
            resp = requests.delete(url, headers=dict(request.headers))
        else:
            resp = requests.request(request.method, url, 
                                  data=request.get_data(),
                                  headers=dict(request.headers))
        
        # Retornar resposta
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, headers)
        return response
        
    except requests.exceptions.ConnectionError:
        return """
        <html>
        <head><title>Sistema Iniciando</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🚀 Sistema de Controle Financeiro</h1>
            <p>O sistema está iniciando, aguarde alguns segundos...</p>
            <script>setTimeout(() => location.reload(), 3000);</script>
        </body>
        </html>
        """, 503

if __name__ == '__main__':
    # Iniciar Django em thread separada
    django_thread = Thread(target=start_django, daemon=True)
    django_thread.start()
    
    # Aguardar Django inicializar
    time.sleep(5)
    
    # Iniciar Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
