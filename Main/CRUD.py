from dotenv import load_dotenv
from winrt.windows.devices.geolocation import (Geolocator, PositionAccuracy)

import os
import serial
import requests
import json
import time
import asyncio

async def main():
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

    load_dotenv("Secrets/bd.env")
    LINK_BD = os.getenv("LINK_BD")
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
        # SELECT - CONSULTAR TAG
        # ========================================

        if linha.startswith("CONSULT_TAG"):
            tagID = linha.split("'")[1]

            req = requests.get(f'{link}/Lote.json')

            if tagID in req.json():
                arduino.write(b"1\n")
            else:
                arduino.write(b"-1\n")


        # ========================================
        # SELECT - CONSULTAR USER
        # ========================================

        if linha.startswith("CONSULT_USER"):
            user_cardID = linha.split("'")[1]

            req = requests.get(f'{link}/User.json')
            dados = req.json()

            if dados and any(
                usuario.get("ID_Cartão") == user_cardID
                for usuario in dados.values()
                if isinstance(usuario, dict)
            ):
                print("Recebido: LOG|Usuario identificado")
                arduino.write(b"1\n")
            else:
                print("Recebido: LOG|Usuario não identificado. Tente novamente!")
                arduino.write(b"-1\n")


        # ========================================
        # INSERT - CADASTRAR
        # ========================================

        elif linha.startswith("INSERT"):
            tagID = linha.split("'")[1]

            ID_Produto = input("Digite ID do Produto: ")

            req = requests.get(f'{link}/Produto/{ID_Produto}.json')
            produto = req.json()

            ### INFORMAÇÕES DO PRODUTO
            nome = produto.get("Nome")
            manufatura = produto.get("Estrutura", {}).get("Manufatura")
            arry_nome_manufatura = produto.get("Estrutura", {}).get("Nome_Manufatura")
            arry_processo = produto.get("Estrutura", {}).get("Processos")
            arry_nome_processo = produto.get("Estrutura", {}).get("Nome_Processo")

            contador = milissegundos = int(time.time() * 1000)
            DADOS = {
                'Nome': nome,
                'Chegada': contador,
                'Saida': 0,
                'TAG_Ativa': True,
                'Index_Manufatura': 1,
                'N_Manufatura': 0,
                'Manufatura': {}
            }

            for i in range(1, manufatura + 1):
                DADOS['Manufatura'][str(i)] = {
                    'Nome': arry_nome_manufatura[i-1],
                    'Chegada': 0,
                    'Responsavel': 0,
                    'Saida': 0,
                    'N_Processo': 0,
                    'Geolocalização': 0,
                    'Processo': {}
                }
                for j in range(0, arry_processo[i-1]):
                    DADOS['Manufatura'][str(i)]['Processo'][str(j+1)] = {
                        'Nome': arry_nome_processo[i-1][j],
                        'Chegada': 0,
                        'Responsavel': 0,
                        'Saida': 0,
                        'Geolocalização': 0,
                }
            

            req = requests.put(f"{link}/Lote/{tagID}.json", data=json.dumps(DADOS))


        # ========================================
        # SELECT - CONSULTAR MANUFACTURE_PROCESS
        # ========================================

        elif linha.startswith("CONSULT MANUFACTURE_PROCESS"):
            tagID = linha.split("'")[1]

            req = requests.get(f'{link}/Lote/{tagID}.json')
            dados = req.json()

            # Manufatura
            n_manufatura = dados.get("N_Manufatura")
            index_manufatura = dados.get("Index_Manufatura")
            manufaturas = dados.get("Manufatura", [])
            n_max_manufatura = (len(manufaturas) - 1) * 2

            # Processo - Se Manufatura = 0
            n_processo = manufaturas[index_manufatura].get("N_Processo")
            processos = manufaturas[index_manufatura].get("Processo")
            n_max_processo = (len(processos) - 1) * 2

            
            new_str = f"M{n_manufatura}P{n_processo}MM{n_max_manufatura}MP{n_max_processo}"

            # Enviar uma String para o arduino
            arduino.write(f"{new_str}\n".encode())


        # ========================================
        # UPDATE - MANUFACTURE
        # ========================================

        elif linha.startswith("UPDATE MANUFACTURE"):
            tagID = linha.split("'")[1]
            user_cardID = linha.split("'")[3]
            responsavel = ""

            ### INFORMAÇÕES DO USUARIO
            req = requests.get(f'{link}/User.json')
            user = req.json()
            for user_ID, dados in user.items():
                if dados["ID_Cartão"] == user_cardID:
                    responsavel = dados["Nome"]
                    break

            ### INFORMAÇÕES DO LOTE
            req = requests.get(f'{link}/Lote/{tagID}.json')
            dados = req.json()

            n_manufatura = dados.get("N_Manufatura")
            n_manufatura +=1

            ### INFORMAÇÕES DO TEMPORIZADOR
            contador = milissegundos = int(time.time() * 1000)  

            if n_manufatura%2 == 1:
                index_manufatura = n_manufatura//2 + 1
            if n_manufatura%2 == 0:
                index_manufatura = n_manufatura//2
            
            DADOS_1 = {
                'N_Manufatura': n_manufatura,
                'Index_Manufatura': index_manufatura
            }

            # Processo ímpar → novo estágio iniciado
            if n_manufatura%2 == 1:
                ### INFORMAÇÕES DA GEOLOCALIZAÇÃO
                local = await obter_localizacao()  
                DADOS_2 = {
                    'Chegada': contador,
                    'Geolocalização': local,
                    'Responsavel': responsavel
                }

            # Processo par → estágio finalizado
            if n_manufatura%2 == 0:
                DADOS_2 = {
                    'Saida': contador,
                    'Responsavel': responsavel
                }

            req = requests.patch(f"{link}/Lote/{tagID}.json", data=json.dumps(DADOS_1))
            req = requests.patch(f"{link}/Lote/{tagID}/Manufatura/{index_manufatura}.json", data=json.dumps(DADOS_2))


        # ========================================
        # UPDATE - PROCESS
        # ========================================

        elif linha.startswith("UPDATE PROCESS"):
            tagID = linha.split("'")[1]
            user_cardID = linha.split("'")[3]
            responsavel = ""

            ### INFORMAÇÕES DO USUARIO
            req = requests.get(f'{link}/User.json')
            user = req.json()
            for user_ID, dados in user.items():
                if dados["ID_Cartão"] == user_cardID:
                    responsavel = dados["Nome"]
                    break

            ### INFORMAÇÕES DO LOTE
            req = requests.get(f'{link}/Lote/{tagID}.json')
            dados = req.json()

            n_manufatura = dados.get("N_Manufatura")
            index_manufatura = dados.get("Index_Manufatura")
            manufaturas = dados.get("Manufatura", [])

            n_processo = manufaturas[index_manufatura].get("N_Processo")
            n_processo +=1

            ### INFORMAÇÕES DO TEMPORIZADOR
            contador = milissegundos = int(time.time() * 1000)  
            
            DADOS_1 = {
                'N_Processo': n_processo
            }

            # Processo ímpar → novo estágio iniciado
            if n_processo%2 == 1:
                ### INFORMAÇÕES DA GEOLOCALIZAÇÃO
                local = await obter_localizacao() 
                aux_p = n_processo//2 + 1
                DADOS_2 = {
                    'Chegada': contador,
                    'Geolocalização': local,
                    'Responsavel': responsavel
                }

            # Processo par → estágio finalizado
            if n_processo%2 == 0:
                aux_p = n_processo//2
                DADOS_2 = {
                    'Saida': contador,
                    'Responsavel': responsavel
                }

            req = requests.patch(f"{link}/Lote/{tagID}/Manufatura/{index_manufatura}.json", data=json.dumps(DADOS_1))
            req = requests.patch(f"{link}/Lote/{tagID}/Manufatura/{index_manufatura}/Processo/{aux_p}.json", data=json.dumps(DADOS_2))


        # ========================================
        # DELETE - DESATIVAR TAG
        # ========================================

        elif linha.startswith("DEACTIVATE TAG"):
            tagID = linha.split("'")[1]
            contador = milissegundos = int(time.time() * 1000)

            DADOS = {
                'Saida': contador,
                'TAG_Ativa': False
            }

            req = requests.patch(f"{link}/Lote/{tagID}.json", data=json.dumps(DADOS))



async def obter_localizacao():
    try:
        geolocator = Geolocator()
        geolocator.desired_accuracy = PositionAccuracy.HIGH
    
        print("Obtendo Geolocalização...")
    
        posicao = await geolocator.get_geoposition_async()
    
        coordenadas = posicao.coordinate
        ponto = coordenadas.point.position
    
        latitude = ponto.latitude
        longitude = ponto.longitude

        localizacao = str(latitude) + ";" + str(longitude)

        print("Localização Encontrada...")

        return localizacao
    
    except Exception as erro:
        print("Não foi possível obter a localização.")
        print("Detalhes:", repr(erro))


if __name__ == "__main__":
    asyncio.run(main())