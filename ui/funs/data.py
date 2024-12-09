import threading  
import time
import csv
from datetime import datetime

class UpdateData:
    """시리얼 데이터 업데이트를 관리하는 클래스"""
    def __init__(self, serial_comm, image_path):
        self.serial_comm = serial_comm
        self.dehumid_info = {"temp": "25°C", "humid": "40%"}
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화", "remaining_time": 999999999}
        self.image_path = image_path  # 이미지 경로 추가
        self.callbacks = {"dehumid": None, "dry": None, "image": None}  # 이미지 업데이트 콜백 추가
        self.data = {}
        self.csv_file = "sensor_data_withpeltire.csv"
        self.init_csv_file()

    def init_csv_file(self):
        # CSV 파일 초기화: 파일이 없으면 헤더를 추가
        try:
            with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Sensor1_Temperature", "Sensor1_Humidity"])
            print(f"{self.csv_file} initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize CSV file: {e}")

    def save_to_csv(self):
        # 센서 데이터를 CSV 파일에 저장
        if "sensor1" in self.data:
            sensor1 = self.data["sensor1"]
            temperature = sensor1.get("temperature", None)
            humidity = sensor1.get("humidity", None)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, temperature, humidity])
                print("Data saved to CSV.")
            except Exception as e:
                print(f"Failed to save data to CSV: {e}")

    def set_update_callbacks(self, dehumid_callback, dry_callback, image_callback):
        """UI 업데이트를 위한 콜백 함수 등록"""
        self.callbacks["dehumid"] = dehumid_callback
        self.callbacks["dry"] = dry_callback
        self.callbacks["image"] = image_callback  # 이미지 업데이트 콜백 등록

    def start(self):
        """데이터 업데이트를 주기적으로 수행하는 쓰레드 시작"""
        self.update_thread = threading.Thread(target=self.update_data_loop, daemon=True)
        self.update_thread.start()

        self.update_dry_time()  # 남은 시간 갱신 시작

    def update_data_loop(self):
        """데이터를 주기적으로 가져와 콜백을 호출"""
        while True:
            try:
                # 시리얼 데이터 읽기
                line = self.serial_comm.read_data()
                if line:
                    self.serial_comm.parse_data(line)
                    data = self.serial_comm.get_data()

                    # Debug: 받은 데이터 확인
                    print(f"수신 데이터: {data}")

                    # sensor1 데이터 -> 제습 프레임 업데이트
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

                    # 이미지 경로 업데이트 예시
                    if self.callbacks["image"]:
                        self.callbacks["image"](self.image_path)  # 이미지 경로를 업데이트하는 콜백 호출
                    self.data = data
                    self.save_to_csv()
                    # 1초 대기
                    time.sleep(1)
            except Exception as e:
                print(f"데이터 업데이트 중 오류 발생: {e}")

    def update_image_path(self, new_image_path):
        """이미지 경로 업데이트 및 콜백 호출"""
        self.image_path = new_image_path
        if self.callbacks["image"]:
            self.callbacks["image"](self.image_path)  # 이미지 경로를 업데이트하는 콜백 호출

    def update_dry_time(self):
        """남은 시간을 1초씩 갱신"""
        if self.dry_info["remaining_time"] > 0:
            self.dry_info["remaining_time"] -= 1
            if self.callbacks["dry"]:
                self.callbacks["dry"](self.dry_info)  # UI 갱신을 위한 콜백 호출
            # 1초 후 다시 호출 (재귀적 호출이 아니라 Timer로 비동기적 갱신)
            threading.Timer(1, self.update_dry_time).start()  # 1초 후 다시 갱신
        else:
            self.dry_info["status"] = "건조 완료"
            if self.callbacks["dry"]:
                self.callbacks["dry"](self.dry_info)  # 상태 변경 후 UI 갱신