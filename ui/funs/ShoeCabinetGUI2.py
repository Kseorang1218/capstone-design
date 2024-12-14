import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import time
import numpy as np

class FontManager:
    """글꼴 관리를 위한 클래스"""
    def __init__(self, title_family="Helvetica", title_size=16, 
                 info_family="Arial", info_size=12):
        self.title_family = title_family
        self.title_size = title_size
        self.info_family = info_family
        self.info_size = info_size
        self._title_font = None
        self._info_font = None

    @property
    def title_font(self):
        if not self._title_font:
            self._title_font = font.Font(family=self.title_family, size=self.title_size, weight="bold")
        return self._title_font

    @property
    def info_font(self):
        if not self._info_font:
            self._info_font = font.Font(family=self.info_family, size=self.info_size)
        return self._info_font


class BaseFrame:
    """기본 프레임 클래스"""
    def __init__(self, parent, config, title, top_color, font_manager):
        self.config = config
        self.font_manager = font_manager
        
        self.frame = tk.Frame(parent, width=400, height=300, bg=config.colors["frame_bg"])
        self.frame.pack(side="left", fill="both", expand=True)
        self.frame.grid_propagate(False)

        # 상단 프레임
        self.top_frame = tk.Frame(self.frame, height=50, bg=top_color)
        self.top_frame.pack(side="top", fill="x")

        # 하단 프레임
        self.bottom_frame = tk.Frame(self.frame, bg=config.colors["frame_bg"])
        self.bottom_frame.pack(side="top", fill="both", expand=True)

        # 버튼 프레임 (라벨 아래쪽에 위치)
        self.button_frame = tk.Frame(self.bottom_frame, bg=config.colors["frame_bg"])
        self.button_frame.pack(side="bottom", pady=10)

        # 제목 추가
        self.add_title(title)

    def add_title(self, title):
        """프레임 상단에 제목 추가"""
        label = tk.Label(
            self.top_frame, 
            text=title, 
            font=self.font_manager.title_font, 
            fg=self.config.colors["text_fg"], 
            bg=self.top_frame["bg"],
            anchor='center'
        )
        label.pack(pady=self.config.paddings["title"][0], padx=self.config.paddings["title"][1])

    def create_button(self, text, command):
        """버튼 생성 및 추가"""
        button = tk.Button(
            self.button_frame,
            text=text,
            font=self.font_manager.info_font,
            bg=self.config.colors["button_bg"],
            fg=self.config.colors["button_fg"],
            command=command
        )
        button.pack(side="left", padx=5)

    def clear_buttons(self):
        """모든 버튼 제거"""
        for widget in self.button_frame.winfo_children():
            widget.destroy()


class DehumidFrame(BaseFrame):
    """제습 프레임 클래스"""
    def __init__(self, parent, config, update_handler, font_manager):
        super().__init__(
            parent, 
            config, 
            "제습", 
            config.colors["dehumid_bg"], 
            font_manager
        )
        
        self.update_handler = update_handler
        self.labels = {}
        
        # 제습 정보 라벨 추가
        for key, value in update_handler.dehumid_info.items():
            label = tk.Label(
                self.bottom_frame, 
                text=f"{key}: {value}", 
                bg=self.config.colors["frame_bg"],
                font=self.font_manager.info_font, 
                fg=self.config.colors["text_fg"],
                anchor="w"
            )
            label.pack(pady=self.config.paddings["label_left"][0], padx=self.config.paddings["label_left"][1], fill="x")
            self.labels[key] = label
        
        # 초기 버튼 설정
        self.create_initial_buttons()

    def create_initial_buttons(self):
        """초기 제습 버튼 생성"""
        self.clear_buttons()
        self.create_button("제습 시작", self.start_dehumidification)
        self.create_button("제습 중지", self.stop_dehumidification)

    def start_dehumidification(self):
        """제습 시작 동작"""
        print("제습을 시작합니다.")

    def stop_dehumidification(self):
        """제습 중지 동작"""
        print("제습을 중지합니다.")

    def update_labels(self, data):
        """제습 정보 라벨 업데이트"""
        for key, value in data.items():
            if key in self.labels:
                self.labels[key].config(text=f"{key}: {value}")


class DryFrame(BaseFrame):
    """건조 프레임 클래스"""
    def __init__(self, parent, config, update_handler, font_manager, model_handler, camera_handler):
        super().__init__(
            parent, 
            config, 
            "건조", 
            config.colors["dry_bg"], 
            font_manager
        )
        
        self.update_handler = update_handler
        self.model_handler = model_handler
        self.camera_handler = camera_handler
        
        self.class_probs = None


        self.labels = {}
        self.shoe_types = {0: "부츠", 1: "구두", 2: "슬리퍼", 3: "운동화"}
        self.shoe_english_names = {"부츠": "boots", "구두": "shoes", "슬리퍼": "slipper", "운동화": "sneakers"}
        
        # 건조 정보 라벨 추가
        for key, value in update_handler.dry_info.items():
            label_text = value if key == 'remaining_time' else f"{key}: {value}"
            label = tk.Label(
                self.bottom_frame, 
                text=label_text, 
                bg=self.config.colors["frame_bg"],
                font=self.font_manager.info_font, 
                fg=self.config.colors["text_fg"],
                anchor="e"
            )
            label.pack(pady=self.config.paddings["label_right"][0], padx=self.config.paddings["label_right"][1], fill="x")
            self.labels[key] = label
        
        # 초기 버튼 설정
        self.create_initial_buttons()

    def create_initial_buttons(self):
        """초기 건조 모드 버튼 생성"""
        self.clear_buttons()
        self.create_button("AI 자동 모드", self.set_ai_auto_mode)
        self.create_button("수동 모드", self.set_manual_mode)

    def set_ai_auto_mode(self):
        """AI 자동 모드 설정"""
        self.clear_buttons()
        self.create_button("신발 인식하기", self.toggle_recognition)
        self.create_button("건조 중지하기", self.stop_drying)
        print("AI 자동 모드로 전환합니다.")

    def set_manual_mode(self):
        """수동 모드 설정"""
        self.clear_buttons()
        materials = ["고무", "면", "가죽", "스웨이드"]
        for material in materials:
            self.create_button(material, lambda m=material: print(m))
        print("수동 모드로 전환합니다.")

    def toggle_recognition(self):
        """신발 인식 동작"""
        try:
            image_path = self.camera_handler.capture_and_crop_image()
            if image_path:
                self.class_probs = self.model_handler.predict_shoe_type(image_path)
                predicted_class = np.argmax(self.class_probs)
                predicted_shoe_type = self.shoe_types.get(predicted_class, "알 수 없음")
                
                self.update_handler.dry_info["shoes_type"] = predicted_shoe_type
                self.update_handler.image_path = f'./figs/{self.shoe_english_names[predicted_shoe_type]}.png'
        except Exception as e:
            print(f"신발 확인 중 오류가 발생했습니다: {e}")

        self.clear_buttons()
        self.create_button("신발 확인", self.check_shoe)
        self.create_button("다시 인식하기", self.retry_recognition)

    def check_shoe(self):
        """신발 확인"""
        print(self.update_handler.dry_info["shoes_type"])
        self.create_initial_buttons()

    def retry_recognition(self):
        """신발 재인식"""
        sorted_indices = np.argsort(self.class_probs)[::-1]
        second_highest_class = sorted_indices[1]
        predicted_shoe_type = self.shoe_types.get(second_highest_class, "알 수 없음")
        self.update_handler.dry_info["shoes_type"] = predicted_shoe_type
        self.update_handler.image_path = f'{self.figs_root}/{self.shoe_english_names[predicted_shoe_type]}.png'

        self.create_initial_buttons()


    def stop_drying(self):
        print("건조를 중지합니다.")

    def update_labels(self, data):
        """건조 정보 라벨 업데이트"""
        for key, value in data.items():
            if key != 'remaining_time' and key in self.labels:
                self.labels[key].config(text=f"{key}: {value}")
            elif key == 'remaining_time':
                self.labels[key].config(text=self.format_time(value))

    def format_time(self, seconds):
        """남은 시간을 '시간:분:초' 형식으로 변환"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

# 이전에 작성한 DehumidFrame과 DryFrame 클래스는 그대로 유지

class ShoeCabinetGUI:
    def __init__(self, config, update_handler, serial_port, camera_handler, model_handler):
        # 폰트 관리자 초기화
        self.font_manager = FontManager()
        
        # 기존 초기화 속성들
        self.config = config
        self.update_handler = update_handler
        self.camera_handler = camera_handler
        self.model_handler = model_handler
        self.serial_port = serial_port

        # 창 설정
        self.window = self._setup_window()
        
        # 시작 버튼 생성
        self._create_start_button()

        # 추가 속성 초기화
        self._initialize_additional_attributes()

    def _setup_window(self):
        """창 설정"""
        window = tk.Tk()
        window.title("신발장 상태")
        window.geometry("800x400")
        window.config(bg=self.config.colors["frame_bg"])
        return window

    def _create_start_button(self):
        """시작 버튼 생성"""
        start_button = tk.Button(
            self.window, 
            text="Start", 
            font=self.font_manager.info_font, 
            command=self.start_app,
            relief="solid", 
            bg=self.config.colors["button_bg"], 
            fg=self.config.colors["button_fg"]
        )
        start_button.pack(pady=30)

    def _initialize_additional_attributes(self):
        """추가 속성 초기화"""
        self.prediction_label = None
        self.image_label = None
        self.current_image = None
        self.class_probabilities = None
        
        # 시간 대기
        time.sleep(2)

    def start_app(self):
        """애플리케이션 시작"""
        # 컨테이너 프레임 생성
        container_frame = tk.Frame(self.window, bg=self.config.colors["frame_bg"])
        container_frame.pack(side="top", fill="both", expand=True)

        # 제습 및 건조 프레임 생성
        self.dehumid_frame = DehumidFrame(
            container_frame, 
            self.config, 
            self.update_handler, 
            self.font_manager
        )
        
        self.dry_frame = DryFrame(
            container_frame, 
            self.config, 
            self.update_handler, 
            self.font_manager,
            self.model_handler, 
            self.camera_handler
        )

        # 입력 핀 관련 위젯 추가
        self._add_pin_input_widgets()

        # 시작 버튼 제거
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget('text') == 'Start':
                widget.destroy()

        # 업데이트 콜백 설정
        self.update_handler.set_update_callbacks(
            self.dehumid_frame.update_labels, 
            self.dry_frame.update_labels, 
            self.update_image
        )
        
        # 업데이트 시작
        self.update_handler.start()

    def _add_pin_input_widgets(self):
        """핀 입력 위젯 추가"""
        self.pin_entry_label = tk.Label(
            self.window, 
            text="Control Pin:", 
            font=self.font_manager.info_font, 
            bg=self.config.colors["frame_bg"]
        )
        self.pin_entry_label.pack(pady=10)

        self.pin_entry = tk.Entry(self.window, font=self.font_manager.info_font)
        self.pin_entry.pack(pady=10)

        self.send_button = tk.Button(
            self.window, 
            text="Send", 
            font=self.font_manager.info_font, 
            command=self.send_to_arduino
        )
        self.send_button.pack(pady=10)

    def update_image(self, image_path):
        """이미지 업데이트"""
        try:
            self.current_image = image_path
            print(self.current_image)
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            self.image_label = tk.Label(
                self.window, 
                image=img_tk, 
                bg=self.config.colors["frame_bg"]
            )
            self.image_label.image = img_tk
            self.image_label.place(x=400, y=100)

        except Exception as e:
            print(f"이미지를 불러오는 중 오류가 발생했습니다: {e}")

    def send_to_arduino(self):
        """아두이노로 핀 값 전송"""
        pin = self.pin_entry.get().strip()
        if pin.isdigit():
            pin = int(pin)
            self.serial_port.write(str(pin).encode())
            print(f"Sent pin {pin} to Arduino.")
        else:
            print("Invalid pin number.")

    def run(self):
        """GUI 실행"""
        self.window.mainloop()