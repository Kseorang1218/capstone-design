import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import serial
import json
import threading
import time
import re  # 정규 표현식 사용

# 시리얼 통신 설정
ser = serial.Serial(
    port='/dev/ttyACM0',  # 아두이노가 연결된 포트
    baudrate=9600,
    timeout=1
)

# 스타일 설정
COLORS = {
    "dehumid_bg": "lightblue",
    "dehumid_fg": "blue",
    "dehumid_text_fg": "navy",
    "dry_bg": "lightcoral",
    "dry_fg": "darkred",
    "dry_text_fg": "maroon"
}

PADDINGS = {
    "title": (15, 5),
    "label_left": (3, (10, 0)),
    "label_right": (3, (0, 10))
}

class ShoeCabinetGUI:
    def __init__(self):
        self.window = self.setup_window()
        self.title_font, self.info_font = self.setup_fonts()
        
        # 데이터 초기화
        self.dehumid_info = {"temp": "25°C", "humid": "40%", "status": "대기중"}
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화"}
        
        # 프레임 생성
        self.dehumid_frame = self.make_dehumid_frame()
        self.dry_frame = self.make_dry_frame()
        
        # 데이터 업데이트 쓰레드 시작
        self.update_thread = threading.Thread(target=self.update_data, daemon=True)
        self.update_thread.start()

    def setup_window(self):
        window = tk.Tk()
        window.title("신발장 상태")
        window.geometry("500x320")
        return window

    def setup_fonts(self):
        title_font = font.Font(family="Helvetica", size=14, weight="bold")
        info_font = font.Font(family="Arial", size=10)
        return title_font, info_font

    def create_section_frame(self, bg_color, side):
        frame = tk.Frame(self.window, bg=bg_color, width=250, height=300)
        frame.pack(side=side, fill="both", expand=True)
        return frame

    def create_label(self, frame, text, bg, font, fg, anchor, padding):
        label = tk.Label(frame, text=text, bg=bg, font=font, fg=fg, anchor=anchor)
        label.pack(pady=padding[0], padx=padding[1], fill="x")
        return label

    def make_dehumid_frame(self):
        frame = self.create_section_frame(COLORS["dehumid_bg"], "left")
        self.dehumid_labels = {}
        
        # 제목 라벨
        self.create_label(frame, "제습", COLORS["dehumid_bg"], self.title_font, 
                         COLORS["dehumid_fg"], 'center', PADDINGS["title"])
        
        # 정보 라벨들
        for key in self.dehumid_info.keys():
            self.dehumid_labels[key] = self.create_label(
                frame, f"{key}: {self.dehumid_info[key]}", 
                COLORS["dehumid_bg"], self.info_font,
                COLORS["dehumid_text_fg"], "w", PADDINGS["label_left"]
            )
        return frame

    def make_dry_frame(self):
        frame = self.create_section_frame(COLORS["dry_bg"], "right")
        self.dry_labels = {}
        
        # 제목 라벨
        self.create_label(frame, "건조", COLORS["dry_bg"], self.title_font,
                         COLORS["dry_fg"], 'center', PADDINGS["title"])
        
        # 정보 라벨들
        for key in self.dry_info.keys():
            self.dry_labels[key] = self.create_label(
                frame, f"{key}: {self.dry_info[key]}", 
                COLORS["dry_bg"], self.info_font,
                COLORS["dry_text_fg"], "e", PADDINGS["label_right"]
            )
            
        # 이미지 추가
        self.add_image_to_frame(frame)
        return frame

    def add_image_to_frame(self, frame, size=(60, 60), padding=(70, 0)):
        try:
            image = Image.open("./pictures/running_shoe.png")
            image = image.resize(size, Image.LANCZOS)
            tk_image = ImageTk.PhotoImage(image)
            image_label = tk.Label(frame, image=tk_image, bg=COLORS["dry_bg"])
            image_label.image = tk_image
            image_label.pack(pady=padding)
        except Exception as e:
            print(f"이미지 로드 실패: {e}")

    def update_labels(self):
        # 제습 영역 라벨 업데이트
        for key, label in self.dehumid_labels.items():
            label.config(text=f"{key}: {self.dehumid_info[key]}")
        
        # 건조 영역 라벨 업데이트
        for key, label in self.dry_labels.items():
            label.config(text=f"{key}: {self.dry_info[key]}")

    def update_data(self):
        while True:
            try:
                if ser.in_waiting > 0:  # 시리얼 데이터가 들어오면
                    # 시리얼 데이터 한 줄 읽기
                    line = ser.readline().decode('utf-8').strip()
                    print(f"받은 데이터: {line}")  # 데이터가 정상적으로 수신되는지 확인
                    
                    # 온도와 습도를 추출하기 위한 정규 표현식
                    temp_match = re.search(r'Temperature:\s*([0-9.]+)', line)
                    humid_match = re.search(r'Humidity:\s*([0-9.]+)', line)

                    if temp_match and humid_match:
                        temp = float(temp_match.group(1))  # 온도 추출
                        humidity = float(humid_match.group(1))  # 습도 추출
                        
                        # 제습 정보 업데이트
                        self.dehumid_info.update({
                            "temp": f"{temp:.1f}°C",  # 소수점 첫째자리까지 표시
                            "humid": f"{humidity:.1f}%",  # 소수점 첫째자리까지 표시
                            "status": "동작중" if temp >= 18 else "대기중"
                        })
                        
                        # GUI 업데이트 (메인 쓰레드에서 실행)
                        self.window.after(0, self.update_labels)  # 메인 쓰레드에서 실행
                    else:
                        print("잘못된 데이터 형식")

                time.sleep(0.1)  # CPU 사용량 감소를 위한 짧은 대기

            except Exception as e:
                print(f"데이터 업데이트 오류: {e}")
                time.sleep(1)


    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ShoeCabinetGUI()
    app.run()