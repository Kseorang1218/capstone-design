import tkinter as tk
from tkinter import font

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


'''Initialize'''
def setup_window():
    window = tk.Tk()
    window.title("신발장 상태")
    window.geometry("500x320")
    return window


def setup_fonts():
    title_font = font.Font(family="Helvetica", size=14, weight="bold")
    info_font = font.Font(family="Arial", size=10)
    return title_font, info_font

'''Creat'''
def create_section_frame(parent, bg_color, side):
    frame = tk.Frame(parent, bg=bg_color, width=250, height=300)
    frame.pack(side=side, fill="both", expand=True)
    return frame

def create_label(frame, text, bg, font, fg, anchor, padding):
    tk.Label(frame, text=text, bg=bg, font=font, fg=fg, anchor=anchor).pack(pady=padding[0], padx=padding[1], fill="x")

def setup_section(frame, title, bg_color, title_font, info_font, info_data, title_fg, text_fg, align, padding):
    create_label(frame, title, bg_color, title_font, title_fg, anchor='center', padding=PADDINGS["title"])
    
    for key, value in info_data.items():
        label_padding = PADDINGS["label_left"] if align == 'w' else PADDINGS["label_right"]
        create_label(frame, f"{key}: {value}", bg_color, info_font, text_fg, anchor=align, padding=label_padding)


def add_image_to_frame(frame, image_path, bg_color, size=(50, 50), padding=(70, 0)):
    # 이미지 로드 및 리사이즈
    image = Image.open(image_path)
    image = image.resize(size, Image.LANCZOS)  # 이미지를 지정한 크기로 리사이즈
    tk_image = ImageTk.PhotoImage(image)  # tkinter에서 사용할 이미지로 변환
    
    # 이미지 라벨 생성
    image_label = tk.Label(frame, image=tk_image, bg=bg_color)
    image_label.image = tk_image  # 참조 유지용
    image_label.pack(pady=padding)

def make_dehumid_frame(dehumid_info, window, title_font, info_font):
    dehumid_frame = create_section_frame(window, COLORS["dehumid_bg"], "left")
    setup_section(dehumid_frame, "제습", COLORS["dehumid_bg"], title_font, info_font, 
                  dehumid_info, COLORS["dehumid_fg"], COLORS["dehumid_text_fg"], "w", PADDINGS)

def make_dry_frame(dry_info, window, title_font, info_font):
    dry_frame = create_section_frame(window, COLORS["dry_bg"], "right")
    setup_section(dry_frame, "건조", COLORS["dry_bg"], title_font, info_font, 
                  dry_info, COLORS["dry_fg"], COLORS["dry_text_fg"], "e", PADDINGS)
    
    add_image_to_frame(dry_frame, "./pictures/running_shoe.png", COLORS["dry_bg"], size=(60, 60))

def main():
    window = setup_window()
    title_font, info_font = setup_fonts()

    dehumid_info = {"temp": "25°C", "humid": "40%", "status": "대기중"}
    dry_info = {"temp": "35°C", "humid": "20%", "status": "건조중", "shoes_type": "운동화"}

    make_dehumid_frame(dehumid_info, window, title_font, info_font)
    make_dry_frame(dry_info, window, title_font, info_font)

    window.mainloop()

if __name__ == "__main__":
    main()
