import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import time

from picamera2 import Picamera2

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
    def __init__(self, config, data_updater, serial_port):
        self.config = config
        self.data_updater = data_updater
        self.window = self.setup_window()
        self.title_font, self.info_font = self.setup_fonts()
        self.create_start_button()
        self.image_label = None
        self.current_image = None

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
        for key, value in self.data_updater.dehumid_info.items():
            self.dehumid_labels[key] = frame.add_label_to_bottom(
                f"{key}: {value}", font=self.info_font, fg=self.config.colors["text_fg"],
                anchor="w", padding=self.config.paddings["label_left"]
            )
        frame.frame.pack(side="left", fill="both", expand=True)
        return frame.frame

    def make_dry_frame(self, parent):
        frame = SectionFrame(parent, top_color=self.config.colors["dry_bg"], bg_color=self.config.colors["frame_bg"], top_height=50, width=400, height=300)
        self.dry_labels = {}
        frame.add_label_to_top("건조", font=self.title_font, fg=self.config.colors["text_fg"],
                                anchor='center', padding=self.config.paddings["title"])
        for key, value in self.data_updater.dry_info.items():
            self.dry_labels[key] = frame.add_label_to_bottom(
                f"{key}: {value}", font=self.info_font, fg=self.config.colors["text_fg"],
                anchor="e", padding=self.config.paddings["label_right"]
            )

        # 신발 인식하기 버튼을 생성
        self.recognize_button = tk.Button(frame.bottom_frame, text="신발 인식하기", font=self.info_font,
                                        bg=self.config.colors["button_bg"], fg=self.config.colors["button_fg"],
                                        command=self.toggle_recognition)
        self.recognize_button.pack(pady=10)

        frame.frame.pack(side="right", fill="both", expand=True)
        return frame.frame

    def toggle_recognition(self):
        """신발 인식 버튼을 눌렀을 때의 동작"""
        # 신발 인식하기 버튼이 있을 때
        if self.recognize_button['text'] == "신발 인식하기":
            # 기존 버튼 제거
            self.recognize_button.destroy()
            
            # 버튼들을 담을 새로운 프레임 생성
            self.button_frame = tk.Frame(self.dry_frame.winfo_children()[1], bg=self.config.colors["frame_bg"])
            self.button_frame.pack(pady=10)
            
            # 신발 확인 버튼 생성
            self.check_shoe_button = tk.Button(
                self.button_frame,
                text="신발 확인", 
                font=self.info_font,
                bg=self.config.colors["button_bg"], 
                fg=self.config.colors["button_fg"],
                command=self.check_shoe
            )
            self.check_shoe_button.pack(side="left", padx=5)
            
            # 다시 인식하기 버튼 생성
            self.retry_recognition_button = tk.Button(
                self.button_frame,
                text="다시 인식하기", 
                font=self.info_font,
                bg=self.config.colors["button_bg"], 
                fg=self.config.colors["button_fg"],
                command=self.retry_recognition
            )
            self.retry_recognition_button.pack(side="left", padx=5)
    
    def check_shoe(self):
        """신발 확인 버튼을 눌렀을 때의 동작"""
        print("신발 확인 완료!")
        
        try:
            # Picamera2 객체 생성
            picam2 = Picamera2()

            # Still Image Config 생성
            config = picam2.create_still_configuration()
            picam2.configure(config)

            # 카메라 시작
            picam2.start()

            # 잠시 기다려 카메라가 준비되도록 함
            time.sleep(2)

            # 사진 촬영 후 저장
            image_path = './data/fig.jpg'
            picam2.capture_file(image_path)
            print(f"사진이 저장되었습니다: {image_path}")

            # 카메라 종료
            picam2.stop()

        except Exception as e:
            print(f"카메라 촬영 중 오류가 발생했습니다: {e}")

    def retry_recognition(self):
        """다시 인식하기 버튼을 눌렀을 때의 동작"""
        # 기존 버튼들 제거
        self.button_frame.destroy()
        
        # 신발 인식하기 버튼 다시 생성
        self.recognize_button = tk.Button(
            self.dry_frame.winfo_children()[1],  # bottom frame
            text="신발 인식하기", 
            font=self.info_font,
            bg=self.config.colors["button_bg"], 
            fg=self.config.colors["button_fg"],
            command=self.toggle_recognition
        )
        self.recognize_button.pack(pady=10)


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

        self.data_updater.set_update_callbacks(self.update_dehumid_frame, self.update_dry_frame, self.update_image)
        self.data_updater.start()

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
