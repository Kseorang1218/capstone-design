import serial
import json

class SerialComm:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, timeout=1, bytesize=8):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout, bytesize=bytesize)
            print(f"Serial port {port} opened successfully!")
        except serial.SerialException as e:
            print(f"Failed to open serial port {port}: {e}")
            self.ser = None
        self.data = {}

    def read_data(self):
        if self.ser and self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').strip()
            # print(f"받은 데이터: {line}")
            return line
        return None

    def parse_data(self, line):
        try:
            json_data = json.loads(line)  # JSON 문자열 파싱
            self.data = {
                "sensor1": json_data.get("sensor1", {}),
                "sensor2": json_data.get("sensor2", {}),
                "sensor3": json_data.get("sensor3", {})
            }
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
        except Exception as e:
            print(f"데이터 처리 오류: {e}")

    def get_data(self):
        return self.data