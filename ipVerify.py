import requests
import time

# Função para obter o IP global atual
def get_current_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        return response.json()['ip']
    except requests.RequestException as e:
        print(f"Erro ao obter IP: {e}")
        return None

# Função para ler o IP salvo do arquivo
def read_saved_ip(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# Função para salvar o IP no arquivo
def save_ip(file_path, ip):
    with open(file_path, 'w') as file:
        file.write(ip)

# Caminho do arquivo onde o IP será salvo
file_path = 'ip_address.txt'

while True:
    current_ip = get_current_ip()
    if current_ip:
        saved_ip = read_saved_ip(file_path)
        if current_ip != saved_ip:
            print(f"IP mudou para {current_ip}")
            save_ip(file_path, current_ip)
        else:
            print(f"IP não mudou. Ainda é {current_ip}")
    else:
        print("Não foi possível obter o IP atual.")
    
    time.sleep(1800)  # Aguarda 30 minutos (1800 segundos) antes de verificar novamente

