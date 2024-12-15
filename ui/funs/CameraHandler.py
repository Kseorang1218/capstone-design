import time
import os
from PIL import Image
from picamera2 import Picamera2

class CameraHandler:
    """카메라로 사진을 찍고 처리하는 클래스"""
    def __init__(self, save_dir="./data"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)  # 저장 디렉터리 생성
        self.picam2 = Picamera2()  # 카메라 객체 초기화
        self.picam2_configured = False  # 카메라 초기화 상태 추적

    def crop_image(self, image, crop_width = 1500):
        width, height = image.size
        # 오른쪽에서 crop_width만큼 잘라내기
        return image.crop((0, 0, width - crop_width, height))
    
    def capture_and_crop_image(self, filename="pic.jpg"):
        """카메라로 사진을 찍고 아래 550 픽셀을 자른 후 저장"""
        try:
            if not self.picam2_configured:
                # 카메라 초기화가 안 된 경우만 초기화
                config = self.picam2.create_still_configuration()
                self.picam2.configure(config)
                self.picam2.start()
                self.picam2_configured = True
                time.sleep(2)  # 카메라 준비 대기

            image_path = os.path.join(self.save_dir, filename)
            self.picam2.capture_file(image_path)

            print(f"사진이 저장되었습니다: {image_path}")

            # 이미지 열고 아래 550 픽셀 자르기
            image = Image.open(image_path)
            cropped_image = self.crop_image(image)  # crop_image 함수 사용

            cropped_image_path = os.path.join(self.save_dir, "cropped_" + filename)
            cropped_image.save(cropped_image_path)
            print(f"이미지에서 550픽셀을 잘랐습니다: {cropped_image_path}")

            return cropped_image_path
        except Exception as e:
            print(f"카메라 촬영 중 오류가 발생했습니다: {e}")
            return None

    def stop_camera(self):
        """카메라 종료 메소드"""
        if self.picam2_configured:
            self.picam2.stop()
            self.picam2_configured = False
            print("카메라가 종료되었습니다.")
