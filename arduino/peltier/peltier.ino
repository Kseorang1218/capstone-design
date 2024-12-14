#include <ArduinoJson.h>
#include "DHT.h"

#define DHTPIN1 5  // DHT22 핀
#define DHTPIN2 9  // DHT11 첫 번째 핀
#define DHTPIN3 8  // DHT11 두 번째 핀
#define DHTTYPE22 DHT22
#define DHTTYPE11 DHT11

DHT dht1(DHTPIN1, DHTTYPE22); // DHT22
DHT dht2(DHTPIN2, DHTTYPE11); // DHT11
DHT dht3(DHTPIN3, DHTTYPE11); // DHT11

// pin map
// 3: 펠티어
// 6, 7: 히터
// 10: LED
// 11: 환풍팬
// 12: UV
const int controlPins[] = {3, 6, 7, 10, 11, 12};
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

    if (input == "0") {
      // 모든 핀을 LOW로 설정
      for (int i = 0; i < numPins; i++) {
        pinStates[i] = 0;
        digitalWrite(controlPins[i], LOW);
      }
      Serial.println("All pins set to LOW.");
    } else {
      int inputPin = input.toInt();  // 입력 값을 정수로 변환
      if (inputPin > 0) {
        // 입력한 핀이 제어 핀에 속하는지 확인
        bool validPin = false;
        for (int i = 0; i < numPins; i++) {
          if (controlPins[i] == inputPin) {
            pinStates[i] = 1;  // 상태를 HIGH로 설정
            digitalWrite(controlPins[i], HIGH);
            Serial.print("Pin ");
            Serial.print(controlPins[i]);
            Serial.println(" set to HIGH.");
            validPin = true;
            break;
          }
        }
        if (!validPin) {
          Serial.println("Invalid pin. Enter a valid control pin number (3, 6, 7, 10, 11, 12) or 0 to turn all off.");
        }
      } else {
        Serial.println("Invalid input. Enter a valid control pin number or 0 to turn all off.");
      }
    }
  }

  // 핀 상태 유지
  for (int i = 0; i < numPins; i++) {
    digitalWrite(controlPins[i], pinStates[i]);
  }

  delay(2000);  // 2초 간격
}
