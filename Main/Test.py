import os
from dotenv import load_dotenv
import requests


#####################################################################################################################################################

# Geolocalização 1
# url = "http://ip-api.com/json/?fields=status,message,lat,lon,city,country"

# try:
#     resposta = requests.get(url, timeout=10)
#     resposta.raise_for_status()
#     dados = resposta.json()

#     if dados.get("status") == "success":
#         latitude = dados["lat"]
#         longitude = dados["lon"]

#         print("Cidade:", dados["city"])
#         print("País:", dados["country"])
#         print("Latitude:", latitude)
#         print("Longitude:", longitude)

#         link = f"https://www.google.com/maps?q={latitude},{longitude}"
#         print("Link do Google Maps:", link)
#     else:
#         print("Erro:", dados.get("message", "Não foi possível localizar."))

# except requests.RequestException as erro:
#     print("Falha na requisição:", erro)


#####################################################################################################################################################

# python -m pip install winrt-Windows.Devices.Geolocation
import asyncio

from winrt.windows.devices.geolocation import (
    Geolocator,
    PositionAccuracy
)


async def obter_localizacao():
    try:
        geolocator = Geolocator()
        geolocator.desired_accuracy = PositionAccuracy.HIGH

        print("Obtendo localização...")

        posicao = await geolocator.get_geoposition_async()

        coordenadas = posicao.coordinate
        ponto = coordenadas.point.position

        latitude = ponto.latitude
        longitude = ponto.longitude

        localizacao = str(latitude) + ";" + str(longitude)

        return localizacao

    except Exception as erro:
        print("Não foi possível obter a localização.")
        print("Detalhes:", repr(erro))

    if __name__ == "__main__":
        asyncio.run(main())


async def main():
    a = int(input("Digite 1 para buscar sua localização: "))

    if a == 1:
        str = await obter_localizacao()

    print(str)


#####################################################################################################################################################
# load_dotenv("Secrets/bd.env")

# LINK_BD = os.getenv("LINK_BD")

# ### Produto ###

# DADOS = {
#     'Nome': 'Pizza de Pepperoni Congelada',
#     'Estrutura': {
#         'Manufatura': 4,
#         'Nome_Manufatura': [
#             'Preparação da Massa',
#             'Preparação dos Ingredientes',
#             'Montagem da Pizza',
#             'Congelamento e Embalagem'
#             ],
#         'Processos': [2, 2, 3, 2],
#         'Nome_Processo': [
#                 ['Mistura e sova da massa', 'Fermentação e abertura da massa'],
#                 ['Preparação do molho', 'Corte e preparação do Pepperoni'],
#                 ['Aplicação do molho', 'Distribuição dos ingredientes', 'Inspeção da montagem'],
#                 ['Congelamento do produto', 'Embalagem e inspeção final']
#             ]
#     }
# }


# req = requests.post(f"{LINK_BD}/Produto.json", data=json.dumps(DADOS))
# print(req)


# DADOS = {
#     'Nome': 'Chocolate em Barra',
#     'Estrutura': {
#         'Manufatura': 3,
#         'Nome_Manufatura': [
#             'Processamento do Cacau',
#             'Preparação do Chocolate',
#             'Moldagem e Embalagem'
#             ],
#         'Processos': [2, 3, 2],
#         'Nome_Processo': [
#                 ['Seleção e Fermentação das Amêndoas', 'Torrefação e Moagem do Cacau'],
#                 ['Mistura dos Ingredientes', 'Refinamento do Chocolate', 'Conchagem e Homogeneização'],
#                 ['Moldagem e resfriamento', 'Embalagem e inspeção final']
#             ]
#     }
# }


# req = requests.post(f"{LINK_BD}/Produto.json", data=json.dumps(DADOS))
# print(req)

# ### User ###

# # Tag ID_User para Inserções: 962fc3 | 7c1c04  

# DADOS = {
#     'Nome': 'Zozimo',
#     'E-mail': 'zozimo.caldeira@alunoufop.com.br',
#     'Idade': '54',
#     'ID_Cartão': '962fc3',
#     'Cargo': 'Diretor Executivo de Projetos'
# }


# req = requests.post(f"{LINK_BD}/User.json", data=json.dumps(DADOS))
# print(req)


# #####################################################################################################################################################

# req = requests.get(f'{LINK_BD}/Produto/-P4AgsMeh_kcS392VrDP.json')
# produto = req.json()

# print(produto)

# ### INFORMAÇÕES DO PRODUTO
# nome = produto.get("Nome")
# manufatura = produto.get("Estrutura", {}).get("Manufatura")
# arry_processo = produto.get("Estrutura", {}).get("Processos")

# print(nome)
# print(manufatura)
# print(arry_processo)

#####################################################################################################################################################


# userID = "7c1c04"

# req = requests.get(f'{LINK_BD}/User.json')
# dados = req.json()

# if dados and any(
#     usuario.get("ID_Cartão") == userID
#     for usuario in dados.values()
#     if isinstance(usuario, dict)
# ):
#     print("LOG|Usuario identificado")
# else:
#     print("LOG|Usuario não identificado")



        # req = requests.get(f'{link}/User.json')
        # user = req.json()
        # ### INFORMAÇÕES DO USUARIO
        # for user_cardID, dados in user.items():
        #     if dados["ID_Cartão"] == user_cardID:
        #         responsavel = dados["Nome"]



    # // ========================================
    # // Solicita a identificação do responsável
    # // ========================================
    # Serial.println("LOG|Identificação do Responsavel para Cadastro da Tag");

    # int Resp_BD_B = 0;

    # do{
    #   responsavelID = "";
    #   while (responsavelID == "") {
    #     if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {

    #       // Monta o ID do cartão do responsável
    #       for (byte i = 0; i < mfrc522.uid.size; i++) {
    #         responsavelID += String(mfrc522.uid.uidByte[i], HEX);
    #       }

    #       // Finaliza a leitura do cartão do responsável
    #       mfrc522.PICC_HaltA();
    #       mfrc522.PCD_StopCrypto1();

    #       delay(500);
    #     }
    #   }
      
    #   // // Limpar dados antigos do Serial
    #   // while (Serial.available() > 0) {
    #   //   Serial.read();
    #   // }

    #   Serial.println("CONSULT_USER|'" + responsavelID + "'");
    #   while (Serial.available() == 0) {
    #     // Aguarda
    #   }
    #   Resp_BD_B = Serial.parseInt();
    #   Serial.println(Resp_BD_B);

    # } while(Resp_BD_B != 1);

#####################################################################################################################################################

# Criar     -> POST
# Criar     -> PUT
# Atualizar -> PATCH
# Pegar     -> GET
# Deletar   -> DELETE
