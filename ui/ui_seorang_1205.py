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

        self.create_start_button()
        
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

    def create_start_button(self):
        """Start 버튼을 만들고 버튼 클릭 시 GUI 시작"""
        start_button = tk.Button(self.window, text="Start", font=self.info_font, command=self.start_app,
                                 relief="solid", bg="skyblue", fg="white")
        start_button.pack(pady=30)

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
            if ser.in_waiting > 0:
                # 시리얼 데이터를 읽음
                line = ser.readline().decode('utf-8').strip()
                print(f"받은 데이터: {line}")
                
                # 온도와 습도 값을 추출하기 위해 정규식 사용
                try:
                    sensor1_pattern = r"Sensor 1 - Temperature:\s*(\d+\.\d+)\s*°C,\s*Humidity:\s*(\d+\.\d+)\s*%"
                    sensor2_pattern = r"Sensor 2 - Temperature:\s*(\d+\.\d+)\s*°C,\s*Humidity:\s*(\d+\.\d+)\s*%"

                    sensor1_match = re.search(sensor1_pattern, line)
                    sensor2_match = re.search(sensor2_pattern, line)
                    
                    if sensor1_match:
                        print(f"Sensor 1 Match: {sensor1_match.group(0)}")  # 성공적으로 매칭된 데이터 출력
                        # 센서 1 데이터 처리
                        temp1 = float(sensor1_match.group(1))
                        humidity1 = float(sensor1_match.group(2))
                                                # 제습 정보 업데이트
                        self.dehumid_info.update({
                            "temp": f"{temp1:.1f}°C",  # 소수점 첫째자리까지 표시
                            "humid": f"{humidity1:.1f}%",  # 소수점 첫째자리까지 표시
                            "status": "동작중" if temp1 >= 18 else "대기중"
                        })

                    else:
                        print("Sensor 1 데이터가 올바르지 않습니다.")  # Sensor 1 데이터 미매칭 처리

                    if sensor2_match:
                        print(f"Sensor 2 Match: {sensor2_match.group(0)}")  # 성공적으로 매칭된 데이터 출력
                        # 센서 2 데이터 처리
                        temp2 = float(sensor2_match.group(1))
                        humidity2 = float(sensor2_match.group(2))
                        self.dehumid_info.update({
                            "temp": f"{temp2:.1f}°C",  # 소수점 첫째자리까지 표시
                            "humid": f"{humidity2:.1f}%",  # 소수점 첫째자리까지 표시
                            "status": "동작중" if temp2 >= 18 else "대기중"
                        })

                    else:
                        print("Sensor 2 데이터가 올바르지 않습니다.")  # Sensor 2 데이터 미매칭 처리

                    # 이곳에서 `temp1`, `humidity1`, `temp2`, `humidity2`를 가지고 후속 작업을 처리

                except ValueError:
                    print("데이터 형식 오류")
                except Exception as e:
                    print(f"오류 발생: {e}")
                
                time.sleep(1)

    def format_time(self, seconds):
        """남은 시간을 '시간:분:초' 형식으로 변환"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_dry_time(self):
        """남은 시간을 1초씩 갱신"""
        if self.dry_info["remaining_time"] > 0:
            self.dry_info["remaining_time"] -= 1
            self.dry_labels["remaining_time_display"].config(
                text=f"남은 시간: {self.format_time(self.dry_info['remaining_time'])}"
            )
            self.window.after(1000, self.update_dry_time)
        else:
            self.dry_info["status"] = "건조 완료"
            self.dry_labels["status"].config(text=f"상태: {self.dry_info['status']}")
            self.show_drying_complete_message()

    def show_drying_complete_message(self):
        """건조 완료 메시지 팝업"""
        messagebox.showinfo("건조 완료", "건조가 끝났습니다!", icon='info')
        self.reset_app()

    def start_app(self):
        """Start 버튼 클릭 후 GUI 시작"""
        # 제습 및 건조 프레임을 담을 컨테이너 프레임
        container_frame = tk.Frame(self.window, bg=self.config.colors["bg"])
        container_frame.pack(side="top", fill="both", expand=True)

        # 제습 및 건조 프레임 생성 및 추가
        self.dehumid_frame = self.make_dehumid_frame(container_frame)
        self.dry_frame = self.make_dry_frame(container_frame)

        # Start 버튼 제거
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        self.update_dry_time()

    def reset_app(self):
        """건조 완료 후 앱을 초기화하고 Start 버튼 화면으로 돌아가기"""
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화", "remaining_time": 5}
        
        for widget in self.window.winfo_children():
            widget.destroy()
        
        self.create_start_button()


    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ShoeCabinetGUI()
    app.run()