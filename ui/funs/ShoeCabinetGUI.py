# ShoeCabinetGUI

import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk

class SectionFrame:
    """GUI의 각 구역을 구성하는 프레임 클래스"""
    def __init__(self, parent, bg_color, side, width=250, height=300):
        self.frame = tk.Frame(parent, bg=bg_color, width=width, height=height)
        self.frame.pack(side=side, fill="both", expand=True)
        self.frame.grid_propagate(False)  # 내부 위젯이 크기 조정되지 않도록 설정

    def add_label(self, text, bg, font, fg, anchor, padding, width=None):
        label = tk.Label(self.frame, text=text, bg=bg, font=font, fg=fg, anchor=anchor, width=width)
        label.pack(pady=padding[0], padx=padding[1], fill="x")
        return label


class ShoeCabinetGUI:
    def __init__(self, config):
        self.config = config
        self.window = self.setup_window()
        self.title_font, self.info_font = self.setup_fonts()
        
        self.dehumid_info = {"temp": "25°C", "humid": "40%"}
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화", "remaining_time": 5}
        
        self.create_start_button()

    def setup_window(self):
        window = tk.Tk()
        window.title("신발장 상태")
        window.geometry("800x600")
        window.config(bg=self.config.colors["bg"])  # 전체 배경색 설정
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

    def make_dehumid_frame(self):
        frame = SectionFrame(self.window, self.config.colors["dehumid_bg"], "left")
        self.dehumid_labels = {}
        
        frame.add_label("제습", self.config.colors["dehumid_bg"], self.title_font, 
                        self.config.colors["dehumid_fg"], 'center', self.config.paddings["title"])
        
        for key, value in self.dehumid_info.items():
            self.dehumid_labels[key] = frame.add_label(f"{key}: {value}", 
                                                       self.config.colors["dehumid_bg"], self.info_font,
                                                       self.config.colors["dehumid_text_fg"], "w", 
                                                       self.config.paddings["label_left"])
        return frame.frame

    def make_dry_frame(self):
        frame = SectionFrame(self.window, self.config.colors["dry_bg"], "right")
        self.dry_labels = {}
        
        frame.add_label("건조", self.config.colors["dry_bg"], self.title_font,
                        self.config.colors["dry_fg"], 'center', self.config.paddings["title"])
        
        for key, value in self.dry_info.items():
            if key != "remaining_time":
                self.dry_labels[key] = frame.add_label(f"{key}: {value}", 
                                                       self.config.colors["dry_bg"], self.info_font,
                                                       self.config.colors["dry_text_fg"], "e", 
                                                       self.config.paddings["label_right"])
        
        self.dry_labels["remaining_time_display"] = frame.add_label(
            f"남은 시간: {self.format_time(self.dry_info['remaining_time'])}",
            self.config.colors["dry_bg"], self.info_font,
            self.config.colors["dry_text_fg"], "e", self.config.paddings["label_right"]
        )

        self.add_image_to_frame(frame.frame)
        return frame.frame

    def add_image_to_frame(self, frame, size=(80, 80), padding=(70, 0)):
        try:
            image = Image.open(self.config.shoes_pic_path)
            image = image.resize(size, Image.LANCZOS)
            tk_image = ImageTk.PhotoImage(image)
            image_label = tk.Label(frame, image=tk_image, bg=self.config.colors["dry_bg"])
            image_label.image = tk_image
            image_label.pack(pady=padding)
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
        self.dehumid_frame = self.make_dehumid_frame()
        self.dry_frame = self.make_dry_frame()

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
