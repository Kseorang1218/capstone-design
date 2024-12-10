import time
import os
from PIL import Image

from picamera2 import Picamera2

import numpy as np
from tflite_runtime.interpreter import Interpreter

class CameraHandler:
    """카메라로 사진을 찍고 처리하는 클래스"""
    def __init__(self, save_dir="./data", model_path="./model/model.tflite"):
        self.save_dir = save_dir
        self.model_path = model_path
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

    def predict_shoe_type(self, image_path):
        """TFLite 모델을 사용하여 신발 유형을 예측"""
        try:
            # 모델 로드
            interpreter = Interpreter(model_path=self.model_path)
            interpreter.allocate_tensors()

            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            input_shape = input_details[0]['shape'][1:3]  # (높이, 너비)
            input_dtype = input_details[0]['dtype']

            # 이미지 전처리
            image = Image.open(image_path).convert("L")  # 그레이스케일로 변환
            image = image.resize(input_shape)  # 모델 입력 크기에 맞게 리사이즈
            input_data = np.expand_dims(np.array(image) / 255.0, axis=(0, -1))  # 정규화 및 채널 차원 추가
            input_data = input_data.astype(input_dtype)

            # 모델 예측
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])[0]

            # 클래스별 확률 계산
            class_probabilities = "\n".join([f"클래스 {i}: {prob:.2f}" for i, prob in enumerate(output_data)])
            predicted_class = np.argmax(output_data)
            return f"예측 결과: 클래스 {predicted_class}\n\n클래스별 확률:\n{class_probabilities}"
        except Exception as e:
            print(f"모델 예측 중 오류가 발생했습니다: {e}")
            return "예측 실패"