import sys
import subprocess
import paramiko
import requests
import time
import re
import configparser
import threading

# Функция для установки библиотеки
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка paramiko
try:
    import paramiko
except ImportError:
    print("Необходимо установить модуль paramiko...")
    install("paramiko")
    import paramiko

# Проверка и установка requests
try:
    import requests
except ImportError:
    print("Необходимо установить модуль requests...")
    install("requests")
    import requests

# Чтение конфигурации из файла
config = configparser.ConfigParser()
config.read('config.ini')

# Получение значений из конфигурации
HOST = config['SSH']['host']
USERNAME = config['SSH']['username']
PASSWORD = config['SSH']['password']

# Получение имени интерфейса с таймаутом
def get_interface_name():
    print("The interface name can be found in the running-config of your internet-center.")
    print("You have 30 seconds to enter the interface name, otherwise the default Wireguard0 will be used.")

    # Функция для чтения ввода с таймаутом и обратным отсчетом
    def input_with_timeout(prompt, timeout, result):
        for t in range(timeout, 0, -1):
            print(f"\r{prompt} (time left: {t} seconds)", end='', flush=True)
            time.sleep(1)
        print("\r", end='', flush=True)  # Очистка строки с обратным отсчетом
        result.append(input())
        
    # Создаем список для хранения ввода
    user_input = []
    
    # Создаем поток для чтения ввода с таймаутом
    input_thread = threading.Thread(target=input_with_timeout, args=("Enter the interface name / leave empty to use default Wireguard0:", 30, user_input))
    input_thread.start()
    
    # Ждем завершения потока с таймаутом
    input_thread.join(timeout=30)
    
    # Получаем ввод пользователя
    interface = user_input[0] if user_input else ""
    
    # Использование интерфейса по умолчанию, если время истекло или ввод пустой
    if not interface.strip():
        print("Using default interface Wireguard0...")
        return "Wireguard0"
    else:
        return interface.strip()

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
# Загрузка whitelist
download_file('http://ishr00m.ddns.net/zapret/whiteips.txt', 'whiteips.lst')

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


# Чтение файла insta.lst и выполнение команды для каждого IP-адреса
def add_ips_from_file(filename, interface):
    print(f"Adding IPs from file {filename}...")
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            # Пропускаем строки, начинающиеся с #
            if line.startswith("#"):
                continue
            ip_address = line.strip()
            command = f"ip route {ip_address} {interface} auto"
            output = execute_ssh_command(HOST, USERNAME, PASSWORD, command)
            if output:
                print(output, end='')

# Чтение файла insta.lst и добавление IP-адресов
add_ips_from_file('whiteips.lst', INTERFACE)

# Чтение файла mine.lst и community.lst и выполнение команд для каждой строки
add_subnets_from_file('mine.lst', INTERFACE)
add_subnets_from_file('community.lst', INTERFACE)
