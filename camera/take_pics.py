from picamera2 import Picamera2
import os

def main():
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()

    print("카메라가 실행 중입니다. 사진을 찍으려면 'y'를 입력하세요. 종료하려면 'q'를 입력하세요.")

    try:
        while True:
            user_input = input("입력: ").strip().lower()
            if user_input == "y":
                while True:
                    filename = input("저장할 파일 이름을 입력하세요 (예: image.jpg): ").strip()
                    if not filename:
                        print("파일 이름을 입력하지 않았습니다. 다시 시도하세요.")
                    elif os.path.exists(filename):
                        print(f"파일 '{filename}'이(가) 이미 존재합니다. 다른 이름을 입력하세요.")
                    else:
                        break
                picam2.capture_file(filename)
                print(f"사진이 저장되었습니다: {filename}")
            elif user_input == "q":
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 입력입니다. 'y' 또는 'q'를 입력하세요.")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()