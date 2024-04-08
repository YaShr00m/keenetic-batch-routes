import sys
import subprocess
import paramiko
import requests
import time
import re
import configparser

# Функция для установки библиотеки
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка paramiko
install("paramiko")
import paramiko

# Проверка и установка requests
install("requests")
import requests

# Чтение конфигурации из файла
config = configparser.ConfigParser()
config.read('config.ini')

# Получение значений из конфигурации
HOST = config['SSH']['host']
USERNAME = config['SSH']['username']
PASSWORD = config['SSH']['password']

# Получение имени интерфейса
def get_interface_name():
    print("The interface name can be found in the running-config of your internet-center.")
    interface = input("Enter the interface name (default is Wireguard0): ")
    return interface.strip() or "Wireguard0"  # Если введена пустая строка, используем Wireguard0

INTERFACE = get_interface_name()

# Функция для выполнения SSH-команды
def execute_ssh_command(ip, username, password, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(ip, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode().strip()
        return output
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
def add_subnets_from_file(filename, interface):
    print(f"Adding subnets from file {filename}...")
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            # Пропускаем строки, начинающиеся с #
            if line.startswith("#"):
                continue
            network = line.strip()
            command = f"ip route {network} 0.0.0.0 {interface} auto"
            output = execute_ssh_command(HOST, USERNAME, PASSWORD, command)
            if output:
                 print(output, end='')

# Чтение файла mine.lst и community.lst и выполнение команд для каждой строки
add_subnets_from_file('mine.lst', INTERFACE)
add_subnets_from_file('community.lst', INTERFACE)
