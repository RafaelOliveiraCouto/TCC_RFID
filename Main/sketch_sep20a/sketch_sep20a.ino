#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 mfrc522(SS_PIN, RST_PIN);

int Limit_Process = 2;                    // Limite de x processos Intermediarios
int Total_Process = Limit_Process*2;      // Cada processo tem início/fim + Chegada + Saída
int PC = 0;

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
  // Monta o ID da Tag
  // ========================================

  // Monta o ID da tag em formato Hexadecimal
  String tagID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    tagID += String(mfrc522.uid.uidByte[i], HEX);
  }

  Serial.print("LOG|Tag detectada: ");
  Serial.println(tagID);


  // ========================================
  // Validando Se a TAG já existe no BD
  // ========================================
  Serial.println("CONSULT|'" + tagID + "'");
  while (Serial.available() == 0) {
    // Aguarda
  }
  int Resp_BD_A = Serial.parseInt();


  // Se não existe ela é criada
  if (Resp_BD_A == -1) {
    Serial.println("INSERT|'" + tagID + "'|" + "WITH '" + Limit_Process + "' PROCESS");
    Serial.println("LOG|Tag nova registrada.");
  } 

  // Validar se a TAG esta Desativada
  // else if{return;}
  

  else {

    // Limpar dados antigos do Serial
    while (Serial.available() > 0) {
      Serial.read();
    }

    // INCREMENTAR PROCESSO
    Serial.println("UPDATE N_PROCESS|'" + tagID + "'");
    while (Serial.available() == 0) {
      // Aguarda resposta do Python
    }
    int Resp_BD_B = Serial.parseInt();
    Serial.print("Processo atual da " + tagID + ": ");
    Serial.println(Resp_BD_B);

    // Processo ímpar → novo estágio iniciado
    if (Resp_BD_B % 2 == 1 && Resp_BD_B <= Total_Process){
      Serial.println("Processo ímpar → novo estágio iniciado");
      PC = Resp_BD_B/2 + 1;
      Serial.print("UPDATE PROCESS '");
      Serial.print(PC);
      Serial.println("'|'" + tagID + "'");


    }
    // Processo par → estágio finalizado
    else if(Resp_BD_B % 2 == 0 && Resp_BD_B <= Total_Process){
      Serial.println("Processo par → estágio finalizado");
      PC = Resp_BD_B/2;
      Serial.print("UPDATE PROCESS '");
      Serial.print(PC);
      Serial.println("'|'" + tagID + "'");

    }
    // Processo finalizado → Desativando TAG
    else {
      Serial.println("Processo finalizado");
      Serial.println("DEACTIVATE TAG|'" + tagID + "'");
    }
  }

  // Finaliza comunicação com a tag
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  delay(1000);
}