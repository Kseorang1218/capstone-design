# ShoeCabinetGUI

import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import threading  
import time

class SectionFrame:
    """GUI의 각 구역을 구성하는 프레임 클래스"""
    def __init__(self, parent, top_color, bg_color="white", top_height=50, width=250, height=300):
        # 전체 프레임
        self.frame = tk.Frame(parent, width=width, height=height, bg=bg_color)
        self.frame.pack(side="top", fill="both", expand=True)
        self.frame.grid_propagate(False)

        # 상단 프레임 (색상은 외부에서 전달받음)
        self.top_frame = tk.Frame(self.frame, height=top_height, bg=top_color)
        self.top_frame.pack(side="top", fill="x")

        # 하단 프레임 (기본적으로 흰색 배경)
        self.bottom_frame = tk.Frame(self.frame, bg=bg_color)
        self.bottom_frame.pack(side="top", fill="both", expand=True)

    def add_label_to_bottom(self, text, font, fg, anchor, padding):
        """하단 영역에 라벨 추가"""
        label = tk.Label(self.bottom_frame, text=text, bg=self.bottom_frame["bg"], font=font, fg=fg, anchor=anchor)
        label.pack(pady=padding[0], padx=padding[1], fill="x")
        return label

    def add_label_to_top(self, text, font, fg, anchor, padding):
        """상단 영역에 라벨 추가 (배경색도 설정된 상태에서 텍스트를 배치)"""
        label = tk.Label(self.top_frame, text=text, font=font, fg=fg, anchor=anchor, bg=self.top_frame["bg"])
        label.pack(pady=padding[0], padx=padding[1], fill="x")
        return label



class ShoeCabinetGUI:
    def __init__(self, config, serial_comm):
        self.config = config
        self.serial_comm = serial_comm  # SerialComm 객체를 전달받음
        self.window = self.setup_window()
        self.title_font, self.info_font = self.setup_fonts()

        self.dehumid_info = {"temp": "25°C", "humid": "40%"}
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화", "remaining_time": 1000}
        
        self.create_start_button()

        # 데이터를 주기적으로 업데이트하는 쓰레드 시작
        self.update_thread = threading.Thread(target=self.update_data, daemon=True)
        self.update_thread.start()

    def setup_window(self):
        window = tk.Tk()
        window.title("신발장 상태")
        window.geometry("800x400")
        window.config(bg=self.config.colors["frame_bg"])  # 전체 배경색 설정
        return window

    def setup_fonts(self):
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        info_font = font.Font(family="Arial", size=12)
        return title_font, info_font

    def create_start_button(self):
        """Start 버튼을 만들고 버튼 클릭 시 GUI 시작"""
        start_button = tk.Button(self.window, text="Start", font=self.info_font, command=self.start_app,
                                 relief="solid", bg=self.config.colors["button_bg"], fg=self.config.colors["button_fg"])
        start_button.pack(pady=30)

    def make_dehumid_frame(self, parent):
        frame = SectionFrame(parent, top_color=self.config.colors["dehumid_bg"], bg_color=self.config.colors["frame_bg"], top_height=50, width=400, height=300)
        self.dehumid_labels = {}
        
        frame.add_label_to_top("제습", font=self.title_font, fg=self.config.colors["text_fg"],
                                anchor='center', padding=self.config.paddings["title"])
        
        for key, value in self.dehumid_info.items():
            self.dehumid_labels[key] = frame.add_label_to_bottom(
                f"{key}: {value}", font=self.info_font, fg=self.config.colors["text_fg"],
                anchor="w", padding=self.config.paddings["label_left"]
            )
        frame.frame.pack(side="left", fill="both", expand=True)  # 가로 배치 (왼쪽)
        return frame.frame

    def make_dry_frame(self, parent):
        frame = SectionFrame(parent, top_color=self.config.colors["dry_bg"], bg_color=self.config.colors["frame_bg"], top_height=50, width=400, height=300)
        self.dry_labels = {}
        
        frame.add_label_to_top("건조", font=self.title_font, fg=self.config.colors["text_fg"],
                                anchor='center', padding=self.config.paddings["title"])
        
        for key, value in self.dry_info.items():
            if key != "remaining_time":
                self.dry_labels[key] = frame.add_label_to_bottom(
                    f"{key}: {value}", font=self.info_font, fg=self.config.colors["text_fg"],
                    anchor="e", padding=self.config.paddings["label_right"]  # 오른쪽 정렬
                )
        
        self.dry_labels["remaining_time_display"] = frame.add_label_to_bottom(
            f"남은 시간: {self.format_time(self.dry_info['remaining_time'])}",
            font=self.info_font, fg=self.config.colors["text_fg"],
            anchor="e", padding=self.config.paddings["label_right"]  # 오른쪽 정렬
        )
        self.add_image_to_frame(frame.frame)
        frame.frame.pack(side="right", fill="both", expand=True)  # 가로 배치 (오른쪽)
        return frame.frame

    def update_data(self):
        """시리얼 데이터를 주기적으로 읽어오는 함수"""
        while True:
            try:
                # 시리얼 데이터 읽기
                line = self.serial_comm.read_data()
                if line:
                    # 시리얼 데이터 파싱 및 가져오기
                    self.serial_comm.parse_data(line)
                    data = self.serial_comm.get_data()  # 수신된 데이터를 파싱한 결과
                    
                    # Debug: 받은 데이터 확인
                    print(f"수신 데이터: {data}")

                    # sensor1 데이터 -> 제습 프레임 업데이트
                    if "sensor1" in data:
                        sensor1 = data["sensor1"]
                        self.dehumid_info["temp"] = f"{sensor1['temperature']}°C"
                        self.dehumid_info["humid"] = f"{sensor1['humidity']}%"
                        # print(f"제습 정보 업데이트: {self.dehumid_info}")  # Debug
                        self.update_dehumid_frame()  # UI 업데이트

                    # sensor2 데이터 -> 건조 프레임 업데이트
                    if "sensor2" in data:
                        sensor2 = data["sensor2"]
                        self.dry_info["temp"] = f"{sensor2['temperature']}°C"
                        self.dry_info["humid"] = f"{sensor2['humidity']}%"
                        # print(f"건조 정보 업데이트: {self.dry_info}")  # Debug
                        self.update_dry_frame()  # UI 업데이트
                    
                    # 1초마다 데이터 확인
                    time.sleep(1)
            except Exception as e:
                print(f"데이터 업데이트 중 오류 발생: {e}")

    def update_dehumid_frame(self):
        """제습 프레임 정보 업데이트"""
        for key, value in self.dehumid_info.items():
            if key in self.dehumid_labels:
                self.dehumid_labels[key].config(text=f"{key}: {value}")
                # print(f"제습 프레임 업데이트: {key} -> {value}")  # Debug 출력

    def update_dry_frame(self):
        """건조 프레임 정보 업데이트"""
        for key, value in self.dry_info.items():
            if key in self.dry_labels:
                self.dry_labels[key].config(text=f"{key}: {value}")
                # print(f"건조 프레임 업데이트: {key} -> {value}")  # Debug 출력

    def add_image_to_frame(self, frame, size=(100, 100), position=(30, 100)):
        try:
            # 이미지 로드 및 크기 조정
            image = Image.open(self.config.shoes_pic_path)
            image = image.resize(size, Image.LANCZOS)
            tk_image = ImageTk.PhotoImage(image)

            # 이미지 라벨 생성
            image_label = tk.Label(frame, image=tk_image, bg=self.config.colors["frame_bg"])
            image_label.image = tk_image

            # 이미지 배치: place 사용
            image_label.place(x=position[0], y=position[1])  # 지정된 (x, y) 위치에 배치
        except Exception as e:
            print(f"이미지 로드 실패: {e}")


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
        container_frame = tk.Frame(self.window, bg=self.config.colors["frame_bg"])
        container_frame.pack(side="top", fill="both", expand=True)

        # 제습 및 건조 프레임 생성 및 추가
        self.dehumid_frame = self.make_dehumid_frame(container_frame)
        self.dry_frame = self.make_dry_frame(container_frame)

        # Start 버튼 제거
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        # 이미 실행 중인 쓰레드가 있으면 새로 생성하지 않음
        if not hasattr(self, "update_thread") or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.update_data, daemon=True)
            self.update_thread.start()

        # 건조 시간 업데이트 시작
        self.update_dry_time()


    def reset_app(self):
        """건조 완료 후 앱을 초기화하고 Start 버튼 화면으로 돌아가기"""
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화", "remaining_time": 1000}
        
        for widget in self.window.winfo_children():
            widget.destroy()
        
        self.create_start_button()

    def run(self):
        self.window.mainloop()
