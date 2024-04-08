import sys
import subprocess
import paramiko
import requests
import time

# Функция для установки библиотеки
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка paramiko
install("paramiko")
import paramiko

# Проверка и установка requests
install("requests")
import requests

# Функция для запроса IP и пароля
def request_credentials():
    ip = input("Enter the IP address: ")
    username = input("Enter the username: ")
    password = input("Enter the password: ")
    return ip, username, password

# Если IP и пароль не указаны, запросить их
HOST = ''
USERNAME = ''
PASSWORD = ''

if not all((HOST, USERNAME, PASSWORD)):
    HOST, USERNAME, PASSWORD = request_credentials()

import re

# Функция для выполнения SSH-команды
def execute_ssh_command(ip, username, password, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(ip, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        for line in stdout:
            cleaned_line = re.sub(r'\x1b\[[0-9;]*[mK]', '', line.strip())
            if cleaned_line:
                print(cleaned_line, end=' ')
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {ip}")
    finally:
        ssh_client.close()

# Функция для загрузки файла из URL и записи в локальный файл
def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

# Загрузка community.lst из URL и запись в локальный файл
download_file('https://community.antifilter.download/list/community.lst', 'community.lst')

# Небольшая задержка перед чтением файла
time.sleep(1)

# Чтение файла mine.lst и выполнение команды для каждой строки
print("Adding subnets from file mine.lst...")
with open('mine.lst', 'r') as file:
    for line in file:
        network = line.strip()
        command = f"ip route {network} 0.0.0.0 Wireguard0 auto"
        execute_ssh_command(HOST, USERNAME, PASSWORD, command)
        print()  # Добавляем пустую строку между выводами для удобства

# Чтение файла community.lst и выполнение команды для каждой строки
print("Adding subnets from file community.lst...")
with open('community.lst', 'r') as file:
    for line in file:
        network = line.strip()
        command = f"ip route {network} 0.0.0.0 Wireguard0 auto"
        execute_ssh_command(HOST, USERNAME, PASSWORD, command)
        print()  # Добавляем пустую строку между выводами для удобства