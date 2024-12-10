import numpy as np
from PIL import Image
from tflite_runtime.interpreter import Interpreter

class ModelHandler:
    """TFLite 모델을 사용하여 예측하는 클래스"""
    def __init__(self, model_path="./model/model.tflite"):
        self.model_path = model_path

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
