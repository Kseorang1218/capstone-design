import tkinter as tk
from tkinter import font

# 윈도우 초기 설정 함수
def setup_window():
    window = tk.Tk()
    window.title("신발장 상태")
    window.geometry("500x320")
    return window

# 폰트 설정 함수
def setup_fonts():
    title_font = font.Font(family="Helvetica", size=14, weight="bold")
    info_font = font.Font(family="Arial", size=10)
    return title_font, info_font

# 프레임 생성 함수
def create_section_frame(parent, bg_color):
    frame = tk.Frame(parent, bg=bg_color, width=250, height=300)
    frame.pack(side="left" if bg_color == "lightblue" else "right", fill="both", expand=True)
    return frame

# 라벨 생성 함수
def create_label(frame, text, bg, font, fg, anchor, padding):
    tk.Label(frame, text=text, bg=bg, font=font, fg=fg, anchor=anchor).pack(pady=padding[0], padx=padding[1], fill="x")

# 섹션 설정 함수
def setup_section(frame, title, bg_color, title_font, info_font, info_data):
    # 제목 설정
    create_label(frame, title, bg_color, title_font, fg="blue" if bg_color == "lightblue" else "darkred", anchor='center', padding=(15, 5))
    
    # 정보 라벨 생성
    for key, value in info_data.items():
        align = 'w' if bg_color == "lightblue" else 'e'
        padding = (10, 0) if align == 'w' else (0, 10)
        create_label(frame, f"{key}: {value}", bg_color, info_font, fg="navy" if bg_color == "lightblue" else "maroon", anchor=align, padding=(3, padding))

# 메인 함수
def main():
    window = setup_window()
    title_font, info_font = setup_fonts()

    # 정보 데이터 정의
    dehumid_info = {"온도": "25°C", "습도": "40%", "상태": "대기중"}
    dry_info = {"온도": "35°C", "습도": "20%", "상태": "건조중", "신발 종류": "운동화"}

    # 제습 섹션 구성
    dehumid_frame = create_section_frame(window, "lightblue")
    setup_section(dehumid_frame, "제습", "lightblue", title_font, info_font, dehumid_info)

    # 건조 섹션 구성
    dry_frame = create_section_frame(window, "lightcoral")
    setup_section(dry_frame, "건조", "lightcoral", title_font, info_font, dry_info)

    window.mainloop()

# 메인 함수 실행
if __name__ == "__main__":
    main()
