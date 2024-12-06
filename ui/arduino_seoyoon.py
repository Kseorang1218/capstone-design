import tkinter as tk
from tkinter import font
import serial
import time

# 시리얼 포트 설정
SERIAL_PORT = '/dev/ttyACM0'  # 아두이노가 연결된 포트
BAUD_RATE = 9600
print(arduino.is_open)  # True여야 합니다.
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(arduino.is_open)  # True여야 합니다.
    time.sleep(2)  # 포트 초기화 대기
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    arduino = None

# 아두이노 명령 전송 함수
def send_command_to_arduino(command):
    if arduino and arduino.is_open:
        try:
            arduino.write(f"{command}\n".encode())
            print(f"Sent to Arduino: {command}")
        except Exception as e:
            print(f"Error sending command: {e}")
    else:
        print("Arduino is not connected.")

# 첫 번째 화면 (Start 버튼)
def show_start_screen():
    # 기존 화면 초기화
    clear_frame()

    def start_button_action():
        send_command_to_arduino("START")  # START 명령 전송
        status_label.config(text="START command sent to Arduino.")
        show_pin_entry_screen()  # 다음 화면으로 이동

    # 새 레이블 생성
    global status_label
    status_label = tk.Label(root, text="", font=custom_font)
    status_label.pack(pady=10)

    # Start 버튼 추가
    start_button = tk.Button(root, text="Start", font=custom_font, command=start_button_action, height=2, width=10)
    start_button.pack(pady=20)

# 두 번째 화면 (핀 입력 및 상태 버튼)
def show_pin_entry_screen():
    clear_frame()

    def send_pin_number():
        pin_number = pin_entry.get().strip()
        if pin_number.isdigit():
            send_command_to_arduino(pin_number)  # 핀 번호 전송
            pin_status_label.config(text=f"Pin {pin_number} set to HIGH.")
        else:
            pin_status_label.config(text="Invalid pin number. Enter a valid number.")

    # 새 레이블 생성
    global pin_status_label
    pin_status_label = tk.Label(root, text="", font=custom_font)
    pin_status_label.pack(pady=5)

    # 핀 번호 입력 UI 추가
    tk.Label(root, text="Enter the pin number:", font=custom_font).pack(pady=10)
    pin_entry = tk.Entry(root, font=custom_font, width=10)
    pin_entry.pack(pady=5)

    send_pin_button = tk.Button(root, text="Set Pin", font=custom_font, command=send_pin_number)
    send_pin_button.pack(pady=10)

    # 제습 및 고온 버튼 추가
    dehumidify_button = tk.Button(root, text="제습", font=custom_font, height=2, width=10)
    dehumidify_button.pack(side="left", padx=20, pady=20)

    high_temp_button = tk.Button(root, text="고온", font=custom_font, height=2, width=10)
    high_temp_button.pack(side="right", padx=20, pady=20)

# 프레임 초기화 함수
def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

# Tkinter UI 설정
root = tk.Tk()
root.title("Arduino Control")
custom_font = font.Font(size=14)

# 공용 레이블 초기화
status_label = None
pin_status_label = None

# 첫 번째 화면 표시
show_start_screen()

# Tkinter 이벤트 루프 실행
root.mainloop()

# 프로그램 종료 시 시리얼 포트 닫기
if arduino and arduino.is_open:
    arduino.close()
