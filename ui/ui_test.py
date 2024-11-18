import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk

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
        self.dehumid_info = {"temp": "25°C", "humid": "40%"}
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화", "remaining_time": 5}  # 10초로 설정해서 테스트
        
        # 시작 버튼 생성
        self.create_start_button()

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
                         COLORS["dehumid_fg"], 'center', PADDINGS["title"] )
        
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
            if key != "remaining_time":  # remaining_time은 제외하고 라벨을 생성
                self.dry_labels[key] = self.create_label(
                    frame, f"{key}: {self.dry_info[key]}", 
                    COLORS["dry_bg"], self.info_font,
                    COLORS["dry_text_fg"], "e", PADDINGS["label_right"]
                )
        
        # 건조 완료 시간 라벨
        self.dry_labels["remaining_time_display"] = self.create_label(
            frame, f"남은 시간: {self.format_time(self.dry_info['remaining_time'])}",
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
            # 1초마다 갱신
            self.window.after(1000, self.update_dry_time)
        else:
            self.dry_info["status"] = "건조 완료"
            self.dry_labels["status"].config(text=f"상태: {self.dry_info['status']}")
            
            # 건조 완료 메시지 팝업
            self.show_drying_complete_message()

    def show_drying_complete_message(self):
        """건조 완료 메시지 팝업"""
        messagebox.showinfo("건조 완료", "건조가 끝났습니다!", icon='info')
        # 건조 완료 후, reset_app 호출
        self.reset_app()

    def create_start_button(self):
        """Start 버튼을 만들고 버튼 클릭 시 GUI 시작"""
        start_button = tk.Button(self.window, text="Start", font=self.info_font, command=self.start_app)
        start_button.pack(pady=20)

    def start_app(self):
        """Start 버튼 클릭 후 GUI 시작"""
        # "Start" 버튼을 숨기고, 제습/건조 프레임을 표시
        self.dehumid_frame = self.make_dehumid_frame()
        self.dry_frame = self.make_dry_frame()
        
        # Start 버튼 제거
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()
        
        # 업데이트 시작
        self.update_dry_time()

    def reset_app(self):
        """건조 완료 후 앱을 초기화하고 Start 버튼 화면으로 돌아가기"""
        self.dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화", "remaining_time": 5}
        
        # 모든 프레임을 제거하고 "Start" 버튼만 보이게 함
        for widget in self.window.winfo_children():
            widget.destroy()
        
        self.create_start_button()

    def update_labels(self):
        # 제습 영역 라벨 업데이트
        for key, label in self.dehumid_labels.items():
            label.config(text=f"{key}: {self.dehumid_info[key]}")
        
        # 건조 영역 라벨 업데이트
        for key, label in self.dry_labels.items():
            label.config(text=f"{key}: {self.dry_info[key]}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ShoeCabinetGUI()
    app.run()
