#include "DHT.h"

#define DHTPIN1 5  // 첫 번째 온습도 센서가 연결된 핀
#define DHTPIN2 9  // 두 번째 온습도 센서가 연결된 핀
#define DHTTYPE DHT22  // 센서 유형을 DHT22로 설정

DHT dht1(DHTPIN1, DHTTYPE);
DHT dht2(DHTPIN2, DHTTYPE);

// 제어할 핀 목록
const int controlPins[] = {3, 6, 7, 10, 11, 12};
const int numPins = sizeof(controlPins) / sizeof(controlPins[0]);

// 각 핀의 현재 상태를 저장할 배열 (LOW = 0, HIGH = 1)
int pinStates[numPins] = {0, 0, 0, 0, 0, 0};

void setup() {
  Serial.begin(9600);

  // 제어할 핀을 출력 모드로 설정하고 초기 상태를 LOW로 설정
  for (int i = 0; i < numPins; i++) {
    pinMode(controlPins[i], OUTPUT);
    digitalWrite(controlPins[i], LOW);
  }

  // 온습도 센서 초기화
  dht1.begin();
  dht2.begin();
}

void loop() {
  // 첫 번째 온습도 센서에서 데이터 읽기
  float temp1 = dht1.readTemperature();
  float humidity1 = dht1.readHumidity();

  // 두 번째 온습도 센서에서 데이터 읽기
  float temp2 = dht2.readTemperature();
  float humidity2 = dht2.readHumidity();

  // 읽기 실패 시 처리
  if (isnan(temp1) || isnan(humidity1)) {
    Serial.println("Failed to read from DHT sensor 1!");
  } else {
    Serial.print("Sensor 1 - Temperature: ");
    Serial.print(temp1, 1);
    Serial.print(" °C, Humidity: ");
    Serial.print(humidity1, 1);
    Serial.println(" %");
  }

  if (isnan(temp2) || isnan(humidity2)) {
    Serial.println("Failed to read from DHT sensor 2!");
  } else {
    Serial.print("Sensor 2 - Temperature: ");
    Serial.print(temp2, 1);
    Serial.print(" °C, Humidity: ");
    Serial.print(humidity2, 1);
    Serial.println(" %");
  }

  // 시리얼 모니터에서 입력을 받음
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // 사용자 입력을 문자열로 읽음
    input.trim();  // 앞뒤 공백 제거
    

    if (input == "0") {
      // 0 입력 시 모든 핀을 LOW로 설정
      for (int i = 0; i < numPins; i++) {
        pinStates[i] = 0;  // 상태 배열에서 모든 핀을 LOW로 설정
        digitalWrite(controlPins[i], LOW);
      }
      Serial.println("All pins set to LOW.");
    } else {
      int inputPin = input.toInt();  // 문자열을 정수로 변환
      if (inputPin > 0) {
        // 제어 핀 배열에 있는 핀인지 확인
        bool validPin = false;
        for (int i = 0; i < numPins; i++) {
          if (controlPins[i] == inputPin) {
            pinStates[i] = 1;  // 상태 배열에서 해당 핀을 HIGH로 설정
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

  // 핀 상태를 유지 (상태 배열 기반으로 설정)
  for (int i = 0; i < numPins; i++) {
    digitalWrite(controlPins[i], pinStates[i]);
  }

  delay(2000);  // 2초 간격으로 반복
}
