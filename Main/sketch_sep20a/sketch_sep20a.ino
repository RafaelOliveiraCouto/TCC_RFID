#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 mfrc522(SS_PIN, RST_PIN);

String responsavelID = "";

void setup() {

  Serial.begin(9600);

  SPI.begin();
  mfrc522.PCD_Init();

  Serial.println("LOG|Sistema iniciado.");
  Serial.println("LOG|Aproxime a tag...");

}

void loop() {

  // ========================================
  // Verifica se existe uma nova tag
  // ========================================
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }


  // ========================================
  // Monta o ID da Tag em formato Hexadecimal
  // ========================================
  String tagID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    tagID += String(mfrc522.uid.uidByte[i], HEX);
  }

  Serial.print("LOG|Tag detectada: ");
  Serial.println(tagID);


  // ========================================
  // Validando Se a TAG já existe no BD
  // ========================================
  Serial.println("CONSULT_TAG|'" + tagID + "'");
  while (Serial.available() == 0) {
    // Aguarda
  }
  int Resp_BD_A = Serial.parseInt();

  // Se não existe ela é criada
  if (Resp_BD_A == -1) {
    Serial.println("INSERT|'" + tagID + "'");
    Serial.println("########################################");
    Serial.println("LOG|Aproxime a tag...");
  } 


  // ========================================
  // Processamento dos Lotes
  // ========================================
  else {
    // Limpar dados antigos do Serial
    while (Serial.available() > 0) {
      Serial.read();
    }

    // CONSULTAR PROCESSO
    Serial.println("CONSULT MANUFACTURE_PROCESS|'" + tagID + "'");
    while (Serial.available() == 0) {
      // Aguarda resposta do Python
    }
    String Resp_BD_B = Serial.readStringUntil('\n');

    Serial.println(Resp_BD_B);

    int posM = Resp_BD_B.indexOf('M');
    int posP = Resp_BD_B.indexOf('P');
    int posMM = Resp_BD_B.indexOf("MM");
    int posMP = Resp_BD_B.indexOf("MP");

    int mafufatura = Resp_BD_B.substring(posM + 1, posP).toInt();
    int processo = Resp_BD_B.substring(posP + 1, posMM).toInt();
    int max_mafufatura = Resp_BD_B.substring(posMM + 2, posMP).toInt();
    int max_processo = Resp_BD_B.substring(posMP + 2).toInt();

    if(mafufatura < max_mafufatura){
      if(mafufatura == 0){
        chamar_responsavel();
        Serial.println("UPDATE MANUFACTURE|'" + tagID + "'|'" + responsavelID + "'");
        Serial.println("########################################");
        Serial.println("LOG|Aproxime a tag...");
      } else if(mafufatura%2 == 1){
        // Manufatura ímpar → nova manufatura iniciada

        if(processo < max_processo){
          chamar_responsavel();
          Serial.println("UPDATE PROCESS|'" + tagID + "'|'" + responsavelID + "'");
          Serial.println("########################################");
          Serial.println("LOG|Aproxime a tag...");
        } else {
          chamar_responsavel();
          Serial.println("UPDATE MANUFACTURE|'" + tagID + "'|'" + responsavelID + "'");
          Serial.println("########################################");
          Serial.println("LOG|Aproxime a tag...");
        }
        
      } else if(mafufatura%2 == 0){
        // Manufatura par → manufatura finalizada

        chamar_responsavel();
        Serial.println("UPDATE MANUFACTURE|'" + tagID + "'|'" + responsavelID + "'");
        Serial.println("########################################");
        Serial.println("LOG|Aproxime a tag...");
      }
    } else {
      Serial.println("Produção finalizado");
      Serial.println("DEACTIVATE TAG|'" + tagID + "'");
      Serial.println("########################################");
      Serial.println("LOG|Aproxime a tag...");
    }
    
  }

  // Finaliza comunicação com a tag
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  delay(1000);
}


void chamar_responsavel() {
  Serial.println("LOG|Informe o responsavel por essa tarefa: ");

  int Resp_BD_C = 0;

  do {
    responsavelID = "";
    while (responsavelID == "") {
      if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {

        // Monta o ID do cartão do responsável
        for (byte i = 0; i < mfrc522.uid.size; i++) {
          responsavelID += String(mfrc522.uid.uidByte[i], HEX);
        }

        // Finaliza a leitura do cartão
        mfrc522.PICC_HaltA();
        mfrc522.PCD_StopCrypto1();

        delay(500);
      }
    }

    // Consulta o responsável no banco de dados
    Serial.println("CONSULT_USER|'" + responsavelID + "'");
    while (Serial.available() == 0) {
      // Aguarda resposta
    }
    Resp_BD_C = Serial.parseInt();

  } while (Resp_BD_C != 1);
}
