import os
from PIL import Image, ImageEnhance
import random

# 입력 및 출력 디렉토리 설정
input_dir = "figs"
cropped_dir = os.path.join(input_dir, "cropped")
os.makedirs(cropped_dir, exist_ok=True)

# 이미지 크롭 함수 (550 픽셀 제거)
def crop_image(image):
    width, height = image.size
    cropped_height = max(0, height - 550)  # 높이가 550보다 작을 경우 대비
    return image.crop((0, 0, width, cropped_height))

# figs 디렉토리의 모든 이미지를 크롭하고 저장
for filename in os.listdir(input_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        input_path = os.path.join(input_dir, filename)
        cropped_path = os.path.join(cropped_dir, filename)
        with Image.open(input_path) as img:
            cropped_img = crop_image(img)
            cropped_img.save(cropped_path)
            print(f"크롭 저장됨: {cropped_path}")

# 증강을 위한 디렉토리 설정
output_dir = os.path.join(cropped_dir, "augmented")
os.makedirs(output_dir, exist_ok=True)

# 증강 함수
def augment_image(image):
    operations = [
        lambda x: x.rotate(random.uniform(-30, 30)),  # 회전
        lambda x: x.transpose(Image.FLIP_LEFT_RIGHT),  # 좌우 반전
        lambda x: ImageEnhance.Brightness(x).enhance(random.uniform(0.7, 1.3)),  # 밝기 조정
        lambda x: x.resize((int(x.width * random.uniform(0.9, 1.1)), int(x.height * random.uniform(0.9, 1.1))))  # 크기 조정
    ]
    for operation in random.sample(operations, random.randint(1, 2)):
        image = operation(image)
    return image

# 데이터 증강: 데이터 불균형을 고려하여 증강 횟수를 조정
augmentation_counts = {
    "shoes": 20,
    "boots": 20,
    "slipper": 10,
    "sneakers": 5
}

for filename in os.listdir(cropped_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        input_path = os.path.join(cropped_dir, filename)
        category = "shoes" if "shoes" in filename else \
                   "boots" if "boots" in filename else \
                   "slipper" if "slipper" in filename else \
                   "sneakers"

        with Image.open(input_path) as img:
            for i in range(augmentation_counts[category]):  # 카테고리별 증강 횟수 적용
                augmented_img = augment_image(img)
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_aug{i}.jpg")
                augmented_img.save(output_path)
                print(f"생성됨: {output_path}")