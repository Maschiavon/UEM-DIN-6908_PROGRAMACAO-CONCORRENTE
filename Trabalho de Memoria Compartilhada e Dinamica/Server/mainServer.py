import socket
import tqdm
import os
import time
import math
import threading
import re
import PySimpleGUI as sg

def tela():
    sg.ChangeLookAndFeel("DarkBrown1")

    # Layout
    layout = [[sg.Text("Este é o PC SERVIDOR, Veja as informações:", font="Roboto")],
              [sg.Text("IP Origem:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip_origem")],
              [sg.Button("Executar Sequencial", font="Roboto"), sg.Button("Executar Paralelo", font="Roboto"),
               sg.Button("Get IP", font="Roboto"), sg.Text("Seu IP:", font="Roboto", key="txtMeuIP")],
              [sg.Output(size=(60, 12), key="output", font="Roboto")]]

    # Janela
    janela = sg.Window('Computador Servidor', layout, icon=r'./ic.ico')

    while True:
        # Extrair os dados da tela
        event, values = janela.Read()

        # Get Ip
        if event == "Get IP":
            hostname = socket.gethostbyname(socket.gethostname())
            janela['txtMeuIP'].update("Seu IP: " + str(hostname))
            janela['ip_origem'].update(hostname)

        # Executar
        elif event == "Executar Sequencial":
            ip_origem = values["ip_origem"]

            porta = 5000
            janela.FindElement("output").Update("")

            # Pega o número de problemas
            num_files = getNumberOfFiles(ip_origem, porta)

            # Por padrão o número de problemas é 6
            recebe_arquivo_sequencial(ip_origem, num_files, porta)

        elif event == "Executar Paralelo":
            ip_origem = values["ip_origem"]
            portas_ida = [5000, 5001, 5002, 5003, 5004, 5005]
            portas_volta = [5006, 5007, 5008, 5009, 5010, 5011]
            janela.FindElement("output").Update("")

            # Pega o número de problemas
            num_files2 = getNumberOfFiles(ip_origem, portas_ida[0])

            # Recebe e processa todos os arquivos Paralelamente
            lista_threads = []

            for i in range(num_files2): #era 6
                thread = threading.Thread(target=recebe_arquivo_paralelo, args=(ip_origem, portas_ida[i], portas_volta))
                lista_threads.append(thread)

            # Inicia threads
            for thr in lista_threads:
                thr.start()

            # Espera threads
            for thr in lista_threads:
                thr.join()

        # Fechar Janela
        else:
            break

def getNumberOfFiles(ip_origem, porta):
    # device's IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((ip_origem, 80))  # 8.8.8.8
    print("IP Origem: ", s.getsockname()[0])
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
    number_of_files = received

    # close the client socket
    client_socket.close()
    # close the server socket
    s.close()

    return int(number_of_files)


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

def envia_arquivo_sequencial(ip_origem, porta):
    print("Memória Distribuída(Servidor) - Sem paralelismo")
    print("Enviando arquivo")

    # Pega e adiciona o ip da origem na lista
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect((ip_origem, 80))
    #print("IP Origem: ", s.getsockname()[0])
    #ip_origem = s.getsockname()[0]
    #s.close()

    # Info adicional
    directory = 'Respostas'
    tempo_total = time.time()

    file_list = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            f_abs = os.path.abspath(f)
            print("Arquivo: ", filename)
            # print("Abs: ", f_abs)
            file_list.append(f_abs)

    for i in range(0, len(file_list)):
        time.sleep(0.01)
        envia_arquivo(ip_origem, porta, file_list[i])

    return 0

def processa_Problemas_sequencial():
    print("Memória Distribuida (Server) - Sem Paralelismo")
    print("Processando Problemas...")

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
    duracao_acumulativa = 0
    tempo_total = time.time()
    for filename in os.listdir(directory):
        start = time.time()
        f = os.path.join(directory, filename)
        # verifica se é arquivo
        if os.path.isfile(f):
            # Abre o arquivo e armazena linha por linha em
            # um vetor de strings sem o \n no final
            print("Arquivo: ", filename)
            with open(f) as arquivo:
                linhas = [linha.rstrip() for linha in arquivo]

            resp_nome = os.path.join(savepath_resp, "r" + str(count) + ".txt")
            r = open(resp_nome, "w")
            for linha in linhas:
                resp = eval(linha)
                duration = time.time() - start
                duracao_acumulativa += duration
                # print("Resposta: ", res)
                print("Duração: ", duration, "\n")
                print("T Acumulado: ", duracao_acumulativa, "\n")
                r.write(str(duration)+"\n")
            r.close()
            count+=1
    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)

def recebe_arquivo_sequencial(ip_origem, num_files, porta):
    savepath = 'Problemas Matematicos'
    # Check whether the specified path exists or not
    isExist = os.path.exists(savepath)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(savepath)

    count = 0
    while True:
        # device's IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip_origem, 80)) # 8.8.8.8
        print("IP Origem: ", s.getsockname()[0])
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

        filesize = re.search(r'\d+', filename).group() # Bug Bizarro
        filesize = int(filesize)

        filename = os.path.join(savepath, filename)

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
        if count == num_files:
            break

    print("\nFULL BREAK")
    processa_Problemas_sequencial()
    envia_arquivo_sequencial(ip_origem, porta)

def envia_arquivo_paralelo(ip_origem, porta, filename):
    print("Memória Distribuída(Servidor) - Com paralelismo")
    print("Enviando arquivo")

    # Pega e adiciona meu ip na lista
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect(("8.8.8.8", 80))
    print("IP Origem: ", ip_origem) #s.getsockname()[0]
    # ip_origem = s.getsockname()[0]
    # s.close()
    # print("Lista IP's:\n", ip_list)

    # Info adicional
    directory = 'Respostas'
    tempo_total = time.time()

    f = os.path.join(directory, filename)

    if os.path.isfile(f):
        f_abs = os.path.abspath(f)
        print("Arquivo: ", filename)
        # print("Abs: ", f_abs)
        envia_arquivo(ip_origem, porta, f_abs)

    return 0

def processa_Problemas_Paralelo(filename):
    print("Memória Distribuida (Server) - Com Paralelismo")
    print("Processando Problemas...")

    count = re.search(r'\d+', filename).group() # é a string do número
    resp_nome = ""

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
    start = time.time()
    f = os.path.join(directory, filename)
    # verifica se é arquivo
    if os.path.isfile(f):
        # Abre o arquivo e armazena linha por linha em
        # um vetor de strings sem o \n no final
        print("Arquivo: ", filename)
        with open(f) as arquivo:
            linhas = [linha.rstrip() for linha in arquivo]

        resp_nome = os.path.join(savepath_resp, "r" + count + ".txt")
        r = open(resp_nome, "w")
        for linha in linhas:
            resp = eval(linha)
            duration = time.time() - start
            # print("Resposta: ", res)
            print("Duração: ", duration, "\n")
            r.write(str(duration) + "\n")
        r.close()
    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)

    return resp_nome


def recebe_arquivo_paralelo(ip_origem, porta_ida, porta_volta):
    savepath = 'Problemas Matematicos'
    # Check whether the specified path exists or not
    isExist = os.path.exists(savepath)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(savepath)

    count = 0
    while True:
        # device's IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip_origem, 80)) # 8.8.8.8
        print("Meu IP: ", s.getsockname()[0])
        SERVER_HOST = s.getsockname()[0]  # "192.168.1.3"
        s.close()

        SERVER_PORT = porta_ida
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
    nome_resposta = processa_Problemas_Paralelo(filename_base)
    nome_resposta_base = os.path.basename(nome_resposta)
    time.sleep(2)
    envia_arquivo_paralelo(SERVER_HOST, porta_volta, nome_resposta_base)


if __name__ == '__main__':
    tela()