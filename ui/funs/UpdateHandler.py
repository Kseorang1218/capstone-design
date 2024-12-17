import threading
import time
import csv
from datetime import datetime

class UpdateHandler:
    """시리얼 데이터 업데이트를 관리하는 클래스"""
    def __init__(self, serial_comm, image_path, model_handler, csv_name):
        self.serial_comm = serial_comm
        self.dehumid_info = {"temp": "25°C", "humid": "40%", "status": "대기중"}
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "대기중", "shoes_type": "운동화", "remaining_time": 999}
        self.image_path = image_path  # 이미지 경로 추가
        self.callbacks = {"dehumid": None, "dry": None, "image": None}  # 이미지 업데이트 콜백 추가
        self.data = {}
        self.csv_file = csv_name
        self.model_handler = model_handler  # ModelHandler 인스턴스를 전달받음
        self.init_csv_file()
        self.heating_on = False  # 히터가 켜져 있는지 여부
        self.drying_stopped = False  # 건조 중지 여부
        self.target_temp = None

    def init_csv_file(self):
        # CSV 파일 초기화: 파일이 없으면 헤더를 추가
        try:
            with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Sensor1_Temperature", "Sensor1_Humidity", "Sensor2_Temperature", "Sensor2_Humidity",  "Sensor3_Temperature", "Sensor3_Humidity"])
            print(f"{self.csv_file} initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize CSV file: {e}")

    def save_to_csv(self):
        # 센서 데이터를 CSV 파일에 저장
        if "sensor1" in self.data:
            sensor1 = self.data["sensor1"]
            temperature1 = sensor1.get("temperature", None)
            humidity1 = sensor1.get("humidity", None)

            sensor2 = self.data["sensor2"]
            temperature2 = sensor2.get("temperature", None)
            humidity2 = sensor2.get("humidity", None)

            sensor3 = self.data["sensor3"]
            temperature3 = sensor3.get("temperature", None)
            humidity3 = sensor3.get("humidity", None)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, temperature1, humidity1, temperature2, humidity2, temperature3, humidity3])
            except Exception as e:
                print(f"Failed to save data to CSV: {e}")

    def set_update_callbacks(self, dehumid_callback, dry_callback, image_callback):
        """UI 업데이트를 위한 콜백 함수 등록"""
        self.callbacks["dehumid"] = dehumid_callback
        self.callbacks["dry"] = dry_callback
        self.callbacks["image"] = image_callback  # 이미지 업데이트 콜백 등록

    def start(self):
        """데이터 업데이트를 주기적으로 수행하는 쓰레드 시작"""
        if self.serial_comm:  # serial_comm이 None이 아닌 경우에만 데이터 업데이트 시작
            self.update_thread = threading.Thread(target=self.update_data_loop, daemon=True)
            self.update_thread.start()

            # self.update_dry_time()  # 남은 시간 갱신 시작
        else:
            print("Serial communication not initialized. Skipping data update.")

    def update_data_loop(self):
        """데이터를 주기적으로 가져와 콜백을 호출"""
        while self.serial_comm:  # serial_comm이 None이 아니면 데이터를 계속 읽음
            try:
                # 시리얼 데이터 읽기
                line = self.serial_comm.read_data()
                if line:
                    self.serial_comm.parse_data(line)
                    data = self.serial_comm.get_data()

                    # Debug: 받은 데이터 확인
                    # print(f"수신 데이터: {data}")

                    # sensor3 데이터 -> 제습 프레임 업데이트
                    if "sensor1" in data:
                        sensor1 = data["sensor1"]
                        self.dehumid_info["temp"] = f"{sensor1['temperature']}°C"
                        self.dehumid_info["humid"] = f"{sensor1['humidity']}%"
                        if self.callbacks["dehumid"]:
                            self.callbacks["dehumid"](self.dehumid_info)

                    # sensor2 데이터 -> 건조 프레임 업데이트
                    if "sensor2" in data:
                        sensor2 = data["sensor2"]
                        self.dry_info["temp"] = f"{sensor2['temperature']}°C"
                        self.dry_info["humid"] = f"{sensor2['humidity']}%"
                        if self.callbacks["dry"]:
                            self.callbacks["dry"](self.dry_info)

                    self.check_shoetype()

                    self.data = data
                    self.save_to_csv()
                    # 1초 대기
                    time.sleep(1)

                    self.check_heating()
                    self.update_dry_time()  # 남은 시간 갱신 시작

            except Exception as e:
                print(f"데이터 업데이트 중 오류 발생: {e}")

    def check_shoetype(self):
        # 이미지 경로 업데이트 및 신발 유형 예측
        if self.callbacks["dry"]:
            self.callbacks["dry"](self.dry_info)  # UI 갱신을 위한 콜백 호출

        if self.callbacks["image"]:
            self.callbacks["image"](self.image_path)  # 이미지 경로를 업데이트하는 콜백 호출

    def update_image_path(self, new_image_path):
        """이미지 경로 업데이트 및 콜백 호출"""
        self.image_path = new_image_path
        if self.callbacks["image"]:
            self.callbacks["image"](self.image_path)  # 이미지 경로를 업데이트하는 콜백 호출

    def update_dry_time(self):
        """남은 시간을 1초씩 갱신"""
        if self.dry_info["remaining_time"] > 0 and not self.drying_stopped:
            self.dry_info["remaining_time"] -= 1
            if self.callbacks["dry"]:
                self.callbacks["dry"](self.dry_info)  # UI 갱신을 위한 콜백 호출
        else:
            self.dry_info["status"] = "건조 완료"
            if self.callbacks["dry"]:
                self.callbacks["dry"](self.dry_info)  # 상태 변경 후 UI 갱신
            self.target_temp = None

    def check_heating(self):
        """히터 제어 및 온도 체크"""
        if self.target_temp:
            current_temp = float(self.dry_info["temp"].replace("°C", ""))

            if current_temp > self.target_temp and self.heating_on:
                self.heating_on = False
                print("온도가 너무 높아서 히터를 끕니다.")
                command = "stop " + " ".join(map(str, [8]))
                self.serial_comm.ser.write(command.encode())
                print(f"Sent stop command for pins {[8]} to Arduino.")
                threading.Timer(60, self.check_temperature).start()  # 1분 후 온도 다시 확인
            elif current_temp < self.target_temp and not self.heating_on:
                self.heating_on = True
                print("온도가 낮아서 히터를 켭니다.")
                for pin in [8]:
                    self.serial_comm.ser.write(str(pin).encode())
                    print(f"Sent pin {pin} to Arduino.")
                    time.sleep(5)  # 각 핀 전송 후 1초 대기

    def check_temperature(self):
        """히터 끄고 1분 후 온도 재확인"""
        if self.target_temp:
            current_temp = float(self.dry_info["temp"].replace("°C", ""))
            if current_temp > self.target_temp:
                print("온도가 여전히 너무 높습니다. 다시 1분 기다립니다.")
                threading.Timer(60, self.check_temperature).start()
            else:
                print("온도가 적정 범위에 도달했습니다. 히터를 다시 켭니다.")
                self.heating_on = True
                for pin in [8]:
                    self.serial_comm.ser.write(str(pin).encode())
                    print(f"Sent pin {pin} to Arduino.")
                    time.sleep(5)  # 각 핀 전송 후 1초 대기
