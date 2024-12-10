import time
import os
from PIL import Image
from picamera2 import Picamera2

class CameraHandler:
    """카메라로 사진을 찍고 처리하는 클래스"""
    def __init__(self, save_dir="./data"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)  # 저장 디렉터리 생성

    def crop_image(self, image):
        """이미지에서 하단 550픽셀을 자르는 함수"""
        width, height = image.size
        cropped_height = max(0, height - 550)  # 높이가 550보다 작을 경우 대비
        return image.crop((0, 0, width, cropped_height))  # (왼쪽, 위쪽, 오른쪽, 아래쪽)
        
    def capture_and_crop_image(self, filename="pic.jpg"):
        """카메라로 사진을 찍고 아래 550 픽셀을 자른 후 저장"""
        try:
            picam2 = Picamera2()
            config = picam2.create_still_configuration()
            picam2.configure(config)
            picam2.start()
            time.sleep(2)  # 카메라 준비 대기

            image_path = os.path.join(self.save_dir, filename)
            picam2.capture_file(image_path)
            picam2.stop()

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
