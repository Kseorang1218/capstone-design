import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import time

import numpy as np

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
    def __init__(self, config, update_handler, serial_port, camera_handler, model_handler):
        self.config = config
        self.update_handler = update_handler
        self.camera_handler = camera_handler
        self.model_handler = model_handler

        self.window = self.setup_window()
        self.title_font, self.info_font = self.setup_fonts()
        self.create_start_button()

        self.prediction_label = None
        self.image_label = None
        self.current_image = None
        self.class_probabilities = None
        self.shoe_types = {0: "부츠", 1: "구두", 2: "슬리퍼", 3: "운동화"}
        self.figs_root = "./figs"
        self.shoe_english_names = {"부츠": "boots", "구두": "shoes", "슬리퍼": "slipper", "운동화": "sneakers"}

        # 시리얼 포트 연결 (아두이노와의 통신)
        self.serial_port = serial_port
        time.sleep(2)  # 아두이노와의 초기 통신을 위해 잠시 대기

    def setup_window(self):
        window = tk.Tk()
        window.title("신발장 상태")
        window.geometry("800x400")
        window.config(bg=self.config.colors["frame_bg"])
        return window

    def setup_fonts(self):
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        info_font = font.Font(family="Arial", size=12)
        return title_font, info_font

    def create_start_button(self):
        start_button = tk.Button(self.window, text="Start", font=self.info_font, command=self.start_app,
                                 relief="solid", bg=self.config.colors["button_bg"], fg=self.config.colors["button_fg"])
        start_button.pack(pady=30)

    def make_dehumid_frame(self, parent):
        frame = SectionFrame(parent, top_color=self.config.colors["dehumid_bg"], bg_color=self.config.colors["frame_bg"], top_height=50, width=400, height=300)
        self.dehumid_labels = {}
        frame.add_label_to_top("제습", font=self.title_font, fg=self.config.colors["text_fg"],
                                anchor='center', padding=self.config.paddings["title"])
        for key, value in self.update_handler.dehumid_info.items():
            self.dehumid_labels[key] = frame.add_label_to_bottom(
                f"{key}: {value}", font=self.info_font, fg=self.config.colors["text_fg"],
                anchor="w", padding=self.config.paddings["label_left"]
            )
        
        # 제습 버튼 프레임 생성
        self.dehumid_button_frame = tk.Frame(frame.bottom_frame, bg=self.config.colors["frame_bg"])
        self.dehumid_button_frame.pack(pady=10)
        
        # 제습 시작 버튼
        self.start_dehumid_button = tk.Button(
            self.dehumid_button_frame,
            text="제습 시작", 
            font=self.info_font,
            bg=self.config.colors["button_bg"], 
            fg=self.config.colors["button_fg"],
            command=self.start_dehumidification
        )
        self.start_dehumid_button.pack(side="left", padx=5)
        
        # 제습 중지 버튼
        self.stop_dehumid_button = tk.Button(
            self.dehumid_button_frame,
            text="제습 중지", 
            font=self.info_font,
            bg=self.config.colors["button_bg"], 
            fg=self.config.colors["button_fg"],
            command=self.stop_dehumidification
        )
        self.stop_dehumid_button.pack(side="left", padx=5)
        
        frame.frame.pack(side="left", fill="both", expand=True)
        return frame.frame

    def make_dry_frame(self, parent):
        frame = SectionFrame(parent, top_color=self.config.colors["dry_bg"], bg_color=self.config.colors["frame_bg"], top_height=50, width=400, height=300)
        self.dry_labels = {}
        frame.add_label_to_top("건조", font=self.title_font, fg=self.config.colors["text_fg"],
                                anchor='center', padding=self.config.paddings["title"])
        for key, value in self.update_handler.dry_info.items():
            self.dry_labels[key] = frame.add_label_to_bottom(
                f"{key}: {value}", font=self.info_font, fg=self.config.colors["text_fg"],
                anchor="e", padding=self.config.paddings["label_right"]
            )

        # 건조 모드 버튼 프레임 생성
        self.dry_mode_button_frame = tk.Frame(frame.bottom_frame, bg=self.config.colors["frame_bg"])
        self.dry_mode_button_frame.pack(pady=10)
        
        # AI 자동 모드 버튼
        self.ai_auto_mode_button = tk.Button(
            self.dry_mode_button_frame,
            text="AI 자동 모드", 
            font=self.info_font,
            bg=self.config.colors["button_bg"], 
            fg=self.config.colors["button_fg"],
            command=self.set_ai_auto_mode
        )
        self.ai_auto_mode_button.pack(side="left", padx=5)
        
        # 수동 모드 버튼
        self.manual_mode_button = tk.Button(
            self.dry_mode_button_frame,
            text="수동 모드", 
            font=self.info_font,
            bg=self.config.colors["button_bg"], 
            fg=self.config.colors["button_fg"],
            command=self.set_manual_mode
        )
        self.manual_mode_button.pack(side="left", padx=5)

        frame.frame.pack(side="right", fill="both", expand=True)
        return frame.frame
    
    def create_button(self, frame, text, command):
        """버튼 생성 및 프레임에 추가"""
        button = tk.Button(
            frame,
            text=text,
            font=self.info_font,
            bg=self.config.colors["button_bg"],
            fg=self.config.colors["button_fg"],
            command=command
        )
        button.pack(side="left", padx=5)
    

    def start_dehumidification(self):
        """제습 시작 버튼을 눌렀을 때의 동작"""
        # 아두이노나 다른 시스템에 제습 시작 신호를 보내는 로직 추가
        print("제습을 시작합니다.")
        # 예: self.serial_port.write(b'START_DEHUMID')

    def stop_dehumidification(self):
        """제습 중지 버튼을 눌렀을 때의 동작"""
        # 아두이노나 다른 시스템에 제습 중지 신호를 보내는 로직 추가
        print("제습을 중지합니다.")
        # 예: self.serial_port.write(b'STOP_DEHUMID')

    def set_ai_auto_mode(self):
        """AI 자동 모드 버튼을 눌렀을 때의 동작"""
        # 기존 버튼들 제거
        self.clear_frame_widgets(self.dry_mode_button_frame)

        # 신발 확인하기 버튼 생성
        self.create_button(
            self.dry_mode_button_frame,
            text="신발 인식하기",
            command=self.toggle_recognition
        )

        # 건조 중지하기 버튼 생성
        self.create_button(
            self.dry_mode_button_frame,
            text="건조 중지하기",
            command=self.stop_drying
        )

        print("AI 자동 모드로 전환합니다.")


    def stop_drying(self):
        """건조 중지 버튼을 눌렀을 때의 동작"""
        print("건조를 중지합니다.")

        # 기존 버튼 제거
        self.clear_frame_widgets(self.dry_mode_button_frame)

        # AI 자동 모드 버튼 복원
        self.create_button(
            self.dry_mode_button_frame,
            text="AI 자동 모드",
            command=self.set_ai_auto_mode
        )

        # 수동 모드 버튼 복원
        self.create_button(
            self.dry_mode_button_frame,
            text="수동 모드",
            command=self.set_manual_mode
        )

    def clear_frame_widgets(self, frame):
        """프레임의 모든 위젯 제거"""
        for widget in frame.winfo_children():
            widget.destroy()

    def echo(self, text):
        print(text)

    def set_manual_mode(self):
        """수동 모드 버튼을 눌렀을 때의 동작"""
        # 수동 모드로 전환하는 로직 추가
        print("수동 모드로 전환합니다.")
        self.clear_frame_widgets(self.dry_mode_button_frame)

        self.create_button(
            self.dry_mode_button_frame,
            text="고무",
            command=lambda: self.echo("고무")
        )

        self.create_button(
            self.dry_mode_button_frame,
            text="면",
            command=lambda: self.echo("면")
        )

        self.create_button(
            self.dry_mode_button_frame,
            text="가죽",
            command=lambda: self.echo("가죽")
        )

        self.create_button(
            self.dry_mode_button_frame,
            text="스웨이드",
            command=lambda: self.echo("스웨이드")
        )
    
    def update_dehumid_frame(self, data):
        for key, value in data.items():
            if key in self.dehumid_labels:
                self.dehumid_labels[key].config(text=f"{key}: {value}")

    def update_dry_frame(self, data):
        for key, value in data.items():
            if key != 'remaining_time' and key in self.dry_labels:
                self.dry_labels[key].config(text=f"{key}: {value}")
            else:
                self.dry_labels[key].config(text=f"{key}: {self.format_time(value)}")


    def toggle_recognition(self):
        """신발 인식 버튼을 눌렀을 때의 동작"""
        # 신발 인식하기 버튼이 있을 때
        try:
            image_path = self.camera_handler.capture_and_crop_image()
            if image_path:
                self.class_probabilities = self.model_handler.predict_shoe_type(image_path)
                predicted_class = np.argmax(self.class_probabilities)
                predicted_shoe_type = self.shoe_types.get(predicted_class, "알 수 없음")  # 예측된 신발 유형
                self.update_handler.dry_info["shoes_type"] = predicted_shoe_type
                self.update_handler.image_path = f'{self.figs_root}/{self.shoe_english_names[predicted_shoe_type]}.png'
                print(self.class_probabilities)
        except Exception as e:
            print(f"신발 확인 중 오류가 발생했습니다: {e}")

        self.clear_frame_widgets(self.dry_mode_button_frame)
        
        # 신발 확인 버튼 생성
        self.create_button(
            self.dry_mode_button_frame,
            text="신발 확인",
            command=self.check_shoe
        )

        self.create_button(
            self.dry_mode_button_frame,
            text="다시 인식하기", 
            command=self.retry_recognition
        )

    def check_shoe(self):
        """신발 확인 버튼을 눌렀을 때의 동작"""

        self.clear_frame_widgets(self.dry_mode_button_frame)
        self.echo(self.update_handler.dry_info["shoes_type"])

    def retry_recognition(self):
        """다시 인식하기 버튼을 눌렀을 때의 동작"""
        sorted_indices = np.argsort(self.class_probabilities)[::-1]
        second_highest_class = sorted_indices[1]
        predicted_shoe_type = self.shoe_types.get(second_highest_class, "알 수 없음")
        self.update_handler.dry_info["shoes_type"] = predicted_shoe_type
        self.update_handler.image_path = f'{self.figs_root}/{self.shoe_english_names[predicted_shoe_type]}.png'
        self.echo(self.update_handler.dry_info["shoes_type"])

    def start_app(self):
        container_frame = tk.Frame(self.window, bg=self.config.colors["frame_bg"])
        container_frame.pack(side="top", fill="both", expand=True)
        self.dehumid_frame = self.make_dehumid_frame(container_frame)
        self.dry_frame = self.make_dry_frame(container_frame)

        # 입력칸 추가
        self.pin_entry_label = tk.Label(self.window, text="Control Pin:", font=self.info_font, bg=self.config.colors["frame_bg"])
        self.pin_entry_label.pack(pady=10)

        self.pin_entry = tk.Entry(self.window, font=self.info_font)
        self.pin_entry.pack(pady=10)

        # "보내기" 버튼 추가
        self.send_button = tk.Button(self.window, text="Send", font=self.info_font, command=self.send_to_arduino)
        self.send_button.pack(pady=10)

        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button) and widget != self.send_button:
                widget.destroy()

        self.update_handler.set_update_callbacks(self.update_dehumid_frame, self.update_dry_frame, self.update_image)
        self.update_handler.start()

    def format_time(self, seconds):
        """남은 시간을 '시간:분:초' 형식으로 변환"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_image(self, image_path):
        """이미지 경로가 변경되었을 때 호출되는 콜백"""
        if self.current_image != image_path:
            try:
                self.current_image = image_path
                img = Image.open(image_path)  # 이미지 열기
                img = img.resize((100, 100), Image.LANCZOS)  # 원하는 크기로 조정 (필요에 따라 조정)
                img_tk = ImageTk.PhotoImage(img)  # Tkinter에서 사용할 수 있는 형식으로 변환
                
                self.image_label = tk.Label(self.window, image=img_tk, bg=self.config.colors["frame_bg"])  # Label에 이미지 설정
                self.image_label.image = img_tk  # 참조를 유지해야 이미지가 표시됩니다.
                self.image_label.place(x=400, y=100)  # 원하는 위치에 배치 (여기서는 위쪽에 배치)

            except Exception as e:
                print(f"이미지를 불러오는 중 오류가 발생했습니다: {e}")

    def send_to_arduino(self):
        """입력된 값을 아두이노로 전송"""
        pin = self.pin_entry.get().strip()  # 사용자가 입력한 값
        if pin.isdigit():
            pin = int(pin)
            self.serial_port.write(str(pin).encode())  # 입력한 값을 시리얼로 전송
            print(f"Sent pin {pin} to Arduino.")
        else:
            print("Invalid pin number.")

    def run(self):
        self.window.mainloop()
