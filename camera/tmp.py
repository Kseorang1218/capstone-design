import os
from PIL import Image, ImageEnhance
import random

# 입력 및 출력 디렉토리 설정
input_dir = "figs/cropped"
output_dir = os.path.join(input_dir, "augmented")
os.makedirs(output_dir, exist_ok=True)

# 증강 함수
def augment_image(image):
    operations = [
        lambda x: x.rotate(random.uniform(-30, 30)),  # 회전
        lambda x: x.transpose(Image.FLIP_LEFT_RIGHT),  # 좌우 반전
        lambda x: ImageEnhance.Brightness(x).enhance(random.uniform(0.7, 1.3)),  # 밝기 조정
        lambda x: x.resize((int(x.width * random.uniform(0.9, 1.1)), int(x.height * random.uniform(0.9, 1.1))))  # 크기 조정
    ]
    # 랜덤하게 한두 가지 변환을 적용
    for operation in random.sample(operations, random.randint(1, 2)):
        image = operation(image)
    return image

# 입력 디렉토리의 모든 이미지 증강
for filename in os.listdir(input_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):  # 이미지 파일만 처리
        input_path = os.path.join(input_dir, filename)
        with Image.open(input_path) as img:
            for i in range(5):  # 각 이미지당 5개의 증강 샘플 생성
                augmented_img = augment_image(img)
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_aug{i}.jpg")
                augmented_img.save(output_path)
                print(f"생성됨: {output_path}")
