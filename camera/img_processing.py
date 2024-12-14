import os
from PIL import Image, ImageEnhance, ImageFilter
import random
import cv2
import numpy as np

# 입력 및 출력 디렉토리 설정
input_dir = "figs"
cropped_dir = os.path.join(input_dir, "cropped")
processed_dir = os.path.join(cropped_dir, "preprocessd")
augmented_dir = os.path.join(processed_dir, "augmented")
resized_dir = os.path.join(augmented_dir, "resized")

# 디렉토리 생성
os.makedirs(cropped_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)
os.makedirs(augmented_dir, exist_ok=True)
os.makedirs(resized_dir, exist_ok=True)

# 이미지 크롭 함수
def crop_image(image, crop_width=1500):
    width, height = image.size
    # 오른쪽에서 crop_width만큼 잘라내기
    return image.crop((0, 0, width - crop_width, height))

# figs 디렉토리의 모든 이미지를 크롭하고 저장
for filename in os.listdir(input_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        input_path = os.path.join(input_dir, filename)
        cropped_path = os.path.join(cropped_dir, filename)
        with Image.open(input_path) as img:
            cropped_img = crop_image(img)
            cropped_img.save(cropped_path)
            print(f"크롭 저장됨: {cropped_path}")

# 이미지 전처리 함수
def gamma_correction(image, gamma):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)

def preprocess_image(input_path, output_path):
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    gamma_corrected = gamma_correction(equalized, gamma=2.0)
    cv2.imwrite(output_path, gamma_corrected)

# 크롭된 이미지를 전처리하고 저장
for filename in os.listdir(cropped_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        input_path = os.path.join(cropped_dir, filename)
        processed_path = os.path.join(processed_dir, filename)
        preprocess_image(input_path, processed_path)
        print(f"전처리 저장됨: {processed_path}")

# 증강을 위한 함수 정의
def add_noise(image):
    np_image = np.array(image)
    noise = np.random.normal(0, 25, np_image.shape)
    noisy_image = np_image + noise
    noisy_image = np.clip(noisy_image, 0, 255)
    return Image.fromarray(noisy_image.astype('uint8'))

def augment_image(image):
    operations = [
        lambda x: x.rotate(random.uniform(-30, 30)),
        lambda x: x.transpose(Image.FLIP_LEFT_RIGHT),
        lambda x: ImageEnhance.Brightness(x).enhance(random.uniform(0.7, 1.3)),
        lambda x: ImageEnhance.Contrast(x).enhance(random.uniform(0.7, 1.3)),
        lambda x: ImageEnhance.Color(x).enhance(random.uniform(0.7, 1.3)),
        lambda x: ImageEnhance.Sharpness(x).enhance(random.uniform(0.7, 1.3)),
        lambda x: add_noise(x),
        lambda x: x.filter(ImageFilter.GaussianBlur(radius=random.uniform(1, 2))),
    ]
    for operation in random.sample(operations, random.randint(1, 3)):
        image = operation(image)
    return image

# 데이터 증강: 데이터 불균형을 고려하여 증강 횟수를 조정
augmentation_counts = {
    "shoes": 21,
    "boots": 21,
    "slipper": 21,
    "sneakers": 12
}

for filename in os.listdir(processed_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        input_path = os.path.join(processed_dir, filename)
        category = "shoes" if "shoes" in filename else \
                   "boots" if "boots" in filename else \
                   "slipper" if "slipper" in filename else \
                   "sneakers"
        augmentation_count = augmentation_counts.get(category, 10)
        
        with Image.open(input_path) as img:
            for i in range(augmentation_count):
                augmented_img = augment_image(img)
                output_path = os.path.join(augmented_dir, f"{os.path.splitext(filename)[0]}_aug{i}.jpg")
                augmented_img.save(output_path)
                print(f"증강 저장됨: {output_path}")

# 증강된 이미지를 96x96 크기로 변환 및 저장
for filename in os.listdir(augmented_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        input_path = os.path.join(augmented_dir, filename)
        resized_path = os.path.join(resized_dir, filename)
        with Image.open(input_path) as img:
            resized_img = img.resize((96, 96))
            resized_img.save(resized_path)
            print(f"크기 변경 저장됨: {resized_path}")
