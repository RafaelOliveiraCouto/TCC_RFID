import os
from dotenv import load_dotenv

load_dotenv("Secrets/bd.env")

LINK_BD = os.getenv("LINK_BD")

import serial
import requests
import json
import time

# =========================
# CONFIGURAÇÕES
# =========================

PORTA = "COM3"
BAUDRATE = 9600

# =========================
# CONEXÃO COM ARDUINO
# =========================

arduino = serial.Serial(
    PORTA,
    BAUDRATE,
    timeout=1
)

# =========================
# CONEXÃO COM FIREBASE
# =========================

link = LINK_BD

# =========================
# LEITURA DA SERIAL
# =========================

while True:

    linha = arduino.readline().decode("utf-8").strip()

    if linha == "":
        continue

    print("Recebido:", linha)

    # ========================================
    # SELECT - CONSULTAR
    # ========================================

    if linha.startswith("CONSULT"):
        tagID = linha.split("'")[1]

        req = requests.get(f'{link}/TAGS.json')

        if tagID in req.json():
            arduino.write(b"1\n")
        else:
            print("TAG não encontrada.")
            arduino.write(b"-1\n")


    # ========================================
    # INSERT - CADASTRAR
    # ========================================

    elif linha.startswith("INSERT"):
        tagID = linha.split("'")[1]
        Limit_Process = int(linha.split("'")[3])

        print("TAG para cadastro:", tagID)

        conteudo = input("Digite o nome do Produto: ")


        contador = milissegundos = int(time.time() * 1000)
        DADOS = {
            'CONTEUDO': conteudo, 
            'N_PROCESSO': 0,
            'PROCESSO': {
                '0' : {
                    'CHEGADA': contador,
                    'GEOLOCALIZACAO': 0,
                }
            },
            'ATIVO': True
        }

        for i in range(1, Limit_Process + 1):
            DADOS['PROCESSO'][str(i)] = {
                'CHEGADA': 0,
                'SAIDA': 0,
                'GEOLOCALIZACAO': 0,
                'RESPONSAVEL' : 0,
        }

        req = requests.put(f"{link}/TAGS/{tagID}.json", data=json.dumps(DADOS))


    # ========================================
    # UPDATE - N_PROCESS
    # ========================================

    elif linha.startswith("UPDATE N_PROCESS"):
        tagID = linha.split("'")[1]

        req = requests.get(f'{link}/TAGS/{tagID}/.json')
        dados = req.json()

        processo = dados.get("N_PROCESSO")
        processo +=1

        DADOS = {'N_PROCESSO': processo}

        req = requests.patch(f"{link}/TAGS/{tagID}/.json", data=json.dumps(DADOS))

        # Enviar o N_Process para o arduino
        arduino.write(f"{processo}\n".encode())


    # ========================================
    # UPDATE - PROCESS X
    # ========================================

    elif linha.startswith("UPDATE PROCESS"):
        tagID = linha.split("'")[3]
        Prc = int(linha.split("'")[1])


        req = requests.get(f'{link}/TAGS/{tagID}/.json')
        dados = req.json()
        processo = dados.get("N_PROCESSO")


        responsavel = input("Digite o responsavel pelo Produto: ")
        contador = milissegundos = int(time.time() * 1000)

        if processo%2 == 1:
            DADOS = {
                'CHEGADA': contador,
                'GEOLOCALIZACAO': 0,
                'RESPONSAVEL' : responsavel
            }
        if processo%2 == 0:
            DADOS = {
                'SAIDA': contador,
                'GEOLOCALIZACAO': 0,
                'RESPONSAVEL' : responsavel
            }

        req = requests.patch(f"{link}/TAGS/{tagID}/PROCESSO/{Prc}.json", data=json.dumps(DADOS))


    # ========================================
    # DELETE - DESATIVAR TAG
    # ========================================

    elif linha.startswith("DEACTIVATE TAG"):
        tagID = linha.split("'")[1]
        contador = milissegundos = int(time.time() * 1000)

        DADOS1 = {
            'ATIVO': False
        }

        DADOS2 = {
            'SAIDA': contador,
            'GEOLOCALIZACAO': 0
        }

        req = requests.patch(f"{link}/TAGS/{tagID}.json", data=json.dumps(DADOS1))

        req = requests.put(f"{link}/TAGS/{tagID}/PROCESSO/3.json", data=json.dumps(DADOS2))