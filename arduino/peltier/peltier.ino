#include "dht11.h"

dht11 DHT11;
#define DHT11PIN 2

void setup() {
  Serial.begin(9600);
  pinMode(3, OUTPUT);
}

void loop() {
  int chk = DHT11.read(DHT11PIN);

  float temp = DHT11.temperature;
  float humidity = DHT11.humidity;

  // 온도와 습도를 소수점 이하 한 자리로 출력
  Serial.print("Temperature: ");
  Serial.print(temp, 1);  // 소수점 1자리까지 출력
  Serial.print(" °C, ");

  Serial.print("Humidity: ");
  Serial.print(humidity, 1);  // 소수점 1자리까지 출력
  Serial.println(" %");

  // 펠티어 모듈 제어
  if(temp >= 18) {
    digitalWrite(3, HIGH);  // 온도가 18도 이상이면 펠티어 모듈 활성화
  } else {
    digitalWrite(3, LOW);   // 온도가 18도 미만이면 펠티어 모듈 비활성화
  }

  delay(2000);  // 2초 간격으로 반복
}
