#include <ArduinoJson.h>
#include "DHT.h"

#define DHTPIN1 5  // DHT11 핀(제습)
#define DHTPIN2 9  // DHT22 첫 번째 핀(건조)
#define DHTPIN3 6  // DHT22 두 번째 핀(히터)
#define DHTTYPE22 DHT22
#define DHTTYPE11 DHT11

// 3 펠티어
// 7 히터팬
// 8 히터
// 11 led
// 12 uv
// 13 환풍
// 5, 9, 6 제습(11), 건조(22), 히터(22) 측 센서

DHT dht1(DHTPIN1, DHTTYPE11); // DHT11
DHT dht2(DHTPIN2, DHTTYPE22); // DHT22
DHT dht3(DHTPIN3, DHTTYPE11); // DHT11

// 제어 핀 정의
const int controlPins[] = {3, 7, 8, 11, 12, 13};
const int numPins = sizeof(controlPins) / sizeof(controlPins[0]);
int pinStates[numPins] = {0, 0, 0, 0, 0, 0};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numPins; i++) {
    pinMode(controlPins[i], OUTPUT);
    digitalWrite(controlPins[i], LOW);
  }
  dht1.begin();
  dht2.begin();
  dht3.begin();
}

void loop() {
  // 온습도 센서 데이터 읽기
  float temp1 = dht1.readTemperature();
  float humidity1 = dht1.readHumidity();
  float temp2 = dht2.readTemperature();
  float humidity2 = dht2.readHumidity();
  float temp3 = dht3.readTemperature();
  float humidity3 = dht3.readHumidity();

  // JSON 데이터 생성
  StaticJsonDocument<256> jsonDoc;

  JsonObject sensor1 = jsonDoc.createNestedObject("sensor1");
  sensor1["temperature"] = isnan(temp1) ? NAN : temp1;
  sensor1["humidity"] = isnan(humidity1) ? NAN : humidity1;

  JsonObject sensor2 = jsonDoc.createNestedObject("sensor2");
  sensor2["temperature"] = isnan(temp2) ? NAN : temp2;
  sensor2["humidity"] = isnan(humidity2) ? NAN : humidity2;

  JsonObject sensor3 = jsonDoc.createNestedObject("sensor3");
  sensor3["temperature"] = isnan(temp3) ? NAN : temp3;
  sensor3["humidity"] = isnan(humidity3) ? NAN : humidity3;

  JsonArray pinArray = jsonDoc.createNestedArray("pinStates");
  for (int i = 0; i < numPins; i++) {
    pinArray.add(pinStates[i]);
  }

  serializeJson(jsonDoc, Serial);
  Serial.println();

  // 시리얼 입력 처리
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("stop")) {
      handleStopCommand(input);
    } else if (input.toInt() > 0) {
      controlPin(input.toInt());
    } else if (input == "0") {
      turnAllOff();
    } else {
      Serial.println("Invalid command. Enter a valid pin number or '0' to turn all off.");
    }
  }

  delay(2000);  // 2초 간격
}

// 특정 핀 활성화 함수
void controlPin(int pin) {
  for (int i = 0; i < numPins; i++) {
    if (controlPins[i] == pin) {
      pinStates[i] = 1;
      digitalWrite(controlPins[i], HIGH);
      Serial.print("Pin ");
      Serial.print(pin);
      Serial.println(" set to HIGH.");
      return;
    }
  }
  Serial.println("Invalid pin. Pin not in control list.");
}

void handleStopCommand(String command) {
  command.remove(0, 5);  // "stop " 제거
  while (command.length() > 0) {
    int spaceIndex = command.indexOf(' ');
    String pinString = (spaceIndex == -1) ? command : command.substring(0, spaceIndex);
    command = (spaceIndex == -1) ? "" : command.substring(spaceIndex + 1);

    int pin = pinString.toInt();
    for (int i = 0; i < numPins; i++) {
      if (controlPins[i] == pin) {
        pinStates[i] = 0;
        digitalWrite(controlPins[i], LOW);
        Serial.print("Pin ");
        Serial.print(pin);
        Serial.println(" set to LOW.");
      }
    }
  }
}

// 모든 핀 끄기 함수
void turnAllOff() {
  for (int i = 0; i < numPins; i++) {
    pinStates[i] = 0;
    digitalWrite(controlPins[i], LOW);
  }
  Serial.println("All pins set to LOW.");
}
