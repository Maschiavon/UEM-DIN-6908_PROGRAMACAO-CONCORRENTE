import socket
import tqdm
import os
import math
import time
import re
import threading
import PySimpleGUI as sg

def tela():
    sg.ChangeLookAndFeel("DarkGrey10")

    # Layout
    layout = [[sg.Text("Selecione um dos métodos pré-definidos:", font="Roboto")],
              [sg.Radio("Memória Compartilhada - Sem Paralelismo", "group1", key="memCompSemParal", font="Roboto", default=True)],
              [sg.Radio("Memória Compartilhada - Com Paralelismo", "group1", key="memCompComParal", font="Roboto")],
              [sg.Radio("Memória Distribuída - Sem paralelismo", "group1", key="memDistSemParal", font="Roboto")],
              [sg.Radio("Memória Distribuída - Com paralelismo", "group1", key="memDistComParal", font="Roboto")],
              [sg.Radio("Todos em Ordem", "group1", key="Todos", font="Roboto")],
              [sg.Text("\nInsira os IP's dos Servidores:", font="Roboto")],
              [sg.Text("1º IP:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip1"),
               sg.Text("2º IP:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip2"),
               sg.Text("3º IP:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip3")],
              [sg.Button("Executar", font="Roboto"), sg.Button("Get IP", font="Roboto"), sg.Text("Seu IP:", font="Roboto", key="txtMeuIP")],
              [sg.Output(size=(60, 12), key="output", font="Roboto")]]

    # Janela
    janela = sg.Window('Computador Cliente', layout, icon=r'./ic.ico')

    while True:
        # Extrair os dados da tela
        event, values = janela.Read()

        # Get Ip
        if event == "Get IP":
            hostname = socket.gethostbyname(socket.gethostname())
            janela['txtMeuIP'].update("Seu IP: " + str(hostname))
            janela['ip1'].update(hostname)

        # Executar
        elif event == "Executar":
            # Pega as opções
            janela.FindElement("output").Update("")
            op1 = values["memCompSemParal"]
            op2 = values["memCompComParal"]
            op3 = values["memDistSemParal"]
            op4 = values["memDistComParal"]
            op5 = values["Todos"]

            # Pega IP's adicionais
            ip1 = values["ip1"]
            ip2 = values["ip2"]
            ip3 = values["ip3"]
            ip_list = [x for x in [ip1,ip2,ip3] if x != '']

            if op1 | op5:
                memCompSemParal()
            elif op2 | op5:
                memCompComParal()
            elif op3 | op5:
                memDistSemParal(ip_list)
            elif op4 | op5:
                memDistComParal(ip_list)

        # Fechar Janela
        else:
            break

def memCompSemParal():
    print("Memória Compartilhada - Sem Paralelismo")

    count = 1
    directory = 'Problemas Matematicos'
    savepath_resp = 'Respostas'
    # Check whether the specified path exists or not
    isExist = os.path.exists(savepath_resp)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(savepath_resp)

    # itera sobre os arquivos
    # daquele diretorio
    tempo_total = time.time()
    duracao_acumulativa = 0
    for filename in os.listdir(directory):
        start = time.time()
        f = os.path.join(directory, filename)
        # verifica se é arquivo
        if os.path.isfile(f):
            # Abre o arquivo e armazena linha por linha em
            # um vetor de strings sem o \n no final
            print("Arquivo: ",filename)
            with open(f) as arquivo:
                linhas = [linha.rstrip() for linha in arquivo]
            resp_nome = os.path.join(savepath_resp, "r" + str(count) + ".txt")
            r = open(resp_nome, "w")
            for linha in linhas:
                res = eval(linha)
                duration = time.time() - start
                duracao_acumulativa += duration
                r.write(str(duration) + "\n")
                #print("Resposta: ", res)
                print("Duração: ", duration,"\n")
                print("T Acumulado: ", duracao_acumulativa, "\n")
            count += 1
    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)
    return 0

def memCompComParal():
    print("Memória Compartilhada - Com Paralelismo")

    directory = 'Problemas Matematicos'
    # itera sobre os arquivos
    # daquele diretorio
    tempo_total = time.time()
    lista_threads = []
    for filename in os.listdir(directory):
        #start = time.time()
        f = os.path.join(directory, filename)
        # verifica se é arquivo
        if os.path.isfile(f):
            # Abre o arquivo e armazena linha por linha em
            # um vetor de strings sem o \n no final
            print("Arquivo: ", filename)
            with open(f) as arquivo:
                linhas = [linha.rstrip() for linha in arquivo]
            for linha in linhas:
                thread = threading.Thread(target=eval, args=(linha,))
                lista_threads.append(thread)

    for thr in lista_threads:
        thr.start()

    for thr in lista_threads:
        thr.join()

    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)
    return 0


def memDistSemParal(ip_list):
    print("Memória Distribuída - Sem paralelismo")

    # Pega os ip's de destino e adiciona eles nas listas
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #ip_list_final = []
    #for ip in ip_list:
    #    s.connect((ip, 80))
    #    print("Adicionando IP: ", s.getsockname()[0])
    #    ip_list_final.append(s.getsockname()[0])
    #s.close()
    #hostname = socket.gethostbyname(socket.gethostname())
    #ip_list = ip_list_final
    #ip_list.append(hostname)
    print("Lista IP's:\n", ip_list)

    # Info adicional
    tam_iplist = len(ip_list)
    directory = 'Problemas Matematicos'
    tempo_total = time.time()
    numero_problemas = len(os.listdir(directory))
    portas = [5000, 5001, 5002]

    file_list = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            f_abs = os.path.abspath(f)
            print("Arquivo: ", filename)
            file_list.append(f_abs)

    # Tamanho de problemas
    tamanho = len(file_list)
    Impar = (True if tamanho % 2 == 1 else False)

    # Exemplo de distribuição: 7 prob / 2 ip =  4 prob pra cada pc
    calc = math.ceil(tamanho / tam_iplist) # 4
    ip_pos = 0
    count = 0

    # Envia o número de problemas para cada computador, e sua porta
    for i in range(0, len(ip_list)):
        # Se for impar o ultimo pc processa - 1
        num_calc = (calc - 1 if Impar & i == len(ip_list) else calc)

        # Faz o envio
        s = socket.socket()
        print(f"[+] Connecting to {ip_list[i]}:{portas[i]}")
        s.connect((ip_list[i], portas[i]))
        print("[+] Connected.")
        s.send(f"{str(num_calc)}".encode())
        s.close()

    # Envia todos os arquivos Sequencialmente
    for i in range(0, tamanho):
        time.sleep(0.01)
        envia_arquivo(ip_list[ip_pos], portas[ip_pos], file_list[i])
        count+=1
        if count == calc:
            ip_pos += 1

    # Falta Receber a Resposta Sequencial !!!! / só funciona de 1 pra um ?
    for i in range(0, len(ip_list)):
        num_calc = (calc - 1 if Impar & i == len(ip_list) else calc)
        recebe_arquivo_sequencial(ip_list[i], num_calc, portas[i])  # calc

    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)
    return 0

def memDistComParal(ip_list):
    print("Memória Distribuída - Com paralelismo")

    # Pega os ip's de destino e adiciona eles nas listas
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #ip_list_final = []
    #for ip in ip_list:
    #    s.connect((ip, 80))
    #    print("Adicionando IP: ", s.getsockname()[0])
    #    ip_list_final.append(s.getsockname()[0])
    #s.close()
    #ip_list = ip_list_final
    print("Lista IP's:\n", ip_list)

    # Info adicional
    tam_iplist = len(ip_list)
    directory = 'Problemas Matematicos'
    tempo_total = time.time()
    numero_problemas = len(os.listdir(directory))
    portas = [5000,5001,5002,5003,5004,5005,5006]
    #portas_volta = portas_ida #[5007,5008,5009,5010,5011,5012]

    file_list = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            f_abs = os.path.abspath(f)
            print("Arquivo: ", filename)
            # print("Abs: ", f_abs)
            file_list.append(f_abs)

    # Tamanho de problemas
    tamanho = len(file_list)
    Impar = (True if tamanho % 2 == 1 else False)

    # Exemplo de distribuição: 7 prob / 2 ip =  4 prob pra cada pc
    calc = math.ceil(len(file_list) / tam_iplist)  # 4
    ip_pos = 0
    count = 0

    # Envia o número de problemas para cada computador, e sua porta
    for i in range(0, len(ip_list)):
        # Se for impar o ultimo pc processa - 1
        num_calc = (calc - 1 if Impar & i == len(ip_list) else calc)

        # Faz o envio
        s = socket.socket()
        print(f"[+] Connecting to {ip_list[i]}:{portas[i]}")
        s.connect((ip_list[i], portas[i]))
        print("[+] Connected.")
        s.send(f"{str(num_calc)}".encode())
        s.close()

    # Envia todos os arquivos Paralelamente
    lista_threads = []
    lista_threads2 = []
    for i in range(0, len(file_list)):
        # Pedido
        thread = threading.Thread(target=envia_arquivo, args=(ip_list[ip_pos], portas[i], file_list[i],))
        lista_threads.append(thread)

        # Receber a Resposta Paralelamente
        thread2 = threading.Thread(target=recebe_arquivo_paralelo, args=(ip_list[ip_pos], portas[i],))
        lista_threads2.append(thread2)

        count += 1
        if count == calc:
            ip_pos += 1

    time.sleep(1)
    # Inicia threads de envio
    for thr in lista_threads:
        thr.start()

    # Espera threads de envio
    for thr in lista_threads:
        thr.join()

    # Inicia threads de resposta
    for thr2 in lista_threads2:
        thr2.start()

    # Espera threads de resposta
    for thr2 in lista_threads2:
        thr2.join()

    # Falta Receber a Resposta Paralelamente !!!!
    # recebe_arquivo_sequencial(calc) # Limite sequencial

    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)
    return 0

def envia_arquivo(host, port, filename):
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096 # send 4096 bytes each time step

    # the ip address or hostname of the server, the receiver
    #host = "192.168.1.3"
    # the port, let's use 5001
    #port = 5002
    # the name of file we want to send, make sure it exists
    #filename = "digdin.txt" # "data.csv"
    # get the file size

    filesize = os.path.getsize(filename)

    # create the client socket
    s = socket.socket()

    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")

    # send the filename and filesize
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    # close the socket
    s.close()

def recebe_arquivo_sequencial(ip, num_files, porta):
    savepath_resp = 'Respostas'
    # Check whether the specified path exists or not
    isExist = os.path.exists(savepath_resp)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(savepath_resp)

    count = 0
    while True:
        # device's IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, 80))
        print("IP Server: ", s.getsockname()[0]) # 8.8.8.8
        SERVER_HOST = s.getsockname()[0] # "192.168.1.3"
        s.close()

        SERVER_PORT = porta
        # receive 4096 bytes each time
        BUFFER_SIZE = 4096
        SEPARATOR = "<SEPARATOR>"

        # create the server socket
        # TCP socket
        s = socket.socket()

        # bind the socket to our local address
        s.bind((SERVER_HOST, SERVER_PORT))

        # enabling our server to accept connections
        # 5 here is the number of unaccepted connections that
        # the system will allow before refusing new connections
        s.listen(5)
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

        # accept connection if there is any
        client_socket, address = s.accept()
        # if below code is executed, that means the sender is connected
        print(f"[+] {address} is connected.")

        # receive the file infos
        # receive using client socket, not server socket
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = re.search(r'\d+', filename).group()  # Bug Bizarro
        filesize = int(filesize)

        filename = os.path.join(savepath_resp, filename)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    count += 1
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

        # close the client socket
        client_socket.close()
        # close the server socket
        s.close()
        if count == num_files:
            break

    print("FULL BREAK")

def recebe_arquivo_paralelo(ip, porta):
    savepath = 'Respostas'
    # Check whether the specified path exists or not
    isExist = os.path.exists(savepath)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(savepath)

    count = 0
    while True:
        # device's IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, 80))
        print("Meu IP: ", s.getsockname()[0])
        SERVER_HOST = s.getsockname()[0]  # "192.168.1.3"
        s.close()

        SERVER_PORT = porta
        # receive 4096 bytes each time
        BUFFER_SIZE = 4096
        SEPARATOR = "<SEPARATOR>"

        # create the server socket
        # TCP socket
        s = socket.socket()

        # bind the socket to our local address
        s.bind((SERVER_HOST, SERVER_PORT))

        # enabling our server to accept connections
        # 5 here is the number of unaccepted connections that
        # the system will allow before refusing new connections
        s.listen(5)
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

        # accept connection if there is any
        client_socket, address = s.accept()
        # if below code is executed, that means the sender is connected
        print(f"[+] {address} is connected.")

        # receive the file infos
        # receive using client socket, not server socket
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename_base = os.path.basename(filename)
        # convert to integer
        filesize = re.search(r'\d+', filename).group()  # Bug Bizarro
        filesize = int(filesize)

        filename = os.path.join(savepath, filename_base)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    f.close()
                    count += 1
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

        # close the client socket
        client_socket.close()
        # close the server socket
        s.close()
        if count == 1:
            break

    print("FULL BREAK")

if __name__ == '__main__':
    tela()
